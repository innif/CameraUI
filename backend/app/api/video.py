from pydantic import BaseModel, Field
from datetime import datetime, time, timedelta
from typing import Optional
import json


class VideoFile(BaseModel):
    """Model representing a video file"""
    
    filename: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @property
    def is_recording(self) -> bool:
        """Check if video is currently recording"""
        return self.end_time is None
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get video duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def age(self) -> timedelta:
        """Get age of the video file"""
        return datetime.now() - self.start_time
    
    def get_descriptor(self) -> str:
        """Get human-readable descriptor"""
        if self.end_time is None:
            return "{} (seit {} laufend)".format(
                self.start_time.strftime("%A, %d.%m.%Y"),
                self.start_time.strftime("%H:%M Uhr")
            )
        
        return "{} ({} - {})".format(
            self.start_time.strftime("%A, %d.%m.%Y"),
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M")
        )
    
    def get_download_filename(self, selected_time: time) -> str:
        """Get download filename for exported video"""
        return "Scheinbar_{}_{}.mp4".format(
            self.start_time.strftime("%Y-%m-%d"),
            selected_time.strftime("%H-%M")
        )
    
    def to_json_file(self, directory: str = "videos") -> str:
        """Export to JSON file"""
        filepath = f"{directory}/{self.filename}.json"
        data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "filename": self.filename
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
        return filepath
    
    @classmethod
    def from_json_file(cls, filepath: str) -> Optional["VideoFile"]:
        """Load from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return cls(
                filename=data["filename"],
                start_time=datetime.fromisoformat(data["start_time"]),
                end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
            )
        except Exception as e:
            print(f"Error loading video file from JSON: {e}")
            return None


class VideoExportRequest(BaseModel):
    """Request model for video export"""
    
    filename: str
    start_time: time
    end_time: time


class VideoFrameRequest(BaseModel):
    """Request model for getting a video frame"""
    
    filename: str
    timestamp: time


class VideoListResponse(BaseModel):
    """Response model for video list"""
    
    videos: list[VideoFile]
    total: int


class VideoExportResponse(BaseModel):
    """Response model for video export"""
    
    success: bool
    filepath: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
