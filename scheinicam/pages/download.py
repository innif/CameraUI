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
                .bind_value(time, "hour", forward=lambda x: int(x))\
                .style("width: 30%; max-width: 10em;")
            num_min = ui.number(label="Minute", min = 0, max=59, format="%02d", on_change=update_img)\
                .bind_value(time, "minute", forward=lambda x: int(x))\
                .style("width: 30%; max-width: 10em;")
            num_s = ui.number(label="Sekunde", min = 0, max=59, format="%02d", on_change=update_img)\
                .bind_value(time, "second", forward=lambda x: int(x))\
                .style("width: 30%; max-width: 10em;")
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

def time_selector2(label, time):
    '''Creates a time selector ui-elements'''
    elements = {
        'hour': {"min": 0, "max": 23, "format": "%02d", "label": "Stunde"},
        'minute': {"min": 0, "max": 59, "format": "%02d", "label": "Minute"},
        'second': {"min": 0, "max": 59, "format": "%02d", "label": "Sekunde"}
    }
    def plus_button(key, n: int):
        def add():
            time[key] = time[key] + n
            if time[key] > elements[key]["max"]:
                time[key] = elements[key]["max"]
        ui.button(text=str(n), on_click=add)\
            .classes("w-full")\
            .bind_enabled_from(time, key, lambda x: x < elements[key]["max"])\
            .props('icon=keyboard_arrow_up')
    def minus_button(key, n: int):
        def sub():
            time[key] = time[key] - n
            if time[key] < elements[key]["min"]:
                time[key] = elements[key]["min"]
        ui.button(text=str(n), on_click=sub)\
            .classes("w-full")\
            .bind_enabled_from(time, key, lambda x: x > elements[key]["min"])\
            .props('icon=keyboard_arrow_down')

    with ui.card().style("margin-bottom: 1em;"):
        ui.label(label).classes("w-full text-subtitle2 text-center")
        with ui.grid(columns=len(elements)).classes("w-full"):
            # add button to increase value
            plus_button("hour", 10)
            plus_button("minute", 10)
            plus_button("second", 10)
            # add button to increase value
            plus_button("hour", 1)
            plus_button("minute", 1)
            plus_button("second", 1)
            # add number input
            for key, value in elements.items():
                ui.number(label=value["label"], min=value["min"], max=value["max"], format=value["format"])\
                    .bind_value(time, key, forward=lambda x: int(x))\
                    .classes("w-full")\
            # add button to decrease value
            minus_button("hour", 1)
            minus_button("minute", 1)
            minus_button("second", 1)
            # add button to decrease value
            minus_button("hour", 10)
            minus_button("minute", 10)
            minus_button("second", 10)


def download_page2(client: Client, filemanager: Filemanager):
    time_selector2("Startzeit", {"hour": 19, "minute": 55, "second": 0})
    time_selector2("Endzeit", {"hour": 22, "minute": 5, "second": 0})

def download_page3(client: Client, filemanager: Filemanager):
    '''Creates the download page'''
    # setup ui elements to specify start and endtime for video crop
    filecontainer = FileContainer(filemanager.newest_file())
    if filecontainer.get_file() is None:
        with ui.card():
            ui.label("Keine Aufnahmen vorhanden")
        return
    
    def new_file_selected(event: ValueChangeEventArguments):
        pass
    
    with ui.card().style("margin-bottom: 1em;"):
        ui.label("Schritt 1: Aufnahme auswählen").classes("text-subtitle2")
        ui.select(filemanager.get_file_dict(), value=filecontainer.get_file(), on_change=new_file_selected).classes("w-full").bind_value(filecontainer, "file")
    with ui.card().style("margin-bottom: 1em;"):
        ui.label("Schritt 2: Startzeit auswählen").classes("text-subtitle2")
        class TimeContainer:
            def __init__(self, time):
                self.time = time
        time_selected = TimeContainer(0)
        start_time = filecontainer.get_file().start_time
        dialog = ui.dialog()
        with ui.row():
            label = ui.label().bind_text_from(time_selected, "time", backward=lambda x: (start_time+datetime.timedelta(seconds=x)).strftime("%H:%M:%S"))
            ui.button("Zeit wählen", on_click=dialog.open)
        with dialog:
            start_time = filecontainer.get_file().start_time
            end_time = filecontainer.get_file().get_end_time()
            range = (end_time - start_time).total_seconds()
            with ui.card().classes("w-full"):
                label = ui.label().bind_text_from(time_selected, "time", backward=lambda x: (start_time+datetime.timedelta(seconds=x)).strftime("%H:%M:%S"))
                with ui.grid(columns=4).classes("w-full"):
                    def add_time(n: int):
                        time_selected.time += n
                    ui.button("-1min", on_click=lambda: add_time(-60))
                    ui.button("-10s", on_click=lambda: add_time(-10))
                    ui.button("+10s", on_click=lambda: add_time(10))
                    ui.button("+1min", on_click=lambda: add_time(60))
                ui.slider(min=0, max=range, step=1, value=0)\
                    .bind_value(time_selected, "time").props('label-always')
    with ui.card().style("margin-bottom: 1em;"):
        ui.label("Schritt 3: Endzeit auswählen").classes("text-subtitle2")
        dialog = ui.dialog()
        with ui.row():
            label = ui.label("20:00:00")
            ui.button("Zeit wählen", on_click=dialog.open)
        with dialog:
            with ui.time(mask="HH:mm:ss").props('with-seconds now-btn format24h').bind_value_to(label, "text"):
                ui.button("OK", on_click=dialog.close)
    with ui.card().style("margin-bottom: 1em;"):
        ui.label("Schritt 4: Video herunterladen").classes("text-subtitle2")
        ui.button("Herunterladen")
