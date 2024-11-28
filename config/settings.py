import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Project settings
PROJECT_NAME = "YouTube Automation"
VERSION = "1.0.0"

# Video settings
VIDEO_SETTINGS = {
    "resolution": (1920, 1080),
    "fps": 30,
    "default_duration": 60,
}

# API endpoints
API_ENDPOINTS = {
    "openai": "https://api.openai.com/v1",
    "elevenlabs": "https://api.elevenlabs.io/v1",
}

# Cache settings
CACHE_DIR = BASE_DIR / "cache"
CACHE_DURATION = 3600  # 1 hour in seconds 