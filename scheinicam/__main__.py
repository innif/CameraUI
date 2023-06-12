from nicegui import ui, app, Client
import time
import threading
import datetime
import logging

from filemanager import VideoFile, Filemanager, FileContainer
from obscontroller import ObsController
from settings import Settings
from ui_object_container import UiObjectContainer
from recording_controller import RecordingController

from pages.download import download_page3 as download_page
from pages.admin import admin_page
from pages.recording import recording_page

#TODO: direkt herunterladen nach aufnahme beenden anbieten

logging.basicConfig(filename=f'logs/log{datetime.datetime.now().strftime("%y-%m-%d--%H-%M-%S")}.log', encoding='utf-8', level=logging.INFO)

obs_controller = ObsController()
filemanager = Filemanager()
settings = Settings()
ui_object_container = UiObjectContainer()
recording_controller = RecordingController(obs_controller, settings, filemanager)

WIDTH = "50em"

app.add_static_files('/videos', 'videos')
app.add_static_files('/assets', 'assets')
              
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
    admin_page(obs_controller)

def update_preview():
    while True:
        try:
            img_data = obs_controller.get_screenshot()
            if img_data is None:
                ui_object_container.html_preview = "<p>Keine Verbindung zu OBS</p>"
            else:
                ui_object_container.html_preview = f"<img src=\"{img_data}\" width=\"100%\"/>"
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not update preview")
        time.sleep(.5)

t = threading.Thread(target=update_preview)
t.start()

filemanager.delete_files_older_than(settings.delete_age)
filemanager.delete_subclips()
ui.timer(1, recording_controller.auto_record)
ui.run(title="ScheiniCam", show=False)