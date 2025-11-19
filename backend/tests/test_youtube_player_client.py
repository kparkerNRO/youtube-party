import pytest

from backend.youtube_player import CLIENT_ATTEMPTS, _build_headers, _build_payload


@pytest.mark.parametrize("idx", range(2))
def test_payload_includes_expected_context(idx):
    profile = CLIENT_ATTEMPTS[idx]
    payload = _build_payload("dQw4w9WgXcQ", profile)

    assert payload["videoId"] == "dQw4w9WgXcQ"
    assert payload["contentCheckOk"] is True
    assert payload["context"]["client"]["clientName"] == profile["client_name"]
    assert payload["thirdParty"]["embedUrl"] == "https://google.com"


def test_headers_drop_authorization_when_not_requested():
    profile = {
        **CLIENT_ATTEMPTS[0],
        "use_auth": False,
    }

    headers = _build_headers(profile, "Bearer abc123")

    assert "Authorization" not in headers
    assert headers["User-Agent"].startswith("com.google.android.youtube/")


@pytest.mark.parametrize("use_auth", [True, False])
def test_headers_honor_authorization_flag(use_auth):
    profile = {**CLIENT_ATTEMPTS[0], "use_auth": use_auth}
    token = "Bearer token"
    headers = _build_headers(profile, token)

    if use_auth:
        assert headers["Authorization"] == token
    else:
        assert "Authorization" not in headers
