"""S-012 real test: heavy work is a job, /health stays fast, cancel drops the partial file.

Run: pytest -m real tests/test_jobs.py
"""

from __future__ import annotations

import statistics
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import requests

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.helpers.jobs import poll_job, start_enhance
from tests.helpers.media import assert_playable


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = max(0, int(round(0.95 * (len(ordered) - 1))))
    return ordered[index]


@pytest.mark.real
def test_health_p95_under_200ms_while_enhance_runs_and_output_is_playable(fixture, live_api) -> None:
    """10s 720p enhance must not block /health. The finished file must be playable."""
    base = live_api["base"]
    clip = fixture("tone_120bpm_720p.mp4")
    job_id = start_enhance(base, clip, "0.6", "natural_gym")

    def _one_health() -> float:
        started = time.perf_counter()
        response = requests.get(base + "/health", timeout=2)
        elapsed = time.perf_counter() - started
        assert response.status_code == 200, response.text[:200]
        assert response.json()["status"] in {"healthy", "warning"}
        return elapsed

    # 10 workers × 5 calls = 50 probes, overlapping the render instead of waiting
    # out a serial 5s of health's own 100ms cpu sample.
    with ThreadPoolExecutor(max_workers=10) as pool:
        latencies = list(pool.map(lambda _: _one_health(), range(50)))
    assert len(latencies) == 50
    p95 = _p95(latencies)
    assert p95 < 0.2, f"/health p95 {p95:.3f}s during enhance (n=50, median {statistics.median(latencies):.3f}s)"

    view = poll_job(base, job_id, timeout=180)
    assert view["status"] == "done", view
    assert view["percent"] == 100, view
    assert view["error"] is None
    result = view["result"]
    assert result and result.get("output_filename", "").endswith(".mp4"), result

    download = requests.get(base + "/muscle/download/" + result["output_filename"], timeout=60)
    assert download.status_code == 200, download.status_code
    out_dir = Path(tempfile.mkdtemp(prefix="ce_job_"))
    out_path = out_dir / result["output_filename"]
    out_path.write_bytes(download.content)
    info = assert_playable(out_path, min_dur=9.0, has_audio=False, width=1280, height=720)
    assert info["video_codec"] is not None


@pytest.mark.real
def test_cancel_at_30_percent_stops_within_2s_and_removes_partial(fixture, live_api) -> None:
    base = live_api["base"]
    clip = fixture("tone_120bpm_720p.mp4")
    job_id = start_enhance(base, clip, "0.6", "natural_gym")

    deadline = time.monotonic() + 120
    seen = None
    while time.monotonic() < deadline:
        seen = requests.get(f"{base}/jobs/{job_id}", timeout=5).json()
        if seen["percent"] >= 30 or seen["status"] in {"done", "error", "cancelled"}:
            break
        time.sleep(0.02)
    assert seen is not None and seen["percent"] >= 30, f"never reached 30%: {seen}"
    assert seen["status"] == "running", seen
    name = seen.get("output_filename")
    assert name, seen

    started = time.perf_counter()
    cancelled = requests.post(f"{base}/jobs/{job_id}/cancel", timeout=5)
    assert cancelled.status_code == 200, cancelled.text[:200]
    final = None
    while time.perf_counter() - started < 2.0:
        final = requests.get(f"{base}/jobs/{job_id}", timeout=5).json()
        if final["status"] == "cancelled":
            break
        time.sleep(0.02)
    elapsed = time.perf_counter() - started
    assert final is not None and final["status"] == "cancelled", f"not stopped in 2s ({elapsed:.2f}s): {final}"
    assert elapsed < 2.0
    assert final["partial_removed"] is True, final
    missing = requests.get(base + "/muscle/download/" + name, timeout=10)
    assert missing.status_code == 404, f"partial file still downloadable: {missing.status_code}"
