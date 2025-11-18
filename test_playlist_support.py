#!/usr/bin/env python3
"""
Test script to verify playlist support
"""
import asyncio
from backend.youtube_api import (
    extract_playlist_id,
    is_playlist_url,
    fetch_playlist_videos,
    extract_video_id
)


async def test_playlist_detection():
    """Test playlist URL detection"""
    print("Testing playlist URL detection...")

    # Test cases
    test_urls = [
        ("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", True),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", True),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", False),
        ("https://youtu.be/dQw4w9WgXcQ", False),
    ]

    for url, expected in test_urls:
        result = is_playlist_url(url)
        status = "✓" if result == expected else "✗"
        print(f"{status} {url[:60]}... → {result}")


async def test_playlist_id_extraction():
    """Test playlist ID extraction"""
    print("\nTesting playlist ID extraction...")

    test_urls = [
        ("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"),
    ]

    for url, expected in test_urls:
        result = extract_playlist_id(url)
        status = "✓" if result == expected else "✗"
        print(f"{status} {url[:60]}... → {result}")


async def test_fetch_playlist():
    """Test fetching videos from a real playlist"""
    print("\nTesting playlist video extraction...")
    print("Using a small test playlist...")

    # Use a small public playlist for testing
    # This is a small playlist with a few videos
    playlist_id = "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    print(f"Fetching videos from playlist: {playlist_id}")
    video_ids = await fetch_playlist_videos(playlist_id, max_videos=10)

    if video_ids:
        print(f"✓ Successfully fetched {len(video_ids)} videos")
        print(f"  First few video IDs: {video_ids[:5]}")
    else:
        print("✗ Failed to fetch videos from playlist")


async def main():
    """Run all tests"""
    print("=" * 70)
    print("YouTube Playlist Support Test")
    print("=" * 70)

    await test_playlist_detection()
    await test_playlist_id_extraction()
    await test_fetch_playlist()

    print("\n" + "=" * 70)
    print("Tests complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
