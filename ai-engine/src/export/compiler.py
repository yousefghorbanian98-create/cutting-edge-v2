"""Compile a timeline request into allow-listed operations.

The assistant may not supply a raw command or a filter graph. The graph is
rebuilt from the operations and rejected if it does not match.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ai_engine.export.audio import audio_filter

ALLOWED_OPS = frozenset(
    {
        "trim",
        "setpts",
        "concat",
        "scale",
        "pad",
        "fps",
        "amix",
        "afade",
        "volume",
        "sidechaincompress",
        "loudnorm",
        "encode",
    }
)
CODECS = {"h264", "h265"}
RATES = {24, 30, 60}


class PlanRejected(ValueError):
    """The request is not a typed, in-bounds export."""


def resolve_inside(workspace: Path, name: str) -> Path:
    """Reject separators, NUL, and any path that leaves the workspace."""
    if not name or name in {".", ".."} or "\x00" in name or "/" in name or "\\" in name:
        raise PlanRejected(f"path rejected: {name!r}")
    root = workspace.resolve()
    try:
        candidate = (root / name).resolve()
        candidate.relative_to(root)
    except (OSError, ValueError) as exc:
        raise PlanRejected(f"path rejected: {name!r}") from exc
    return candidate


def _clip(raw: dict, workspace: Path) -> dict:
    if not isinstance(raw, dict):
        raise PlanRejected("clip must be an object")
    for banned in ("raw_command", "filter_graph", "filter_complex"):
        if banned in raw:
            raise PlanRejected(f"{banned} rejected")
    name = str(raw.get("name") or "")
    path = resolve_inside(workspace, name)
    kind = raw.get("kind")
    if kind not in {"video", "audio"}:
        raise PlanRejected(f"kind rejected: {kind}")
    start = int(raw["start_ms"])
    duration = int(raw["duration_ms"])
    if start < 0 or duration <= 0:
        raise PlanRejected("clip timing rejected")
    return {
        "id": str(raw.get("id") or name),
        "name": name,
        "path": path,
        "kind": kind,
        "start_ms": start,
        "duration_ms": duration,
        "in_ms": int(raw.get("in_ms") or 0),
        "gain_db": float(raw.get("gain_db") or 0),
        "fade_in_ms": int(raw.get("fade_in_ms") or 0),
        "fade_out_ms": int(raw.get("fade_out_ms") or 0),
        "duck": bool(raw.get("duck") or False),
    }


def graph_from_ops(ops: list[dict], settings: dict) -> tuple[str, str | None]:
    """Build the only filter graph the runner is allowed to execute."""
    videos = [op for op in ops if op["op"] == "trim" and op["kind"] == "video"]
    if not videos:
        raise PlanRejected("video trim missing")
    width = int(settings["width"])
    height = int(settings["height"])
    fps = int(settings["fps"])
    parts: list[str] = []
    labels: list[str] = []
    for index, op in enumerate(videos):
        label = f"v{index}"
        start = op["in_s"]
        end = op["in_s"] + op["duration_s"]
        parts.append(
            f"[{op['input']}:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}[{label}]"
        )
        labels.append(f"[{label}]")
    parts.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0[vout]")
    try:
        audio = audio_filter(ops, settings)
    except ValueError as exc:
        raise PlanRejected(str(exc)) from exc
    if audio:
        parts.append(audio)
    return ";".join(parts), "aout" if audio else None


def compile_plan(request: dict, workspace: Path) -> dict:
    """Return a plan. Network is not used. Extra command fields are rejected."""
    if not isinstance(request, dict):
        raise PlanRejected("request must be an object")
    for banned in ("raw_command", "filter_graph", "filter_complex", "argv"):
        if banned in request:
            raise PlanRejected(f"{banned} rejected")
    settings = request.get("settings")
    if not isinstance(settings, dict):
        raise PlanRejected("settings missing")
    for banned in ("raw_command", "filter_graph"):
        if banned in settings:
            raise PlanRejected(f"{banned} rejected")
    codec = settings.get("codec")
    fps = settings.get("fps")
    width = int(settings.get("width") or 0)
    height = int(settings.get("height") or 0)
    if codec not in CODECS or fps not in RATES:
        raise PlanRejected("codec or fps rejected")
    if not (16 <= width <= 3840 and 16 <= height <= 2160):
        raise PlanRejected("frame size rejected")
    clips = [_clip(item, workspace) for item in request.get("clips") or []]
    if not any(item["kind"] == "video" for item in clips):
        raise PlanRejected("video clip missing")
    output_name = str(settings.get("output_name") or "")
    resolve_inside(workspace, output_name)
    ops: list[dict] = []
    inputs: list[str] = []
    for clip in clips:
        if clip["name"] not in inputs:
            inputs.append(clip["name"])
        index = inputs.index(clip["name"])
        ops.append(
            {
                "op": "trim",
                "kind": clip["kind"],
                "input": index,
                "in_s": clip["in_ms"] / 1000,
                "duration_s": clip["duration_ms"] / 1000,
                "start_s": clip["start_ms"] / 1000,
                "gain_db": clip["gain_db"],
                "fade_in_ms": clip["fade_in_ms"],
                "fade_out_ms": clip["fade_out_ms"],
                "duck": clip["duck"],
                "id": clip["id"],
            }
        )
    ops.append({"op": "scale", "width": width, "height": height})
    ops.append({"op": "pad", "width": width, "height": height})
    ops.append({"op": "fps", "fps": fps})
    ops.append({"op": "concat", "n": sum(1 for item in clips if item["kind"] == "video")})
    if settings.get("mix") == "bed":
        ops.append({"op": "sidechaincompress"})
        ops.append({"op": "loudnorm", "i": -14})
    ops.append({"op": "encode", "codec": codec})
    unknown = {op["op"] for op in ops} - ALLOWED_OPS
    if unknown:
        raise PlanRejected(f"op rejected: {sorted(unknown)}")
    graph, audio_label = graph_from_ops(ops, settings)
    digest = hashlib.sha256(json.dumps(ops, sort_keys=True).encode()).hexdigest()
    return {
        "ops": ops,
        "inputs": inputs,
        "graph": graph,
        "audio_label": audio_label,
        "output_name": output_name,
        "settings": {
            "width": width,
            "height": height,
            "fps": int(fps),
            "codec": codec,
            "audio_codec": settings.get("audio_codec") or "aac",
            "overwrite": bool(settings.get("overwrite") or False),
            "pace": settings.get("pace") or "fast",
            "mix": settings.get("mix") or "copy",
            "crf": int(settings.get("crf") or 23),
        },
        "plan_id": digest,
    }


def assert_graph_matches(plan: dict) -> None:
    graph, _audio = graph_from_ops(plan["ops"], plan["settings"])
    if graph != plan["graph"]:
        raise PlanRejected("filter graph does not match typed operations")
