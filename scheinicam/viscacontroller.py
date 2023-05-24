import time
import numpy
from visca_over_ip import Camera

PRESET_STAGE = 1
PRESET_PIANO = 2
PRESET_STAGE_WIDE = 3
PRESET_STAGE_CLOSE = 4

class ViscaController:
    def __init__(self, ip, port=52381):
        self.cam = Camera(ip, port=port)
        time.sleep(2)

    def __del__(self):
        self.cam.close_connection()

    def recall_preset(self, preset):
        self.cam.recall_preset(preset)

    def home_camera(self):
        self.cam.pantilt_home()

    def move_camera(self, x, y): 
        self.cam.pantilt(x, y)
    
    def stop_camera(self):
        self.cam.pantilt(0, 0)

    def move_to(self, sx, sy, x, y):
        self.cam.pantilt(sx, sy, x, y, relative=True)

    def zoom_test(self):
        print("Tele Standard")
        self.cam._send_command("04 07 02")
        time.sleep(1)
        print("Wide Standard")
        self.cam._send_command("04 07 03")
        time.sleep(1)
        print("Zoom Stop")
        self.cam._send_command("04 07 00")
        time.sleep(1)

if __name__ == "__main__":
    visca_controller = ViscaController("192.168.1.22")
    visca_controller.home_camera()
    time.sleep(2)
    while True:
        print("zoom")
        visca_controller.zoom_test()
