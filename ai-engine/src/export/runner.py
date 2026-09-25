"""Safe export execution. Never takes a raw command from the caller."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from ai_engine.core.ffmpeg import find_ffmpeg, find_ffprobe
from ai_engine.export.compiler import PlanRejected, assert_graph_matches, resolve_inside

SOFTWARE = {"h264": "libx264", "h265": "libx265"}
NVENC = {"h264": "h264_nvenc", "h265": "hevc_nvenc"}


class CapabilityError(RuntimeError):
    def __init__(self, state: str, detail: str) -> None:
        self.state = state
        super().__init__(detail)


class OverwriteRefused(RuntimeError):
    pass


class ExportCancelled(RuntimeError):
    def __init__(self, kill_s: float) -> None:
        self.kill_s = kill_s
        super().__init__(f"cancelled in {kill_s:.3f}s")


def choose_encoder(codec: str, encoders: list[str] | None) -> tuple[str, str]:
    """Return (encoder, nvenc capability). unknown and missing are not a pass."""
    if encoders is None:
        raise CapabilityError("unknown", "encoder list unknown")
    hardware = NVENC[codec]
    software = SOFTWARE[codec]
    if hardware in encoders:
        return hardware, "available"
    if software in encoders:
        return software, "missing"
    raise CapabilityError("missing", f"{software} missing")


def list_encoders(ffmpeg: str) -> list[str] | None:
    try:
        proc = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    names: list[str] = []
    for line in (proc.stdout or "").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0][:1] in {"V", "A"}:
            names.append(parts[1])
    return names


def list_filters(ffmpeg: str) -> set[str] | None:
    try:
        proc = subprocess.run([ffmpeg, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    found: set[str] = set()
    for line in (proc.stdout or "").splitlines():
        if "->" not in line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            found.add(parts[1])
    return found


def _need_filters(plan: dict) -> set[str]:
    needed = {"trim", "scale", "pad", "fps", "concat"}
    if plan.get("audio_label"):
        needed.update({"atrim", "amix", "aformat"})
    if plan["settings"].get("mix") == "bed":
        needed.update({"sidechaincompress", "loudnorm", "afade", "volume", "asplit", "aresample"})
    return needed


def _duration_seconds(value: str | None) -> float | None:
    if not value or value == "N/A":
        return None
    if ":" not in value:
        try:
            return float(value)
        except ValueError:
            return None
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def probe_output(path: Path) -> dict[str, Any]:
    """Structured ffprobe JSON first. Textual ffmpeg -i is the explicit fallback."""
    probe = find_ffprobe()
    if probe:
        proc = subprocess.run(
            [probe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if proc.returncode == 0 and (proc.stdout or "").strip():
            payload = json.loads(proc.stdout)
            result = _from_json(payload)
            if result["width"] is not None and result["duration_s"] is not None:
                return result
    return _from_text(path)


def _from_json(payload: dict) -> dict[str, Any]:
    fmt = payload.get("format") if isinstance(payload.get("format"), dict) else {}
    result: dict[str, Any] = {
        "probe": "ffprobe-json",
        "duration_s": _duration_seconds(str(fmt.get("duration"))) if fmt.get("duration") else None,
        "width": None,
        "height": None,
        "video_codec": None,
        "audio": False,
        "fps": None,
    }
    for stream in payload.get("streams") or []:
        if not isinstance(stream, dict):
            continue
        if stream.get("codec_type") == "video" and result["video_codec"] is None:
            result["video_codec"] = stream.get("codec_name")
            if isinstance(stream.get("width"), int):
                result["width"] = stream["width"]
                result["height"] = stream["height"]
            rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
            result["fps"] = _rate(rate)
        if stream.get("codec_type") == "audio":
            result["audio"] = True
    return result


def _rate(value: object) -> float | None:
    if not isinstance(value, str) or value in {"0/0", "N/A"}:
        return None
    if "/" in value:
        num, den = value.split("/", 1)
        if float(den) == 0:
            return None
        return float(num) / float(den)
    return float(value)


def _from_text(path: Path) -> dict[str, Any]:
    """Explicit fallback. A null width still fails verification."""
    ffmpeg = find_ffmpeg()
    proc = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True, timeout=20)
    text = proc.stderr or ""
    result: dict[str, Any] = {
        "probe": "ffmpeg-text",
        "duration_s": None,
        "width": None,
        "height": None,
        "video_codec": None,
        "audio": False,
        "fps": None,
    }
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Duration:"):
            result["duration_s"] = _duration_seconds(stripped.split("Duration:")[1].split(",")[0].strip())
        if "Video:" in stripped:
            result["video_codec"] = stripped.split("Video:")[1].split(",")[0].strip()
            import re

            size = re.search(r"(\d{2,5})x(\d{2,5})", stripped)
            if size:
                result["width"] = int(size.group(1))
                result["height"] = int(size.group(2))
            fps = re.search(r"(\d+(?:\.\d+)?)\s+fps", stripped)
            if fps:
                result["fps"] = float(fps.group(1))
        if "Audio:" in stripped:
            result["audio"] = True
    return result


def _integrated_lufs(ffmpeg: str, path: Path) -> float | None:
    proc = subprocess.run(
        [ffmpeg, "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    found = None
    for line in (proc.stderr or "").splitlines():
        if "I:" in line and "LUFS" in line:
            found = float(line.split("I:")[1].split("LUFS")[0].strip())
    return found


def _correct_bed_loudness(ffmpeg: str, path: Path, target: float = -14.0) -> None:
    measured = _integrated_lufs(ffmpeg, path)
    if measured is None:
        return
    gain = target - measured
    if abs(gain) <= 0.4:
        return
    corrected = path.with_name(f"{path.stem}.loud{path.suffix}")
    proc = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(path),
            "-af",
            f"volume={gain:.2f}dB",
            "-c:v",
            "copy",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            str(corrected),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not corrected.exists():
        corrected.unlink(missing_ok=True)
        return
    os.replace(corrected, path)


def _expected_duration(plan: dict) -> float:
    ends = [op["start_s"] + op["duration_s"] for op in plan["ops"] if op["op"] == "trim" and op["kind"] == "video"]
    return max(ends)


def verify_output(path: Path, plan: dict) -> dict[str, Any]:
    probed = probe_output(path)
    if probed["width"] is None or probed["height"] is None or probed["duration_s"] is None:
        raise CapabilityError("missing", "probe returned no width, height, or duration")
    settings = plan["settings"]
    if probed["width"] != settings["width"] or probed["height"] != settings["height"]:
        raise RuntimeError(f"resolution {probed['width']}x{probed['height']} != settings")
    if probed["fps"] is None or abs(float(probed["fps"]) - settings["fps"]) > 0.01:
        raise RuntimeError(f"fps {probed['fps']} != {settings['fps']}")
    frame = 1 / settings["fps"]
    if abs(float(probed["duration_s"]) - _expected_duration(plan)) > frame:
        raise RuntimeError(f"duration {probed['duration_s']} outside one frame")
    if not probed["video_codec"]:
        raise CapabilityError("missing", "video codec missing")
    return probed


def _argv(ffmpeg: str, plan: dict, encoder: str, partial: Path, workspace: Path) -> list[str]:
    argv = [ffmpeg, "-hide_banner", "-nostats", "-progress", "pipe:1"]
    pace = plan["settings"].get("pace")
    for name in plan["inputs"]:
        if pace == "realtime":
            argv.append("-re")
        argv.extend(["-i", str(resolve_inside(workspace, name))])
    argv.extend(["-filter_complex", plan["graph"], "-map", "[vout]"])
    if plan.get("audio_label"):
        argv.extend(
            [
                "-map",
                f"[{plan['audio_label']}]",
                "-c:a",
                "pcm_s16le" if plan["settings"]["audio_codec"] == "pcm" else "aac",
            ]
        )
    argv.extend(["-c:v", encoder, "-pix_fmt", "yuv420p", "-r", str(plan["settings"]["fps"]), str(partial)])
    return argv


def _progress(line: str, duration: float) -> float | None:
    if duration <= 0 or "=" not in line:
        return None
    key, raw = line.split("=", 1)
    if key == "out_time_ms":
        value = int(raw or "0")
        seconds = value / 1_000_000 if value > duration * 1000 else value / 1000
    elif key == "out_time_us":
        seconds = int(raw or "0") / 1_000_000
    elif key == "out_time":
        seconds = _duration_seconds(raw) or 0
    else:
        return None
    return max(0.0, min(0.99, seconds / duration))


def run_export(
    plan: dict,
    workspace: Path,
    *,
    cancel: threading.Event | None = None,
    on_progress: Any = None,
    encoders: list[str] | None = None,
    filters: set[str] | None = None,
) -> dict[str, Any]:
    """Execute a compiled plan inside `workspace`. Consent is required to replace."""
    assert_graph_matches(plan)
    root = workspace.resolve()
    for name in plan["inputs"]:
        path = resolve_inside(root, name)
        if not path.is_file():
            raise PlanRejected(f"input missing: {name}")
    final = resolve_inside(root, plan["output_name"])
    if final.exists() and not plan["settings"]["overwrite"]:
        raise OverwriteRefused(str(final))
    stem = Path(plan["output_name"]).stem
    suffix = Path(plan["output_name"]).suffix or ".mp4"
    partial = resolve_inside(root, f"{stem}.partial{suffix}")
    if partial.exists():
        partial.unlink()
    ffmpeg = find_ffmpeg()
    found = encoders if encoders is not None else list_encoders(ffmpeg)
    encoder, nvenc = choose_encoder(plan["settings"]["codec"], found)
    have = filters if filters is not None else list_filters(ffmpeg)
    if have is None:
        raise CapabilityError("unknown", "filter list unknown")
    missing = sorted(_need_filters(plan) - have)
    if missing:
        raise CapabilityError("missing", f"filters missing: {', '.join(missing)}")
    duration = _expected_duration(plan)
    proc = subprocess.Popen(
        _argv(ffmpeg, plan, encoder, partial, root),
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stderr: list[str] = []

    def _drain() -> None:
        if proc.stderr is not None:
            stderr.append(proc.stderr.read())

    drain = threading.Thread(target=_drain, daemon=True)
    drain.start()
    kill_s = 0.0
    cancelled = False
    if proc.stdout is None:
        raise RuntimeError("ffmpeg stdout missing")
    for line in proc.stdout:
        stripped = line.strip()
        fraction = _progress(stripped, duration)
        if fraction is not None and on_progress is not None:
            on_progress(fraction)
        if cancel is not None and cancel.is_set():
            started = time.monotonic()
            proc.kill()
            proc.wait(timeout=2)
            kill_s = time.monotonic() - started
            cancelled = True
            break
    if not cancelled:
        code = proc.wait(timeout=120)
        drain.join(timeout=2)
        if code != 0:
            partial.unlink(missing_ok=True)
            tail = "".join(stderr)[-800:]
            raise RuntimeError(f"ffmpeg failed rc={code}: {tail}")
    else:
        partial.unlink(missing_ok=True)
        raise ExportCancelled(kill_s)
    probed = verify_output(partial, plan)
    os.replace(partial, final)
    if plan["settings"].get("mix") == "bed":
        _correct_bed_loudness(ffmpeg, final)
        probed = verify_output(final, plan)
    provenance = {
        "plan_id": plan["plan_id"],
        "encoder": encoder,
        "nvenc": nvenc,
        "probe": probed["probe"],
        "output": probed,
        "overwrite": plan["settings"]["overwrite"],
        "mix": plan["settings"].get("mix"),
    }
    final.with_suffix(final.suffix + ".provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    return {"path": str(final), "provenance": provenance, "kill_s": kill_s}
