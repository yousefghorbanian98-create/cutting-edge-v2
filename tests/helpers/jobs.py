"""Poll the S-012 job API. Shared by the live enhance tests and test_jobs.py."""

from __future__ import annotations

import time
from typing import Any

import requests


def poll_job(base: str, job_id: str, timeout: float = 180.0) -> dict[str, Any]:
    """Block until the job is done, error, or cancelled. Raises on timeout."""
    deadline = time.monotonic() + timeout
    last: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        response = requests.get(f"{base}/jobs/{job_id}", timeout=5)
        assert response.status_code == 200, response.text[:200]
        last = response.json()
        if last["status"] in {"done", "error", "cancelled"}:
            return last
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not finish: {last}")


def start_enhance(base: str, clip, intensity: str, preset: str) -> str:
    """POST /muscle/enhance and return the job id. The call must not wait for the render."""
    with open(clip, "rb") as handle:
        response = requests.post(
            base + "/muscle/enhance",
            files={"file": (clip.name, handle, "video/mp4")},
            data={"intensity": intensity, "preset": preset},
            timeout=30,
        )
    assert response.status_code == 202, f"enhance accept failed: {response.status_code} {response.text[:200]}"
    body = response.json()
    assert body.get("job_id"), body
    return body["job_id"]
