import asyncio
import logging
from datetime import datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from app.services.obs_service import OBSService
from app.services.file_service import FileService
from app.core.config import settings

logger = logging.getLogger(__name__)


class RecordingScheduler:
    """Service for automatic recording scheduling with robust error handling"""

    def __init__(self, obs_service: OBSService, file_service: FileService):
        self.obs_service = obs_service
        self.file_service = file_service
        self.auto_started = False
        self._task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_cleanup: Optional[datetime] = None

        # Locks to prevent concurrent start/stop operations
        self._recording_lock = asyncio.Lock()

        # Resilience tracking
        self._start_attempts = 0
        self._stop_attempts = 0
        self._last_start_error: Optional[str] = None
        self._last_stop_error: Optional[str] = None
    
    async def start(self):
        """Start the scheduler"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Recording scheduler started")
        logger.info(f"Recording schedule: {settings.WEEKDAYS} from {settings.START_TIME} to {settings.END_TIME}")
    
    async def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Recording scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop with robust error handling"""
        while self._running:
            try:
                await self._check_recording_schedule()
                await self._check_shutdown_schedule()
            except asyncio.CancelledError:
                logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Unexpected error in scheduler loop: {e}")
                # Don't stop the scheduler on errors, just log and continue
                await asyncio.sleep(5)  # Wait a bit before retrying
                continue

            await asyncio.sleep(1)
    
    async def _check_recording_schedule(self):
        """Check if recording should start or stop based on schedule"""
        is_recording_time = self._is_recording_time()
        
        if is_recording_time:
            # Should be recording
            if not self.auto_started and not self.obs_service.recording:
                logger.info("Starting automatic recording")
                success = await self.start_recording()
                if success:
                    self.auto_started = True
        else:
            # Should not be recording
            if self.obs_service.recording and self.auto_started:
                logger.info("Stopping automatic recording")
                success = await self.stop_recording()
                if success:
                    self.auto_started = False
    
    async def _check_shutdown_schedule(self):
        """Check if system should shutdown"""
        pass
        # if self._is_shutdown_time():
        #     logger.warning("Shutdown time reached - initiating system shutdown")
        #     # Note: This would require appropriate permissions
        #     # In production, you might want to use systemd or another service
        #     try:
        #         import subprocess
        #         subprocess.run(["shutdown", "-h", "now"])
        #     except Exception as e:
        #         logger.error(f"Failed to shutdown system: {e}")
    
    async def start_recording(self) -> bool:
        """
        Start recording with retry logic and locking to prevent race conditions.

        Returns:
            bool: True if recording started successfully, False otherwise
        """
        # Use lock to prevent concurrent start operations
        async with self._recording_lock:
            if not self.obs_service.connected:
                self._last_start_error = "OBS not connected"
                logger.error(f"Cannot start recording: {self._last_start_error}")
                return False

            if self.obs_service.recording:
                logger.warning("Recording already in progress")
                return False

            # Retry logic for robustness
            max_retries = settings.RECORDING_START_RETRIES
            retry_delay = settings.RECORDING_RETRY_DELAY

            for attempt in range(1, max_retries + 1):
                try:
                    self._start_attempts += 1
                    logger.info(f"Starting recording (attempt {attempt}/{max_retries})...")

                    # Reload camera before starting (helps with stability)
                    try:
                        await asyncio.to_thread(self.obs_service.reload_camera)
                        logger.info("Camera reloaded successfully")
                    except Exception as cam_error:
                        logger.warning(f"Camera reload failed (attempt {attempt}/{max_retries}): {cam_error}")
                        # Continue anyway - camera reload is best-effort

                    # Give camera time to stabilize
                    await asyncio.sleep(1)

                    # Start recording
                    video_file = await self.obs_service.start_recording()

                    if video_file:
                        # Add to file manager
                        self.file_service.add_file(video_file)

                        # Save metadata
                        try:
                            video_file.to_json_file(self.file_service.video_directory)
                        except Exception as meta_error:
                            logger.warning(f"Failed to save metadata: {meta_error}")
                            # Continue - metadata can be regenerated later

                        self._last_start_error = None
                        logger.info(
                            f"✓ Recording started successfully: {video_file.filename} "
                            f"(attempt {attempt}/{max_retries})"
                        )
                        return True
                    else:
                        raise Exception("No file created by OBS")

                except Exception as e:
                    self._last_start_error = str(e)
                    logger.error(
                        f"Failed to start recording (attempt {attempt}/{max_retries}): {e}"
                    )

                    # Wait before retry (except on last attempt)
                    if attempt < max_retries:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(
                            f"✗ Failed to start recording after {max_retries} attempts. "
                            f"Last error: {self._last_start_error}"
                        )

            return False
    
    async def stop_recording(self) -> bool:
        """
        Stop recording with retry logic and locking to prevent race conditions.

        Returns:
            bool: True if recording stopped successfully, False otherwise
        """
        # Use lock to prevent concurrent stop operations
        async with self._recording_lock:
            if not self.obs_service.connected:
                self._last_stop_error = "OBS not connected"
                logger.error(f"Cannot stop recording: {self._last_stop_error}")
                return False

            if not self.obs_service.recording:
                logger.warning("No recording in progress")
                return False

            # Retry logic for robustness
            max_retries = settings.RECORDING_START_RETRIES  # Reuse same setting
            retry_delay = settings.RECORDING_RETRY_DELAY

            for attempt in range(1, max_retries + 1):
                try:
                    self._stop_attempts += 1
                    logger.info(f"Stopping recording (attempt {attempt}/{max_retries})...")

                    # Stop recording
                    video_file = await self.obs_service.stop_recording()

                    if video_file:
                        # Update metadata
                        try:
                            video_file.to_json_file(self.file_service.video_directory)
                        except Exception as meta_error:
                            logger.warning(f"Failed to save metadata: {meta_error}")
                            # Continue - metadata can be regenerated later

                        self._last_stop_error = None
                        logger.info(
                            f"✓ Recording stopped successfully: {video_file.filename} "
                            f"(attempt {attempt}/{max_retries})"
                        )
                        return True
                    else:
                        raise Exception("No file returned from OBS")

                except Exception as e:
                    self._last_stop_error = str(e)
                    logger.error(
                        f"Failed to stop recording (attempt {attempt}/{max_retries}): {e}"
                    )

                    # Wait before retry (except on last attempt)
                    if attempt < max_retries:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(
                            f"✗ Failed to stop recording after {max_retries} attempts. "
                            f"Last error: {self._last_stop_error}"
                        )

            return False
    
    def _is_recording_time(self) -> bool:
        """Check if current time is within recording schedule"""
        # Get current time in local timezone
        local_tz = ZoneInfo(settings.TIMEZONE)
        now = datetime.now(timezone.utc).astimezone(local_tz)
        current_time = now.time()
        current_weekday = now.weekday()

        # Check if today is a recording day
        if current_weekday not in settings.WEEKDAYS:
            return False

        # Check if current time is within recording hours
        return settings.START_TIME <= current_time <= settings.END_TIME
    
    def _is_shutdown_time(self) -> bool:
        """Check if it's time to shutdown"""
        # Get current time in local timezone
        local_tz = ZoneInfo(settings.TIMEZONE)
        now = datetime.now(timezone.utc).astimezone(local_tz).time()
        shutdown_time = settings.SHUTDOWN_TIME

        # Create a 10-second window around shutdown time
        # This is simplified - in production you'd want more robust logic
        return now.hour == shutdown_time.hour and now.minute == shutdown_time.minute

    def get_next_scheduled_recording(self) -> Optional[dict]:
        """Get information about the next scheduled recording"""
        local_tz = ZoneInfo(settings.TIMEZONE)
        now = datetime.now(timezone.utc).astimezone(local_tz)

        # If weekdays is empty, no recordings are scheduled
        if not settings.WEEKDAYS:
            return None

        # Try to find the next recording time within the next 7 days
        for days_ahead in range(8):
            check_date = now + timedelta(days=days_ahead)
            check_weekday = check_date.weekday()

            # Skip if not a recording day
            if check_weekday not in settings.WEEKDAYS:
                continue

            # For today, check if the start time hasn't passed yet
            if days_ahead == 0:
                current_time = now.time()
                # If we're before the start time, that's our next recording
                if current_time < settings.START_TIME:
                    next_recording = datetime.combine(check_date.date(), settings.START_TIME, tzinfo=local_tz)
                    return self._format_next_recording(next_recording, now)
                # If we're currently recording, next is tomorrow or next recording day
                continue
            else:
                # For future days, use the start time
                next_recording = datetime.combine(check_date.date(), settings.START_TIME, tzinfo=local_tz)
                return self._format_next_recording(next_recording, now)

        return None

    def _format_next_recording(self, next_recording: datetime, now: datetime) -> dict:
        """Format next recording information for display"""
        # German weekday names
        weekday_names = [
            "Montag", "Dienstag", "Mittwoch", "Donnerstag",
            "Freitag", "Samstag", "Sonntag"
        ]

        # Calculate time difference
        time_until = next_recording - now
        days_until = time_until.days
        hours_until = time_until.seconds // 3600
        minutes_until = (time_until.seconds % 3600) // 60

        # Format day description
        if days_until == 0:
            day_description = "heute"
        elif days_until == 1:
            day_description = "morgen"
        else:
            day_description = weekday_names[next_recording.weekday()]

        # Format time
        time_str = next_recording.strftime("%H:%M")

        return {
            "next_recording_time": next_recording.isoformat(),
            "day_description": day_description,
            "time_str": time_str,
            "days_until": days_until,
            "hours_until": hours_until,
            "minutes_until": minutes_until,
            "weekday": weekday_names[next_recording.weekday()],
            "formatted_message": f"Die Aufnahme startet automatisch {day_description} um {time_str} Uhr"
        }

    async def _cleanup_loop(self):
        """Periodic cleanup loop for old files and subclips with robust error handling"""
        while self._running:
            try:
                await self._run_cleanup()
            except asyncio.CancelledError:
                logger.info("Cleanup loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Unexpected error in cleanup loop: {e}")
                # Don't stop the cleanup loop on errors
                await asyncio.sleep(60)  # Wait a minute before retrying
                continue

            # Run cleanup based on configured interval
            await asyncio.sleep(settings.cleanup_interval)

    async def _run_cleanup(self):
        """Run cleanup tasks"""
        now = datetime.now(timezone.utc)
        cleanup_interval = timedelta(seconds=settings.cleanup_interval)

        # Run cleanup if it hasn't been done yet or if enough time has passed
        if self._last_cleanup is None or (now - self._last_cleanup) >= cleanup_interval:
            logger.info("Running periodic cleanup tasks")

            # Delete old video files
            if settings.delete_age:
                deleted_count = await self.file_service.delete_old_files(settings.delete_age)
                logger.info(f"Cleanup: Deleted {deleted_count} old video files")

            # Delete subclips (older than configured minimum age)
            subclip_count = await self.file_service.delete_subclips(settings.subclip_min_age)
            logger.info(f"Cleanup: Deleted {subclip_count} subclip files (older than {settings.subclip_min_age})")

            # Delete old log files (keep logs for the same duration as videos)
            if settings.delete_age:
                log_count = await self.file_service.delete_old_logs(
                    settings.delete_age,
                    settings.LOGS_DIRECTORY
                )
                logger.info(f"Cleanup: Deleted {log_count} old log files")

            self._last_cleanup = now
            logger.info("Periodic cleanup completed")
