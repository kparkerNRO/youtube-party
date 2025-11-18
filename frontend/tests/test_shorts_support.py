#!/usr/bin/env python3
"""
Test script to verify YouTube Shorts URL parsing support
"""

import sys
from pathlib import Path

# Add backend to path (two levels up from frontend/tests/)
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from youtube_api import extract_video_id

# Test cases for various YouTube URL formats
test_cases = [
    # Standard YouTube URLs
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Standard watch URL"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Short youtu.be URL"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Embed URL"),
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Mobile watch URL"),

    # YouTube Shorts URLs (NEW)
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Shorts URL with www"),
    ("https://youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Shorts URL without www"),
    ("https://m.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Mobile Shorts URL"),

    # Edge cases
    ("dQw4w9WgXcQ", "dQw4w9WgXcQ", "Just the video ID"),
    ("https://example.com/watch?v=dQw4w9WgXcQ", None, "Invalid domain"),
    ("https://www.youtube.com/watch", None, "Missing video ID"),
]

print("Testing YouTube Shorts URL Support")
print("=" * 60)

passed = 0
failed = 0

for url, expected_id, description in test_cases:
    result = extract_video_id(url)
    status = "✓ PASS" if result == expected_id else "✗ FAIL"

    if result == expected_id:
        passed += 1
    else:
        failed += 1

    print(f"{status} | {description}")
    print(f"      URL: {url}")
    print(f"      Expected: {expected_id}, Got: {result}")
    print()

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

if failed == 0:
    print("✓ All tests passed! YouTube Shorts support is working correctly.")
    sys.exit(0)
else:
    print("✗ Some tests failed. Please review the implementation.")
    sys.exit(1)
