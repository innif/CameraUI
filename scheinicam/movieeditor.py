import time

start = time.time()

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
ffmpeg_extract_subclip("videos/out.mp4", 0, 10, targetname="test.mp4")

end = time.time()
print(end - start)
