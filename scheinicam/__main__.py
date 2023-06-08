from nicegui import ui, app, Client
from nicegui.events import ValueChangeEventArguments
from obscontroller import ObsController
import time
import threading
from filemanager import VideoFile, Filemanager, FileContainer
import datetime
import logging

#TODO: direkt herunterladen nach aufnahme beenden anbieten
#TODO: Löschen von Aufnahmen
#TODO: Admin-Seite

logging.basicConfig(filename=f'logs/log{datetime.datetime.now().strftime("%y-%m-%d--%H-%M-%S")}.log', encoding='utf-8', level=logging.INFO)

html_preview = ""
status_text = "Bereit"

obs_controller = ObsController()
filemanager = Filemanager()

WIDTH = "50em"
start_time = datetime.time(1, 45, 0)
end_time = datetime.time(1, 50, 0)
delete_age = datetime.timedelta(days=7)

app.add_static_files('/videos', 'videos')
app.add_static_files('/assets', 'assets')

def set_time_marker():
    ui.notify("Zeitmarker gesetzt")

def start_record():
    global status_text
    if not obs_controller.connected or obs_controller.recording:
        logging.warning("Could not start recording because OBS is not connected or already recording")
        return
    try:
        file = obs_controller.record()
        if file is None:
            logging.error("Could not start recording because file is None")
            return
        filemanager.add_file(file)
        file.export_as_json()
        status_text = "Aufnahme läuft"
        logging.info(f"Started recording {file.filename}")
    except Exception as e:
        logging.exception(e)
        logging.error(f"Could not start recording")
        return

def stop_record():
    global status_text
    if not obs_controller.connected or not obs_controller.recording:
        logging.warning("Could not stop recording because OBS is not connected or not recording")
        return
    try:
        obs_controller.stop()
        obs_controller.file.stop_recording()
        logging.info(f"Stopped recording {obs_controller.file.filename}")
    except Exception as e:
        logging.exception(e)
        logging.error(f"Could not stop recording")
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
    try:
        logging.info(f"Download Dialog for {file.filename} from {from_time_dict} to {to_time_dict}")
        dialog.open()
        with dialog, ui.card():
            ui.label(f"Video herunterladen von {from_time.strftime('%H:%M')} bis {to_time.strftime('%H:%M')}")
            waiting = ui.row().style("align-items: center")
            with waiting:
                ui.spinner()
                ui.label("Video wird exportiert...")
            path = file.get_subclip(from_time, to_time)
            waiting.set_visibility(False)
            ui.button("Herunterladen", on_click=lambda: ui.download(path, "video.mp4"))
    except Exception as e:
        logging.exception(e)
        logging.error(f"Could not export video")
        ui.notify("Fehler beim Exportieren des Videos")
        dialog.close()

def download_page(client: Client):
    # setup ui elements to specify start and endtime for video crop
    filecontainer = FileContainer(filemanager.newest_file())
    def new_file_selected(event: ValueChangeEventArguments):
        set_start_time(filecontainer.get_file().start_time + datetime.timedelta(seconds=2))
        set_end_time(filecontainer.get_file().get_end_time() - datetime.timedelta(seconds=2))
    with ui.card().style("margin-bottom: 1em;"):
        ui.select(filemanager.get_file_dict(), value=filecontainer.get_file(), on_change=new_file_selected).classes("w-full").bind_value(filecontainer, "file")

    def time_selector(label, time):
        with ui.card().tight().style("min-width: 100%;"):
            time = {"hour": time.hour, "minute": time.minute, "second": time.second}
            img = ui.image("") #TODO: replace with preview image
            label = None
            with ui.card_section():
                label = ui.label("Vorschau nicht möglich")
            def update_img(value = None):
                f = filecontainer.get_file()
                img_available = False
                if f is not None:
                    frame = f.get_frame_at(time_dict_to_time(time))
                    img.set_source(frame)
                    img_available = frame is not None
                label.set_visibility(not img_available)
                img.set_visibility(img_available)
            with ui.card_section(), ui.row():
                num_h = ui.number(label="Stunde", min = 0, max=23, format="%02d", on_change=update_img)\
                    .bind_value(time, "hour", forward=lambda x: int(x))
                num_min = ui.number(label="Minute", min = 0, max=59, format="%02d", on_change=update_img)\
                    .bind_value(time, "minute", forward=lambda x: int(x))
                num_s = ui.number(label="Sekunde", min = 0, max=59, format="%02d", on_change=update_img)\
                    .bind_value(time, "second", forward=lambda x: int(x))
            def set_time(new_time: datetime.time):
                time["hour"] = new_time.hour
                time["minute"] = new_time.minute
                time["second"] = new_time.second
                threading.Thread(target=update_img).start()
            update_img()
            # with ui.card_section(), ui.row(): #TODO: add buttons to change time
            #     ui.button("-30s")   
            #     ui.button("+30s")   
            return time, set_time
    time_select_row = ui.row().classes("w-full").style("margin-bottom: 1em;")
    with time_select_row:
        start, set_start_time = time_selector("Startzeit", filecontainer.get_file().start_time + datetime.timedelta(seconds=2))
        end, set_end_time = time_selector("Endzeit", filecontainer.get_file().get_end_time() - datetime.timedelta(seconds=2))
    ui.button("Herunterladen", on_click=lambda: download_dialog(filecontainer.get_file(), start, end))
              
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
    # TODO Add options for start and end time

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
            logging.exception(e)
            logging.error(f"Could not update preview")
        time.sleep(.5)

t = threading.Thread(target=update_preview)
t.start()

# create a thread that automatically starts and stops the recording at the specified times
def auto_record():
    if not obs_controller.connected:
        return
    now = datetime.datetime.now().time()
    if now > start_time and now < end_time:
        if not obs_controller.recording:
            logging.info("Starting recording")
            start_record()
    else:
        if obs_controller.recording:
            logging.info("Stopping recording")
            stop_record()


filemanager.delete_files_older_than(delete_age)
filemanager.delete_subclips()
ui.timer(1, auto_record)
ui.run(title="ScheiniCam")