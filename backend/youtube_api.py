import re
import httpx
from typing import Optional, Tuple


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If it's already just the ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    return None


async def fetch_video_metadata(video_id: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Fetch video metadata using oEmbed API (no API key required)
    Returns: (title, thumbnail_url, duration)
    Note: oEmbed doesn't provide duration, so we return None for that
    """
    try:
        async with httpx.AsyncClient() as client:
            # Use YouTube's oEmbed endpoint - no API key needed
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = await client.get(oembed_url, timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "Unknown Title")
                thumbnail = data.get("thumbnail_url", f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg")
                # oEmbed doesn't provide duration, use default thumbnail
                return title, thumbnail, None
            else:
                # Fallback to basic info
                return None, f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg", None

    except Exception as e:
        print(f"Error fetching metadata for {video_id}: {e}")
        # Return fallback thumbnail
        return None, f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg", None


async def validate_video_url(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Validate a YouTube URL and return metadata
    Returns: (is_valid, video_id, title, thumbnail)
    """
    video_id = extract_video_id(url)

    if not video_id:
        return False, None, None, None

    # Try to fetch metadata to confirm video exists
    title, thumbnail, _ = await fetch_video_metadata(video_id)

    # If we got a title back, video exists
    is_valid = title is not None

    return is_valid, video_id, title, thumbnail
