import os
import logging
import asyncio
from typing import List, Optional, Dict
from datetime import datetime, time, timedelta
import cv2
import base64
from io import BytesIO
from PIL import Image
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from app.models.video import VideoFile

logger = logging.getLogger(__name__)


class FileService:
    """Service for managing video files"""
    
    def __init__(self, video_directory: str = "videos"):
        self.video_directory = video_directory
        self.files: List[VideoFile] = []
        self._initialized = False
    
    async def initialize(self, delete_age: Optional[timedelta] = None):
        """Initialize file service"""
        if self._initialized:
            return
        
        await self.scan_files()
        
        if delete_age:
            await self.delete_old_files(delete_age)
        
        await self.delete_subclips()
        
        self._initialized = True
        logger.info("File service initialized")
    
    async def scan_files(self):
        """Scan video directory for existing files"""
        pass
    
    def add_file(self, video_file: VideoFile):
        """Add a video file to the managed list"""
        pass
    
    def remove_file(self, filename: str) -> bool:
        """Remove a video file from the managed list"""
        pass
    
    def get_file(self, filename: str) -> Optional[VideoFile]:
        """Get a video file by filename"""
        pass
    
    def get_all_files(self) -> List[VideoFile]:
        """Get all video files"""
        pass
    
    def get_newest_file(self) -> Optional[VideoFile]:
        """Get the newest video file"""
        pass
    
    def get_file_dict(self) -> Dict[str, str]:
        """Get dictionary of files with descriptors"""
        pass
    
    async def delete_file(self, filename: str) -> bool:
        """Delete a video file (both .mp4 and .json)"""
        pass
    
    async def delete_old_files(self, max_age: timedelta) -> int:
        """Delete files older than specified age"""
        pass
    
    async def delete_subclips(self) -> int:
        """Delete all subclip files"""
        pass
    
    async def export_subclip(
        self,
        filename: str,
        start_time: time,
        end_time: time
    ) -> Optional[str]:
        """
        Export a subclip from a video file
        
        Args:
            filename: Source video filename
            start_time: Start time for the subclip
            end_time: End time for the subclip
        
        Returns:
            Path to the exported subclip or None on error
        """
        pass
    
    async def get_frame_at_time(
        self,
        filename: str,
        timestamp: time
    ) -> Optional[str]:
        """
        Get a frame from a video at a specific time as base64
        
        Args:
            filename: Video filename
            timestamp: Time in the video
        
        Returns:
            Base64 encoded image string or None
        """
        pass
    
    async def calculate_video_duration(self, filename: str) -> Optional[float]:
        """Calculate duration of a video file in seconds"""
        pass
    
    def get_video_path(self, filename: str) -> str:
        """Get full path to a video file"""
        return os.path.join(self.video_directory, f"{filename}.mp4")
    
    def get_json_path(self, filename: str) -> str:
        """Get full path to a video JSON metadata file"""
        return os.path.join(self.video_directory, f"{filename}.json")
    
    def video_exists(self, filename: str) -> bool:
        """Check if a video file exists"""
        return os.path.exists(self.get_video_path(filename))
    
    async def _extract_frame_base64(
        self,
        video_path: str,
        timestamp_seconds: float
    ) -> Optional[str]:
        """
        Internal method to extract a frame and encode as base64
        
        Args:
            video_path: Path to video file
            timestamp_seconds: Timestamp in seconds
        
        Returns:
            Base64 encoded JPEG image
        """
        try:
            # Open video with cv2
            cap = cv2.VideoCapture(video_path)
            
            # Set position to timestamp
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_seconds * 1000)
            
            # Read frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            # Convert color space and resize
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 450))
            
            # Convert to PIL Image and encode as JPEG
            img = Image.fromarray(frame, 'RGB')
            buff = BytesIO()
            img.save(buff, format="JPEG")
            
            # Encode as base64
            img_base64 = base64.b64encode(buff.getvalue()).decode("utf-8")
            return f"data:image/jpg;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error extracting frame: {e}")
            return None
    
    def get_filesize(self, filepath: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(filepath)
        except:
            return 0
    
    def get_filesize_string(self, filepath: str) -> str:
        """Get human-readable file size"""
        size = self.get_filesize(filepath)
        
        if size < 1024:
            return f"{size} B"
        elif size < 1024**2:
            return f"{size/1024:.2f} KB"
        elif size < 1024**3:
            return f"{size/1024**2:.2f} MB"
        elif size < 1024**4:
            return f"{size/1024**3:.2f} GB"
        else:
            return f"{size/1024**4:.2f} TB"
