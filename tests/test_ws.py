"""S-029 real progress socket. Fewer than 10 increases is a failure."""

from __future__ import annotations

import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import requests
import uvicorn
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai-engine"))

from ai_engine.core.ffmpeg import find_ffmpeg  # noqa: E402
from ai_engine.main import app, storage  # noqa: E402

pytestmark = pytest.mark.real
PORT = 8765


def _video(path: Path) -> None:
    proc = subprocess.run(
        [find_ffmpeg(), "-y", "-f", "lavfi", "-i", "color=c=navy:s=160x90:r=30:d=15", "-pix_fmt", "yuv420p", str(path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-400:])


@pytest.fixture(scope="module")
def server() -> str:
    thread = threading.Thread(
        target=uvicorn.run,
        kwargs={"app": app, "host": "127.0.0.1", "port": PORT, "log_level": "warning"},
        daemon=True,
    )
    thread.start()
    base = f"http://127.0.0.1:{PORT}"
    for _ in range(50):
        try:
            if requests.get(f"{base}/health", timeout=0.2).status_code == 200:
                return base
        except requests.RequestException:
            time.sleep(0.05)
    raise RuntimeError("export server did not start")


def _start(base: str) -> str:
    name = "ws-source.mp4"
    target = Path(storage.base_dir) / name
    if not target.exists():
        _video(target)
    created = requests.post(
        f"{base}/export",
        json={
            "w": 160,
            "h": 90,
            "fps": 30,
            "codec": "h264",
            "clips": [{"id": "a", "name": name, "kind": "video", "start_ms": 0, "duration_ms": 15000, "in_ms": 0}],
            "output_name": "ws-out.mp4",
            "pace": "realtime",
            "overwrite": True,
        },
        timeout=5,
    )
    assert created.status_code == 202, created.text
    return created.json()["job_id"]


def test_websocket_emits_ten_increasing_percents(server: str) -> None:
    job_id = _start(server)
    percents: list[int] = []
    with connect(f"ws://127.0.0.1:{PORT}/ws/jobs/{job_id}") as socket:
        for _ in range(80):
            message = socket.recv(timeout=20)
            import json

            payload = json.loads(message)
            assert {"percent", "fps", "eta", "stage", "log"} <= set(payload)
            if not percents or payload["percent"] > percents[-1]:
                percents.append(int(payload["percent"]))
            if payload["stage"] in {"done", "error", "cancelled"}:
                break
    assert len(percents) >= 10, percents
    assert percents == sorted(percents)


def test_closed_socket_still_finishes_via_polling(server: str) -> None:
    job_id = _start(server)
    with connect(f"ws://127.0.0.1:{PORT}/ws/jobs/{job_id}") as socket:
        socket.recv(timeout=20)
    status = "running"
    for _ in range(80):
        view = requests.get(f"{server}/jobs/{job_id}", timeout=5)
        assert view.status_code == 200
        status = view.json()["status"]
        if status in {"done", "error", "cancelled"}:
            break
        time.sleep(0.25)
    assert status == "done"
