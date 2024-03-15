from nicegui import ui, app, Client
import os
from obscontroller import ObsController
from filemanager import Filemanager
from ui_object_container import UiObjectContainer
from recording_controller import RecordingController
from threading import Thread



async def check_page(obs_controller: ObsController, filemanager: Filemanager, ui_object_container: UiObjectContainer, recording_controller: RecordingController):
    ''' Admin page of the web interface '''
    audio = await obs_controller.check_audio()
    print("Checked Audio")
    with ui.column().style("margin: 0em; width: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;"):
        with ui.column().style("max-width: 600px;"):
            # Add Previewp
            if audio:
                ui.label("Audio funktioniert").classes("text-xl text-positive")
            else:
                ui.label("Audio Fehler!!!").classes("text-xl text-negative")
            preview = ui.html("")
            preview.bind_content_from(ui_object_container, 'html_preview')
            ui.button("Neu testen", on_click= lambda: ui.run_javascript("location.reload()")).classes("w-full")