import asyncio
import aiohttp
import json
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
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
import torch
import functools
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from bark import SAMPLE_RATE, generate_audio, preload_models
import scipy.io.wavfile as wavfile
from agent.image_generator import generate_image
from huggingface_hub import login
import gc
import torch.serialization
import numpy as np
import soundfile as sf
import random
import asyncio
from datetime import datetime, timedelta
from transformers import BitsAndBytesConfig

# Allowlist the numpy scalar type (np.generic is the base for numpy scalars)
torch.serialization.add_safe_globals({'numpy.core.multiarray.scalar': np.generic})

# Monkey-patch torch.load to force weights_only=False
old_torch_load = torch.load

def custom_torch_load(f, map_location=None, **kwargs):
    kwargs['weights_only'] = False
    return old_torch_load(f, map_location=map_location, **kwargs)

torch.load = custom_torch_load

# List of historical topics
HISTORICAL_TOPICS = [
    "The Best English Kings",
    "Fascinating Queens of Europe",
    "Notorious Villains in History",
    "Major World Wars",
    "The Rise and Fall of the Roman Empire",
    "The Medieval Crusades",
    "Renaissance Art and Culture",
    "Industrial Revolution Breakthroughs",
    "The Cold War Era",
    "Ancient Egyptian Pharaohs",
    "Greek Mythology and Legends",
    "The History of the British Monarchy",
    "The French Revolution",
    "The American Civil War",
    "The Age of Exploration",
    "Piracy in the Caribbean",
    "The Viking Age",
    "Feudal Japan",
    "The Ottoman Empire",
    "The Ming Dynasty",
    "Ancient Mesopotamia",
    "The Inca Empire",
    "The Aztec Empire",
    "Colonialism in Africa",
    "The Age of Enlightenment",
    "Revolutionary France",
    "Napoleonic Wars",
    "The Fall of the Berlin Wall",
    "The History of Democracy",
    "The Silk Road",
    "Ancient Greek City-States",
    "Roman Conquests",
    "The Crusades",
    "The Spanish Inquisition",
    "The Tudor Dynasty",
    "The Plantagenets",
    "Victorian Britain",
    "World War I Trench Warfare",
    "The Great Depression",
    "The Russian Revolution",
    "The Civil Rights Movement",
    "The Reformation",
    "The Battle of Hastings",
    "The Sacking of Rome",
    "The Battle of Waterloo",
    "Ancient Indian Empires",
    "The Maurya Dynasty",
    "The Gupta Empire",
    "The Mughal Empire",
    "The Partition of India",
    "Medieval European Feudalism",
    "The Battle of Agincourt",
    "The Age of Discovery",
    "Christopher Columbus",
    "The Fall of Constantinople",
    "The Renaissance in Italy",
    "Baroque Art and Architecture",
    "The Enlightenment Thinkers",
    "The Industrial Revolution",
    "The Scientific Revolution",
    "The Space Race",
    "The History of Aviation",
    "The Gold Rush",
    "The History of Slavery",
    "The Trail of Tears",
    "The Underground Railroad",
    "The Vietnam War",
    "The Korean War",
    "The Cuban Missile Crisis",
    "The Partition of Africa",
    "The Suez Crisis",
    "Ancient Mayan Civilization",
    "The History of Islam",
    "The Crusades in the Middle East",
    "The Byzantine Empire",
    "The History of the Samurai",
    "The Opium Wars",
    "The Boxer Rebellion",
    "The Meiji Restoration",
    "The Russian Tsars",
    "The Russian Revolution of 1917",
    "The Fall of the Soviet Union",
    "Modern European Integration",
    "The European Union's Formation",
    "Historical Conquests of Alexander the Great",
    "Ancient Carthage",
    "The Punic Wars",
    "The Life of Julius Caesar",
    "The History of the Huns",
    "Attila the Hun",
    "Medieval Trade Routes",
    "The Black Death",
    "The History of the Plague",
    "The Sumerians and Babylonians",
    "The Construction of the Pyramids",
    "Ancient Chinese Dynasties",
    "The Qin Dynasty",
    "The Han Dynasty",
    "The Warring States Period",
    "The Feudal System",
    "Medieval European Castles",
    "The Rise of Islam",
    "The Battle of Tours",
    "The Norman Conquest",
    "Medieval Chivalry",
    "The Crusader States",
    "Historical Maritime Exploration",
    "The Discovery of America",
    "Colonial America",
    "The History of the Constitution",
    "The Civil War and Reconstruction",
    "The Gilded Age",
    "The Progressive Era",
    "The History of American Industry",
    "The Story of Silicon Valley",
    "The Evolution of Warfare",
    "The Age of Imperialism",
    "The History of Human Rights",
    "The Evolution of Modern Democracy",
    "The History of Banking and Finance",
    "The Renaissance of Science",
    "Historical Figures Who Changed the World",
    "The Battle of Stalingrad",
    "The Rise and Fall of the Byzantine Empire",
    "The Story of Ancient Troy",
    "The Renaissance in Northern Europe",
    "The Sumerian Civilization",
    "The Siege of Constantinople",
    "The Reign of King Henry VIII",
    "The Rise of the British Empire",
    "The Fall of the Western Roman Empire",
    "The Age of the Pharaohs",
    "The Life of Cleopatra",
    "The History of Ancient Greece",
    "The Medici Family's Influence",
    "The Battle of Thermopylae",
    "The Great Fire of London",
    "The Mongol Empire's Expansion",
    "The Age of Jackson",
    "The Marshall Plan",
    "The History of the Eiffel Tower",
    "The Zulu Kingdom",
    "The History of the Taj Mahal",
    "The Berlin Airlift",
    "The Origins of the First Crusade",
    "The Fall of the Aztec Empire",
    "The Battle of Gettysburg",
    "The Rise of Nationalism in Europe",
    "The Harlem Renaissance",
    "The Reconstruction Era in the US",
    "The History of the American West",
    "The Battle of the Bulge",
    "The History of the United Nations",
    "The Rise of the Ottoman Empire",
    "The Reign of Louis XIV",
    "The Battle of Trafalgar",
    "The Story of Anne Frank",
    "The History of the Space Shuttle",
    "The Haitian Revolution",
    "The Invention of the Printing Press",
    "The History of the Magna Carta",
    "The Fall of Napoleon Bonaparte",
    "The Evolution of the British Navy",
    "The Life of King Tutankhamun",
    "The History of the Pyramids of Giza",
    "The Greek and Persian Wars",
    "The Invention of the Airplane",
    "The Origins of the Cold War",
    "The Rise of Fascism in Europe",
    "The Influence of the Roman Empire",
    "The Life and Death of Socrates",
    "The Evolution of Naval Warfare",
    "The Age of Sail",
    "The Significance of the Rosetta Stone",
    "The Age of Exploration in the Americas",
    "The Role of Women in World War II",
    "The Battle of Midway",
    "The Rise of the Communist Party in China",
    "The History of the Roman Republic",
    "The Salem Witch Trials",
    "The History of Nuclear Weapons",
    "The Fall of the Inca Empire",
    "The Uprising of 1857 in India",
    "The Evolution of the Printing Press",
    "The History of the Underground Railroad",
    "The History of Ancient China",
    "The Impact of the Black Death",
    "The Battle of Antietam",
    "The Great Schism in the Christian Church",
    "The Rise of the Aztec Civilization",
    "The Origins of Ancient Egypt",
    "The Wars of the Roses in England",
    "The Founding of the Roman Empire"
]
HISTORICAL_TOPICS = list(dict.fromkeys(HISTORICAL_TOPICS))

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Define directory constants
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
SCRIPT_DIR = OUTPUT_DIR / "scripts"
AUDIO_DIR = OUTPUT_DIR / "audio"
IMAGE_DIR = OUTPUT_DIR / "images"
VIDEO_DIR = OUTPUT_DIR / "videos"
for dir in [SCRIPT_DIR, AUDIO_DIR, IMAGE_DIR, VIDEO_DIR]:
    dir.mkdir(parents=True, exist_ok=True)

