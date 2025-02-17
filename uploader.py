from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    """Authenticate and return the YouTube API client."""
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def upload_to_youtube(video_path, title, description, tags):
    """Upload a video to YouTube."""
    youtube = authenticate_youtube()
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # 22 = People & Blogs, change this if needed
            },
            "status": {
                "privacyStatus": "public"  # Options: "public", "private", "unlisted"
            }
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    
    response = request.execute()
    print("✅ Video uploaded successfully! Video ID:", response["id"])
    return response["id"]

# Example Usage:
# upload_to_youtube("your_video.mp4", "My Video Title", "Description here", ["tag1", "tag2"])
if __name__ == "__main__":
    upload_to_youtube("test_video.mp4", "Test Video", "This is a test upload.", ["test", "bot"])
