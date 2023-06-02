from nicegui import ui, app, Client
from nicegui.events import ValueChangeEventArguments
from obscontroller import ObsController
import time
import threading
from filemanager import VideoFile, Filemanager

#TODO: direkt herunterladen nach aufnahme beenden anbieten
#TODO: Löschen von Aufnahmen
#TODO: Admin-Seite

html_preview = ""
status_text = "Bereit"

obs_controller = ObsController()
filemanager = Filemanager()

WIDTH = "50em"

app.add_static_files('/videos', 'videos')
app.add_static_files('/assets', 'assets')

def start_record(name, ip):
    global status_text
    if obs_controller.recording:
        ui.notify("Aufnahme läuft bereits")
        return
    if name == "":
        ui.notify("Bitte Namen eingeben")
        return
    try:
        obs_controller.record(name, ip)
        ui.notify(f'Start recording {name}')
        status_text = "Aufnahme für " + name + " läuft"
    except Exception as e:
        ui.notify(e)
        return

def stop_record():
    global status_text, recording
    if not obs_controller.recording:
        ui.notify("Keine Aufnahme läuft")
        return
    try:
        file = obs_controller.stop()
        filemanager.add_file(file)
        file.export_as_json()
        ui.notify('Stop recording')
    except Exception as e:
        ui.notify(e)
    status_text = "Bereit"

# Title
# ui.markdown('# ScheiniCam')

def recording_page(client: Client):
    connecting_card = ui.card().style("margin-bottom: 1em;")
    with connecting_card:
        with ui.row().style('align-items: center'):
            ui.spinner()
            ui.label('Verbinde mit OBS')
    connecting_card.bind_visibility_from(obs_controller, 'connected', backward=lambda x: not x)

    # Camera Preview
    with ui.expansion("Vorschau", icon="image", value=True):
        preview = ui.html("")
        preview.bind_content(globals(), 'html_preview')

    # Buttons
    with ui.row().style("margin-top: 1em;").bind_visibility_from(obs_controller, 'connected'):
        recording_icon = ui.spinner('pie', size='1em', color='red')
        recording_icon.bind_visibility_from(obs_controller, 'recording')
        status_label = ui.badge('', color="red")
        status_label.bind_text(globals(), 'status_text')

    # Name Input
    name_input = ui.input('Name').style("margin-bottom: 1em;")

    # Record Controls
    record_row = ui.row()
    with record_row:
        ui.button('Aufnahme starten', color="red", on_click=lambda: start_record(name_input.value, client.ip))
        ui.button('Aufnahme stoppen', color="blue", on_click=stop_record)
    record_row.bind_visibility_from(obs_controller, 'connected')

def download_page(client: Client):
    def refresh():
        file_column.clear()
        with file_column:
            for file in filemanager.files:
                if file.ip == client.ip:
                    file.generate_ui()
            with ui.expansion('Aufnahmen von anderen Geräten').classes('w-full'):
                with ui.column().classes('w-full'):
                    for file in filemanager.files:
                        if file.ip != client.ip:
                            file.generate_ui()
      
    ui.button('Aktualisieren', on_click=refresh).style("margin-bottom: 1em;")
    file_column = ui.column()
    ui.timer(1.0, refresh, once=True)

@ui.page("/")
def index(client: Client):
    with ui.column().style("margin: 0em; width: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;"):
        with ui.tabs().style(f"width: {WIDTH}; max-width: 100%; display: block;") as tabs: 
            ui.tab('Aufnahme', icon='videocam')
            ui.tab('Download', icon='file_download')
        # Content
        with ui.tab_panels(tabs, value='Aufnahme').style(f"width: {WIDTH}; max-width: 100%;"):
            with ui.tab_panel('Aufnahme').style("width: 100%;"):
                recording_page(client)
            with ui.tab_panel('Download').style("width: 100%;"):
                download_page(client)

# add admin page
@ui.page("/admin")
def admin(client: Client):
    # Add Button to Mute and Unmute Recording
    with ui.row().style("margin-top: 1em;").bind_visibility_from(obs_controller, 'connected'):
        ui.button('Aufnahme stumm schalten', color="red", on_click=obs_controller.mute_video)
        ui.button('Aufnahme wieder einschalten', color="blue", on_click=obs_controller.unmute_video)

def update_preview():
    global html_preview
    while True:
        try:
            img_data = obs_controller.get_screenshot()
            if img_data is None:
                html_preview = "<p>Keine Verbindung zu OBS</p>"
            else:
                html_preview = f"<img src=\"{img_data}\" width=\"512\" style=\"max-width: 100%;\" />"
        except Exception as e:
            print(e)
        time.sleep(.5)

t = threading.Thread(target=update_preview)
t.start()

ui.run(title="ScheiniCam")