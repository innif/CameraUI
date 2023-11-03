import time
from nicegui import ui, app, Client
from nicegui.events import ValueChangeEventArguments
import logging
from filemanager import VideoFile, Filemanager, FileContainer
import threading
import datetime
import asyncio
import os

class TimeSelectContainer:
    def __init__(self):
        '''Container for the time selection'''
        self.time = 0
        self.start_time = None
        self.end_time = None
        self.file = None

    def set_values(self, time: int, start_time: datetime.datetime, end_time: datetime.datetime, file: VideoFile):
        '''Sets the values of the container'''
        self.time = time
        self.start_time = start_time
        self.end_time = end_time
        self.file = file

    def set_from_file(self, file: VideoFile, end=False):
        ''''Sets the values of the container from a file'''
        self.time = 0
        self.start_time = file.start_time
        self.end_time = file.get_end_time()
        self.file = file
        if end:
            self.time = self.duration()
    
    def duration(self):
        '''Returns the duration of the container in seconds'''
        return (self.end_time - self.start_time).total_seconds()
    
    def time_as_datetime(self) -> datetime.datetime:
        '''Returns the time as a datetime object'''
        return self.start_time + datetime.timedelta(seconds=self.time)

async def download_dialog(file: VideoFile, from_time: datetime.time, to_time: datetime.time):
    '''Creates a download dialog for a video file'''
    dialog = ui.dialog()
    try:
        logging.info(f"Download Dialog for {file.filename} from {from_time.strftime('%H:%M')} to {time.strftime('%H:%M')}")
        dialog.open()
        with dialog, ui.card():
            ui.label(f"Video herunterladen von {from_time.strftime('%H:%M')} bis {to_time.strftime('%H:%M')}")
            waiting = ui.row().style("align-items: center")
            with waiting:
                ui.spinner()
                ui.label("Video wird exportiert...")
            await asyncio.sleep(0.1)
            path = await file.get_subclip(from_time, to_time)
            waiting.set_visibility(False)
            ui.label(f"Dateigröße: {get_filesize_string(path)}")
            def download():
                dialog.close()
                ui.download(path, file.get_download_filename(from_time))
                ui.notify("Download gestartet")
            ui.button("Herunterladen", on_click=download)
    except Exception as e:
        print(e)
        logging.exception(e)
        logging.error(f"Could not export video")
        ui.notify("Fehler beim Exportieren des Videos")
        dialog.close()

def preview(container: TimeSelectContainer):
    '''Creates a preview for the time selection'''
    img = ui.image("")
    ui.button("Vorschau Aktualisieren", on_click=lambda: update_img()).style("margin-top: 1em; margin-left: 1em; margin-right: 1em;")
    label = ui.label("Vorschau nicht möglich")
    def update_img():
        f = container.file
        img_available = False
        if f is not None:
            frame = f.get_frame_at(container.time_as_datetime().time())
            img.set_source(frame)
            img_available = frame is not None
        label.set_visibility(not img_available)
        img.set_visibility(img_available)
    update_img()
    return update_img

