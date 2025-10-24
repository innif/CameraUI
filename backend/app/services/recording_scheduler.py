import asyncio
import logging
from datetime import datetime, time
from typing import Optional

from app.services.obs_service import OBSService
from app.services.file_service import FileService
from app.core.config import settings

logger = logging.getLogger(__name__)


class RecordingScheduler:
    """Service for automatic recording scheduling"""
    
    def __init__(self, obs_service: OBSService, file_service: FileService):
        self.obs_service = obs_service
        self.file_service = file_service
        self.auto_started = False
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the scheduler"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Recording scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Recording scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self._running:
            try:
                await self._check_recording_schedule()
                await self._check_shutdown_schedule()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
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
        if self._is_shutdown_time():
            logger.warning("Shutdown time reached - initiating system shutdown")
            # Note: This would require appropriate permissions
            # In production, you might want to use systemd or another service
            try:
                import subprocess
                subprocess.run(["shutdown", "-h", "now"])
            except Exception as e:
                logger.error(f"Failed to shutdown system: {e}")
    
    async def start_recording(self) -> bool:
        """Manually start recording"""
        if not self.obs_service.connected:
            logger.error("Cannot start recording: OBS not connected")
            return False
        
        if self.obs_service.recording:
            logger.warning("Recording already in progress")
            return False
        
        try:
            # Reload camera before starting
            await asyncio.to_thread(self.obs_service.reload_camera)
            await asyncio.sleep(1)  # Give camera time to reload
            
            # Start recording
            video_file = await self.obs_service.start_recording()
            
            if video_file:
                # Add to file manager
                self.file_service.add_file(video_file)
                
                # Save metadata
                video_file.to_json_file(self.file_service.video_directory)
                
                logger.info(f"Recording started successfully: {video_file.filename}")
                return True
            else:
                logger.error("Failed to start recording: No file created")
                return False
                
        except Exception as e:
            logger.exception(e)
            logger.error("Error starting recording")
            return False
    
    async def stop_recording(self) -> bool:
        """Manually stop recording"""
        if not self.obs_service.connected:
            logger.error("Cannot stop recording: OBS not connected")
            return False
        
        if not self.obs_service.recording:
            logger.warning("No recording in progress")
            return False
        
        try:
            # Stop recording
            video_file = await self.obs_service.stop_recording()
            
            if video_file:
                # Update metadata
                video_file.to_json_file(self.file_service.video_directory)
                
                logger.info(f"Recording stopped successfully: {video_file.filename}")
                return True
            else:
                logger.error("Failed to stop recording")
                return False
                
        except Exception as e:
            logger.exception(e)
            logger.error("Error stopping recording")
            return False
    
    def _is_recording_time(self) -> bool:
        """Check if current time is within recording schedule"""
        now = datetime.now()
        current_time = now.time()
        current_weekday = now.weekday()
        
        # Check if today is a recording day
        if current_weekday not in settings.WEEKDAYS:
            return False
        
        # Check if current time is within recording hours
        return settings.START_TIME <= current_time <= settings.END_TIME
    
    def _is_shutdown_time(self) -> bool:
        """Check if it's time to shutdown"""
        now = datetime.now().time()
        shutdown_time = settings.SHUTDOWN_TIME
        
        # Create a 10-second window around shutdown time
        # This is simplified - in production you'd want more robust logic
        return now.hour == shutdown_time.hour and now.minute == shutdown_time.minute
