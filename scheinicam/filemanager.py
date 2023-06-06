import datetime
from nicegui import ui
import json
import os
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from PIL import Image
from io import BytesIO
import base64

class VideoFile:
    def __init__(self, start_time=None, filename=None):
        if start_time is None:
            start_time = datetime.datetime.now()
        self.start_time = start_time
        if filename is None:
            self._generate_filename()
            print("new file: ", self.filename)
        else:
            self.filename = filename
        self.clip = None

    def _generate_filename(self):
        ''' Generate filename '''
        now = datetime.datetime.now()
        output = now.strftime("%y-%m-%d_%H-%M-%S")
        self.filename = f"{output}"
    
    def generate_ui(self):
        '''Generate UI'''
        with ui.card().classes('w-full'):
            #with ui.row():
            ui.html(f"{self.start_time.strftime('%d.%m.%Y, %H:%M')}")
            with ui.row():
                ui.button("Preview", on_click=lambda: ui.open(f"videos/{self.filename}.mp4"))
                ui.button("Download", on_click=lambda: ui.download(f"videos/{self.filename}.mp4"))

    def export_as_json(self):
        '''Export as json'''
        data = {
            "start_time": self.start_time.isoformat(),
            "filename": self.filename,
        }
        json.dump(data, open(f"videos/{self.filename}.json", "w"))

    def get_subclip(self, start: datetime.time, end: datetime.time):
        '''Get subclip'''
        self.generate_video_clip()
        start = datetime.datetime.combine(self.start_time.date(), start)
        end = datetime.datetime.combine(self.start_time.date(), end)
        # calculate start and end in seconds
        start_seconds = (start - self.start_time).total_seconds()
        end_seconds = (end - self.start_time).total_seconds()
        if end_seconds < start_seconds or start_seconds < 0 or end_seconds > self.clip.duration:
            raise Exception("Invalid time range")
        print(f"start: {start_seconds}, end: {end_seconds}")
        output_path = f"videos/{self.filename}-{start_seconds}-{end_seconds}.mp4"
        ffmpeg_extract_subclip(f"videos/{self.filename}.mp4", start_seconds, end_seconds, targetname=output_path)
        return output_path
    
    def get_frame_at(self, time: datetime.time):
        if self.clip is None:
            self.generate_video_clip()
        timestamp = datetime.datetime.combine(self.start_time.date(), time)
        timestamp_seconds = (timestamp - self.start_time).total_seconds()
        if self.clip is None or timestamp_seconds < 0 or timestamp_seconds > self.clip.duration:
            return None
        frame = self.clip.get_frame(timestamp_seconds)
        # convert to frame base64 with jpg encoding
        img = Image.fromarray(frame, 'RGB')
        buff = BytesIO()
        img.save(buff, format="JPEG")
        img_string = base64.b64encode(buff.getvalue()).decode("utf-8")
        return f"data:image/jpg;base64,{img_string}" 
    
    def generate_video_clip(self):
        try:
            self.clip = mp.VideoFileClip(f"videos/{self.filename}.mp4")
        except Exception as e:
            print("Could not load video clip")

    def get_descriptor(self):
        '''Get descriptor'''
        return self.start_time.strftime("%d.%m.%Y") #TODO: Add more information


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
        start_time = datetime.datetime.fromisoformat(data["start_time"])
        file = VideoFile(start_time, data["filename"])
        return file

    def get_file_dict(self):
        '''Get file dict'''
        return {file: file.get_descriptor() for file in self.files}