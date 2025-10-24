from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from datetime import time, timedelta
import json


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
    WEEKDAYS: List[int] = [0, 1, 2, 3, 4, 5, 6]  # Monday=0, Sunday=6
    
    # File management
    DELETE_AGE_SECONDS: float = 1209600.0  # 14 days
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def delete_age(self) -> timedelta:
        """Get delete age as timedelta"""
        return timedelta(seconds=self.DELETE_AGE_SECONDS)
    
    @classmethod
    def load_from_json(cls, filepath: str = "settings.json"):
        """Load settings from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Convert time strings to time objects
            if 'start_time' in data:
                data['START_TIME'] = time.fromisoformat(data.pop('start_time'))
            if 'end_time' in data:
                data['END_TIME'] = time.fromisoformat(data.pop('end_time'))
            if 'shutdown_time' in data:
                data['SHUTDOWN_TIME'] = time.fromisoformat(data.pop('shutdown_time'))
            if 'delete_age' in data:
                data['DELETE_AGE_SECONDS'] = data.pop('delete_age')
            if 'weekdays' in data:
                data['WEEKDAYS'] = data.pop('weekdays')
            if 'show_logo' in data:
                data['SHOW_LOGO'] = data.pop('show_logo')
            
            # Handle OBS settings
            if 'obs_settings' in data:
                obs = data.pop('obs_settings')
                data['OBS_HOST'] = obs.get('host', 'localhost')
                data['OBS_PORT'] = obs.get('port', 4455)
                data['OBS_PASSWORD'] = obs.get('password', '')
            
            return cls(**data)
        except Exception as e:
            print(f"Error loading settings from JSON: {e}")
            return cls()
    
    def save_to_json(self, filepath: str = "settings.json"):
        """Save settings to JSON file"""
        data = {
            "start_time": self.START_TIME.isoformat(),
            "end_time": self.END_TIME.isoformat(),
            "shutdown_time": self.SHUTDOWN_TIME.isoformat(),
            "delete_age": self.DELETE_AGE_SECONDS,
            "weekdays": self.WEEKDAYS,
            "show_logo": self.SHOW_LOGO,
            "obs_settings": {
                "host": self.OBS_HOST,
                "port": self.OBS_PORT,
                "password": self.OBS_PASSWORD
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)


# Global settings instance
settings = Settings.load_from_json()
