"""Artifact assertion helpers for S-006.

`assert_playable` uses `ai_engine.core.ffmpeg.probe_duration_and_streams`
(the ffprobe-equivalent over `ffmpeg -i`) plus light OpenCV frame validation,
so it works in a sandbox/CI that only has the bundled imageio-ffmpeg binary.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from ai_engine.core.ffmpeg import probe_duration_and_streams


def _parse_duration_seconds(dur: str | None) -> float | None:
    if not dur:
        return None
    parts = dur.split(":")
    try:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    except (IndexError, ValueError):
        return None


def assert_playable(
    path: str | Path,
    min_dur: float | None = None,
    has_audio: bool | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict:
    """Assert a media file is really playable and matches expected properties.

    Returns the probe dict. Raises AssertionError on any mismatch.
    """
    path = Path(path)
    assert path.exists() and path.stat().st_size > 0, f"file missing/empty: {path}"
    info = probe_duration_and_streams(path)

    if min_dur is not None:
        d = _parse_duration_seconds(info["duration"])
        assert d is not None and d >= min_dur - 0.05, (
            f"duration {info['duration']} < {min_dur}s for {path.name}"
        )

    if has_audio is not None:
        assert info["audio"] == has_audio, (
            f"audio={info['audio']}, expected {has_audio} for {path.name}"
        )

    if width is not None and info["width"] is not None:
        assert abs(info["width"] - width) <= 2, f"width {info['width']} != {width}"
    if height is not None and info["height"] is not None:
        assert abs(info["height"] - height) <= 2, f"height {info['height']} != {height}"

    # Sanity: OpenCV can actually open + read at least one frame for video.
    if not info["duration"] or info["video_codec"]:
        cap = cv2.VideoCapture(str(path))
        ok, frame = cap.read()
        cap.release()
        if ok:
            assert frame is not None and frame.size > 0, f"no decodable frame: {path.name}"

    return info


def frame_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Absolute per-pixel difference between two same-shaped frames."""
    assert a.shape == b.shape, f"shape mismatch {a.shape} vs {b.shape}"
    return np.abs(a.astype(np.int16) - b.astype(np.int16)).astype(np.uint8)


def mean_abs_pixel_diff(a: np.ndarray, b: np.ndarray) -> float:
    """Mean absolute per-pixel difference (0..255)."""
    return float(frame_diff(a, b).mean())


def ssim_region(a: np.ndarray, b: np.ndarray) -> float:
    """Lightweight structural-similarity over a sliding region (0..1).

    Uses a small local mean/variance formula on grayscale so it needs no extra
    deps beyond numpy. Higher = more similar.
    """
    import cv2 as _cv2

    ga = _cv2.cvtColor(a, _cv2.COLOR_BGR2GRAY).astype(np.float32)
    gb = _cv2.cvtColor(b, _cv2.COLOR_BGR2GRAY).astype(np.float32)
    # Gaussian window
    win = _cv2.getGaussianKernel(7, 1.5)
    window = np.outer(win, win)

    def _local_mean(x: np.ndarray) -> np.ndarray:
        return _cv2.filter2D(x, -1, window, borderType=_cv2.BORDER_REFLECT)

    mu1 = _local_mean(ga)
    mu2 = _local_mean(gb)
    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = _local_mean(ga * ga) - mu1_sq
    sigma2_sq = _local_mean(gb * gb) - mu2_sq
    sigma12 = _local_mean(ga * gb) - mu1_mu2

    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / (
        (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
    )
    return float(ssim_map.mean())
