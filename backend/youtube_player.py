"""Utilities for retrieving playable YouTube streams using the internal youtubei API."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import httpx

YOUTUBEI_PLAYER_URL = "https://www.youtube.com/youtubei/v1/player"

# These API keys are public constants used by the official YouTube clients.
# They were pulled from the Android, Android embedded player, iOS, and web
# bundles in the same way the Kodi plugin does (see the research notes linked
# in docs/research_investigation.md).
INNERTUBE_API_KEYS: Dict[str, str] = {
    "android": "AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w",
    "android_embedded": "AIzaSyCjc_pVEDi4qsv5MtC2dMXzpIaDoRFLsxw",
    "ios": "AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc",
    "web": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
}

ANDROID_CLIENT_VERSION = os.getenv("YOUTUBE_ANDROID_CLIENT_VERSION", "19.08.35")
ANDROID_EMBEDDED_VERSION = os.getenv("YOUTUBE_ANDROID_EMBEDDED_VERSION", "19.08.35")

RETRYABLE_STATUSES = {"UNPLAYABLE", "AGE_CHECK_REQUIRED", "CONTENT_CHECK_REQUIRED"}

DEFAULT_EMBED_URL = "https://google.com"
DEFAULT_LANGUAGE = os.getenv("YOUTUBE_CLIENT_LANG", "en")
DEFAULT_REGION = os.getenv("YOUTUBE_CLIENT_REGION", "US")


def _android_user_agent(version: str) -> str:
    return f"com.google.android.youtube/{version} (Linux; U; Android 12) gzip"


CLIENT_ATTEMPTS = (
    {
        "client_name": "ANDROID",
        "client_version": ANDROID_CLIENT_VERSION,
        "api_key": INNERTUBE_API_KEYS["android"],
        "user_agent": _android_user_agent(ANDROID_CLIENT_VERSION),
        "use_auth": True,
    },
    {
        "client_name": "ANDROID_EMBEDDED_PLAYER",
        "client_version": ANDROID_EMBEDDED_VERSION,
        "api_key": INNERTUBE_API_KEYS["android_embedded"],
        "user_agent": _android_user_agent(ANDROID_EMBEDDED_VERSION),
        "use_auth": True,
    },
    {
        "client_name": "ANDROID",
        "client_version": ANDROID_CLIENT_VERSION,
        "api_key": INNERTUBE_API_KEYS["android"],
        "user_agent": _android_user_agent(ANDROID_CLIENT_VERSION),
        "use_auth": False,
    },
    {
        "client_name": "ANDROID_EMBEDDED_PLAYER",
        "client_version": ANDROID_EMBEDDED_VERSION,
        "api_key": INNERTUBE_API_KEYS["android_embedded"],
        "user_agent": _android_user_agent(ANDROID_EMBEDDED_VERSION),
        "use_auth": False,
    },
)

AUTH_TOKEN = os.getenv("YOUTUBEI_AUTHORIZATION")


class YouTubePlayabilityError(Exception):
    """Raised when YouTube reports that a video cannot be played."""

    def __init__(self, reason: str, status: Optional[str] = None):
        super().__init__(reason)
        self.status = status or "UNKNOWN"


def _build_payload(video_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    client_name = profile["client_name"]
    payload = {
        "videoId": video_id,
        "contentCheckOk": True,
        "racyCheckOk": True,
        "context": {
            "client": {
                "hl": DEFAULT_LANGUAGE,
                "gl": DEFAULT_REGION,
                "clientName": client_name,
                "clientVersion": profile["client_version"],
                "androidSdkVersion": 31,
                "osName": "Android",
                "osVersion": "12",
                "deviceMake": "Google",
                "deviceModel": "Pixel 5",
                "platform": "MOBILE",
                "userAgent": profile["user_agent"],
                "timeZone": "UTC",
                "clientFormFactor": "SMALL_FORM_FACTOR",
                "clientScreen": "EMBED" if client_name == "ANDROID_EMBEDDED_PLAYER" else "WATCH",
            },
        },
        "thirdParty": {"embedUrl": DEFAULT_EMBED_URL},
        "user": {"lockedSafetyMode": False},
        "playbackContext": {
            "contentPlaybackContext": {
                "html5Preference": "HTML5_PREF_WANTS",
                "autonavState": "STATE_NONE",
            }
        },
    }
    return payload


def _build_headers(profile: Dict[str, Any], auth_token: Optional[str]) -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": profile["user_agent"],
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if profile.get("use_auth") and auth_token:
        headers["Authorization"] = auth_token
    return headers


def _extract_stream(streaming_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    if not streaming_data:
        return None, None

    if streaming_data.get("hlsManifestUrl"):
        return streaming_data["hlsManifestUrl"], "hls"
    if streaming_data.get("dashManifestUrl"):
        return streaming_data["dashManifestUrl"], "dash"

    for entry in streaming_data.get("formats", []):
        url = entry.get("url")
        if url:
            return url, "progressive"
    for entry in streaming_data.get("adaptiveFormats", []):
        url = entry.get("url")
        if url:
            return url, "adaptive"
    return None, None


async def fetch_playable_stream(video_id: str) -> Dict[str, Any]:
    """Fetch a playable stream URL by emulating multiple Android client profiles."""

    last_reason: Optional[str] = None

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as session:
        for attempt_index, profile in enumerate(CLIENT_ATTEMPTS, start=1):
            payload = _build_payload(video_id, profile)
            headers = _build_headers(profile, AUTH_TOKEN)
            params = {"key": profile["api_key"]}

            try:
                response = await session.post(
                    YOUTUBEI_PLAYER_URL,
                    params=params,
                    json=payload,
                    headers=headers,
                )
            except httpx.HTTPError as exc:
                last_reason = f"Network error: {exc}"  # noqa: TRY401
                continue

            if response.status_code != 200:
                last_reason = f"HTTP {response.status_code}"
                continue

            data: Dict[str, Any] = response.json()
            status = (data.get("playabilityStatus") or {}).get("status", "ERROR")
            reason = (data.get("playabilityStatus") or {}).get("reason")

            if status == "OK":
                streaming_data = data.get("streamingData") or {}
                stream_url, stream_type = _extract_stream(streaming_data)
                if not stream_url:
                    last_reason = "No streaming data returned"
                    continue

                expires_raw = streaming_data.get("expiresInSeconds")
                expires_in = int(expires_raw) if expires_raw and str(expires_raw).isdigit() else None

                return {
                    "video_id": video_id,
                    "status": status,
                    "stream_url": stream_url,
                    "stream_type": stream_type,
                    "client_name": profile["client_name"],
                    "client_version": profile["client_version"],
                    "attempts": attempt_index,
                    "expires_in": expires_in,
                    "playability_reason": reason,
                }

            if status not in RETRYABLE_STATUSES:
                raise YouTubePlayabilityError(reason or "Video is not playable", status)

            last_reason = reason or status

    raise YouTubePlayabilityError(last_reason or "Unable to create a playable stream", "FAILED")


__all__ = [
    "YouTubePlayabilityError",
    "fetch_playable_stream",
    "CLIENT_ATTEMPTS",
    "_build_headers",
    "_build_payload",
]
