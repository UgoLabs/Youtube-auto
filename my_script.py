# my_script.py
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# Your editing code here
clip = VideoFileClip("input.mp4")
final_clip = clip.fx(resize, width=1280)
final_clip.write_videofile("output.mp4")
