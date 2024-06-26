import datetime
from nicegui import ui, run, app
import json
import os
import moviepy.editor as mp 
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import cv2
from PIL import Image
from io import BytesIO
import base64
import logging
import asyncio
import time

def get_base64_img(cv2_clip, seconds):
    print("cv2 operation")
    # get frame
    cv2_clip.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
    _, frame = cv2_clip.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (800, 450))
    # convert to frame base64 with jpg encoding
    img = Image.fromarray(frame, 'RGB')
    buff = BytesIO()
    img.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

class VideoFile:
    '''Represents a video file'''
    def __init__(self, start_time=None, filename=None, end_time = None):
        '''Initialize'''
        if start_time is None:
            start_time = datetime.datetime.now() # if no start time is given, use current time
        self.start_time = start_time
        if filename is None:
            self._generate_filename() # if no filename is given, generate one
            logging.info(f"new file: {self.filename}")
        else:
            self.filename = filename
        self.clip = None
        self.cv_clip = None
        self.end_time = end_time # end time None means that the video is still recording

    def _generate_filename(self):
        ''' Generate filename like 22-04-16_12-34-56.mp4'''
        now = datetime.datetime.now()
        output = now.strftime("%y-%m-%d_%H-%M-%S")
        self.filename = f"{output}"
    
    def generate_ui(self):
        '''
        Generate UI Card, presenting options to download and preview the video
        TODO: add option to delete video
        '''
        with ui.card().classes('w-full'):
            ui.html(f"{self.start_time.strftime('%d.%m.%Y, %H:%M')}")
            with ui.row():
                ui.button("Preview", on_click=lambda: ui.open(f"videos/{self.filename}.mp4"))
                ui.button("Download", on_click=lambda: ui.download(f"videos/{self.filename}.mp4"))

    async def export_as_json(self):
        '''Export as json'''
        data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time is not None else None,
            "filename": self.filename,
        }
        await run.io_bound(json.dump, data, open(f"videos/{self.filename}.json", "w"))

    async def get_subclip(self, start: datetime.time, end: datetime.time):
        '''
        Get subclip
        start: start time of subclip
        end: end time of subclip
        returns: path to subclip
        '''
        await self.generate_video_clip()
        start = datetime.datetime.combine(self.start_time.date(), start)
        end = datetime.datetime.combine(self.start_time.date(), end)
        # calculate start and end in seconds
        start_seconds = (start - self.start_time).total_seconds()
        end_seconds = (end - self.start_time).total_seconds()
        # validate time range
        if end_seconds < start_seconds or start_seconds < 0 or end_seconds > self.clip.duration:
            raise Exception("Invalid time range") # TODO: give warning to user
        logging.info(f"subclip in range start: {start_seconds}, end: {end_seconds}")
        output_path = f"videos/subclip_{self.filename}-{start_seconds}-{end_seconds}.mp4"
        # create subclip
        await run.cpu_bound(ffmpeg_extract_subclip, f"videos/{self.filename}.mp4", start_seconds, end_seconds, targetname=output_path)
        return output_path
    
    async def get_frame_at(self, time: datetime.time):
        '''Get frame at time, output as base64'''
        try:
            print("get frame at time")
            # generate video clip if not already generated or if video is still recording and clip is older than 10 seconds
            if self.clip is None or (self.end_time is None and self.get_age() > self.clip.duration + 10):
                print("generate video clip")
                await self.generate_video_clip()
            # calculate timestamp in seconds
            timestamp = datetime.datetime.combine(self.start_time.date(), time)
            timestamp_seconds = (timestamp - self.start_time).total_seconds()
            # validate clip and timestamp
            if self.clip is None or timestamp_seconds < 0 or timestamp_seconds > self.clip.duration:
                print("none")
                return None
            
            # img_string = await run.cpu_bound(get_base64_img, self.clip, timestamp_seconds)
            img_string = get_base64_img(self.cv_clip, timestamp_seconds)
            # return base64 string
            return f"data:image/jpg;base64,{img_string}" 
        except Exception as e:
            logging.exception(e)
            logging.error("Could not load frame at time")
            return ""
    
    async def generate_video_clip(self):
        '''Generate video clip'''
        try:
            logging.info(f"Generating video clip: {self.filename}")
            self.clip = mp.VideoFileClip(f"videos/{self.filename}.mp4", target_resolution=(300, None), resize_algorithm='fast_bilinear', audio=False)
            #self.clip = self.clip.set_fps(2)
            self.cv_clip = cv2.VideoCapture(f"videos/{self.filename}.mp4")
            # TODO: run in seperate Thread
        except Exception as e:
            logging.exception(e)
            logging.error("Could not load video clip")
        logging.info("Video clip generated")

    def get_descriptor(self):
        '''Get descriptor for selector in download dialog'''
        if self.end_time is None:
            return "{} (seit {} laufend)".format(
                self.start_time.strftime("%A, %d.%m.%Y"),
                self.start_time.strftime("%H:%M Uhr"))

        return "{} ({} - {})".format(
            self.start_time.strftime("%A, %d.%m.%Y"), 
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M")) #TODO: Add more information
    
    def get_download_filename(self, time: datetime.time):
        '''Get download filename'''
        return "Scheinbar_{}_{}.mp4".format(self.start_time.strftime("%Y-%m-%d"), time.strftime("%H-%M"))
    
    async def stop_recording(self):
        '''Stop recording'''
        self.clip = None
        self.end_time = datetime.datetime.now() - datetime.timedelta(seconds=1) # move end time one second back
        await self.export_as_json()

    def get_end_time(self):
        '''Get end time'''
        if self.end_time is None:
            return datetime.datetime.now()
        return self.end_time
    
    async def calculate_end_time(self):
        '''Calculate end time based on length of video clip'''
        if self.clip is None:
            await self.generate_video_clip()
        self.end_time = self.start_time + datetime.timedelta(seconds=self.clip.duration) # calculate end time based on length of video clip
        self.end_time = self.end_time - datetime.timedelta(seconds=1) # move end time one second back

    def get_age(self):
        '''Get clip age'''
        return (datetime.datetime.now() - self.start_time).total_seconds()

    def close(self):
        '''Close clip'''
        if self.clip is not None:
            self.clip.close()

class Filemanager:
    def __init__(self, delete_old_files_age: datetime.timedelta = None):
        '''Initialize Filemanager'''
        self.files = [] # TODO: Load files from json
        app.on_startup(self.startup(delete_old_files_age))

    async def startup(self, age: datetime.timedelta):
        await self.scan_files()
        if age is not None:
            self.delete_files_older_than(age)
            self.delete_subclips()

    def add_file(self, file: VideoFile):
        '''Add file to filemanager'''
        self.files.append(file)
        
    async def scan_files(self):
        '''scan for json files and add them to the list'''
        for filename in os.listdir("videos"):
            if filename.endswith(".json"):
                file = await self.file_from_json(f"videos/{filename}")
                if file is None:
                    continue
                try:
                    if file.end_time is None:
                        await file.calculate_end_time()
                        await file.export_as_json()
                    self.files.append(file)
                except Exception as e:
                    logging.exception(e)
                    logging.error(f"Could not load file {filename}")

    async def file_from_json(self, filename):
        '''Create file from json'''
        try:
            data = await run.io_bound(json.load, open(filename, "r"))
            start_time = datetime.datetime.fromisoformat(data["start_time"])
            end_time = None if data["end_time"] is None else datetime.datetime.fromisoformat(data["end_time"])
            file = VideoFile(start_time=start_time, end_time=end_time, filename=data["filename"])
            return file
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not load file {filename}")
            return None

    def get_file_dict(self):
        '''Get file dict'''
        return {file: file.get_descriptor() for file in self.files}
    
    def newest_file(self):
        '''Get newest file'''
        if len(self.files) == 0:
            return None
        return max(self.files, key=lambda file: file.start_time)
    
    def delete_file(self, file: VideoFile):
        '''Delete file'''
        try:
            file.close()
            self.files.remove(file)
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not remove file {file}")
        try:
            os.remove(f"videos/{file.filename}.mp4")
            os.remove(f"videos/{file.filename}.json")
        except Exception as e:
            logging.exception(e)
            logging.error(f"Could not remove file {file}")

    def delete_files_older_than(self, age: datetime.timedelta):
        '''Delete files older than age'''
        for file in self.files:
            logging.info(f"Checking file {file}")
            if file.start_time < datetime.datetime.now() - age:
                logging.info(f"Deleting file {file}")
                self.delete_file(file)

    def delete_subclips(self):
        '''Delete subclips'''
        for filename in os.listdir("videos"):
            if filename.startswith("subclip_"):
                try:
                    logging.info(f"Deleting subclip {filename}")
                    os.remove(f"videos/{filename}")
                except Exception as e:
                    logging.exception(e)
                    logging.error(f"Could not remove file {filename}")
    
class FileContainer:
    def __init__(self, file: VideoFile):
        '''Initialize FileContainer'''
        self.file = file

    def get_file(self):
        '''Get file'''
        return self.file