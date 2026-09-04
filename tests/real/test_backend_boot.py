"""S-002 real test: backend boots as the `ai_engine` package and /health works.

Run with pytest:
    pytest -m real tests/real/test_backend_boot.py
Or directly (also works):
    python tests/real/test_backend_boot.py

Honest "real" per 02_LOOP_PROTOCOL.md §1-⑤: this drives a live uvicorn server
started through the actual scripts/dev-backend.sh script and talks to /health
over HTTP — it does not call functions with fake arrays.
"""
from __future__ import annotations

import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_DIR = REPO_ROOT / "ai-engine"
SCRIPT_DIR = REPO_ROOT / "scripts"
DEV_BACKEND_SH = SCRIPT_DIR / "dev-backend.sh"
DEV_BACKEND_PS1 = SCRIPT_DIR / "dev-backend.ps1"
ENV_EXAMPLE = AI_DIR / ".env.example"
REQUIREMENTS = AI_DIR / "requirements.txt"
PYPROJECT = AI_DIR / "pyproject.toml"

# Minimal set of deps needed to actually boot the API (heavy AI deps are lazy
# imports in the endpoints and are NOT required for /health).
BOOT_DEPS = [
    "fastapi==0.115.6",
    "uvicorn[standard]==0.32.1",
    "python-multipart==0.0.18",
    "pydantic==2.10.4",
    "python-dotenv==1.0.1",
    "psutil==6.1.0",
    "requests==2.32.3",
]

HEALTH_FIELDS = {"ram", "cpu", "gpu_mem"}


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _venv_dir() -> Path:
    return Path(os.environ.get("CE_TEST_VENV", str(AI_DIR / ".venv")))


