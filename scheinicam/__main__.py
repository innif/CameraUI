from nicegui import ui, app, Client, run
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
from pages.check import check_page

import locale
import asyncio

# constants
WIDTH = "50em"

# set locale & logging
locale.setlocale(locale.LC_ALL, 'de_DE')
logging.basicConfig(filename=f'logs/log{datetime.datetime.now().strftime("%y-%m-%d--%H-%M-%S")}.log', encoding='utf-8', level=logging.INFO)

# create objects
settings = Settings()
obs_controller = ObsController(settings=settings)
filemanager = Filemanager(delete_old_files_age=settings.delete_age)
ui_object_container = UiObjectContainer()
recording_controller = RecordingController(obs_controller, settings, filemanager)

# add static folders
app.add_static_files('/videos', 'videos')
app.add_static_files('/assets', 'assets')
app.add_static_files('/logs', 'logs')
              
# main landing page
@ui.page("/")
async def index(client: Client):
    '''Main page of the web interface'''
    with ui.column().style("margin: 0em; width: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;"):
        with ui.tabs().style(f"width: {WIDTH}; max-width: 100%; display: block;") as tabs: 
            ui.tab('Aufnahme', icon='videocam')
            ui.tab('Videoarchiv', icon='file_download')
        # Content
        with ui.tab_panels(tabs, value='Aufnahme').style(f"width: {WIDTH}; max-width: 100%;") as panels:
            with ui.tab_panel('Aufnahme').style("width: 100%;"):
                recording_page(client, obs_controller, settings, ui_object_container)
                ui.button("Zum Download-Bereich", on_click=lambda: panels.set_value('Videoarchiv')).classes("w-full")
            with ui.tab_panel('Videoarchiv').style("width: 100%; padding: 0em;"):
                await download_page(client, filemanager)

# admin landing page
@ui.page("/admin")
def admin(client: Client):
    '''Admin page of the web interface'''
    admin_page(obs_controller, filemanager, ui_object_container, recording_controller)

# admin landing page
@ui.page("/check")
async def check(client: Client):
    '''Admin page of the web interface'''
    await check_page(obs_controller, filemanager, ui_object_container, recording_controller)

@ui.page("/download")
async def download(client: Client):
    with ui.grid(columns=2):
        for file, descriptor in filemanager.get_file_dict().items():
            ui.label(descriptor).style("margin-right: 1em;")
            ui.button("Download", on_click=lambda: ui.download(f"videos/{file.filename}.mp4"))
            
async def update_preview():
    '''Regularly updates the preview image'''
    try:
        if obs_controller.muted:
            ui_object_container.html_preview = "<div style=\"padding:1em;\"><p>Aufnahme pausiert auf Wunsch eines Künstlers</p></div>"
            return
        img_data = await obs_controller.get_screenshot()
        if img_data is None:
            ui_object_container.html_preview = "<div style=\"padding:1em;\"><p>Keine Verbindung zu OBS</p></div>"
        else:
            ui_object_container.html_preview = f"<img src=\"{img_data}\" width=\"100%\"/>"
    except Exception as e:
        logging.exception(e)
        logging.error(f"Could not update preview")

# create thread for updating preview
ui.timer(1, update_preview)

def auto_shutdown():
    '''Shuts down the computer at the time given in settings object'''
    now = datetime.datetime.now()
    shutdown_time = datetime.datetime.combine(datetime.date.today(), settings.shutdown_time)
    if now > shutdown_time and now < shutdown_time + datetime.timedelta(seconds=10):
        logging.info("Shutting down...")
        print("Shutting down...")
        os.system("shutdown /s /t 1")

# register service
#zeroconfserver = ZeroconfServer("camera", 80)
#zeroconfserver.register_service()

#TODO remove from ui-thread
ui.timer(1, recording_controller.auto_record)
ui.timer(1, auto_shutdown)

# run app
ui.run(title="ScheiniCam", show=False, port=80, favicon="📹", reload=False)