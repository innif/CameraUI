from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
from datetime import time, timedelta


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    DEBUG: bool = False
    APP_NAME: str = "ScheinCam"
    API_V1_PREFIX: str = "/api"
    
    # Recording schedule
    START_TIME: time = time(19, 50, 0)
    END_TIME: time = time(22, 10, 0)
    SHUTDOWN_TIME: time = time(1, 0, 0)
    WEEKDAYS: Union[List[int], str] = [0, 1, 2, 3, 4, 5, 6]  # Monday=0, Sunday=6

    # Timezone settings
    TIMEZONE: str = "Europe/Berlin"  # Local timezone for display and scheduling
    
    @field_validator('WEEKDAYS', mode='before')
    @classmethod
    def parse_weekdays(cls, v):
        """Parse WEEKDAYS from string or list"""
        if isinstance(v, str):
            # Parse comma-separated string
            return [int(day.strip()) for day in v.split(',') if day.strip()]
        return v
    
    # File management
    DELETE_AGE_SECONDS: float = 1209600.0  # 14 days
    CLEANUP_INTERVAL_SECONDS: int = 3600  # 1 hour
    VIDEO_DIRECTORY: str = "videos"
    ASSETS_DIRECTORY: str = "assets"
    LOGS_DIRECTORY: str = "logs"
    
    # OBS settings
    OBS_HOST: str = "localhost"
    OBS_PORT: int = 4455
    OBS_PASSWORD: str = "tXqFcBWo7WngUnAs"
    
    # UI settings
    SHOW_LOGO: bool = True
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30

    # Authentication
    WEB_PASSWORD: str = "deinSicheresPasswort123"

    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def delete_age(self) -> timedelta:
        """Get delete age as timedelta"""
        return timedelta(seconds=self.DELETE_AGE_SECONDS)

    @property
    def cleanup_interval(self) -> int:
        """Get cleanup interval in seconds"""
        return self.CLEANUP_INTERVAL_SECONDS


# Global settings instance
settings = Settings()