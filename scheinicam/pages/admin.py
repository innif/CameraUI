from nicegui import ui, app, Client
import os
from obscontroller import ObsController

#TODO: Löschen von Aufnahmen
#TODO: Einstellungen

def admin_page(obs_controller: ObsController):
    # Add Button to Mute and Unmute Recording
    with ui.card().bind_visibility_from(obs_controller, 'connected'), ui.row().style("margin-top: 1em;"):
        ui.button('Aufnahme stumm schalten', color="red", on_click=obs_controller.mute_video).classes("w-full").style("height: 6em;")
        ui.button('Aufnahme wieder einschalten', color="blue", on_click=obs_controller.unmute_video).classes("w-full").style("height: 6em;")
    with ui.expansion("Erweiterte Funktionen"):
        ui.button("Computer herunterfahren", color="red", on_click=lambda: os.system("shutdown /s /t 1"))
    # TODO Add options for start and end time