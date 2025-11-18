"""
Test suite to verify YouTube playlist support
"""

import pytest
from backend.youtube_api import (
    extract_playlist_id,
    is_playlist_url,
    fetch_playlist_videos,
    extract_video_id
)


class TestPlaylistDetection:
    """Tests for playlist URL detection"""

    def test_playlist_url_with_list_parameter(self):
        """Test detection of playlist URL with list parameter"""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert is_playlist_url(url) is True

    def test_watch_url_with_playlist(self):
        """Test detection of watch URL that includes a playlist"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert is_playlist_url(url) is True

    def test_regular_watch_url_not_playlist(self):
        """Test that regular watch URLs are not detected as playlists"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_playlist_url(url) is False

    def test_short_url_not_playlist(self):
        """Test that short URLs are not detected as playlists"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert is_playlist_url(url) is False


class TestPlaylistIdExtraction:
    """Tests for playlist ID extraction"""

    def test_extract_from_playlist_url(self):
        """Test extracting playlist ID from playlist URL"""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert extract_playlist_id(url) == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    def test_extract_from_watch_url_with_playlist(self):
        """Test extracting playlist ID from watch URL with playlist parameter"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert extract_playlist_id(url) == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"


@pytest.mark.asyncio
class TestPlaylistVideoFetching:
    """Tests for fetching videos from playlists"""

    async def test_fetch_playlist_videos(self):
        """Test fetching videos from a real playlist"""
        # Use a small public playlist for testing
        playlist_id = "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

        video_ids = await fetch_playlist_videos(playlist_id, max_videos=10)

        assert video_ids is not None, "fetch_playlist_videos should not return None"
        assert len(video_ids) > 0, "Should fetch at least one video from the playlist"
        assert len(video_ids) <= 10, "Should respect max_videos limit"

        # Verify all returned items are valid video IDs (11 characters)
        for video_id in video_ids:
            assert isinstance(video_id, str), f"Video ID should be string, got {type(video_id)}"
            assert len(video_id) == 11, f"Video ID should be 11 characters, got {len(video_id)}"


@pytest.mark.parametrize("url,expected", [
    ("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", True),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", True),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", False),
    ("https://youtu.be/dQw4w9WgXcQ", False),
])
def test_is_playlist_url_parametrized(url, expected):
    """Parametrized test for playlist URL detection"""
    result = is_playlist_url(url)
    assert result == expected, f"Expected {expected} for {url}, got {result}"


@pytest.mark.parametrize("url,expected_id", [
    ("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"),
])
def test_extract_playlist_id_parametrized(url, expected_id):
    """Parametrized test for playlist ID extraction"""
    result = extract_playlist_id(url)
    assert result == expected_id, f"Expected {expected_id} for {url}, got {result}"