def time_selector3(container: TimeSelectContainer):
    '''Creates a time selector for the download dialog'''
    dialog = ui.dialog()

    ui.button("Zeit wählen", on_click=dialog.open)
    ui.label().bind_text_from(container, "time", backward=lambda x: (container.start_time + datetime.timedelta(seconds=x)).strftime("Gewählt: %H:%M:%S Uhr"))

    with dialog:
        range = container.duration()
        card = ui.card().tight().classes("w-full")
        with card:
            preview_update = preview(container)

        with card, ui.card_section().classes("w-full"):
            with ui.element("div").classes("w-full"):
                label = ui.label()\
                    .bind_text_from(container, "time", backward=lambda x: "Gewählte Zeit: " + (container.start_time + datetime.timedelta(seconds=x)).strftime("%H:%M:%S Uhr"))\
                    .classes("text-subtitle2").style("margin-bottom: 1em;")

            def move_label(event: ValueChangeEventArguments = None):
                if event is None:
                    val = 100*(slider.value/range)
                else:
                    val = 100*(event.value/range)
                translate = "transform: translate(-100%, 0%);" if val > 80 else\
                            "transform: translate(0%, 0%);" if val < 20 else\
                            "transform: translate(-50%, 0%);"
                badge.style(f"left: {val}%; "+translate)
                # preview_update() TODO: Automatic Update without stuttering
            with ui.grid(columns=4).classes("w-full").style("margin-bottom: 1em;"):
                def add_time(n: int):
                    container.time += n
                    if container.time < 0:
                        container.time = 0
                    elif container.time > range:
                        container.time = range
                ui.button("-1min", on_click=lambda: add_time(-60))
                ui.button("-10s", on_click=lambda: add_time(-10))
                ui.button("+10s", on_click=lambda: add_time(10))
                ui.button("+1min", on_click=lambda: add_time(60))
            slider = ui.slider(min=0, max=range, step=1, value=0, on_change=move_label)\
                .bind_value(container, "time")\
                .props("marker-labels")
            print(slider.slots)
            with slider.add_slot("marker-label-group"):
                with ui.row().classes("w-full"):
                    ui.label(container.start_time.strftime("%H:%M Uhr"))
                    ui.element("div").classes("grow")
                    ui.label(container.end_time.strftime("%H:%M Uhr"))
                #copilot, please make position relative to center
                badge = ui.badge('', color='red').props('floating').style('position: relative; left: 50%; top: 0%; transform: translate(-50%, 0%);')\
                    .bind_text_from(container, "time", backward=lambda x: (container.start_time + datetime.timedelta(seconds=x)).strftime("%H:%M:%S"))
            move_label()
            #add ok button to close dialog
            ui.button("Ok", on_click=dialog.close).style("margin-top: 1em;").classes("w-full")

    

def download_page3(client: Client, filemanager: Filemanager):
    '''Creates the download page'''
    # setup ui elements to specify start and endtime for video crop
    filecontainer = FileContainer(filemanager.newest_file())
    if filecontainer.get_file() is None:
        with ui.card():
            ui.label("Keine Aufnahmen vorhanden")
        return
    # create containers for start and end time
    time_selected_start = TimeSelectContainer()
    time_selected_end = TimeSelectContainer()
    
    def new_file_selected(event: ValueChangeEventArguments):
        ''' Called when a new file is selected '''
        time_selected_start.set_from_file(filecontainer.get_file())
        time_selected_end.set_from_file(filecontainer.get_file(), True)
        with start_card:
            start_card.clear()
            time_selector3(time_selected_start)
            with ui.stepper_navigation():
                ui.button('Weiter', on_click=stepper.next, color="green")
                ui.button('Zurück', on_click=stepper.previous).props('flat')
        with end_card:
            end_card.clear()
            time_selector3(time_selected_end)
            with ui.stepper_navigation():
                ui.button('Weiter', on_click=stepper.next, color="green")
                ui.button('Zurück', on_click=stepper.previous).props('flat')
    
    # create card to download video
    async def dialog():
        await download_dialog(filecontainer.get_file(), time_selected_start.time_as_datetime().time(), time_selected_end.time_as_datetime().time())
    
    with ui.stepper().props('vertical').classes('w-full') as stepper:
        with ui.step('Vorstellung auswählen', icon='videocam'):
            ui.label("Hier musst du den Tag auswählen, von dem du das Video herunterladen willst. Standardmäßig wird das neueste Video ausgewählt.")
            ui.select(filemanager.get_file_dict(), value=filecontainer.get_file(), on_change=new_file_selected).classes("w-full").bind_value(filecontainer, "file")
            with ui.stepper_navigation():
                ui.button('Weiter', on_click=stepper.next, color="green")
        start_card = ui.step('Startzeit auswählen', icon='timer')
        end_card = ui.step('Endzeit auswählen', icon='timer')
        with ui.step('Video exportieren', icon='file_download'):
            ui.button("Exportieren", on_click=dialog)
            ui.label("Wenn du auf den Button klickst, wird dein Video automatisch vom Server zugeschnitten. Anschließend kannst du es herunterladen.")
            with ui.stepper_navigation():
                ui.button('Zurück', on_click=stepper.previous).props('flat')
    
    new_file_selected(None)

def get_filesize_string(path: str):
    '''Returns the filesize as a string'''
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size/1024:.2f} KB"
    elif size < 1024**3:
        return f"{size/1024**2:.2f} MB"
    elif size < 1024**4:
        return f"{size/1024**3:.2f} GB"
    else:
        return f"{size/1024**4:.2f} TB"
