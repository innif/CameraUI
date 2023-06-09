import obsws_python as obs
import time
from filemanager import VideoFile
import threading
import logging

HOST = "localhost"
PORT = 4455
PASSWORD = "tXqFcBWo7WngUnAs"

class ObsController:
    def __init__(self, host=HOST, port=PORT, password=PASSWORD): # TODO: Error handling
        '''Initialize ObsController'''
        self.client = None
        self.recording = False
        self.preview = ""
        self.file = None
        self.connected = False
        def connect():
            while True:
                if not self.connected:
                    self._try_connect(host, port, password)
                time.sleep(1)
        threading.Thread(target=connect).start()

    def _try_connect(self, host, port, password):
        '''Try to connect to OBS'''
        try:
            self.client = obs.ReqClient(host=host, port=port, password=password)
            status = self.client.get_record_status()
            self.recording = status.output_active
            self.connected = True
        except:
            self.connected = False

    def record(self): # TODO: Error handling
        '''
        Start recording with given name
        '''
        if self.recording: 
            return None# Recording already running
        try:
            self.file = VideoFile()
        except:
            raise Exception("Error creating VideoFile")
        try:
            self.client.set_profile_parameter("Output", "FilenameFormatting", self.file.filename)
            self.client.start_record()
            self.recording = True
        except Exception as e:
            self.connected = False
            logging.exception(e)
            logging.error("Error starting recording")
            raise Exception("Error starting recording")
        return self.file

    def stop(self): # TODO: Error handling
        '''Stop recording'''
        if not self.recording:
            return None# No recording running
        try:
            self.client.stop_record()
        except Exception as e:
            self.connected = False
            logging.exception(e)
            logging.error("Error stopping recording")
            raise Exception("Error stopping recording")
        self.recording = False
        logging.info("Recording stopped")
        return self.file

    def get_screenshot(self):
        '''Get screenshot'''
        if not self.connected:
            return None
        try:
            out = self.client.get_source_screenshot(name="main", img_format="jpg", width=512, height=288, quality=50)
            return out.image_data
        except Exception as e:
            self.connected = False
            logging.exception(e)
            logging.error("Error getting screenshot")
            raise Exception("Error getting screenshot")
    
    def mute_video(self):
        '''mute video by switching to scene "muted"'''
        if not self.connected:
            return
        try:
            self.client.set_current_program_scene("muted")
        except Exception as e:
            self.connected = False
            logging.exception(e)
            logging.error("Error muting video")
            raise Exception("Error muting video")
        
    def unmute_video(self):
        '''unmute video by switching to scene back to "main"'''
        if not self.connected:
            return
        try:
            self.client.set_current_program_scene("main")
        except Exception as e:
            self.connected = False
            logging.exception(e)
            logging.error("Error unmuting video")
            raise Exception("Error unmuting video")
        
    def reload_camera(self):
        '''reloading camera by disabling and re-enabling camera source'''
        if not self.connected:
            return
        try:
            settings = self.client.get_input_settings("Camera")
            settings.input_settings["active"] = False
            logging.info("disabling camera")
            self.client.set_input_settings("Camera", {"disable": True}, True)
        except Exception as e:
            self.connected = False
            logging.exception(e)
            logging.error("Error disabling camera")
            raise Exception("Error disabling camera")
        

    def __del__(self):
        '''Destructor'''
        pass

if __name__ == "__main__":
    obs_controller = ObsController()
    time.sleep(5)
    obs_controller.reload_camera()
    exit()
