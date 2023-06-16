from nicegui import ui, app, Client
import os
from obscontroller import ObsController

#TODO: Löschen von Aufnahmen
#TODO: Einstellungen

def admin_page(obs_controller: ObsController):
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
        # TODO Add options for start and end time