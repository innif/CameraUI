from datetime import datetime
from nicegui import ui
import json
import os

class VideoFile:
    def __init__(self, username, start_time=None, end_time=None, filename=None, ip=None):
        if start_time is None:
            start_time = datetime.now()
        self.start_time = start_time
        self.end_time = end_time
        self.username = username
        self.ip = ip
        if filename is None:
            self._generate_filename()
        else:
            self.filename = filename

    def _generate_filename(self):
        ''' Generate filename '''
        now = datetime.now()
        output = now.strftime("%y-%m-%d_%H-%M-%S")
        self.filename = f"{self.username}_{output}"
    
    def set_end_time(self, end_time=None):
        if end_time is None:
            end_time = datetime.now()
        self.end_time = end_time

    def generate_ui(self):
        '''Generate UI'''
        with ui.card().classes('w-full'):
            #with ui.row():
            ui.html(f"<b>{self.username}</b><br/>{self.start_time.strftime('%d.%m.%Y, von %H:%M')} bis {self.end_time.strftime('%H:%M')}")
            with ui.row():
                ui.button("Preview", on_click=lambda: ui.open(f"videos/{self.filename}.mp4"))
                ui.button("Download", on_click=lambda: ui.download(f"videos/{self.filename}.mp4"))

    def export_as_json(self):
        '''Export as json'''
        data = {
            "username": self.username,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "filename": self.filename,
            "ip": self.ip
        }
        json.dump(data, open(f"videos/{self.filename}.json", "w"))

class Filemanager:
    def __init__(self):
        '''Initialize Filemanager'''
        self.files = [] # TODO: Load files from json
        self.scan_files()

    def add_file(self, file: VideoFile):
        '''Add file to filemanager'''
        self.files.append(file)
        
    def scan_files(self):
        '''scan for json files and add them to the list'''
        for filename in os.listdir("videos"):
            if filename.endswith(".json"):
                self.files.append(self.file_from_json(f"videos/{filename}"))

    def file_from_json(self, filename):
        '''Create file from json'''
        data = json.load(open(filename, "r"))
        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.fromisoformat(data["end_time"])
        file = VideoFile(data["username"], start_time, end_time, data["filename"], data.get("ip"))
        return file
