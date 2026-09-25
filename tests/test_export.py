"""S-028 real export. Missing ffmpeg is a failure, not a skip."""

from __future__ import annotations

import sys
import threading
import time
import wave
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai-engine"))

from ai_engine.core.ffmpeg import find_ffmpeg  # noqa: E402
from ai_engine.export.compiler import PlanRejected, compile_plan  # noqa: E402
from ai_engine.export.runner import CapabilityError, ExportCancelled, OverwriteRefused, run_export  # noqa: E402

pytestmark = pytest.mark.real


def _ffmpeg(*args: str) -> None:
    import subprocess

    proc = subprocess.run([find_ffmpeg(), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-400:])


def _video(path: Path, seconds: float, color: str) -> None:
    _ffmpeg(
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=320x180:r=30:d={seconds}",
        "-pix_fmt",
        "yuv420p",
        str(path),
    )


def _click(path: Path) -> None:
    rate = 22050
    frames = rate * 3
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        click_at = int(2.0 * rate)
        samples = bytearray(frames * 2)
        for offset in range(int(0.02 * rate)):
            value = 32000 if offset % 2 == 0 else -32000
            index = (click_at + offset) * 2
            samples[index : index + 2] = int(value).to_bytes(2, "little", signed=True)
        handle.writeframes(samples)


def test_three_clips_match_duration_and_click_lands_at_two_seconds(tmp_path: Path) -> None:
    import librosa

    for name, color in (("a.mp4", "red"), ("b.mp4", "green"), ("c.mp4", "blue")):
        _video(tmp_path / name, 1, color)
    _click(tmp_path / "click.wav")
    plan = compile_plan(
        {
            "clips": [
                {"id": "a", "name": "a.mp4", "kind": "video", "start_ms": 0, "duration_ms": 1000, "in_ms": 0},
                {"id": "b", "name": "b.mp4", "kind": "video", "start_ms": 1000, "duration_ms": 1000, "in_ms": 0},
                {"id": "c", "name": "c.mp4", "kind": "video", "start_ms": 2000, "duration_ms": 1000, "in_ms": 0},
                {"id": "click", "name": "click.wav", "kind": "audio", "start_ms": 0, "duration_ms": 3000, "in_ms": 0},
            ],
            "settings": {
                "width": 320,
                "height": 180,
                "fps": 30,
                "codec": "h264",
                "audio_codec": "pcm",
                "output_name": "out.mov",
                "overwrite": False,
            },
        },
        tmp_path,
    )
    result = run_export(plan, tmp_path)
    assert result["provenance"]["nvenc"] in {"available", "missing"}
    assert result["provenance"]["nvenc"] != "pass"
    wav = tmp_path / "out.wav"
    _ffmpeg("-i", str(tmp_path / "out.mov"), str(wav))
    audio, rate = librosa.load(wav, sr=22050)
    onsets = librosa.onset.onset_detect(y=audio, sr=rate, units="time", backtrack=True)
    assert len(onsets) > 0
    assert min(abs(item - 2.0) for item in onsets) <= 0.02


def test_duration_resolution_fps_and_provenance(tmp_path: Path) -> None:
    for name, color in (("a.mp4", "red"), ("b.mp4", "green"), ("c.mp4", "blue")):
        _video(tmp_path / name, 1, color)
    plan = compile_plan(
        {
            "clips": [
                {"id": "a", "name": "a.mp4", "kind": "video", "start_ms": 0, "duration_ms": 1000, "in_ms": 0},
                {"id": "b", "name": "b.mp4", "kind": "video", "start_ms": 1000, "duration_ms": 1000, "in_ms": 0},
                {"id": "c", "name": "c.mp4", "kind": "video", "start_ms": 2000, "duration_ms": 1000, "in_ms": 0},
            ],
            "settings": {
                "width": 320,
                "height": 180,
                "fps": 30,
                "codec": "h264",
                "output_name": "sum.mp4",
                "overwrite": False,
            },
        },
        tmp_path,
    )
    result = run_export(plan, tmp_path)
    output = result["provenance"]["output"]
    assert abs(output["duration_s"] - 3.0) <= 1 / 30
    assert output["width"] == 320
    assert output["height"] == 180
    assert abs(output["fps"] - 30) <= 0.01
    assert (tmp_path / "sum.mp4.provenance.json").is_file()


def test_overwrite_and_missing_capability_fail(tmp_path: Path) -> None:
    _video(tmp_path / "a.mp4", 1, "red")
    (tmp_path / "blocked.mp4").write_bytes(b"keep")
    plan = compile_plan(
        {
            "clips": [{"id": "a", "name": "a.mp4", "kind": "video", "start_ms": 0, "duration_ms": 1000, "in_ms": 0}],
            "settings": {
                "width": 320,
                "height": 180,
                "fps": 30,
                "codec": "h264",
                "output_name": "blocked.mp4",
                "overwrite": False,
            },
        },
        tmp_path,
    )
    with pytest.raises(OverwriteRefused):
        run_export(plan, tmp_path)
    assert (tmp_path / "blocked.mp4").read_bytes() == b"keep"
    with pytest.raises(PlanRejected):
        compile_plan(
            {
                "clips": [
                    {"id": "a", "name": "a.mp4", "kind": "video", "start_ms": 0, "duration_ms": 1000, "in_ms": 0}
                ],
                "settings": {"width": 320, "height": 180, "fps": 30, "codec": "hevc", "output_name": "x.mp4"},
            },
            tmp_path,
        )
    missing = compile_plan(
        {
            "clips": [{"id": "a", "name": "a.mp4", "kind": "video", "start_ms": 0, "duration_ms": 1000, "in_ms": 0}],
            "settings": {
                "width": 320,
                "height": 180,
                "fps": 30,
                "codec": "h264",
                "output_name": "missing.mp4",
                "overwrite": False,
            },
        },
        tmp_path,
    )
    with pytest.raises(CapabilityError):
        run_export(missing, tmp_path, encoders=[])
    with pytest.raises(CapabilityError):
        run_export(missing, tmp_path, filters=set())


def test_cancel_at_40_percent_kills_within_one_second(tmp_path: Path) -> None:
    _video(tmp_path / "long.mp4", 8, "gray")
    plan = compile_plan(
        {
            "clips": [
                {"id": "long", "name": "long.mp4", "kind": "video", "start_ms": 0, "duration_ms": 8000, "in_ms": 0}
            ],
            "settings": {
                "width": 320,
                "height": 180,
                "fps": 30,
                "codec": "h264",
                "output_name": "cancelled.mp4",
                "pace": "realtime",
                "overwrite": False,
            },
        },
        tmp_path,
    )
    cancel = threading.Event()

    def watch(fraction: float) -> None:
        if fraction >= 0.4:
            cancel.set()

    started = time.monotonic()
    with pytest.raises(ExportCancelled) as caught:
        run_export(plan, tmp_path, cancel=cancel, on_progress=watch)
    assert time.monotonic() - started < 20
    assert caught.value.kill_s < 1
    assert not (tmp_path / "cancelled.mp4").exists()
