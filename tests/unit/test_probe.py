"""S-006 reopen: expected size must fail when the probe omits it.

ffprobe JSON is the primary path. The textual ffmpeg -i parser is fallback only.
"""

from __future__ import annotations

import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "ai-engine" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

pytestmark = pytest.mark.unit


def test_expected_size_fails_when_probe_returns_none(tmp_path, monkeypatch) -> None:
    from tests.helpers.media import assert_playable

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"not-empty")
    monkeypatch.setattr(
        "tests.helpers.media.probe_duration_and_streams",
        lambda path: {
            "duration": "1.5",
            "video_codec": "h264",
            "audio": False,
            "width": None,
            "height": None,
            "probe": "ffprobe-json",
        },
    )
    with pytest.raises(AssertionError, match="width probe missing"):
        assert_playable(clip, width=640, height=360)


def test_ffprobe_json_is_primary_and_text_parser_is_not_called(tmp_path, monkeypatch) -> None:
    from ai_engine.core import ffmpeg

    script = tmp_path / "ffprobe"
    script.write_text(
        "#!/bin/sh\n"
        "cat <<'JSON'\n"
        '{"format":{"duration":"2.5"},"streams":['
        '{"codec_type":"video","codec_name":"h264","width":640,"height":360},'
        '{"codec_type":"audio","codec_name":"aac"}]}\n'
        "JSON\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("CE_FFPROBE_BIN", str(script))

    def fail_text(path: str | Path) -> dict:
        raise AssertionError(f"text parser must not run for {path}")

    monkeypatch.setattr(ffmpeg, "_probe_ffmpeg_text", fail_text)
    info = ffmpeg.probe_duration_and_streams(tmp_path / "missing.mp4")
    assert info["probe"] == "ffprobe-json"
    assert info["width"] == 640
    assert info["height"] == 360
    assert info["audio"] is True
    assert info["duration"] == "2.5"
    assert info["video_codec"] == "h264"


def test_text_parser_runs_only_when_ffprobe_is_missing(monkeypatch) -> None:
    from ai_engine.core import ffmpeg

    monkeypatch.setattr(ffmpeg, "find_ffprobe", lambda: None)
    monkeypatch.setattr(
        ffmpeg,
        "_probe_ffmpeg_text",
        lambda path: {
            "duration": "00:00:01.00",
            "video_codec": "h264",
            "audio": False,
            "width": 320,
            "height": 240,
            "probe": "ffmpeg-text",
        },
    )
    info = ffmpeg.probe_duration_and_streams("clip.mp4")
    assert info["probe"] == "ffmpeg-text"
    assert info["width"] == 320
