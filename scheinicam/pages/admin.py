from nicegui import ui, app, Client
import os
from obscontroller import ObsController
from filemanager import Filemanager

#TODO: Löschen von Aufnahmen
#TODO: Einstellungen
# TODO Add options for start and end time

def delete_logfiles():
    for file in os.listdir("logs"):
        if file.endswith(".log"):
            os.remove(f"logs/{file}")

def admin_page(obs_controller: ObsController, filemanager: Filemanager):
    with ui.column().style("margin: 0em; width: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;"):
        # Add Identifier showing if Recording is muted
        with ui.card().bind_visibility_from(obs_controller, 'muted').classes("w-full").style("max-width: 600px;"):
            with ui.row():
                ui.spinner('puff', size='3em', color='red')
                ui.label("Aufnahme stummgeschaltet").style("font-size: 2em;")
        # Add Button to Mute and Unmute Recording
        with ui.card().bind_visibility_from(obs_controller, 'connected').classes("w-full").style("max-width: 600px;"), \
                ui.row().style("margin-top: 1em;").classes("w-full"):
            ui.button('Aufnahme stumm schalten', color="red", on_click=obs_controller.mute_video).classes("w-full").style("height: 6em;")
            ui.button('Aufnahme wieder einschalten', color="blue", on_click=obs_controller.unmute_video).classes("w-full").style("height: 6em;")
        with ui.expansion("Erweiterte Funktionen").classes("w-full").style("max-width: 600px;"):
            ui.button("Computer herunterfahren", color="red", on_click=lambda: os.system("shutdown /s /t 1")).classes("w-full")
        with ui.expansion("Logfiles").classes("w-full").style("max-width: 600px;"):
            with ui.column():
                for file in os.listdir("logs"):
                    if file.endswith(".log"):
                        ui.link(file + "\n", f"logs/{file}")
            ui.button("Logfiles löschen", color="red", on_click=delete_logfiles).classes("w-full")
        # add section to delete videos
        with ui.expansion("Aufnahmen löschen").classes("w-full").style("max-width: 600px;"):
            pass
