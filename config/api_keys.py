import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def validate_api_keys():
    """Validate that all required API keys are present."""
    required_keys = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
        "YOUTUBE_API_KEY": YOUTUBE_API_KEY,
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}") 