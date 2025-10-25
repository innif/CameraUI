import asyncio
import logging
from typing import Optional
import obsws_python as obs
from datetime import datetime

from app.models.video import VideoFile

logger = logging.getLogger(__name__)


class OBSService:
    """Service for interacting with OBS Studio"""
    
    def __init__(self):
        self.client: Optional[obs.ReqClient] = None
        self.event_client: Optional[obs.EventClient] = None
        self.connected: bool = False
        self.recording: bool = False
        self.muted: bool = False
        self.current_file: Optional[VideoFile] = None
        self.show_logo: bool = True
        
        # Connection settings (will be set via configure method)
        self.host: str = "localhost"
        self.port: int = 4455
        self.password: str = ""
        
        # Background connection task
        self._connection_task: Optional[asyncio.Task] = None
    
    async def configure(self, host: str, port: int, password: str, show_logo: bool = True):
        """Configure OBS connection settings"""
        self.host = host
        self.port = port
        self.password = password
        self.show_logo = show_logo
        
        # Start connection loop
        if self._connection_task is None or self._connection_task.done():
            self._connection_task = asyncio.create_task(self._connection_loop())
    
    async def _connection_loop(self):
        """Background task to maintain OBS connection"""
        while True:
            if not self.connected:
                await self._try_connect()
            else:
                # Verify recording status if we think we're recording
                await self._verify_recording_status()
            await asyncio.sleep(1)
    
    async def _try_connect(self):
        """Try to connect to OBS"""
        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password
            )
            self.event_client = obs.EventClient(
                host=self.host,
                port=self.port,
                password=self.password,
                subs=obs.Subs.INPUTVOLUMEMETERS
            )
            
            # Get current recording status
            status = self.client.get_record_status()
            self.recording = status.output_active
            
            self.connected = True
            self.unmute_video()
            self.set_logo(self.show_logo)
            
            logger.info("Successfully connected to OBS")
        except Exception as e:
            self.connected = False
            logger.warning(f"Failed to connect to OBS: {e}")
    
    async def _verify_recording_status(self):
        """Verify that the actual recording status matches our internal state"""
        try:
            if self.client:
                status = await asyncio.to_thread(self.client.get_record_status)
                actual_recording = status.output_active

                # If there's a mismatch, update our state and log it
                if actual_recording != self.recording:
                    logger.warning(
                        f"Recording status mismatch detected! "
                        f"Expected: {self.recording}, Actual: {actual_recording}. "
                        f"Synchronizing state..."
                    )
                    self.recording = actual_recording

                    # If recording stopped unexpectedly, clear current file
                    if not actual_recording and self.current_file:
                        logger.warning(f"Recording stopped unexpectedly: {self.current_file.filename}")
                        self.current_file = None
        except Exception as e:
            logger.debug(f"Could not verify recording status: {e}")
            # Don't disconnect on verification errors, just skip this check

    async def disconnect(self):
        """Disconnect from OBS"""
        if self._connection_task:
            self._connection_task.cancel()

        self.connected = False
        self.client = None
        self.event_client = None
    
    async def start_recording(self) -> Optional[VideoFile]:
        """Start recording"""
        if not self.connected:
            logger.error("Cannot start recording: Not connected to OBS")
            return None

        if self.recording:
            logger.warning("Recording already running")
            return None

        try:
            # Create new video file
            self.current_file = VideoFile()

            # Set filename in OBS profile
            self.client.set_profile_parameter("Output", "FilenameFormatting", self.current_file.filename)

            # Start recording
            self.client.start_record()
            self.recording = True

            logger.info(f"Started recording: {self.current_file.filename}")
            return self.current_file

        except Exception as e:
            self.connected = False
            logger.exception(f"Error starting recording: {e}")
            raise Exception("Error starting recording")
    
    async def stop_recording(self) -> Optional[VideoFile]:
        """Stop recording"""
        if not self.connected:
            logger.error("Cannot stop recording: Not connected to OBS")
            return None

        if not self.recording:
            logger.warning("No recording running")
            return None

        try:
            # Stop recording
            self.client.stop_record()
            self.recording = False

            logger.info("Recording stopped")

            # Return the file that was recorded
            file = self.current_file
            self.current_file = None
            return file

        except Exception as e:
            self.connected = False
            logger.exception(f"Error stopping recording: {e}")
            raise Exception("Error stopping recording")
    
    async def get_screenshot(self) -> Optional[str]:
        """Get screenshot from OBS as base64"""
        if not self.connected:
            logger.error("Cannot get screenshot: Not connected to OBS")
            return None

        try:
            # Get screenshot from "main" source
            result = await asyncio.to_thread(
                self.client.get_source_screenshot,
                name="main",
                img_format="jpg",
                width=512,
                height=288,
                quality=50
            )
            return result.image_data

        except Exception as e:
            self.connected = False
            logger.exception(f"Error getting screenshot: {e}")
            raise Exception("Error getting screenshot")
    
    def mute_video(self):
        """Mute video by switching to 'muted' scene"""
        if not self.connected:
            logger.warning("Cannot mute video: Not connected to OBS")
            return

        try:
            self.client.set_current_program_scene("muted")
            self.muted = True
            logger.info("Video muted")

        except Exception as e:
            self.connected = False
            logger.exception(f"Error muting video: {e}")
            raise Exception("Error muting video")
    
    def unmute_video(self):
        """Unmute video by switching back to 'main' scene"""
        if not self.connected:
            logger.warning("Cannot unmute video: Not connected to OBS")
            return

        try:
            self.client.set_current_program_scene("main")
            self.muted = False
            logger.info("Video unmuted")

        except Exception as e:
            self.connected = False
            logger.exception(f"Error unmuting video: {e}")
            raise Exception("Error unmuting video")
    
    def reload_camera(self):
        """Reload camera source by disabling and re-enabling it"""
        if not self.connected:
            logger.warning("Cannot reload camera: Not connected to OBS")
            return

        try:
            # Get current camera settings
            settings = self.client.get_input_settings("Camera")

            # Disable camera
            logger.info("Disabling camera")
            self.client.set_input_settings("Camera", {"disable": True}, True)

        except Exception as e:
            self.connected = False
            logger.exception(f"Error disabling camera: {e}")
            raise Exception("Error disabling camera")
    
    def set_logo(self, visible: bool = True):
        """Set logo visibility by enabling/disabling the 'hide' filter"""
        if not self.connected:
            logger.warning("Cannot set logo: Not connected to OBS")
            return

        try:
            # Enable/disable the "hide" filter on the "logo" source
            # If visible=True, we disable the "hide" filter (to show the logo)
            # If visible=False, we enable the "hide" filter (to hide the logo)
            self.client.set_source_filter_enabled("logo", "hide", not visible)
            logger.info(f"Logo visibility set to: {visible}")

        except Exception as e:
            self.connected = False
            logger.exception(f"Error setting logo visibility: {e}")
            raise Exception("Error setting logo visibility")
    
    async def check_audio(self) -> float:
        """Check audio levels and return range (max - min)"""
        if not self.connected:
            logger.warning("Cannot check audio: Not connected to OBS")
            return 0

        try:
            vol = {"min": 1, "max": 0}

            def on_input_volume_meters(data):
                """Callback to collect audio volume data"""
                for source in data.inputs:
                    if source.get("inputName") == "Camera":
                        try:
                            val = source.get("inputLevelsMul")[0][0]
                        except:
                            continue
                        if val < vol["min"]:
                            vol["min"] = val
                        if val > vol["max"]:
                            vol["max"] = val

            # Register callback
            self.event_client.callback.register(on_input_volume_meters)

            # Wait for 2 seconds to collect data
            await asyncio.sleep(2)

            # Deregister callback
            self.event_client.callback.deregister(on_input_volume_meters)

            # Return the range
            return vol["max"] - vol["min"]

        except Exception as e:
            logger.exception(f"Error checking audio: {e}")
            return 0
    
    def get_status(self) -> dict:
        """Get current OBS status"""
        return {
            "is_connected": self.connected,
            "is_recording": self.recording,
            "muted": self.muted,
            "current_file": self.current_file.filename if self.current_file else None
        }
