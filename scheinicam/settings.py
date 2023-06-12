import datetime
import json
import logging

SETTINGS_FILE = "settings.json"

class Settings:
    def __init__(self):
        '''Load settings from json or set default values'''
        if not self.load_from_json(SETTINGS_FILE):
            self.set_default_values()
            self.save_to_json(SETTINGS_FILE)

    def load_from_json(self, filename: str) -> bool:
        '''Load settings from json, return True if successful'''
        try:
            data = json.load(open(filename, "r"))
            self.start_time = datetime.fromisoformat(data["start_time"])
            self.end_time = datetime.fromisoformat(data["end_time"])
            self.delete_age = datetime.timedelta(seconds=data["delete_age"])
            return True
        except Exception as e:
            logging.exception(e)
            logging.warning(f"Could not load settings from {filename}")
            return False
        
    def save_to_json(self, filename: str):
        '''Save settings to json'''
        try:
            data = {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "delete_age": self.delete_age.total_seconds()
            }
            json.dump(data, open(filename, "w"))
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not save settings to {filename}")

    def set_default_values(self):
        '''Set default values'''
        self.start_time = datetime.time(1, 55, 0)
        self.end_time = datetime.time(4, 55, 0)
        self.delete_age = datetime.timedelta(days=7)
