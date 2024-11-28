from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import logging

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
                "status": {"privacyStatus": "private"},
            },
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )
        
        # Execute upload
        response = request.execute()
        return response
        
    except Exception as e:
        logging.error(f"Error uploading video: {e}")
        raise
