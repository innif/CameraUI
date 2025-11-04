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
    SUBCLIP_MIN_AGE_SECONDS: float = 7200.0  # 2 hours - minimum age before subclips are deleted
    VIDEO_DIRECTORY: str = "videos"
    ASSETS_DIRECTORY: str = "assets"
    LOGS_DIRECTORY: str = "logs"
    
    # OBS settings
    OBS_HOST: str = "localhost"
    OBS_PORT: int = 4455
    OBS_PASSWORD: str = ""
    OBS_RECONNECT_MAX_DELAY: int = 30  # Maximum delay between reconnection attempts

    # Audio monitoring settings
    AUDIO_CHECK_INTERVAL: int = 30  # Seconds between automatic audio checks
    AUDIO_CHECK_RETRIES: int = 3  # Number of retry attempts for audio checks
    AUDIO_FAILURE_THRESHOLD: int = 2  # Consecutive failures before camera reload
    AUDIO_THRESHOLD: float = 0.01  # Minimum audio level to consider as "has audio"

    # Recording resilience settings
    RECORDING_START_RETRIES: int = 3  # Number of attempts to start recording
    RECORDING_RETRY_DELAY: int = 2  # Seconds between recording start retries

    # UI settings
    SHOW_LOGO: bool = True
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30

    # Authentication
    WEB_PASSWORD: str = "deinSicheresPasswort123"

    # SSH settings for system control (shutdown/reboot)
    SSH_HOST: str = OBS_HOST  # Use same host as OBS
    SSH_PORT: int = 22
    SSH_USERNAME: str = "obsuser"
    SSH_PASSWORD: str = "obsuser"
    SSH_KEY_FILE: str = ""  # Path to SSH private key file (optional)

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

    @property
    def subclip_min_age(self) -> timedelta:
        """Get minimum subclip age as timedelta"""
        return timedelta(seconds=self.SUBCLIP_MIN_AGE_SECONDS)


# Global settings instance
settings = Settings()