# Asynchronous helper functions for API calls
async def fetch_data_with_retries(url, session, params=None, headers=None, retries=3, delay=2):
    logging.info(f"Attempting to fetch data from: {url}")
    for attempt in range(retries):
        try:
            async with session.get(url, params=params, headers=headers) as response:
                logging.info(f"Response status: {response.status}")
                if response.status == 200:
                    data = await response.text()
                    if data.startswith(")]}'"):
                        data = data[5:]
                    return json.loads(data)
                logging.warning(f"Attempt {attempt + 1}: Failed with status {response.status}")
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
        await asyncio.sleep(delay)
    raise Exception("Failed to fetch data after multiple retries")

async def get_trending_topics():
    async with aiohttp.ClientSession() as session:
        response = await fetch_data_with_retries("https://trends.google.com/trends/api/dailytrends", session, params={"geo": "US"})
        trends = response["default"]["trendingSearchesDays"][0]["trendingSearches"]
        return [trend["title"]["query"] for trend in trends]

def generate_script(topic):
    try:
        initial_prompt = f"Write a 500-word YouTube video script about {topic}."
        generator = pipeline("text-generation", model="microsoft/phi-2",  # Changed from Mixtral
                             device=0 if torch.cuda.is_available() else -1)
        generation = generator(initial_prompt, max_length=1024, do_sample=True)
        initial_script = generation[0]['generated_text']
        cleanup_prompt = ("Clean up this script to contain ONLY the spoken narration. \n"
                          "Remove any stage directions, scene descriptions, technical instructions, "
                          'and any "Narrator:" or "V.O.:" prefixes or markers. Return only the spoken words.')
        full_prompt = initial_script + "\n\n" + cleanup_prompt
        clean_generation = generator(full_prompt, max_length=1024, do_sample=True)
        clean_script = clean_generation[0]['generated_text']
        save_script(initial_script, "generated_script_full.txt")
        save_script(clean_script, "generated_script_clean.txt")
        return clean_script
    except Exception as e:
        logging.error(f"Error generating script: {e}")
        raise

