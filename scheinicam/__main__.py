from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments
from obscontroller import ObsController
import time
import threading

status = "Bereit"
html_preview = ""
status_text = "Bereit"

obs_controller = ObsController()

def start_record(name):
    global status_text
    if obs_controller.recording:
        ui.notify("Aufnahme läuft bereits")
        return
    if name == "":
        ui.notify("Bitte Namen eingeben")
        return
    obs_controller.record(name)
    ui.notify(f'Start recording {name}')
    status_text = "Aufnahme für " + name + " läuft"

def stop_record():
    global status_text, recording
    if not obs_controller.recording:
        ui.notify("Keine Aufnahme läuft")
        return
    obs_controller.stop()
    ui.notify('Stop recording')
    status_text = "Bereit"

# Title
# ui.markdown('# ScheiniCam')

def recording_page():
    # Camera Preview
    with ui.expansion("Vorschau", icon="image", value=True):
        preview = ui.html("")
        preview.bind_content(globals(), 'html_preview')

    # Buttons
    with ui.row().style("margin-top: 1em;"):
        recording_icon = ui.spinner('pie', size='1em', color='red')
        recording_icon.bind_visibility(obs_controller, 'recording')
        status_label = ui.badge('', color="red")
        status_label.bind_text(globals(), 'status_text')

    # Name Input
    name_input = ui.input('Name').style("margin-bottom: 1em;")

    # Record Controls
    with ui.row():
        ui.button('Aufnahme starten', color="red", on_click=lambda: start_record(name_input.value))
        ui.button('Aufnahme stoppen', color="blue", on_click=stop_record)
    
    # PTZ-Controls
    # ui.separator().style("margin-top: 1em; margin-bottom: 1em;")
    # with ui.expansion("Kamera bewegen", icon="control_camera"):
    #     with ui.column().classes('w-full items-center'):
    #         with ui.row():
    #             ui.button('Bühne Weit')
    #             ui.button('Bühne Closeup')
    #             ui.button('Klavier')
    #         ui.joystick(color='black', size=200,
    #         on_move=lambda e: coordinates.set_text(f"{e.x:.3f}, {e.y:.3f}"),
    #         on_end=lambda _: coordinates.set_text('0, 0')
    #         )
    #         coordinates = ui.label('0, 0')

def download_page():
    ui.label('This is the second tab')
    ui.button('Download', on_click=lambda: ui.download("/videos/video.mp4", "Entwurf Intro.mp4"))

@ui.page("/")
def index():
    with ui.tabs() as tabs:
        ui.tab('Aufnahme', icon='videocam')
        ui.tab('Download', icon='file_download')
    # Content
    with ui.tab_panels(tabs, value='Aufnahme'):
        with ui.tab_panel('Aufnahme'):
            recording_page()
        with ui.tab_panel('Download'):
            download_page()

def update_preview():
    global html_preview
    while True:
        img_data = obs_controller.get_screenshot()
        html_preview = f"<img src=\"{img_data}\" width=\"512\" style=\"max-width: 100%;\" />"
        time.sleep(.5)

t = threading.Thread(target=update_preview)
t.start()

app.add_static_files('/videos', 'videos')

ui.run(title="ScheiniCam")