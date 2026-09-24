"""S-012 — one GPU inference slot, CPU fallback, no forbidden Style Match runtimes.

These tests do not install a model and do not treat a missing GPU as a pass.
"""

from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.unit

FORBIDDEN = ("ollama", "pyside6", "gradio", "ultralytics")
MANIFESTS = (
    ROOT / "ai-engine" / "requirements.txt",
    ROOT / "ai-engine" / "requirements-tooling.txt",
    ROOT / "ai-engine" / "pyproject.toml",
    ROOT / "package.json",
    ROOT / "apps" / "desktop" / "package.json",
    ROOT / "apps" / "desktop" / "src-tauri" / "Cargo.toml",
)
SOURCE_ROOTS = (ROOT / "ai-engine" / "src", ROOT / "apps" / "desktop" / "src")
IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+(ollama|PySide6|gradio|ultralytics)\b", re.I)


def _wait(manager, job_id: str, timeout: float = 3.0) -> dict:
    deadline = time.monotonic() + timeout
    view = None
    while time.monotonic() < deadline:
        view = manager.get(job_id)
        if view and view["status"] in {"done", "error", "cancelled"}:
            return view
        time.sleep(0.01)
    raise AssertionError(f"job did not finish: {view}")


def test_one_gpu_inference_at_a_time_cpu_job_still_runs() -> None:
    from ai_engine.core.jobs import JobManager

    manager = JobManager(max_workers=2, gpu_probe=lambda: True)
    state = {"inside": 0, "max": 0}
    lock = threading.Lock()
    entered = threading.Event()
    release = threading.Event()

    def inference(_control):
        with lock:
            state["inside"] += 1
            state["max"] = max(state["max"], state["inside"])
        entered.set()
        assert release.wait(timeout=2)
        with lock:
            state["inside"] -= 1
        return {"ok": True}

    first = manager.submit_inference(inference)
    assert entered.wait(timeout=2)
    second = manager.submit_inference(inference)
    time.sleep(0.05)
    with lock:
        assert state["max"] == 1
        assert state["inside"] == 1
    cpu_id = manager.submit(lambda _control: {"cpu": True})
    cpu_view = _wait(manager, cpu_id, timeout=1)
    assert cpu_view["status"] == "done", cpu_view
    assert cpu_view["device"] == "cpu"
    with lock:
        assert state["inside"] == 1, "CPU work must not wait behind a second GPU job"
    release.set()
    for job_id in (first, second):
        view = _wait(manager, job_id)
        assert view["status"] == "done", view
        assert view["device"] == "gpu", view
        assert view["gpu"] == "slot", view
        assert view["gpu"] != "pass"
    assert state["max"] == 1


def test_missing_gpu_is_unverified_and_falls_back_to_cpu() -> None:
    from ai_engine.core.jobs import JobManager

    manager = JobManager(max_workers=2, gpu_probe=lambda: False)
    barrier = threading.Barrier(2)

    def inference(_control):
        barrier.wait(timeout=2)
        return {"ok": True}

    ids = [manager.submit_inference(inference) for _ in range(2)]
    views = [_wait(manager, job_id) for job_id in ids]
    assert all(view["status"] == "done" for view in views), views
    assert {view["device"] for view in views} == {"cpu"}
    assert {view["gpu"] for view in views} == {"unverified"}
    assert all(view["gpu"] != "pass" for view in views)


def test_host_probe_does_not_report_gpu_pass() -> None:
    from ai_engine.core.jobs import JobManager, probe_gpu

    available = probe_gpu()
    manager = JobManager()
    view = _wait(manager, manager.submit_inference(lambda _control: {"ok": True}))
    assert view["status"] == "done", view
    assert view["gpu"] != "pass"
    if not available:
        assert view["device"] == "cpu", view
        assert view["gpu"] == "unverified", view
    else:
        assert view["device"] == "gpu", view


def test_forbidden_style_match_runtimes_are_absent() -> None:
    hits: list[str] = []
    for path in MANIFESTS:
        text = path.read_text(encoding="utf-8").lower()
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            blob = json.dumps(
                {
                    "dependencies": data.get("dependencies", {}),
                    "devDependencies": data.get("devDependencies", {}),
                    "optionalDependencies": data.get("optionalDependencies", {}),
                }
            ).lower()
        else:
            blob = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
        for name in FORBIDDEN:
            if name in blob:
                hits.append(f"{path.relative_to(ROOT)} declares {name}")
    for root in SOURCE_ROOTS:
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".ts", ".tsx"} or not path.is_file():
                continue
            for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if IMPORT_RE.match(line):
                    hits.append(f"{path.relative_to(ROOT)}:{line_no} {line.strip()}")
    guard = (ROOT / "scripts" / "supervise.py").read_text(encoding="utf-8").lower()
    for name in FORBIDDEN:
        if name not in guard:
            hits.append(f"scripts/supervise.py does not forbid {name}")
    assert hits == []
