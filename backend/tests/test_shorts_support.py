"""
Test suite to verify YouTube Shorts URL parsing support
"""

import pytest
from backend.youtube_api import extract_video_id


class TestYouTubeShortsSupport:
    """Tests for YouTube URL parsing including Shorts URLs"""

    def test_standard_watch_url(self):
        """Test standard YouTube watch URL"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_youtu_be_url(self):
        """Test short youtu.be URL"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        """Test YouTube embed URL"""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_mobile_watch_url(self):
        """Test mobile YouTube watch URL"""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_shorts_url_with_www(self):
        """Test YouTube Shorts URL with www"""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_shorts_url_without_www(self):
        """Test YouTube Shorts URL without www"""
        url = "https://youtube.com/shorts/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_mobile_shorts_url(self):
        """Test mobile YouTube Shorts URL"""
        url = "https://m.youtube.com/shorts/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_just_video_id(self):
        """Test with just the video ID"""
        url = "dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_invalid_domain(self):
        """Test that invalid domains return None"""
        url = "https://example.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) is None

    def test_missing_video_id(self):
        """Test that URLs without video ID return None"""
        url = "https://www.youtube.com/watch"
        assert extract_video_id(url) is None


@pytest.mark.parametrize("url,expected_id,description", [
    # Standard YouTube URLs
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Standard watch URL"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Short youtu.be URL"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Embed URL"),
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Mobile watch URL"),
    # YouTube Shorts URLs
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Shorts URL with www"),
    ("https://youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Shorts URL without www"),
    ("https://m.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Mobile Shorts URL"),
    # Edge cases
    ("dQw4w9WgXcQ", "dQw4w9WgXcQ", "Just the video ID"),
    ("https://example.com/watch?v=dQw4w9WgXcQ", None, "Invalid domain"),
    ("https://www.youtube.com/watch", None, "Missing video ID"),
])
def test_extract_video_id_parametrized(url, expected_id, description):
    """Parametrized test for various YouTube URL formats"""
    result = extract_video_id(url)
    assert result == expected_id, f"Failed for {description}: expected {expected_id}, got {result}"
