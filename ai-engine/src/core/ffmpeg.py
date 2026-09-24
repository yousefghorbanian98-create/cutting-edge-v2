"""FFmpeg discover + audio extraction (S-004: FFmpeg-first, MoviePy fallback).

BUG 4: `from moviepy.editor import VideoFileClip` was removed in MoviePy 2.0 and
the `verbose=False` kwarg no longer exists, so audio extraction always fell into
`except` and returned "". The reliable path is an FFmpeg subprocess with a
binary found in the standard places.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


class FFmpegNotFoundError(RuntimeError):
    """Raised when no FFmpeg binary can be located."""


def find_ffmpeg() -> str:
    """Return a usable ffmpeg executable path.

    Discovery order (card S-004):
      1. `CE_FFMPEG_BIN` env override (tests/CI),
      2. `ffmpeg` on PATH (a full distro build),
      3. the binary bundled by `imageio-ffmpeg` (wheel fallback).
    """
    override = os.getenv("CE_FFMPEG_BIN")
    if override and Path(override).is_file():
        return override

    found = shutil.which("ffmpeg")
    if found:
        return found

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001 - surface a clear message
        raise FFmpegNotFoundError(
            "FFmpeg binary not found. Install ffmpeg or `imageio-ffmpeg`, or set CE_FFMPEG_BIN."
        ) from exc


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    """Run ffmpeg with `args` (after `-y`) and raise on non-zero exit."""
    ff = find_ffmpeg()
    cmd = [ff, "-y", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip()[-800:]
        raise RuntimeError(f"ffmpeg failed (rc={proc.returncode}): {tail}")
    return proc


def extract_audio(
    video_path: str | Path,
    out_path: str | Path | None = None,
    sample_rate: int = 22050,
    mono: bool = True,
) -> str:
    """Extract audio from `video_path` to a WAV via FFmpeg; returns out path.

    `out_path` defaults to `<video_stem>_audio.wav` next to the video. Falls
    back to MoviePy (v2 import) if FFmpeg fails or no binary is found.
    """
    video_path = str(video_path)
    if out_path is None:
        out_path = str(Path(video_path).with_name(Path(video_path).stem + "_audio.wav"))

    try:
        args = ["-i", video_path, "-vn"]
        if mono:
            args += ["-ac", "1"]
        args += ["-ar", str(sample_rate), str(out_path)]
        run_ffmpeg(args)
        return str(out_path)
    except (FFmpegNotFoundError, RuntimeError, subprocess.SubprocessError):
        return _extract_audio_moviepy(video_path, str(out_path), sample_rate, mono)


def _extract_audio_moviepy(video_path: str, out_path: str, sample_rate: int, mono: bool) -> str:
    """MoviePy 2.0 fallback (correct import; no `verbose=` kwarg)."""
    try:
        from moviepy import VideoFileClip  # MoviePy 2.x location
    except Exception:  # noqa: BLE001 - try the legacy import, then give up
        from moviepy.editor import VideoFileClip  # type: ignore[no-redef]

    try:
        clip = VideoFileClip(video_path)
        try:
            if clip.audio is None:
                return ""
            clip.audio.write_audiofile(out_path, fps=sample_rate, nbytes=2, logger=None)
            return out_path
        finally:
            clip.close()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"MoviePy audio extraction failed: {exc}") from exc


def find_ffprobe() -> str | None:
    """Return an ffprobe binary, or None when capability is missing.

    Discovery order: `CE_FFPROBE_BIN`, PATH, then a sibling of the ffmpeg binary.
    A missing binary is not a pass. Callers fall back only after this returns None.
    """
    override = os.getenv("CE_FFPROBE_BIN")
    if override:
        path = Path(override)
        return str(path) if path.is_file() else None
    found = shutil.which("ffprobe")
    if found:
        return found
    try:
        ffmpeg = find_ffmpeg()
    except FFmpegNotFoundError:
        return None
    for name in ("ffprobe", "ffprobe.exe"):
        sibling = Path(ffmpeg).with_name(name)
        if sibling.is_file():
            return str(sibling)
    return None


def probe_duration_and_streams(video_path: str | Path) -> dict:
    """Return duration, codecs, and resolution.

    Structured `ffprobe -print_format json` is the primary path. The textual
    `ffmpeg -i` parser is only the fallback when ffprobe is missing or cannot
    return JSON. A JSON result with null width/height is returned as-is.
    """
    probe = find_ffprobe()
    if probe:
        parsed = _probe_ffprobe_json(probe, video_path)
        if parsed is not None:
            return parsed
    return _probe_ffmpeg_text(video_path)


def _probe_ffprobe_json(probe: str, video_path: str | Path) -> dict | None:
    proc = subprocess.run(
        [probe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    result: dict = {
        "duration": None,
        "video_codec": None,
        "audio": False,
        "width": None,
        "height": None,
        "probe": "ffprobe-json",
    }
    fmt = payload.get("format") if isinstance(payload.get("format"), dict) else {}
    duration = fmt.get("duration")
    if duration not in (None, "", "N/A"):
        result["duration"] = str(duration)
    for stream in payload.get("streams") or []:
        if not isinstance(stream, dict):
            continue
        if stream.get("codec_type") == "video" and result["video_codec"] is None:
            result["video_codec"] = stream.get("codec_name")
            width, height = stream.get("width"), stream.get("height")
            if isinstance(width, int) and isinstance(height, int):
                result["width"], result["height"] = width, height
        if stream.get("codec_type") == "audio":
            result["audio"] = True
    return result


def _probe_ffmpeg_text(video_path: str | Path) -> dict:
    """Fallback parser for `ffmpeg -i` stderr. Not the primary probe path."""
    ff = find_ffmpeg()
    proc = subprocess.run([ff, "-i", str(video_path)], capture_output=True, text=True)
    info = proc.stderr or ""
    result: dict = {
        "duration": None,
        "video_codec": None,
        "audio": False,
        "width": None,
        "height": None,
        "probe": "ffmpeg-text",
    }
    for line in info.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            duration = line.split("Duration:")[1].split(",")[0].strip()
            result["duration"] = duration
        if "Video:" in line:
            codec = line.split("Video:")[1].strip().split(",")[0].strip()
            result["video_codec"] = codec
            res = _find_resolution(line)
            if res:
                result["width"], result["height"] = res
        if "Audio:" in line:
            result["audio"] = True
    return result


def _find_resolution(line: str) -> tuple[int, int] | None:
    import re

    m = re.search(r"(?P<w>\d{2,5})x(?P<h>\d{2,5})", line)
    if m:
        return int(m.group("w")), int(m.group("h"))
    return None