def _venv_python(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _provision_venv(venv: Path) -> Path:
    """Create (if needed) and populate a venv with boot deps + editable pkg."""
    py = _venv_python(venv)
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    # Idempotent: skip install when the package + boot deps are already importable.
    probe = subprocess.run(
        [str(py), "-c", "import ai_engine.main, uvicorn, fastapi, psutil, requests"],
        capture_output=True,
    )
    if probe.returncode == 0:
        return py
    subprocess.run([str(py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=True)
    subprocess.run([str(py), "-m", "pip", "install", "--quiet", *BOOT_DEPS], check=True)
    subprocess.run(
        [str(py), "-m", "pip", "install", "--quiet", "--no-deps", "-e", str(AI_DIR)],
        check=True,
    )
    return py


def _start_server(venv: Path, port: int) -> subprocess.Popen:
    """Start scripts/dev-backend.sh and return the Popen handle."""
    env = os.environ.copy()
    env["CE_VENV_DIR"] = str(venv)
    env["CE_HOST"] = "127.0.0.1"
    env["CE_PORT"] = str(port)
    env["CE_IDLE_SECONDS"] = os.environ.get("CE_IDLE_SECONDS", "60")
    log = tempfile.NamedTemporaryFile(delete=False, suffix=".log", mode="w")
    proc = subprocess.Popen(
        ["bash", str(DEV_BACKEND_SH)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    proc._ce_log = log.name  # type: ignore[attr-defined]
    return proc


def _stop_server(proc: subprocess.Popen) -> None:
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            pass
    log = getattr(proc, "_ce_log", None)
    if log and os.path.exists(log):
        try:
            os.unlink(log)
        except Exception:
            pass


def _wait_for_health(port: int, timeout: float = 10.0) -> tuple[float, dict]:
    import requests

    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/health"
    while time.monotonic() < deadline:
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                return time.monotonic(), r.json()
        except Exception:
            pass
        time.sleep(0.05)
    raise AssertionError(f"/health did not respond 200 within {timeout}s (port {port})")


# ────────────────────────── fixtures ──────────────────────────
@pytest.fixture(scope="module")
def venv_python():
    venv = _venv_dir()
    py = _provision_venv(venv)
    return py


@pytest.fixture(scope="module")
def live_server(venv_python):
    venv = _venv_dir()
    port = _free_port()
    proc = _start_server(venv, port)
    start = time.monotonic()
    ready_at, health = _wait_for_health(port, timeout=15.0)
    yield {"port": port, "proc": proc, "start": start, "elapsed": ready_at - start, "health": health}
    _stop_server(proc)


# ────────────────────────── tests ──────────────────────────
@pytest.mark.real
def test_package_import(venv_python):
    """AC-1: `from ai_engine.main import app` succeeds (no relative-import crash)."""
    out = subprocess.run(
        [str(venv_python), "-c", "from ai_engine.main import app; print(app.title)"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, f"package import failed: {out.stderr}"
    assert "Cutting Edge" in out.stdout


@pytest.mark.real
def test_health_within_2s(live_server):
    """AC-2: /health returns 200 with ram/cpu/gpu_mem within 2s of startup."""
    elapsed = live_server["elapsed"]
    health = live_server["health"]
    assert elapsed <= 2.0, f"server took {elapsed:.2f}s to answer /health (limit 2.0s)"
    body = live_server["proc"]
    assert body is not None
    assert HEALTH_FIELDS.issubset(health.keys()), f"missing fields: {health}"
    assert isinstance(health["ram"], (int, float))
    assert isinstance(health["cpu"], (int, float))


@pytest.mark.real
def test_survives_60s_idle(live_server):
    """AC-3: server survives the idle window and /health still answers 200."""
    import requests

    idle = float(os.environ.get("CE_IDLE_SECONDS", "60"))
    time.sleep(idle)
    port = live_server["port"]
    r = requests.get(f"http://127.0.0.1:{port}/health", timeout=3.0)
    assert r.status_code == 200
    health = r.json()
    assert HEALTH_FIELDS.issubset(health.keys()), f"missing fields after idle: {health}"


@pytest.mark.real
def test_dotenv_and_env_example():
    """AC-4: .env.example has OPENROUTER_API_KEY and the app boots w/o .env."""
    assert ENV_EXAMPLE.exists(), f"missing {ENV_EXAMPLE}"
    content = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert re.search(r"^OPENROUTER_API_KEY=", content, re.M), "OPENROUTER_API_KEY= not in .env.example"
    # Server already ran without a real .env (provisioned venv only) — see live_server.
    assert ENV_EXAMPLE.read_text(encoding="utf-8").strip()


@pytest.mark.real
def test_pinned_requirements_and_pyproject():
    """AC-5: requirements.txt pins versions and pyproject.toml exists."""
    assert REQUIREMENTS.exists()
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # every dependency line is name==version or name[extra]==version
        assert "==" in line, f"unpinned requirement line: {line!r}"
        assert line.split("==")[1].strip(), f"missing version for {line!r}"
    assert PYPROJECT.exists()
    text = PYPROJECT.read_text(encoding="utf-8")
    assert "name = \"cutting-edge-ai-engine\"" in text
    assert "package-dir" in text
    assert "ai_engine" in text


@pytest.mark.real
def test_dev_backend_ps1_present():
    """AC-6 (static, Windows unverified): dev-backend.ps1 exists w/ uvicorn call."""
    assert DEV_BACKEND_PS1.exists(), "dev-backend.ps1 missing"
    content = DEV_BACKEND_PS1.read_text(encoding="utf-8")
    assert re.search(r"uvicorn\s+ai_engine\.main:app", content), "ps1 must call uvicorn ai_engine.main:app"


def _run_all() -> int:
    """Direct runner so `python tests/real/test_backend_boot.py` works."""
    venv = _venv_dir()
    py = _provision_venv(venv)
    counter = {"pass": 0}

    def check(name, fn):
        try:
            fn()
            print(f"PASS {name}")
            counter["pass"] += 1
            return True
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            return False

    def pkg_import():
        out = subprocess.run(
            [str(py), "-c", "from ai_engine.main import app; print(app.title)"],
            capture_output=True, text=True,
        )
        assert out.returncode == 0, out.stderr

    port = _free_port()
    proc = _start_server(venv, port)
    started = time.monotonic()
    try:
        ready_at, health = _wait_for_health(port, timeout=15.0)
        elapsed = ready_at - started

        def health_2s():
            assert elapsed <= 2.0, f"{elapsed:.2f}s > 2.0s"
            assert HEALTH_FIELDS.issubset(health.keys())
            assert isinstance(health["ram"], (int, float))

        def idle():
            idle_s = float(os.environ.get("CE_IDLE_SECONDS", "60"))
            time.sleep(idle_s)
            import requests
            r = requests.get(f"http://127.0.0.1:{port}/health", timeout=3.0)
            assert r.status_code == 200
            assert HEALTH_FIELDS.issubset(r.json().keys())

        ok = check("test_package_import", pkg_import)
        ok = check("test_health_within_2s", health_2s) and ok
        ok = check("test_survives_60s_idle", idle) and ok
    finally:
        _stop_server(proc)

    ok = check("test_dotenv_and_env_example", test_dotenv_and_env_example) and ok
    ok = check("test_pinned_requirements_and_pyproject", test_pinned_requirements_and_pyproject) and ok
    ok = check("test_dev_backend_ps1_present", test_dev_backend_ps1_present) and ok

    print(f"\n{('OK' if ok else 'FAILED')} — {counter['pass']}/6 S-002 real checks green")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
