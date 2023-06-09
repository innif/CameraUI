import time
from nicegui import ui, app, Client
from nicegui.events import ValueChangeEventArguments
import logging
import util
from filemanager import VideoFile, Filemanager, FileContainer
import threading
import datetime
import asyncio

async def download_dialog(file, from_time_dict, to_time_dict):
    '''Creates a download dialog for a video file'''
    from_time = util.time_dict_to_time(from_time_dict)
    to_time = util.time_dict_to_time(to_time_dict)
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
            await asyncio.sleep(0.1)
            path = file.get_subclip(from_time, to_time)
            waiting.set_visibility(False)
            ui.button("Herunterladen", on_click=lambda: ui.download(path, "video.mp4"))
    except Exception as e:
        logging.exception(e)
        logging.error(f"Could not export video")
        ui.notify("Fehler beim Exportieren des Videos")
        dialog.close()

def time_selector(label, time, filecontainer: FileContainer):
    '''Creates a time selector ui-elements with a preview image'''
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
                frame = f.get_frame_at(util.time_dict_to_time(time))
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

def download_page(client: Client, filemanager: Filemanager):
    '''Creates the download page'''
    # setup ui elements to specify start and endtime for video crop
    filecontainer = FileContainer(filemanager.newest_file())
    if filecontainer.get_file() is None:
        with ui.card():
            ui.label("Keine Aufnahmen vorhanden")
        return
    def new_file_selected(event: ValueChangeEventArguments):
        set_start_time(filecontainer.get_file().start_time + datetime.timedelta(seconds=2))
        set_end_time(filecontainer.get_file().get_end_time() - datetime.timedelta(seconds=2))
    with ui.card().style("margin-bottom: 1em;"):
        ui.select(filemanager.get_file_dict(), value=filecontainer.get_file(), on_change=new_file_selected).classes("w-full").bind_value(filecontainer, "file")
    time_select_row = ui.row().classes("w-full").style("margin-bottom: 1em;")
    with time_select_row:
        start, set_start_time = time_selector("Startzeit", filecontainer.get_file().start_time + datetime.timedelta(seconds=2), filecontainer)
        end, set_end_time = time_selector("Endzeit", filecontainer.get_file().get_end_time() - datetime.timedelta(seconds=2), filecontainer)
    async def dialog():
        await download_dialog(filecontainer.get_file(), start, end)
    ui.button("Herunterladen", on_click=dialog)