import obsws_python as obs
import time

HOST = "localhost"
PORT = 4455
PASSWORD = "tXqFcBWo7WngUnAs"

class ObsController:
    def __init__(self, host=HOST, port=PORT, password=PASSWORD):
        '''Initialize ObsController'''
        self.client = obs.ReqClient(host=host, port=port, password=password)
        status = self.client.get_record_status()
        self.state = "recording" if status.output_active else "ready"

    def record(self, name):
        '''Start recording with given name'''
        if self.state == "recording": 
            return # Recording already running
        self.client.set_profile_parameter("Output", "FilenameFormatting", f"{name}_%CCYY-%MM-%DD_%hh-%mm-%ss")
        self.client.start_record()
        self.state = "recording"

    def stop(self):
        '''Stop recording'''
        if self.state == "ready":
            return # No recording running
        out = self.client.get_record_directory().record_directory
        print(out)
        self.client.stop_record()
        self.state = "ready"

    def __del__(self):
        '''Destructor'''
        pass

if __name__ == "__main__":
    obs_controller = ObsController()
    obs_controller.record("test")
    time.sleep(5)
    obs_controller.stop()
