from nicegui import ui, app, Client
from nicegui.events import ValueChangeEventArguments
from obscontroller import ObsController
import time
import threading
from filemanager import VideoFile, Filemanager
import datetime

#TODO: direkt herunterladen nach aufnahme beenden anbieten
#TODO: Löschen von Aufnahmen
#TODO: Admin-Seite

html_preview = ""
status_text = "Bereit"

obs_controller = ObsController()
filemanager = Filemanager()

WIDTH = "50em"
start_time = datetime.time(1, 43, 0)
end_time = datetime.time(6, 44, 0)

app.add_static_files('/videos', 'videos')
app.add_static_files('/assets', 'assets')

def set_time_marker():
    ui.notify("Zeitmarker gesetzt")

def start_record():
    global status_text
    if obs_controller.recording:
        return
    try:
        file = obs_controller.record()
        if file is None:
            return
        filemanager.add_file(file)
        file.export_as_json()
        status_text = "Aufnahme läuft"
    except Exception as e:
        return

def stop_record():
    global status_text
    if not obs_controller.recording:
        return
    try:
        obs_controller.stop()
    except Exception as e:
        return
    status_text = "Bereit"

# Title
# ui.markdown('# ScheiniCam')

def recording_page(client: Client):
    with ui.card().tight().style("margin-bottom: 1em;"):
        with ui.expansion("Anleitung", icon="description").classes("w-full"):
            with ui.card_section():
                ui.markdown(open("assets/manual.md").read())

    connecting_card = ui.card().style("margin-bottom: 1em;")
    with connecting_card:
        with ui.row().style('align-items: center'):
            ui.spinner()
            ui.label('Verbinde mit OBS')
    connecting_card.bind_visibility_from(obs_controller, 'connected', backward=lambda x: not x)

    recording_card = ui.card().tight().style("margin-bottom: 1em;")
    with recording_card:
        # Show Camera Preview
        preview = ui.html("")
        preview.bind_content_from(globals(), 'html_preview')
        with ui.card_section():
            with ui.row().style('align-items: center'):
                ui.button('Zeitmarker setzen', on_click=set_time_marker)
                ui.spinner('pie', size='1em', color='red')
                ui.badge('Aufnahme läuft', color="red")
    recording_card.bind_visibility_from(obs_controller, 'recording')

    no_recording_card = ui.card().style("margin-bottom: 1em;")
    with no_recording_card:
        ui.html(f"<p>Zur Zeit läuft keine Aufnahme.</p> <p>Die Aufnahme startet {start_time.strftime('%H:%M')} Uhr und endet {end_time.strftime('%H:%M')} Uhr automatisch.</p> <p>Die Aufnahmen können weiterhin heruntergeladen werden.</p>")
    no_recording_card.bind_visibility_from(obs_controller, 'recording', backward=lambda x: not x)

def time_dict_to_time(time_dict):
    return datetime.time(time_dict["hour"], time_dict["minute"], time_dict["second"])

def download_dialog(file, from_time_dict, to_time_dict):
    from_time = time_dict_to_time(from_time_dict)
    to_time = time_dict_to_time(to_time_dict)
    dialog = ui.dialog()
    dialog.open()
    ui.image()
    with dialog, ui.card():
        ui.label(f"Video herunterladen von {from_time.strftime('%H:%M')} bis {to_time.strftime('%H:%M')}")
        waiting = ui.row().style("align-items: center")
        with waiting:
            ui.spinner()
            ui.label("Video wird exportiert...")
        path = obs_controller.file.get_subclip(from_time, to_time)
        waiting.set_visibility(False)
        ui.button("Herunterladen", on_click=lambda: ui.download(path, "video.mp4"))

def download_page(client: Client):
    # setup ui elements to specify start and endtime for video crop
    with ui.card().style("margin-bottom: 1em;"):
        ui.select(filemanager.get_file_dict()).classes("w-full")

    def time_selector(label, time):
        with ui.card().tight().style("min-width: 100%;"):
            time = {"hour": time.hour, "minute": time.minute, "second": time.second}
            img = ui.image("") #TODO: replace with preview image
            def update_img(value):
                if obs_controller.file is not None:
                    img.set_source(obs_controller.file.get_frame_at(time_dict_to_time(time)))
            ui.button("Vorschau", on_click=update_img)
            with ui.card_section(), ui.row():
                ui.number(label="Stunde", min = start_time.hour, max=end_time.hour, format="%02d", on_change=update_img).bind_value(time, "hour", forward=lambda x: int(x))
                ui.number(label="Minute", min = 0, max=59, format="%02d", on_change=update_img).bind_value(time, "minute", forward=lambda x: int(x))
                ui.number(label="Sekunde", min = 0, max=59, format="%02d", on_change=update_img).bind_value(time, "second", forward=lambda x: int(x))
            # with ui.card_section(), ui.row(): #TODO: add buttons to change time
            #     ui.button("-30s")   
            #     ui.button("+30s")   
            return time
    with ui.row().classes("w-full").style("margin-bottom: 1em;"):
        start = time_selector("Startzeit", start_time)
        end = time_selector("Endzeit", end_time)
    ui.button("Herunterladen", on_click=lambda: download_dialog(obs_controller.file, start, end))
              
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
    with ui.row().style("margin-top: 1em;").bind_visibility_from(obs_controller, 'connected'):
        ui.button('Aufnahme starten', color="red", on_click=start_record)
        ui.button('Aufnahme stoppen', color="blue", on_click=stop_record)

def update_preview():
    global html_preview
    while True:
        try:
            img_data = obs_controller.get_screenshot()
            if img_data is None:
                html_preview = "<p>Keine Verbindung zu OBS</p>"
            else:
                html_preview = f"<img src=\"{img_data}\" width=\"100%\"/>"
        except Exception as e:
            print(e)
        time.sleep(.5)

t = threading.Thread(target=update_preview)
t.start()

# create a thread that automatically starts and stops the recording at the specified times
def auto_record():
    if not obs_controller.connected:
        time.sleep(1)
        return
    now = datetime.datetime.now().time()
    if now > start_time and now < end_time:
        if not obs_controller.recording:
            start_record()
            print("started recording")
    else:
        if obs_controller.recording:
            stop_record()

ui.timer(1, auto_record)
ui.run(title="ScheiniCam")