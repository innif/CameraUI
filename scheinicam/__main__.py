from nicegui import ui, app, Client
import time
import threading
import datetime
import logging
import os

from filemanager import VideoFile, Filemanager, FileContainer
from obscontroller import ObsController
from settings import Settings
from ui_object_container import UiObjectContainer
from recording_controller import RecordingController
from zeroconfserver import ZeroconfServer

from pages.download import download_page3 as download_page
from pages.admin import admin_page
from pages.recording import recording_page

import locale

locale.setlocale(locale.LC_ALL, 'de_DE')

logging.basicConfig(filename=f'logs/log{datetime.datetime.now().strftime("%y-%m-%d--%H-%M-%S")}.log', encoding='utf-8', level=logging.INFO)

settings = Settings()
obs_controller = ObsController(settings=settings)
filemanager = Filemanager()
ui_object_container = UiObjectContainer()
recording_controller = RecordingController(obs_controller, settings, filemanager)

zeroconfserver = ZeroconfServer("camera", 80)

WIDTH = "50em"

filemanager.delete_files_older_than(settings.delete_age)
filemanager.delete_subclips()

app.add_static_files('/videos', 'videos')
app.add_static_files('/assets', 'assets')
app.add_static_files('/logs', 'logs')
              
@ui.page("/")
def index(client: Client):
    with ui.column().style("margin: 0em; width: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;"):
        with ui.tabs().style(f"width: {WIDTH}; max-width: 100%; display: block;") as tabs: 
            ui.tab('Aufnahme', icon='videocam')
            ui.tab('Download', icon='file_download')
        # Content
        with ui.tab_panels(tabs, value='Aufnahme').style(f"width: {WIDTH}; max-width: 100%;"):
            with ui.tab_panel('Aufnahme').style("width: 100%;"):
                recording_page(client, obs_controller, settings, ui_object_container)
            with ui.tab_panel('Download').style("width: 100%;"):
                download_page(client, filemanager)

# add admin page
@ui.page("/admin")
def admin(client: Client):
    admin_page(obs_controller, filemanager, settings)

def update_preview():
    while True:
        try:
            if obs_controller.muted:
                ui_object_container.html_preview = "<div style=\"padding:1em;\"><p>Aufnahme pausiert auf Wunsch eines Künstlers</p></div>"
                continue
            img_data = obs_controller.get_screenshot()
            if img_data is None:
                ui_object_container.html_preview = "<div style=\"padding:1em;\"><p>Keine Verbindung zu OBS</p></div>"
            else:
                ui_object_container.html_preview = f"<img src=\"{img_data}\" width=\"100%\"/>"
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not update preview")
        time.sleep(.5)

t = threading.Thread(target=update_preview)
t.start()

def auto_shutdown():
    '''Shuts down the computer at the time given in settings object'''
    now = datetime.datetime.now()
    shutdown_time = datetime.datetime.combine(datetime.date.today(), settings.shutdown_time)
    if now > shutdown_time and now < shutdown_time + datetime.timedelta(seconds=10):
        logging.info("Shutting down...")
        print("Shutting down...")
        os.system("shutdown /s /t 1")

ui.timer(1, recording_controller.auto_record)
ui.timer(1, auto_shutdown)
zeroconfserver.register_service()
ui.run(title="ScheiniCam", show=False, port=80, favicon="📹")