from nicegui import ui
from nicegui.events import ValueChangeEventArguments
import obsws_python as obs

name = ""
status = "Bereit"
recording = False
try:
    cl = obs.ReqClient(host='localhost', port=4455, password='tXqFcBWo7WngUnAs')
    resp = cl.get_record_status()
    print(resp)
except Exception as e:
    e.printStackTrace()
    print("OBS nicht erreichbar")

def update_name(event: ValueChangeEventArguments):
    global name
    name = event.value

def start_record():
    global status, name, recording
    if recording:
        ui.notify("Aufnahme läuft bereits")
        return
    if name == "":
        ui.notify("Bitte Namen eingeben")
        return
    ui.notify(f'Start recording {name}')
    status = "Aufnahme für " + name + " läuft"
    status_label.set_text(f'Status: {status}')
    recording = True
    recording_icon.visible = recording

def stop_record():
    global status, recording
    if not recording:
        ui.notify("Keine Aufnahme läuft")
        return
    ui.notify('Stop recording')
    status = "Bereit"
    status_label.set_text(f'Status: {status}')
    recording = False
    recording_icon.visible = recording

# Title
# ui.markdown('# ScheiniCam')

with ui.tabs() as tabs:
    ui.tab('Aufnahme', icon='videocam')
    ui.tab('Download', icon='file_download')

# Content
with ui.tab_panels(tabs, value='Aufnahme'):
    with ui.tab_panel('Aufnahme'):
        # Camera Preview
        image_url = "http://192.168.188.116:8080/video"#"https://www.scheinbar.de/site/assets/files/11659/scheinbar_by_max_zerrahn-10.jpeg"
        html = f"<img src=\"{image_url}\" width=\"500\" style=\"max-width: 100%\"/>"
        ui.html(html)
        # Buttons
        with ui.row().style("margin-top: 1em;"):
            recording_icon = ui.spinner('pie', size='1em', color='red')
            recording_icon.visible = recording
            status_label = ui.badge(f'Status: {status}', color="red")

        ui.input('Name', on_change=update_name).style("margin-bottom: 1em;")
        with ui.row():
            ui.button('Aufnahme starten', color="red", on_click=start_record)
            ui.button('Aufnahme stoppen', color="blue", on_click=stop_record)
        ui.separator().style("margin-top: 1em; margin-bottom: 1em;")
        with ui.expansion("Kamera bewegen", icon="control_camera"):
            with ui.column().classes('w-full items-center'):
                with ui.row():
                    ui.button('Bühne Weit')
                    ui.button('Bühne Closeup')
                    ui.button('Klavier')
                ui.joystick(color='black', size=200,
                on_move=lambda e: coordinates.set_text(f"{e.x:.3f}, {e.y:.3f}"),
                on_end=lambda _: coordinates.set_text('0, 0')
                )
                coordinates = ui.label('0, 0')

    with ui.tab_panel('Download'):
        ui.label('This is the second tab')

ui.run()