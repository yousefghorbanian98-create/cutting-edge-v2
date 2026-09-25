"""S-032 loudness and ducking. Missing filters fail; they are not skipped."""

from __future__ import annotations

import math
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai-engine"))

from ai_engine.core.ffmpeg import find_ffmpeg  # noqa: E402
from ai_engine.export.compiler import compile_plan  # noqa: E402
from ai_engine.export.runner import run_export  # noqa: E402

pytestmark = pytest.mark.real


def _tone(path: Path, seconds: float, freq: float, gain: float, start: float, end: float) -> None:
    rate = 22050
    frames = int(seconds * rate)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        data = bytearray(frames * 2)
        for i in range(frames):
            t = i / rate
            sample = 0.0
            if start <= t < end:
                sample = gain * math.sin(2 * math.pi * freq * t)
            value = max(-32767, min(32767, int(sample * 32767)))
            data[i * 2 : i * 2 + 2] = value.to_bytes(2, "little", signed=True)
        handle.writeframes(data)


def _video(path: Path) -> None:
    import subprocess

    proc = subprocess.run(
        [find_ffmpeg(), "-f", "lavfi", "-i", "color=c=black:s=320x180:r=30:d=4", "-pix_fmt", "yuv420p", str(path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-400:])


def _band_rms(samples: np.ndarray, rate: int, freq: float) -> float:
    spec = np.fft.rfft(samples)
    bins = np.fft.rfftfreq(len(samples), 1 / rate)
    band = (bins > freq - 30) & (bins < freq + 30)
    if not np.any(band):
        return 0.0
    return float(np.sqrt(np.mean(np.abs(spec[band]) ** 2)))


def test_music_bed_hits_loudness_and_ducks_under_voice(tmp_path: Path) -> None:
    _video(tmp_path / "v.mp4")
    _tone(tmp_path / "voice.wav", 4, 200, 0.8, 1.0, 2.0)
    _tone(tmp_path / "music.wav", 4, 440, 10 ** (-12 / 20), 0.0, 4.0)
    plan = compile_plan(
        {
            "clips": [
                {"id": "v", "name": "v.mp4", "kind": "video", "start_ms": 0, "duration_ms": 4000, "in_ms": 0},
                {
                    "id": "voice",
                    "name": "voice.wav",
                    "kind": "audio",
                    "start_ms": 0,
                    "duration_ms": 4000,
                    "in_ms": 0,
                    "gain_db": 0,
                },
                {
                    "id": "music",
                    "name": "music.wav",
                    "kind": "audio",
                    "start_ms": 0,
                    "duration_ms": 4000,
                    "in_ms": 0,
                    "gain_db": -12,
                    "fade_in_ms": 20,
                    "fade_out_ms": 20,
                    "duck": True,
                },
            ],
            "settings": {
                "width": 320,
                "height": 180,
                "fps": 30,
                "codec": "h264",
                "audio_codec": "pcm",
                "output_name": "mix.mov",
                "mix": "bed",
                "overwrite": False,
            },
        },
        tmp_path,
    )
    run_export(plan, tmp_path)
    import subprocess

    measured = subprocess.run(
        [find_ffmpeg(), "-i", str(tmp_path / "mix.mov"), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    loudness = None
    for line in (measured.stderr or "").splitlines():
        if "I:" in line and "LUFS" in line:
            loudness = float(line.split("I:")[1].split("LUFS")[0].strip())
    assert loudness is not None
    assert abs(loudness - (-14)) <= 1
    wav = tmp_path / "mix.wav"
    extracted = subprocess.run(
        [find_ffmpeg(), "-i", str(tmp_path / "mix.mov"), "-c:a", "pcm_s16le", str(wav)],
        capture_output=True,
        text=True,
    )
    if extracted.returncode != 0:
        raise RuntimeError(extracted.stderr[-400:])
    import wave

    with wave.open(str(wav)) as handle:
        rate = handle.getframerate()
        frames = np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16).astype(np.float64)
    voice = _band_rms(frames[rate : rate * 2], rate, 440)
    silence = _band_rms(frames[rate * 3 : rate * 4], rate, 440)
    assert silence > 0
    drop = 20 * math.log10(silence / max(voice, 1e-9))
    assert drop >= 6
