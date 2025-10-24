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
            logger.debug(f"Failed to connect to OBS: {e}")
    
    async def disconnect(self):
        """Disconnect from OBS"""
        if self._connection_task:
            self._connection_task.cancel()
        
        self.connected = False
        self.client = None
        self.event_client = None
    
    async def start_recording(self) -> Optional[VideoFile]:
        """Start recording"""
        pass
    
    async def stop_recording(self) -> Optional[VideoFile]:
        """Stop recording"""
        pass
    
    async def get_screenshot(self) -> Optional[str]:
        """Get screenshot from OBS as base64"""
        pass
    
    def mute_video(self):
        """Mute video by switching to 'muted' scene"""
        pass
    
    def unmute_video(self):
        """Unmute video by switching back to 'main' scene"""
        pass
    
    def reload_camera(self):
        """Reload camera source"""
        pass
    
    def set_logo(self, visible: bool = True):
        """Set logo visibility"""
        pass
    
    async def check_audio(self) -> float:
        """Check audio levels and return range"""
        pass
    
    def get_status(self) -> dict:
        """Get current OBS status"""
        return {
            "connected": self.connected,
            "recording": self.recording,
            "muted": self.muted,
            "current_file": self.current_file.filename if self.current_file else None
        }
