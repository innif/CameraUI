import obsws_python as obs
import time
from datetime import datetime

HOST = "localhost"
PORT = 4455
PASSWORD = "tXqFcBWo7WngUnAs"

class ObsController:
    def __init__(self, host=HOST, port=PORT, password=PASSWORD):
        '''Initialize ObsController'''
        self.client = obs.ReqClient(host=host, port=port, password=password)
        status = self.client.get_record_status()
        self.recording = status.output_active
        self.preview = ""
        self.filename = ""

    def _generate_filename(self, name):
        '''Generate filename'''
        now = datetime.now()
        output = now.strftime("%y-%m-%d_%H-%M-%S")
        return f"{name}_{output}"

    def record(self, name):
        '''Start recording with given name'''
        if self.recording: 
            return # Recording already running
        filename = self._generate_filename(name)
        self.client.set_profile_parameter("Output", "FilenameFormatting", filename)
        self.client.start_record()
        self.recording = True

    def stop(self):
        '''Stop recording'''
        if not self.recording:
            return # No recording running
        self.client.stop_record()
        self.recording = False
        self.filename = ""

    def get_screenshot(self):
        '''Get screenshot'''
        out = self.client.get_source_screenshot(name="main", img_format="jpg", width=512, height=288, quality=50)
        return out.image_data

    def __del__(self):
        '''Destructor'''
        pass

if __name__ == "__main__":
    obs_controller = ObsController()
    obs_controller.record("test")
    time.sleep(5)
    obs_controller.stop()
