# main.py
import json
import requests
import praw
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
    PEXELS_API_KEY,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
)
from google_auth_oauthlib.flow import InstalledAppFlow  # Import here
import auth # Import the auth.py script

# --- Reddit API Example using PRAW ---
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent='SocialMediaBot/0.1 by YourRedditUsername'
)

print("Top 5 posts from r/popular:")
for submission in reddit.subreddit('popular').hot(limit=5):
    print("-", submission.title)

# --- Pexels API Example using requests ---
headers = {"Authorization": PEXELS_API_KEY}
url = "https://api.pexels.com/v1/search?query=education&per_page=4"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    image_urls = [photo["src"]["large"] for photo in data.get("photos", [])]
    print("\nPexels image URLs:", image_urls)
else:
    print("Error fetching images:", response.status_code)

# --- Google API OAuth Example ---
# The URL is now printed by auth.py.  You'll need to run auth.py first.
# After authenticating, you can proceed to use the credentials.

# Option A: Use a client_secret.json file downloaded from the Google Cloud Console.
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)
# If you prefer to build your own JSON dynamically, you can do:
credentials_dict = {
    "installed": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": "your-project-id",  # Replace with your project ID
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": [GOOGLE_REDIRECT_URI]
    }
}
# Optionally, write the dictionary to a JSON file:
with open("client_secret.json", "w") as f:
    json.dump(credentials_dict, f, indent=4)

# Now create the OAuth flow using that file:
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

# You can now use the credentials obtained from auth.py in your uploader.py script.
print("\nGoogle OAuth flow initialized.  Run auth.py first to get the URL.")
