import base64
import asyncio
import aiohttp
import openai
import json
from openai import Client
from gtts import gTTS
from PIL import Image
from io import BytesIO
# type: ignore
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time
import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from utils.logging_utils import setup_logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from utils.youtube_utils import upload_to_youtube
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")

# Initialize OpenAI client after loading API key
client = Client(api_key=OPENAI_API_KEY)

# Constants
TRENDING_API_URL = "https://trends.google.com/trends/api/dailytrends"
IMAGE_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

# Constants for directories
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
SCRIPT_DIR = OUTPUT_DIR / "scripts"
AUDIO_DIR = OUTPUT_DIR / "audio"
IMAGE_DIR = OUTPUT_DIR / "images"
VIDEO_DIR = OUTPUT_DIR / "videos"

# Create directories if they don't exist
for dir in [SCRIPT_DIR, AUDIO_DIR, IMAGE_DIR, VIDEO_DIR]:
    dir.mkdir(parents=True, exist_ok=True)

# Add these functions after the constants and before VideoGeneratorApp class

async def fetch_data_with_retries(url, session, params=None, headers=None, retries=3, delay=2):
    """Fetch data from an API with retry logic."""
    logging.info(f"Attempting to fetch data from: {url}")
    logging.info(f"Parameters: {params}")
    logging.info(f"Headers: {headers}")
    
    for attempt in range(retries):
        try:
            logging.info(f"Attempt {attempt + 1} of {retries}")
            async with session.get(url, params=params, headers=headers) as response:
                logging.info(f"Response status: {response.status}")
                if response.status == 200:
                    data = await response.text()  # Get raw response first
                    logging.info(f"Raw response: {data[:200]}...")  # Log first 200 chars
                    
                    # Handle Google Trends specific response format
                    if data.startswith(")]}'"):
                        data = data[5:]  # Remove the security prefix
                        logging.info("Removed Google Trends security prefix")
                    
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError as je:
                        logging.error(f"JSON decode error: {je}")
                        raise
                logging.warning(f"Attempt {attempt + 1}: Failed with status {response.status}")
        except Exception as e:
            logging.error(f"Error fetching data: {type(e).__name__} - {str(e)}")
            logging.error(f"Full exception: {e}", exc_info=True)
        await asyncio.sleep(delay)
    raise Exception("Failed to fetch data after multiple retries")

async def get_trending_topics():
    """Fetch trending topics from Google Trends."""
    async with aiohttp.ClientSession() as session:
        response = await fetch_data_with_retries(
            TRENDING_API_URL, session, params={"geo": "US"}
        )
        trends = response["default"]["trendingSearchesDays"][0]["trendingSearches"]
        return [trend["title"]["query"] for trend in trends]

async def generate_script(topic):
    """Generate a video script using OpenAI."""
    try:
        # Step 1: Generate the initial script
        initial_prompt = f"Write a 500-word YouTube video script about {topic}."
        initial_response = client.chat.completions.create(
            model="gpt-4",  # Fixed typo from gpt-4o
            messages=[
                {"role": "system", "content": "You're a scriptwriter."},
                {"role": "user", "content": initial_prompt},
            ]
        )
        initial_script = initial_response.choices[0].message.content
        
        # Step 2: Clean up the script
        cleanup_prompt = """Please clean up this script to contain ONLY the spoken narration. 
        Remove all:
        - [Stage directions]
        - Scene descriptions
        - Technical instructions
        - "Narrator:" or "V.O.:" prefixes
        - [SEGMENT] headers
        - [INTRO]/[OUTRO] markers
        
        Return ONLY the actual spoken words that should be read aloud."""
        
        cleanup_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a script editor."},
                {"role": "user", "content": initial_script},
                {"role": "user", "content": cleanup_prompt},
            ]
        )
        
        clean_script = cleanup_response.choices[0].message.content
        
        # Save both versions
        save_script(initial_script, "generated_script_full.txt")
        save_script(clean_script, "generated_script_clean.txt")
        
        return clean_script  # Return the clean version for TTS
        
    except Exception as e:
        logging.error(f"Error generating script: {e}")
        raise
def save_script(text, filename):
    """Save the generated script to a file."""
    try:
        filepath = SCRIPT_DIR / filename
        with open(filepath, "w") as f:
            f.write(text)
        logging.info(f"Script saved to: {filepath}")
        return str(filepath)
    except Exception as e:
        logging.error(f"Error saving script: {e}")
        raise
def text_to_speech(text):
    """Convert text to speech using gTTS."""
    try:
        tts = gTTS(text=text, lang='en')
        audio_file = AUDIO_DIR / "temp_audio.mp3"
        tts.save(str(audio_file))
        return str(audio_file)
    except Exception as e:
        logging.error(f"Error converting text to speech: {e}")
        raise

