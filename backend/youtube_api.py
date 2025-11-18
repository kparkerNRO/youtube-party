import re
import httpx
from typing import Optional, Tuple, List


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


def extract_playlist_id(url: str) -> Optional[str]:
    """
    Extract YouTube playlist ID from various URL formats
    Supports:
    - https://www.youtube.com/playlist?list=PLAYLIST_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
    - https://youtube.com/playlist?list=PLAYLIST_ID
    """
    patterns = [
        r'[?&]list=([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            playlist_id = match.group(1)
            # Filter out special playlists that aren't real playlists
            if not playlist_id.startswith(('WL', 'LL', 'PL')) and len(playlist_id) < 10:
                continue
            return playlist_id

    return None


def is_playlist_url(url: str) -> bool:
    """
    Check if a URL is a playlist URL
    """
    return extract_playlist_id(url) is not None


async def fetch_playlist_videos(playlist_id: str, max_videos: int = 50) -> List[str]:
    """
    Fetch video IDs from a YouTube playlist
    Uses HTML scraping since oEmbed doesn't support playlists and we want to avoid API keys
    Returns: List of video IDs
    """
    try:
        async with httpx.AsyncClient() as client:
            # Fetch the playlist page
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            response = await client.get(playlist_url, timeout=10.0, follow_redirects=True)

            if response.status_code != 200:
                print(f"Failed to fetch playlist: HTTP {response.status_code}")
                return []

            html = response.text

            # Extract video IDs from the HTML
            # YouTube includes video data in ytInitialData JSON
            video_ids = []

            # Look for video IDs in the HTML - they appear in various patterns
            # Pattern 1: "videoId":"VIDEO_ID"
            video_id_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            matches = re.findall(video_id_pattern, html)

            # Remove duplicates while preserving order
            seen = set()
            for video_id in matches:
                if video_id not in seen:
                    seen.add(video_id)
                    video_ids.append(video_id)
                    if len(video_ids) >= max_videos:
                        break

            print(f"Found {len(video_ids)} videos in playlist {playlist_id}")
            return video_ids

    except Exception as e:
        print(f"Error fetching playlist {playlist_id}: {e}")
        return []


async def fetch_playlist_metadata(playlist_id: str) -> Tuple[Optional[str], int]:
    """
    Fetch basic playlist metadata
    Returns: (playlist_title, video_count)
    """
    try:
        async with httpx.AsyncClient() as client:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            response = await client.get(playlist_url, timeout=10.0, follow_redirects=True)

            if response.status_code != 200:
                return None, 0

            html = response.text

            # Try to extract playlist title
            title_pattern = r'"title":"([^"]+)".*?"playlistId":"' + re.escape(playlist_id)
            title_match = re.search(title_pattern, html)
            title = title_match.group(1) if title_match else None

            # Count videos
            video_count = len(re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html))

            return title, video_count

    except Exception as e:
        print(f"Error fetching playlist metadata for {playlist_id}: {e}")
        return None, 0
