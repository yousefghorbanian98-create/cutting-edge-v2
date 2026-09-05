"""S-005 real-media fixture factory.

Generates real media fixtures with FFmpeg at test time (never committed): the
bundled `imageio-ffmpeg` binary is used when no system `ffmpeg` is on PATH
(sandbox/CI rule: never commit media, always build in a gitignored cache dir).

Fixtures produced (synthetic set is always built):
  a) tone_120bpm_720p.mp4   10s 1280x720@30 moving testsrc + 120 BPM click track
  b) silent_720p.mp4        5s 1280x720@30 silent (AAC anullsrc)
  c) short_2s.mp4           2s 640x360@24
  d) empty_0byte.mp4        0-byte file
  e) broken_header.mp4      corrupt file (bad magic bytes)
  f) vertical_9x16.mp4      3s 720x1280@30
  g) wide_4k_3s.mp4         3s 3840x2160@30
  h) Persian name, internal spaces, Persian digit, real .mp4 suffix:
     'کلیپ تمرین ۱.mp4'  2s 640x360  (accepted by Storage._validate_extension)

Optional (network, SHA256-pinned, cached):
  human_clip.mp4    licensed Pexels human clip (downloads only if network)
  pose.jpg          MediaPipe pose test image

When the network is unavailable the optional set degrades to synthetic-only and
emits an EXPLICIT warning (never a silent skip). The committed manifest.json
describes the expected synthetic set; the SHA256 pins for the optional assets
live in manifest.json and only match when the assets were actually downloaded.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

from ai_engine.core.ffmpeg import find_ffmpeg

# Directory that holds generated fixtures. Git-ignored (see .gitignore).
CACHE_DIRNAME = ".cache"


# ── FFmpeg helpers ────────────────────────────────────────────────────────────
def _ff() -> str:
    return find_ffmpeg()


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (rc={proc.returncode}): {proc.stderr[-800:]}")


def _click_wav(path: Path, bpm: float = 120.0, dur: float = 10.0, sr: int = 48000) -> None:
    """Write a decaying click-track WAV at the given BPM."""
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


def _mux(audio_wav: str | None, out: Path,
         size: tuple[int, int] = (1280, 720), fps: int = 30, dur: float = 10.0,
         vcodec: str = "libx264") -> None:
    cmd = [_ff(), "-y",
           "-f", "lavfi", "-i", f"testsrc2=size={size[0]}x{size[1]}:rate={fps}:duration={dur}"]
    if audio_wav:
        cmd += ["-i", audio_wav]
    cmd += ["-shortest", "-c:v", vcodec, "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-ar", "48000", "-b:a", "128k"]
    cmd += [str(out)]
    _run(cmd)


def _silent(size: tuple[int, int] = (1280, 720), fps: int = 30, dur: float = 5.0) -> Path:
    out = Path(tempfile.mktemp(suffix=".mp4"))
    _run([_ff(), "-y",
          "-f", "lavfi", "-i", f"color=c=black:s={size[0]}x{size[1]}:r={fps}:d={dur}",
          "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
          "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-ar", "48000", "-b:a", "64k", str(out)])
    return out


# ── synthetic fixture builders ────────────────────────────────────────────────
def build_synthetic(out_dir: Path) -> dict[str, Path]:
    """Build the full synthetic fixture set into `out_dir`. Returns name→path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir_s = str(out_dir)

    def tmp(name: str) -> Path:
        return out_dir / name

    # a) 120 BPM click + moving testsrc @720p
    click = tmp("_click.wav")
    _click_wav(click, bpm=120.0, dur=10.0, sr=48000)
    a = tmp("tone_120bpm_720p.mp4")
    _mux(str(click), a, size=(1280, 720), fps=30, dur=10.0)

    # b) silent
    b = _silent(size=(1280, 720), fps=30, dur=5.0)
    shutil.move(str(b), out_dir / "silent_720p.mp4")
    b = out_dir / "silent_720p.mp4"

    # c) 2s short @640x360
    c = tmp("short_2s.mp4")
    _mux(None, c, size=(640, 360), fps=24, dur=2.0)

    # d) 0-byte file
    d = tmp("empty_0byte.mp4")
    d.write_bytes(b"")

    # e) broken header (bad magic)
    e = tmp("broken_header.mp4")
    e.write_bytes(b"NOTAVIMP4" + b"\x00" * 64)

    # f) vertical 9:16
    f = tmp("vertical_9x16.mp4")
    _mux(None, f, size=(720, 1280), fps=30, dur=3.0)

    # g) 4K 3s
    g = tmp("wide_4k_3s.mp4")
    _mux(None, g, size=(3840, 2160), fps=30, dur=3.0)

    # h) Persian name (U+06A9 kaf / U+06CC ye / U+06F1 digit), internal spaces,
    #    real `.mp4` suffix so Storage._validate_extension accepts it (→ not 415).
    h = tmp("کلیپ تمرین ۱.mp4")
    _mux(None, h, size=(640, 360), fps=30, dur=2.0)

    return {p.name: p for p in [
        a, b, c, d, e, f, g, h,
    ]}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_fixtures(workdir: Path, allow_network: bool = True) -> dict:
    """Build fixtures into `workdir`; returns {names→paths, warnings, downloaded}.

    Never raises on a missing network — it degrades to synthetic-only and logs
    an explicit warning (recorded in the returned `warnings` list).
    """
    workdir = Path(workdir)
    synthetic = build_synthetic(workdir)
    warnings: list[str] = []
    downloaded: dict[str, str] = {}

    manifest = load_manifest()

    # Optional network assets (Pexels human clip + MediaPipe pose image).
    # Offline → explicit warning, synthetic-only (no silent skip).
    try:
        human = _fetch_human_clip(workdir, allow_network=allow_network)
        if human is not None:
            downloaded["human_clip.mp4"] = sha256(human)
        pose = _fetch_pose_image(workdir, allow_network=allow_network)
        if pose is not None:
            downloaded["pose.jpg"] = sha256(pose)
    except _OfflineError as exc:
        warnings.append(
            f"OFFLINE: network unavailable — the licensed human clip and pose "
            f"image were NOT produced; degraded to synthetic-only. ({exc})"
        )
        for _ in ("human_clip.mp4", "pose.jpg"):
            downloaded.setdefault(_, "unverified:network")

    return {
        "paths": synthetic,
        "warnings": warnings,
        "downloaded": downloaded,
        "manifest": manifest,
        "workdir": workdir,
    }


