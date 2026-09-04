"""S-004 real test: FFmpeg-first audio extraction + BPM detection (BUG 4).

Run: pytest -m real tests/test_beat_sync.py   (or python tests/test_beat_sync.py)

Fixtures are generated on the fly with real FFmpeg (discovered via
ai_engine.core.ffmpeg, which falls back to the imageio-ffmpeg bundled binary).
This exercises the exact code path used by the app, not mocked arrays.
"""
from __future__ import annotations

import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
import pytest

from ai_engine.core.ffmpeg import extract_audio, find_ffmpeg  # noqa: E402
from ai_engine.editor_ai.beat_sync import BeatSyncEngine  # noqa: E402


def _make_click_wav(path: Path, bpm: float = 120.0, dur: float = 10.0, sr: int = 48000) -> None:
    n = int(sr * dur)
    y = np.zeros(n, dtype=np.float32)
    click_len = int(0.05 * sr)
    step = int(sr * 60.0 / bpm)
    t0 = np.arange(click_len) / sr
    env = np.exp(-t0 * 40)
    click = (np.sin(2 * np.pi * 1000 * t0) * env).astype(np.float32)
    click += (0.5 * np.sin(2 * np.pi * 2000 * t0) * env).astype(np.float32)
    i = 0
    while i < n:
        j = min(i + click_len, n)
        y[i:j] += click[: j - i]
        i += step
    y = y / (np.max(np.abs(y)) + 1e-9)
    pcm = (y * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def _make_mp4(out: Path, audio_wav: Path, dur: float, audio_sr: int) -> None:
    ff = find_ffmpeg()
    cmd = [
        ff, "-y",
        "-f", "lavfi", "-i", f"color=c=black:s=320x240:d={dur}",
        "-i", str(audio_wav),
        "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", str(audio_sr), "-b:a", "128k",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"fixture generation failed: {proc.stderr[-400:]}"


def _make_silent_mp4(out: Path, dur: float = 5.0) -> None:
    ff = find_ffmpeg()
    cmd = [
        ff, "-y",
        "-f", "lavfi", "-i", f"color=c=black:s=320x240:d={dur}",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
        "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-b:a", "64k",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"silent fixture failed: {proc.stderr[-400:]}"


@pytest.mark.real
def test_click_track_bpm_within_3():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        click_wav = td / "click.wav"
        _make_click_wav(click_wav, bpm=120.0, dur=10.0, sr=48000)
        mp4 = td / "click.mp4"
        _make_mp4(mp4, click_wav, dur=10.0, audio_sr=48000)

        engine = BeatSyncEngine()
        beats = engine.analyze_audio(str(mp4))
        assert beats, "expected non-empty beats on a click track"
        bpm = engine.tempo_bpm
        assert abs(bpm - 120.0) <= 3.0, f"BPM {bpm} not within ±3 of 120"


@pytest.mark.real
def test_silent_mp4_returns_empty_without_exception():
    with tempfile.TemporaryDirectory() as td:
        mp4 = Path(td) / "silent.mp4"
        _make_silent_mp4(mp4, dur=5.0)

        engine = BeatSyncEngine()
        beats = engine.analyze_audio(str(mp4))  # must NOT raise
        assert beats == [], f"expected [] on silence, got {len(beats)} beats"
        assert engine.tempo_bpm == 0.0 or engine.tempo_bpm is None


@pytest.mark.real
def test_ffmpeg_extract_aac():
    """BUG-4: MP4 with AAC 48k audio → WAV 22050 mono via FFmpeg."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        click_wav = td / "src.wav"
        _make_click_wav(click_wav, bpm=120.0, dur=6.0, sr=48000)
        mp4 = td / "aac.mp4"
        _make_mp4(mp4, click_wav, dur=6.0, audio_sr=48000)

        out_wav = td / "out.wav"
        path = extract_audio(str(mp4), str(out_wav), sample_rate=22050, mono=True)
        assert path == str(out_wav) and out_wav.exists()

        with wave.open(str(out_wav), "rb") as w:
            assert w.getframerate() == 22050, f"expected 22050, got {w.getframerate()}"
            assert w.getnchannels() == 1, f"expected mono, got {w.getnchannels()}"


def _run_all() -> int:
    results = []

    def check(name, fn):
        try:
            fn()
            print(f"PASS {name}")
            results.append(True)
        except (AssertionError, Exception) as e:  # noqa: BLE001
            print(f"FAIL {name}: {e}")
            results.append(False)

    check("test_click_track_bpm_within_3", test_click_track_bpm_within_3)
    check("test_silent_mp4_returns_empty_without_exception", test_silent_mp4_returns_empty_without_exception)
    check("test_ffmpeg_extract_aac", test_ffmpeg_extract_aac)
    ok = all(results)
    print(f"\n{('OK' if ok else 'FAILED')} — {sum(results)}/{len(results)} S-004 beat-sync checks green")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
