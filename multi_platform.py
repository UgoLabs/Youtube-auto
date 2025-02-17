from typing import List

def upload_to_tiktok(video_path: str, title: str, tags: List[str]) -> str:
    """
    Stub for uploading a video to TikTok.
    Replace with integration using TikTok’s API or a scheduling service.
    """
    print(f"[UPLOAD TIKTOK] Title: {title}")
    print(f"[UPLOAD TIKTOK] Tags: {tags}")
    print(f"[UPLOAD TIKTOK] Video Path: {video_path}")
    return "TIKTOK_VIDEO_ID_STUB"

def upload_to_instagram(video_path: str, caption: str, tags: List[str]) -> str:
    """
    Stub for uploading a video to Instagram (Reels/IGTV).
    """
    print(f"[UPLOAD INSTAGRAM] Caption: {caption}")
    print(f"[UPLOAD INSTAGRAM] Tags: {tags}")
    print(f"[UPLOAD INSTAGRAM] Video Path: {video_path}")
    return "INSTAGRAM_VIDEO_ID_STUB"

def upload_to_facebook(video_path: str, caption: str, tags: List[str]) -> str:
    """
    Stub for uploading a video to Facebook.
    """
    print(f"[UPLOAD FACEBOOK] Caption: {caption}")
    print(f"[UPLOAD FACEBOOK] Tags: {tags}")
    print(f"[UPLOAD FACEBOOK] Video Path: {video_path}")
    return "FACEBOOK_VIDEO_ID_STUB"
