from nicegui import ui, app, Client
import os
from obscontroller import ObsController
from filemanager import Filemanager
from settings import Settings

#TODO: Löschen von Aufnahmen
#TODO: Einstellungen
# TODO Add options for start and end time

def delete_logfiles():
    for file in os.listdir("logs"):
        if file.endswith(".log"):
            os.remove(f"logs/{file}")

def admin_page(obs_controller: ObsController, filemanager: Filemanager, settings: Settings):
    with ui.column().style("margin: 0em; width: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;"):
        # Add Identifier showing if Recording is muted
        with ui.card().bind_visibility_from(obs_controller, 'muted').classes("w-full").style("max-width: 800px;"):
            with ui.row():
                ui.spinner('puff', size='3em', color='red')
                ui.label("Aufnahme stummgeschaltet").style("font-size: 2em;")
        # Add Button to Mute and Unmute Recording
        with ui.card().bind_visibility_from(obs_controller, 'connected').classes("w-full").style("max-width: 800px;"), \
                ui.expansion("Aufnahme stumm schalten", value=True).classes("w-full"), \
                ui.row().style("margin-top: 1em;").classes("w-full"):
            ui.button('Aufnahme stumm schalten', color="red", on_click=obs_controller.mute_video).classes("w-full").style("height: 6em;")
            ui.button('Aufnahme wieder einschalten', color="blue", on_click=obs_controller.unmute_video).classes("w-full").style("height: 6em;")
        with ui.card().classes("w-full").style("max-width: 800px;"), ui.expansion("Erweiterte Funktionen").classes("w-full"):
            ui.button("Kamera neu laden", color="blue", on_click=obs_controller.reload_camera).classes("w-full").style("margin-bottom: 1em;")
            ui.button("Computer herunterfahren", color="red", on_click=lambda: os.system("shutdown /s /t 1")).classes("w-full").style("margin-bottom: 1em;")
        with ui.card().classes("w-full").style("max-width: 800px;"),  ui.expansion("Logfiles").classes("w-full"):
            with ui.column():
                for file in os.listdir("logs"):
                    if file.endswith(".log"):
                        ui.link(file + "\n", f"logs/{file}")
            ui.button("Logfiles löschen", color="red", on_click=delete_logfiles).classes("w-full")
        # add section to delete videos
        with ui.card().classes("w-full").style("max-width: 800px;"), ui.expansion("Aufnahmen löschen").classes("w-full"):
            grid = ui.grid(columns=2)
            def fill_grid():
                with grid:
                    for file, descriptor in filemanager.get_file_dict().items():
                        file_copy = file
                        ui.label(descriptor).style("margin-right: 1em;")
                        ui.button("Löschen", color="red", on_click=lambda event, file=file: [filemanager.delete_file(file), grid.clear(), fill_grid()])
            fill_grid()
        # add section to edit settings
        with ui.card().classes("w-full").style("max-width: 800px;"), ui.expansion("Einstellungen").classes("w-full"):
            with ui.row():
                with ui.time(settings.start_time.strftime("%H:%M")).props("format24h").add_slot("default"):
                    ui.label("Startzeit")
                with ui.time(settings.end_time.strftime("%H:%M")).props("format24h").add_slot("default"):
                    ui.label("Endzeit")
                with ui.time(settings.shutdown_time.strftime("%H:%M")).props("format24h").add_slot("default"):
                    ui.label("Shutdown-Zeit")
            ui.number("Löschen nach (Tage)", value=settings.delete_age.days, min=1, max=28)
            ui.checkbox("Logo anzeigen", value=settings.show_logo)
            ui.label("Wochentage")
            with ui.row():
                ui.checkbox("Montag", value = 0 in settings.weekdays)
                ui.checkbox("Dienstag", value = 1 in settings.weekdays)
                ui.checkbox("Mittwoch", value = 2 in settings.weekdays)
                ui.checkbox("Donnerstag", value = 3 in settings.weekdays)
                ui.checkbox("Freitag", value = 4 in settings.weekdays)
                ui.checkbox("Samstag", value = 5 in settings.weekdays)
                ui.checkbox("Sonntag", value = 6 in settings.weekdays)
            ui.button("Speichern") #TODO: Save settings
