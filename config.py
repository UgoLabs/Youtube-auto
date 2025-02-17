# config.py
import os
from dotenv import load_dotenv

# Explicitly set the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Retrieve the environment variables
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# For debugging (remove later)
if __name__ == "__main__":
    print("Reddit Client ID:", REDDIT_CLIENT_ID)
    print("Reddit Client Secret:", REDDIT_CLIENT_SECRET)
    print("PEXELS_API_KEY:", PEXELS_API_KEY)
    print("Google Client ID:", GOOGLE_CLIENT_ID)
    print("Google Client Secret:", GOOGLE_CLIENT_SECRET)
    print("Google Redirect URI:", GOOGLE_REDIRECT_URI)
