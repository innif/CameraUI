import asyncio
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class AudioMonitorService:
    """
    Service for continuous audio monitoring and automatic recovery.

    This service runs independently in the background and:
    - Periodically checks audio levels
    - Automatically attempts to fix audio issues
    - Does NOT interrupt ongoing recordings
    - Logs all recovery attempts
    """

    def __init__(self, obs_service, config):
        self.obs_service = obs_service
        self.config = config
        self.running = False
        self._monitor_task: Optional[asyncio.Task] = None

        # Failure tracking
        self.consecutive_failures = 0
        self.last_check_time: Optional[datetime] = None
        self.last_failure_time: Optional[datetime] = None
        self.total_checks = 0
        self.total_failures = 0
        self.camera_reloads = 0

    async def start(self):
        """Start the audio monitoring service"""
        if self.running:
            logger.warning("Audio monitor already running")
            return

        self.running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(
            f"Audio monitor started (interval: {self.config.AUDIO_CHECK_INTERVAL}s, "
            f"threshold: {self.config.AUDIO_FAILURE_THRESHOLD} failures)"
        )

    async def stop(self):
        """Stop the audio monitoring service"""
        self.running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Audio monitor stopped")

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(self.config.AUDIO_CHECK_INTERVAL)

                # Only check if OBS is connected
                if not self.obs_service.connected:
                    logger.debug("Audio check skipped: OBS not connected")
                    continue

                await self._perform_audio_check()

            except asyncio.CancelledError:
                logger.info("Audio monitor loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in audio monitor loop: {e}")
                # Don't stop the loop on errors, just log and continue
                await asyncio.sleep(5)  # Wait a bit before retrying

    async def _perform_audio_check(self):
        """
        Perform a single audio check with retries.
        This is the core logic that detects and fixes audio issues.
        """
        self.total_checks += 1
        self.last_check_time = datetime.now()

        logger.debug(f"Performing audio check #{self.total_checks}")

        # Try multiple times to get a valid audio reading
        audio_detected = False
        last_range = 0.0

        for attempt in range(1, self.config.AUDIO_CHECK_RETRIES + 1):
            try:
                # Perform the audio check
                audio_range = await self.obs_service.check_audio()
                last_range = audio_range

                # Check if audio is present
                if audio_range > self.config.AUDIO_THRESHOLD:
                    audio_detected = True
                    logger.debug(
                        f"Audio check #{self.total_checks} attempt {attempt}/{self.config.AUDIO_CHECK_RETRIES}: "
                        f"SUCCESS (range: {audio_range:.4f})"
                    )
                    break
                else:
                    logger.warning(
                        f"Audio check #{self.total_checks} attempt {attempt}/{self.config.AUDIO_CHECK_RETRIES}: "
                        f"NO AUDIO (range: {audio_range:.4f}, threshold: {self.config.AUDIO_THRESHOLD})"
                    )

                    # Wait before retry (except on last attempt)
                    if attempt < self.config.AUDIO_CHECK_RETRIES:
                        await asyncio.sleep(1)

            except Exception as e:
                logger.error(
                    f"Audio check #{self.total_checks} attempt {attempt}/{self.config.AUDIO_CHECK_RETRIES} "
                    f"failed with exception: {e}"
                )
                if attempt < self.config.AUDIO_CHECK_RETRIES:
                    await asyncio.sleep(1)

        # Handle result
        if audio_detected:
            # Audio is OK - reset failure counter
            if self.consecutive_failures > 0:
                logger.info(
                    f"Audio recovered! (after {self.consecutive_failures} consecutive failures)"
                )
            self.consecutive_failures = 0
        else:
            # Audio check failed
            self.consecutive_failures += 1
            self.total_failures += 1
            self.last_failure_time = datetime.now()

            logger.error(
                f"Audio check FAILED (consecutive failures: {self.consecutive_failures}/"
                f"{self.config.AUDIO_FAILURE_THRESHOLD}, "
                f"last range: {last_range:.4f})"
            )

            # Check if we need to reload the camera
            if self.consecutive_failures >= self.config.AUDIO_FAILURE_THRESHOLD:
                await self._attempt_camera_reload()

    async def _attempt_camera_reload(self):
        """
        Attempt to fix audio issues by reloading the camera.
        This is done carefully to avoid interrupting recordings.
        """
        logger.warning(
            f"Audio failure threshold reached ({self.consecutive_failures}/"
            f"{self.config.AUDIO_FAILURE_THRESHOLD}). Attempting camera reload..."
        )

        # Check if we're currently recording
        if self.obs_service.recording:
            logger.error(
                "⚠️  CRITICAL: Audio failure detected during active recording! "
                "Camera reload SKIPPED to preserve recording. Manual intervention may be required."
            )
            # Don't reload during recording to avoid interrupting it
            return

        try:
            # Reload the camera
            self.camera_reloads += 1
            logger.info(f"Reloading camera (reload #{self.camera_reloads})...")

            # Use the existing reload_camera method
            await asyncio.to_thread(self.obs_service.reload_camera)

            # Wait for camera to stabilize
            await asyncio.sleep(2)

            # Reset consecutive failures counter (but not total failures)
            self.consecutive_failures = 0

            logger.info(f"Camera reload #{self.camera_reloads} completed")

            # Perform immediate verification check
            logger.info("Performing verification audio check...")
            await asyncio.sleep(1)  # Give camera time to initialize
            verification_range = await self.obs_service.check_audio()

            if verification_range > self.config.AUDIO_THRESHOLD:
                logger.info(
                    f"✓ Camera reload successful! Audio detected (range: {verification_range:.4f})"
                )
            else:
                logger.error(
                    f"✗ Camera reload may have failed. Still no audio detected "
                    f"(range: {verification_range:.4f}). Will retry on next check."
                )

        except Exception as e:
            logger.exception(f"Error during camera reload: {e}")

    def get_status(self) -> dict:
        """Get current status of the audio monitor"""
        return {
            "running": self.running,
            "consecutive_failures": self.consecutive_failures,
            "total_checks": self.total_checks,
            "total_failures": self.total_failures,
            "camera_reloads": self.camera_reloads,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "check_interval": self.config.AUDIO_CHECK_INTERVAL,
            "failure_threshold": self.config.AUDIO_FAILURE_THRESHOLD,
        }
