from obscontroller import ObsController
from settings import Settings
from filemanager import Filemanager

import logging
import datetime

class RecordingController:
    def __init__(self, obs_controller: ObsController, settings: Settings, filemanager: Filemanager):
        ''' Controller for recording '''
        self.obs_controller = obs_controller
        self.settings = settings
        self.filemanager = filemanager

    def auto_record(self):
        ''' Automatically start and stop recording based on settings '''
        if not self.obs_controller.connected:
            return
        now = datetime.datetime.now().time()
        if now > self.settings.start_time and now < self.settings.end_time and datetime.datetime.now().weekday() in self.settings.weekdays:
            if not self.obs_controller.recording:
                logging.info("Starting recording")
                self.start_record()
        else:
            if self.obs_controller.recording:
                logging.info("Stopping recording")
                self.stop_record()

    def start_record(self):
        ''' Start recording '''
        if not self.obs_controller.connected or self.obs_controller.recording:
            logging.warning("Could not start recording because OBS is not connected or already recording")
            return
        try:
            file = self.obs_controller.record()
            if file is None:
                logging.error("Could not start recording because file is None")
                return
            self.filemanager.add_file(file)
            file.export_as_json()
            logging.info(f"Started recording {file.filename}")
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not start recording")
            return

    def stop_record(self):
        ''' Stop recording '''
        if not self.obs_controller.connected or not self.obs_controller.recording:
            logging.warning("Could not stop recording because OBS is not connected or not recording")
            return
        try:
            self.obs_controller.stop()
            self.obs_controller.file.stop_recording()
            logging.info(f"Stopped recording {self.obs_controller.file.filename}")
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not stop recording")
            return