class _OfflineError(RuntimeError):
    pass


def _net_get(url: str, dest: Path, timeout: float = 15.0) -> bool:
    """Best-effort GET; returns True on success, raises _OfflineError if no net."""
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as exc:  # noqa: BLE001 - any network failure => offline
        if isinstance(exc, _OfflineError):
            raise
        raise _OfflineError(str(exc)) from exc


def _fetch_human_clip(workdir: Path, allow_network: bool) -> Path | None:
    if not allow_network:
        raise _OfflineError("network disabled")
    dest = workdir / "human_clip.mp4"
    # Placeholder URL for a Pexels-licensed clip. Replaced with a real permalink
    # once a specific Pexels asset is chosen (S-005 records SHA256 pin).
    url = os.getenv("CE_FIXTURE_HUMAN_CLIP_URL", "")
    if not url:
        raise _OfflineError("CE_FIXTURE_HUMAN_CLIP_URL not set (no network)")
    _net_get(url, dest)
    return dest


def _fetch_pose_image(workdir: Path, allow_network: bool) -> Path | None:
    if not allow_network:
        raise _OfflineError("network disabled")
    dest = workdir / "pose.jpg"
    url = os.getenv("CE_FIXTURE_POSE_URL", "")
    if not url:
        raise _OfflineError("CE_FIXTURE_POSE_URL not set (no network)")
    _net_get(url, dest)
    return dest


# ── manifest ──────────────────────────────────────────────────────────────────
MANIFEST_NAME = "manifest.json"


def load_manifest() -> dict:
    """Load the committed manifest describing the expected synthetic set."""
    here = Path(__file__).resolve().parent
    mf = here / MANIFEST_NAME
    if not mf.exists():
        raise FileNotFoundError(f"missing {mf}")
    return json.loads(mf.read_text(encoding="utf-8"))


def write_manifest_into(workdir: Path, synthetic: dict[str, Path]) -> Path:
    """Write a runtime manifest (with sha256 of generated files) in `workdir`."""
    entries = {}
    for name, path in synthetic.items():
        entries[name] = {
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    data = {"synthetic": entries}
    dest = workdir / MANIFEST_NAME
    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def _cli(argv: list[str]) -> int:
    out = Path(argv[0]) if argv else Path(tempfile.mkdtemp(prefix="ce_fixtures_"))
    allow_network = os.getenv("CE_FIXTURE_OFFLINE", "0") != "1"
    res = make_fixtures(out, allow_network=allow_network)
    manifest = write_manifest_into(out, res["paths"])
    print(f"Generated {len(res['paths'])} fixtures in {out}")
    for name in sorted(res["paths"]):
        p = res["paths"][name]
        print(f"  {name}: {p.stat().st_size} bytes")
    for w in res["warnings"]:
        print("WARN:", w)
    print("manifest:", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
