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
        self.auto_started = False

    async def auto_record(self):
        ''' Automatically start and stop recording based on settings '''
        if not self.obs_controller.connected:
            return
        now = datetime.datetime.now().time()
        if now > self.settings.start_time and now < self.settings.end_time and datetime.datetime.now().weekday() in self.settings.weekdays:
            if not self.auto_started and not self.obs_controller.recording:
                logging.info("Starting recording")
                if await self.start_record():
                    self.auto_started = True
        else:
            if self.obs_controller.recording and self.auto_started:
                logging.info("Stopping recording")
                if await self.stop_record():
                    self.auto_started = False

    async def start_record(self):
        ''' Start recording '''
        if not self.obs_controller.connected or self.obs_controller.recording:
            logging.warning("Could not start recording because OBS is not connected or already recording")
            return False
        try:
            self.obs_controller.reload_camera()
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not reload camera")
            return
        try:
            file = self.obs_controller.record()
            if file is None:
                logging.error("Could not start recording because file is None")
                return False
            self.filemanager.add_file(file)
            await file.export_as_json()
            logging.info(f"Started recording {file.filename}")
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not start recording")
            return False
        return True

    async def stop_record(self):
        ''' Stop recording '''
        if not self.obs_controller.connected or not self.obs_controller.recording:
            logging.warning("Could not stop recording because OBS is not connected or not recording")
            return False
        try:
            self.obs_controller.stop()
            await self.obs_controller.file.stop_recording()
            logging.info(f"Stopped recording {self.obs_controller.file.filename}")
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not stop recording")
            return False
        return True