async def generate_image(prompt):
    """Generate an image using Stability AI."""
    if not IMAGE_API_KEY:
        raise Exception("Stability AI API key not found in environment variables")
        
    headers = {
        "Authorization": f"Bearer {IMAGE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
        "cfg_scale": 7,
        "steps": 30,
        "width": 1024,
        "height": 1024,
        "samples": 1,
        "style_preset": "photographic"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                IMAGE_API_URL, 
                headers=headers, 
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Save the first generated image
                    image_data = base64.b64decode(data['artifacts'][0]['base64'])
                    image = Image.open(BytesIO(image_data))
                    image_file = IMAGE_DIR / "temp_image.png"
                    image.save(str(image_file))
                    logging.info(f"Image generated successfully and saved as {image_file}")
                    return str(image_file)
                else:
                    error_text = await response.text()
                    logging.error(f"Image generation failed with status {response.status}: {error_text}")
                    raise Exception(f"Failed to generate image: {error_text}")
    except Exception as e:
        logging.error(f"Error in generate_image: {str(e)}")
        raise

def create_video(image_file, audio_file, output_file="output_video.mp4"):
    """Assemble an image and audio into a video."""
    try:
        output_path = VIDEO_DIR / output_file
        image_clip = ImageClip(image_file).set_duration(60)
        audio_clip = AudioFileClip(audio_file)
        video = image_clip.set_audio(audio_clip)
        video.write_videofile(str(output_path), fps=24, codec="libx264", verbose=False, logger=None)
        return str(output_path)
    except Exception as e:
        logging.error(f"Error creating video: {e}")
        raise

def upload_to_youtube(video_file, title, description):
    """Upload a video to YouTube using OAuth."""
    try:
        # Load client secrets
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            ["https://www.googleapis.com/auth/youtube.upload"]
        )
        
        # Get credentials
        credentials = flow.run_local_server(port=0)
        
        # Build YouTube service
        youtube = build("youtube", "v3", credentials=credentials)
        
        # Upload video
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["Trending", "AI Generated"],
                    "categoryId": "22",
                },
                "status": {"privacyStatus": "private"},  # Start as private for safety
            },
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )
        
        # Execute upload
        response = request.execute()
        return response
        
    except Exception as e:
        logging.error(f"Error uploading video: {e}")
        raise

class VideoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Generator")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Topic Entry
        ttk.Label(self.main_frame, text="Topic:").pack(anchor=tk.W)
        self.topic_entry = ttk.Entry(self.main_frame, width=50)
        self.topic_entry.pack(fill=tk.X, pady=5)
        
        # Trending Topics Button
        ttk.Button(
            self.main_frame, 
            text="Get Trending Topics", 
            command=self.get_trending
        ).pack(pady=5)
        
        # Generate Button
        ttk.Button(
            self.main_frame, 
            text="Generate Video", 
            command=self.generate_video
        ).pack(pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            self.main_frame, 
            length=300, 
            mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self.main_frame, 
            textvariable=self.status_var
        ).pack(pady=5)
        
        # Save/Upload Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame, 
            text="Save Video", 
            command=self.save_video
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Upload to YouTube", 
            command=self.upload_video
        ).pack(side=tk.LEFT, padx=5)

        # Store generated files
        self.generated_video = None
        self.generated_script = None

    def get_trending(self):
        """Get trending topics"""
        asyncio.run(self._get_trending_async())

    async def _get_trending_async(self):
        try:
            topics = await get_trending_topics()
            self.show_topic_selection(topics)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get trending topics: {str(e)}")

    def show_topic_selection(self, topics):
        """Show topic selection window"""
        window = tk.Toplevel(self.root)
        window.title("Select Topic")
        for topic in topics:
            ttk.Button(
                window,
                text=topic,
                command=lambda t=topic: self.select_topic(t, window)
            ).pack(pady=2, padx=5, fill=tk.X)

    def select_topic(self, topic, window):
        """Select a topic from the list"""
        self.topic_entry.delete(0, tk.END)
        self.topic_entry.insert(0, topic)
        window.destroy()

    def generate_video(self):
        """Generate the video"""
        topic = self.topic_entry.get()
        if not topic:
            messagebox.showerror("Error", "Please enter a topic first!")
            return
        
        # Run the generation in a separate thread to not block GUI
        asyncio.run(self._generate_video_async(topic))

    async def _generate_video_async(self, topic):
        try:
            self.status_var.set("Generating script...")
            self.progress['value'] = 20
            self.root.update_idletasks()
            
            # Generate and save script (now returns clean version)
            clean_script = await generate_script(topic)
            self.generated_script_full = "generated_script_full.txt"
            self.generated_script_clean = "generated_script_clean.txt"
            
            self.status_var.set("Creating voiceover...")
            self.progress['value'] = 40
            self.root.update_idletasks()
            
            # Use clean script for TTS
            audio_file = text_to_speech(clean_script)
            self.generated_audio = audio_file
            
            self.status_var.set("Generating image...")
            self.progress['value'] = 60
            self.root.update_idletasks()
            
            # Generate image
            image_file = await generate_image(f"{topic} visuals")
            self.generated_image = image_file
            
            self.status_var.set("Creating video...")
            self.progress['value'] = 80
            self.root.update_idletasks()
            
            # Create final video
            self.generated_video = create_video(image_file, audio_file)
            
            self.progress['value'] = 100
            self.status_var.set("Video generated successfully!")
            
            # Show summary of generated files
            summary = f"""Generated files:
            Full Script: {self.generated_script_full}
            Clean Script: {self.generated_script_clean}
            Audio: {self.generated_audio}
            Image: {self.generated_image}
            Video: {self.generated_video}"""
            messagebox.showinfo("Success", summary)
            
        except Exception as e:
            self.status_var.set("Error occurred!")
            messagebox.showerror("Error", str(e))

    def save_video(self):
        """Save the video locally"""
        if not self.generated_video:
            messagebox.showerror("Error", "No video has been generated yet!")
            return
        messagebox.showinfo("Save", f"Video saved as: {self.generated_video}")

    def upload_video(self):
        """Upload the video to YouTube"""
        if not self.generated_video:
            messagebox.showerror("Error", "No video has been generated yet!")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to upload to YouTube?"):
            try:
                topic = self.topic_entry.get()
                response = upload_to_youtube(
                    self.generated_video,
                    topic,
                    f"Automated video about {topic}"
                )
                messagebox.showinfo("Success", "Video uploaded to YouTube!")
            except Exception as e:
                messagebox.showerror("Error", f"Upload failed: {str(e)}")

# Keep all your existing async functions here
# (get_trending_topics, generate_script, generate_image, etc.)
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoGeneratorApp(root)
    root.mainloop()