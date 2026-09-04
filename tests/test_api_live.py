"""S-006 real test: live-server API tests + artifact assertions.

Run: pytest -m real tests/test_api_live.py

Boots a real uvicorn (via the `live_api` session fixture) on a free port, uploads
real FFmpeg-generated media over HTTP, and asserts on the actual response (JSON
schema + non-empty clips) and on the enhanced download output via
`assert_playable` + mean-abs pixel diff vs the input (> 2.0).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.helpers.media import assert_playable, mean_abs_pixel_diff


def _read_first_frame(path: Path) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    ok, frame = cap.read()
    cap.release()
    assert ok and frame is not None, f"could not read a frame from {path}"
    return frame


@pytest.mark.real
def test_beat_sync_live_http(fixture, live_api):
    import requests

    clip = fixture("tone_120bpm_720p.mp4")
    with open(clip, "rb") as fh:
        r = requests.post(
            live_api["base"] + "/editor/beat-sync",
            files={"file": ("tone.mp4", fh, "video/mp4")},
            timeout=60,
        )
    assert r.status_code == 200, f"beat-sync failed: {r.status_code} {r.text[:200]}"
    body = r.json()
    # JSON schema valid
    assert set(body) == {"status", "bpm", "total_beats", "clips"}, f"unexpected schema: {body.keys()}"
    assert body["status"] == "success"
    assert abs(body["bpm"] - 120.0) <= 3.0, f"bpm {body['bpm']}"
    assert body["total_beats"] > 0
    # clips non-empty and well-formed
    assert isinstance(body["clips"], list) and len(body["clips"]) > 0
    for c in body["clips"]:
        assert {"id", "start", "end", "energyLevel", "emotionTag"} <= set(c), f"bad clip: {c}"
        assert c["end"] > c["start"]
        assert 0.0 <= c["energyLevel"] <= 1.0


@pytest.mark.real
@pytest.mark.heavy
def test_muscle_enhance_live_http(fixture, live_api):
    import requests

    clip = fixture("short_2s.mp4")
    with open(clip, "rb") as fh:
        r = requests.post(
            live_api["base"] + "/muscle/enhance",
            files={"file": ("short.mp4", fh, "video/mp4")},
            data={"intensity": "0.6", "preset": "natural_gym"},
            timeout=180,
        )
    assert r.status_code == 200, f"enhance failed: {r.status_code} {r.text[:200]}"
    out_name = r.json()["output_filename"]
    assert out_name.endswith(".mp4"), out_name

    # Download the enhanced file over HTTP.
    dl = requests.get(live_api["base"] + "/muscle/download/" + out_name, timeout=60)
    assert dl.status_code == 200, f"download: {dl.status_code}"
    out_path = Path(__file__).parent / f"_dl_{out_name}"
    # write into a temp dir, not the repo tree
    import tempfile
    out_dir = Path(tempfile.mkdtemp(prefix="ce_dl_"))
    out_path = out_dir / out_name
    out_path.write_bytes(dl.content)

    # assert_playable on the enhanced output (video-only; no audio expected).
    info = assert_playable(out_path, min_dur=1.5, has_audio=False, width=640, height=360)
    assert info["video_codec"] is not None, "no video stream"

    # Pixel-diff: enhanced output must differ from input (intensity > 0).
    in_frame = _read_first_frame(clip)
    # decode a frame from the enhanced output
    cap = cv2.VideoCapture(str(out_path))
    ok, out_frame = cap.read()
    cap.release()
    assert ok and out_frame is not None, "could not decode enhanced frame"
    # the preserve-face path may keep some pixels, but overall must differ.
    diff = mean_abs_pixel_diff(in_frame, out_frame)
    assert diff > 2.0, f"mean abs pixel diff {diff} <= 2.0 (enhance not effective)"


@pytest.mark.real
def test_assert_playable_helper(fixture):
    # Positive: the 120 BPM fixture is playable with audio.
    info = assert_playable(fixture("tone_120bpm_720p.mp4"), min_dur=9.0, has_audio=True, width=1280, height=720)
    assert info["duration"] is not None
    # Negative: a 0-byte file must raise.
    with pytest.raises(AssertionError):
        assert_playable(fixture("empty_0byte.mp4"))


# pytest is the canonical runner for S-006 (these tests are fixture-driven and
# require a live uvicorn server via the `live_api` session fixture).
