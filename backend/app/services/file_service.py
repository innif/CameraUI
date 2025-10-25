import os
import logging
import asyncio
from typing import List, Optional, Dict
from datetime import datetime, time, timedelta, timezone
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
        try:
            if not os.path.exists(self.video_directory):
                os.makedirs(self.video_directory)
                logger.info(f"Created video directory: {self.video_directory}")
                return
            
            # Scan for JSON metadata files
            for filename in os.listdir(self.video_directory):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.video_directory, filename)
                    video_file = VideoFile.from_json_file(filepath)
                    
                    if video_file:
                        # Calculate end time if missing
                        if video_file.end_time is None:
                            duration = await self.calculate_video_duration(video_file.filename)
                            if duration:
                                video_file.end_time = video_file.start_time + timedelta(seconds=duration - 1)
                                video_file.to_json_file(self.video_directory)
                        
                        self.files.append(video_file)
                        logger.info(f"Loaded video file: {video_file.filename}")
            
            logger.info(f"Scanned {len(self.files)} video files")
            
        except Exception as e:
            logger.exception(e)
            logger.error("Error scanning video files")
    
    def add_file(self, video_file: VideoFile):
        """Add a video file to the managed list"""
        if video_file not in self.files:
            self.files.append(video_file)
            logger.info(f"Added video file: {video_file.filename}")
    
    def remove_file(self, filename: str) -> bool:
        """Remove a video file from the managed list"""
        for video_file in self.files:
            if video_file.filename == filename:
                self.files.remove(video_file)
                logger.info(f"Removed video file from list: {filename}")
                return True
        return False
    
    def get_file(self, filename: str) -> Optional[VideoFile]:
        """Get a video file by filename"""
        for video_file in self.files:
            if video_file.filename == filename:
                return video_file
        return None
    
    def get_all_files(self) -> List[VideoFile]:
        """Get all video files"""
        return sorted(self.files, key=lambda f: f.start_time, reverse=True)
    
    def get_newest_file(self) -> Optional[VideoFile]:
        """Get the newest video file"""
        if not self.files:
            return None
        return max(self.files, key=lambda f: f.start_time)
    
    def get_file_dict(self) -> Dict[str, str]:
        """Get dictionary of files with descriptors"""
        return {file.filename: file.get_descriptor() for file in self.files}
    
    async def delete_file(self, filename: str) -> bool:
        """Delete a video file (both .mp4 and .json)"""
        try:
            video_path = self.get_video_path(filename)
            json_path = self.get_json_path(filename)
            
            # Remove from list
            self.remove_file(filename)
            
            # Delete files
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Deleted video file: {video_path}")
            
            if os.path.exists(json_path):
                os.remove(json_path)
                logger.info(f"Deleted JSON file: {json_path}")
            
            return True
            
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error deleting file: {filename}")
            return False
    
    async def delete_old_files(self, max_age: timedelta) -> int:
        """Delete files older than specified age"""
        deleted_count = 0
        files_to_delete = []
        
        for video_file in self.files:
            if video_file.age > max_age:
                files_to_delete.append(video_file.filename)
        
        for filename in files_to_delete:
            if await self.delete_file(filename):
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} old video files")
        return deleted_count
    
    async def delete_subclips(self) -> int:
        """Delete all subclip files"""
        deleted_count = 0
        
        try:
            for filename in os.listdir(self.video_directory):
                if filename.startswith("subclip_"):
                    filepath = os.path.join(self.video_directory, filename)
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted subclip: {filename}")
        
        except Exception as e:
            logger.exception(e)
            logger.error("Error deleting subclips")
        
        return deleted_count
    
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
        try:
            video_file = self.get_file(filename)
            if not video_file:
                logger.error(f"Video file not found: {filename}")
                return None
            
            # Calculate timestamps in seconds
            start_datetime = datetime.combine(video_file.start_time.date(), start_time)
            end_datetime = datetime.combine(video_file.start_time.date(), end_time)
            
            start_seconds = (start_datetime - video_file.start_time).total_seconds()
            end_seconds = (end_datetime - video_file.start_time).total_seconds()
            
            # Validate time range
            if end_seconds <= start_seconds or start_seconds < 0:
                logger.error("Invalid time range for export")
                return None
            
            # Generate output path
            output_filename = f"subclip_{filename}-{int(start_seconds)}-{int(end_seconds)}.mp4"
            output_path = os.path.join(self.video_directory, output_filename)
            
            # Extract subclip using ffmpeg
            source_path = self.get_video_path(filename)
            await asyncio.to_thread(
                ffmpeg_extract_subclip,
                source_path,
                start_seconds,
                end_seconds,
                targetname=output_path
            )
            
            logger.info(f"Exported subclip: {output_filename}")
            return output_path
            
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error exporting subclip from {filename}")
            return None
    
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
        try:
            video_file = self.get_file(filename)
            if not video_file:
                logger.error(f"Video file not found: {filename}")
                return None
            
            # Calculate timestamp in seconds
            timestamp_datetime = datetime.combine(video_file.start_time.date(), timestamp)
            timestamp_seconds = (timestamp_datetime - video_file.start_time).total_seconds()
            
            if timestamp_seconds < 0:
                logger.error("Timestamp before video start")
                return None
            
            # Extract frame
            video_path = self.get_video_path(filename)
            frame_base64 = await self._extract_frame_base64(video_path, timestamp_seconds)
            
            return frame_base64
            
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error getting frame from {filename}")
            return None
    
    async def calculate_video_duration(self, filename: str) -> Optional[float]:
        """Calculate duration of a video file in seconds"""
        try:
            video_path = self.get_video_path(filename)
            if not os.path.exists(video_path):
                return None
            
            # Use cv2 to get video duration
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                duration = frame_count / fps
                return duration
            
            return None
            
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error calculating duration for {filename}")
            return None
    
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

    async def delete_old_logs(self, max_age: timedelta, log_directory: str = "logs") -> int:
        """Delete log files older than specified age"""
        deleted_count = 0

        try:
            if not os.path.exists(log_directory):
                return 0

            now = datetime.now(timezone.utc)

            for filename in os.listdir(log_directory):
                if filename.endswith(".log"):
                    filepath = os.path.join(log_directory, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)
                    file_age = now - file_mtime

                    if file_age > max_age:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"Deleted old log file: {filename}")

        except Exception as e:
            logger.exception(e)
            logger.error("Error deleting old log files")

        return deleted_count