def save_script(text, filename):
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
    try:
        from bark import generate_audio, preload_models, SAMPLE_RATE
        preload_models()
        audio_array = generate_audio(text)
        audio_file = AUDIO_DIR / "temp_audio.wav"
        sf.write(str(audio_file), audio_array, SAMPLE_RATE)
        return str(audio_file)
    except Exception as e:
        logging.error(f"Error converting text to speech: {e}")
        raise

async def generate_image(prompt):
    from agent.image_generator import generate_image as generate_image_sync
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_image_sync, prompt)

def create_video(image_file, audio_file, output_file="output_video.mp4"):
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
    try:
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
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
        # For headless servers
        credentials = flow.run_console()
        youtube = build("youtube", "v3", credentials=credentials)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["Trending", "AI Generated"],
                    "categoryId": "22",
                },
                "status": {"privacyStatus": "private"},
            },
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )
        response = request.execute()
        return f"https://youtu.be/{response.get('id')}"
    except Exception as e:
        logging.error(f"Error uploading video: {e}")
        raise

def setup_huggingface():
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_TOKEN not found in environment variables")
    login(token=token)

class VideoCreator:
    def __init__(self):
        setup_huggingface()
        self.setup_directories()
        self.setup_models()
        self.youtube_credentials = None
        self.available_topics = HISTORICAL_TOPICS.copy()
        
    def setup_directories(self):
        self.base_dir = Path(__file__).resolve().parent
        self.dirs = {
            'audio': self.base_dir / "output/audio",
            'video': self.base_dir / "output/video",
            'script': self.base_dir / "output/scripts"
        }
        for dir in self.dirs.values():
            dir.mkdir(parents=True, exist_ok=True)
            
    def setup_models(self):
        try:
            model_id = "microsoft/phi-2"  # Changed from mistralai/Mistral-7B-Instruct-v0.2

            # Required 4-bit quantization config - still needed for Phi-2
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            )

            # Load with quantization
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",
                quantization_config=quantization_config,
                torch_dtype=torch.float16
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                token=os.getenv("HUGGINGFACE_TOKEN"),
                trust_remote_code=True
            )
            preload_models()
            logging.info("Models loaded successfully")
        except Exception as e:
            logging.error(f"Error setting up models: {e}")
            raise
        
    def generate_script(self, topic: str) -> str:
        prompt = f"""You are a professional script writer for educational history videos.
    
Write an engaging 45-minute YouTube script about {topic}.
The script should be informative and entertaining.
Format: Clear introduction, the main points, and conclusion.
"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=1000,
            temperature=0.7,
            num_return_sequences=1,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        script = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        script_path = self.dirs['script'] / f"{topic.replace(' ', '_')}.txt"
        script_path.write_text(script)
        return script
    
    def generate_voice(self, text: str) -> str:
        audio_array = generate_audio(text)
        output_path = str(self.dirs['audio'] / "audio.wav")
        wavfile.write(output_path, SAMPLE_RATE, audio_array)
        return output_path
        
    async def create_video_async(self, topic: str) -> dict:
        # Wrap all blocking functions in asyncio.to_thread
        script = await asyncio.to_thread(self.generate_script, topic)
        await asyncio.to_thread(self.cleanup_memory)
        audio_path = await asyncio.to_thread(self.generate_voice, script)
        image_path = await generate_image(topic)
        video_path = await asyncio.to_thread(self._create_video_from_media, image_path, audio_path, topic)
        youtube_url = await asyncio.to_thread(
            self.upload_to_youtube,
            video_path,
            f"The History of {topic}: Explained",  # Changed from "Understanding {topic} - AI Explained"
            f"A comprehensive exploration of {topic} throughout history.\n\n{script[:500]}..."  # Removed AI references
        )
        return {
            "video_path": video_path,
            "youtube_url": youtube_url,
            "script": script
        }
    
    def _create_video_from_media(self, image_file: str, audio_file: str, topic: str) -> str:
        try:
            video_dir = self.dirs['video']
            video_path = str(video_dir / f"{topic.replace(' ', '_')}.mp4")
            audio_clip = AudioFileClip(audio_file)
            image_clip = ImageClip(image_file).set_duration(audio_clip.duration)
            video = image_clip.set_audio(audio_clip)
            video.write_videofile(video_path, fps=24, codec="libx264", logger=None)
            return video_path
        except Exception as e:
            logging.error(f"Error creating video: {e}")
            raise

    def upload_to_youtube(self, video_path: str, title: str, description: str) -> str:
        try:
            client_secrets_file = os.path.join(self.base_dir, 'client_secrets.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file,
                ['https://www.googleapis.com/auth/youtube.upload']
            )
            # Change this line for headless servers
            credentials = flow.run_console()  # <-- CHANGE THIS LINE
            youtube = build('youtube', 'v3', credentials=credentials)
            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": ["History", "Education", "Historical"],  # Removed "AI Generated"
                        "categoryId": "27"
                    },
                    "status": {
                        "privacyStatus": "private",
                        "selfDeclaredMadeForKids": False
                    }
                },
                media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
            )
            response = request.execute()
            return f"https://youtu.be/{response.get('id')}"
        except Exception as e:
            logging.error(f"YouTube upload error: {e}")
            raise

    def cleanup_memory(self):
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

class VideoGeneratorGUI:
    def __init__(self):
        self.creator = VideoCreator()
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Historical Video Generator")
        self.root.geometry("800x600")
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Select Historical Topic:", font=('Helvetica', 12)).pack(pady=10)
        self.topic_var = tk.StringVar()
        self.topic_combo = ttk.Combobox(frame, textvariable=self.topic_var, width=60, values=HISTORICAL_TOPICS)
        self.topic_combo.pack(pady=10)
        self.topic_combo.set("Select a topic")
        self.status_label = ttk.Label(frame, text="", font=('Helvetica', 10))
        self.status_label.pack(pady=10)
        self.progress_text = tk.Text(frame, height=15, width=70)
        self.progress_text.pack(pady=10)
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Generate & Upload Video", command=self.generate_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Random Topic", command=self.select_random_topic).pack(side=tk.LEFT, padx=5)
    
    def select_random_topic(self):
        import random
        self.topic_var.set(random.choice(HISTORICAL_TOPICS))
        
    def generate_video(self):
        topic = self.topic_var.get()
        if topic == "Select a topic":
            messagebox.showerror("Error", "Please select a historical topic")
            return
        self.progress_text.delete(1.0, tk.END)
        self.status_label.config(text="Processing... Please wait")
        self.update_progress(f"Starting video generation for: {topic}")
        try:
            result = self.creator.create_video(topic)
            self.update_progress(f"Video created: {result['video_path']}")
            self.update_progress(f"YouTube URL: {result['youtube_url']}")
            self.status_label.config(text="Success!")
            messagebox.showinfo("Success", f"Video created and uploaded!\nYouTube URL: {result['youtube_url']}")
        except Exception as e:
            self.status_label.config(text="Error!")
            self.update_progress(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def update_progress(self, message):
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.see(tk.END)
        self.root.update()

    def run(self):
        self.root.mainloop()

class ContinuousVideoCreator:
    def __init__(self, creator, interval_hours=6):
        """Set up a continuous video creator that runs every interval_hours"""
        self.creator = creator
        self.interval_hours = interval_hours
        self.topics = HISTORICAL_TOPICS.copy()
        random.shuffle(self.topics)
        self.topic_index = 0
        
    def get_next_topic(self):
        """Get the next topic, cycling through the shuffled list"""
        topic = self.topics[self.topic_index]
        self.topic_index = (self.topic_index + 1) % len(self.topics)
        if self.topic_index == 0:  # We've gone through all topics, shuffle again
            random.shuffle(self.topics)
        return topic
        
    async def run_forever(self):
        """Run video creation continuously at specified intervals"""
        while True:
            try:
                topic = self.get_next_topic()
                logging.info(f"Starting video creation for topic: {topic}")
                
                start_time = datetime.now()
                result = await self.creator.create_video_async(topic)
                
                end_time = datetime.now()
                duration = end_time - start_time
                logging.info(f"Video created in {duration} - YouTube URL: {result['youtube_url']}")
                
                # Calculate time until next run
                next_run = timedelta(hours=self.interval_hours) - duration
                if next_run.total_seconds() > 0:
                    logging.info(f"Waiting {next_run} until next video creation")
                    await asyncio.sleep(next_run.total_seconds())
                
            except Exception as e:
                logging.error(f"Error in continuous video creation: {e}", exc_info=True)
                # Even if there's an error, wait before trying again
                await asyncio.sleep(60 * 30)  # Wait 30 minutes after an error

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Auto Video Generator")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI mode without GUI")
    parser.add_argument("--topic", type=str, help="Specific topic to generate video for")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous mode")
    parser.add_argument("--interval", type=int, default=6, help="Hours between videos in continuous mode")
    args = parser.parse_args()
    
    if args.continuous:
        logging.info("Starting in continuous mode")
        creator = VideoCreator()
        continuous_creator = ContinuousVideoCreator(creator, interval_hours=args.interval)
        asyncio.run(continuous_creator.run_forever())
    elif args.no_gui:
        import random
        logging.info("Starting in CLI mode")
        creator = VideoCreator()
        topic = args.topic if args.topic else random.choice(HISTORICAL_TOPICS)
        logging.info(f"Selected topic: {topic}")
        try:
            result = asyncio.run(creator.create_video_async(topic))
            logging.info(f"Video created: {result['video_path']}")
            logging.info(f"YouTube URL: {result['youtube_url']}")
        except Exception as e:
            logging.error(f"Error in video creation: {e}")
    else:
        app = VideoGeneratorGUI()
        app.run()