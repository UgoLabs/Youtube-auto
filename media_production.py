import pyttsx3
import random
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from config import Config
from script_generation import generate_script
from data_fetch import fetch_trending_data

def text_to_speech(script_text, output_audio="output_audio.mp3"):
    engine = pyttsx3.init()
    engine.save_to_file(script_text, output_audio)
    engine.runAndWait()
    return output_audio

def create_faceless_video(topic):
    script_text = generate_script(topic)
    audio_file = text_to_speech(script_text)

    image_paths = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg"]  # Replace with API-fetched images

    clips = [ImageClip(img).set_duration(Config.VIDEO_DURATION_PER_IMAGE) for img in image_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    
    audio_clip = AudioFileClip(audio_file)
    if final_clip.duration > audio_clip.duration:
        final_clip = final_clip.subclip(0, audio_clip.duration)

    final_clip = final_clip.set_audio(audio_clip)
    output_video = f"{topic.replace(' ', '_')}.mp4"
    final_clip.write_videofile(output_video, fps=24, codec="libx264")

    return output_video
