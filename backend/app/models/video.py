from pydantic import BaseModel, Field
from datetime import datetime, time, timedelta, timezone
from typing import Optional
import json
from zoneinfo import ZoneInfo


def _generate_filename() -> str:
    """Generate filename based on current local time"""
    from app.core.config import settings
    utc_now = datetime.now(timezone.utc)
    local_tz = ZoneInfo(settings.TIMEZONE)
    local_now = utc_now.astimezone(local_tz)
    return local_now.strftime("%y-%m-%d--%H-%M-%S")


class VideoFile(BaseModel):
    """Model representing a video file"""

    filename: str = Field(default_factory=_generate_filename)
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
        now = datetime.now(timezone.utc)
        start = self.start_time

        # Handle naive datetimes (legacy data) - assume they are in local timezone
        if start.tzinfo is None:
            from app.core.config import settings
            local_tz = ZoneInfo(settings.TIMEZONE)
            start = start.replace(tzinfo=local_tz).astimezone(timezone.utc)

        return now - start
    
    def get_descriptor(self) -> str:
        """Get human-readable descriptor in local timezone"""
        from app.core.config import settings

        # Convert UTC times to local timezone for display
        local_tz = ZoneInfo(settings.TIMEZONE)

        # Handle naive datetimes (legacy data) - assume they are already in local timezone
        if self.start_time.tzinfo is None:
            start_local = self.start_time
        else:
            start_local = self.start_time.astimezone(local_tz)

        if self.end_time is None:
            return "{} (seit {} laufend)".format(
                start_local.strftime("%A, %d.%m.%Y"),
                start_local.strftime("%H:%M Uhr")
            )

        # Handle naive end_time
        if self.end_time.tzinfo is None:
            end_local = self.end_time
        else:
            end_local = self.end_time.astimezone(local_tz)

        return "{} ({} - {})".format(
            start_local.strftime("%A, %d.%m.%Y"),
            start_local.strftime("%H:%M"),
            end_local.strftime("%H:%M")
        )
    
    def get_download_filename(self, selected_time: time) -> str:
        """Get download filename for exported video in local timezone"""
        from app.core.config import settings

        # Convert UTC time to local timezone for filename
        local_tz = ZoneInfo(settings.TIMEZONE)

        # Handle naive datetimes (legacy data) - assume they are already in local timezone
        if self.start_time.tzinfo is None:
            start_local = self.start_time
        else:
            start_local = self.start_time.astimezone(local_tz)

        return "Scheinbar_{}_{}.mp4".format(
            start_local.strftime("%Y-%m-%d"),
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
        """Load from JSON file and handle legacy naive datetimes"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Parse timestamps
            start_time = datetime.fromisoformat(data["start_time"])
            end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None

            # Convert naive datetimes to timezone-aware (assume local timezone for legacy data)
            if start_time.tzinfo is None:
                from app.core.config import settings
                local_tz = ZoneInfo(settings.TIMEZONE)
                start_time = start_time.replace(tzinfo=local_tz).astimezone(timezone.utc)

            if end_time and end_time.tzinfo is None:
                from app.core.config import settings
                local_tz = ZoneInfo(settings.TIMEZONE)
                end_time = end_time.replace(tzinfo=local_tz).astimezone(timezone.utc)

            return cls(
                filename=data["filename"],
                start_time=start_time,
                end_time=end_time
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
