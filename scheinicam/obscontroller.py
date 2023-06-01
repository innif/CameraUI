import obsws_python as obs
import time
from filemanager import VideoFile

HOST = "localhost"
PORT = 4455
PASSWORD = "tXqFcBWo7WngUnAs"

class ObsController:
    def __init__(self, host=HOST, port=PORT, password=PASSWORD): # TODO: Error handling
        '''Initialize ObsController'''
        self.client = obs.ReqClient(host=host, port=port, password=password)
        status = self.client.get_record_status()
        self.recording = status.output_active
        self.preview = ""
        self.file = None

    

    def record(self, name, ip): # TODO: Error handling
        '''
        Start recording with given name
        '''
        if self.recording: 
            return # Recording already running
        self.file = VideoFile(name, ip=ip)
        print(ip)
        self.client.set_profile_parameter("Output", "FilenameFormatting", self.file.filename)
        self.client.start_record()
        self.recording = True

    def stop(self): # TODO: Error handling
        '''Stop recording'''
        if not self.recording:
            return # No recording running
        self.client.stop_record()
        self.file.set_end_time()
        self.recording = False
        return self.file

    def get_screenshot(self):
        '''Get screenshot'''
        out = self.client.get_source_screenshot(name="main", img_format="jpg", width=512, height=288, quality=50)
        return out.image_data

    def __del__(self):
        '''Destructor'''
        pass

if __name__ == "__main__":
    obs_controller = ObsController()
    time.sleep(5)
    obs_controller.stop()
