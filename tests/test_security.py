"""S-003 real test: secure storage (path traversal, size & type limits, CORS).

Run with pytest (the live-server tests boot a real uvicorn on a free port and
exercise HTTP status codes over the wire):
    pytest -m real tests/test_security.py
Or directly: python tests/test_security.py

Security properties verified:
  (a) upload with a traversal filename is stored inside the storage dir only,
  (b) download traversal (../etc/passwd) returns 404,
  (c) oversized upload returns 413,
  (d) disallowed extension (.exe) returns 415,
  (e) CORS origin allow-list excludes arbitrary origins.
"""
from __future__ import annotations

import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_DIR = REPO_ROOT / "ai-engine"
DEV_BACKEND_SH = REPO_ROOT / "scripts" / "dev-backend.sh"

# Keep the size limit small so we can trigger 413 without a 3 GB upload.
MAX_UPLOAD_MB = os.environ.get("CE_TEST_MAX_UPLOAD_MB", "1")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _venv_python() -> Path:
    venv = Path(os.environ.get("CE_TEST_VENV", str(AI_DIR / ".venv")))
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _provision_venv() -> Path:
    venv = Path(os.environ.get("CE_TEST_VENV", str(AI_DIR / ".venv")))
    py = _venv_python()
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    probe = subprocess.run(
        [str(py), "-c", "import ai_engine.main, uvicorn, fastapi, psutil, requests"],
        capture_output=True,
    )
    if probe.returncode != 0:
        for pkg in (
            "fastapi==0.115.6", "uvicorn[standard]==0.32.1", "python-multipart==0.0.18",
            "pydantic==2.10.4", "python-dotenv==1.0.1", "psutil==6.1.0",
            "requests==2.32.3",
        ):
            subprocess.run([str(py), "-m", "pip", "install", "--quiet", pkg], check=True)
        subprocess.run(
            [str(py), "-m", "pip", "install", "--quiet", "--no-deps", "-e", str(AI_DIR)],
            check=True,
        )
    return py


def _start_server(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["CE_VENV_DIR"] = str(Path(os.environ.get("CE_TEST_VENV", str(AI_DIR / ".venv"))))
    env["CE_HOST"] = "127.0.0.1"
    env["CE_PORT"] = str(port)
    env["CE_MAX_UPLOAD_MB"] = MAX_UPLOAD_MB
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


def _wait_for_health(port: int, timeout: float = 15.0) -> None:
    import requests

    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/health"
    while time.monotonic() < deadline:
        try:
            if requests.get(url, timeout=1.0).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.05)
    raise AssertionError(f"/health did not answer 200 within {timeout}s (port {port})")


@pytest.fixture(scope="module")
def live_server():
    import requests

    _provision_venv()
    port = _free_port()
    proc = _start_server(port)
    try:
        _wait_for_health(port)
        yield {"port": port, "base": f"http://127.0.0.1:{port}"}
    finally:
        _stop_server(proc)


# ─────────────────────────────────────────────────────────────────────────────
# (a) upload path-traversal stays inside the storage dir
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.real
def test_upload_traversal_stays_in_storage():
    from fastapi import UploadFile

    from ai_engine.core.storage import Storage, sanitize_filename

    with tempfile.TemporaryDirectory() as td:
        st = Storage(base_dir=td, max_upload_bytes=10 * 1024 * 1024)
        malicious = "../../../../etc/evil.mp4"
        safe = sanitize_filename(malicious)
        assert "/" not in safe and ".." not in safe, f"sanitize failed: {safe!r}"

        content = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64  # small fake mp4 bytes
        f = UploadFile(filename=malicious, file=tempfile.NamedTemporaryFile())
        f.file.write(content)
        f.file.seek(0)
        stored = Path(st.save_upload(f))
        stored_resolved = stored.resolve()
        base_resolved = Path(td).resolve()
        assert base_resolved in stored_resolved.parents, "stored path escaped base dir"

        # The name on disk is a UUID with a whitelisted extension, not the input.
        assert re.fullmatch(r"[0-9a-f]{32}\.mp4", stored.name), f"bad stored name: {stored.name}"


@pytest.mark.real
def test_sanitize_filename_strips_separators_and_dotdot():
    from ai_engine.core.storage import sanitize_filename

    cases = {
        "../../evil.txt": "evil.txt",
        "C:\\Windows\\evil.mp4": "evil.mp4",
        "..\\..\\config.json": "config.json",
        "my video.mp4": "my video.mp4",
    }
    for raw, expected in cases.items():
        assert sanitize_filename(raw) == expected, f"{raw!r} -> {sanitize_filename(raw)!r}"


# ─────────────────────────────────────────────────────────────────────────────
# (b) download traversal -> 404
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.real
def test_download_traversal_returns_404(live_server):
    import requests

    r = requests.get(live_server["base"] + "/muscle/download/..%2F..%2Fetc%2Fpasswd")
    assert r.status_code == 404, f"expected 404, got {r.status_code}: {r.text}"
    r2 = requests.get(live_server["base"] + "/muscle/download/../../../etc/passwd")
    assert r2.status_code == 404, f"expected 404, got {r2.status_code}"


# ─────────────────────────────────────────────────────────────────────────────
# (c) oversized upload -> 413
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.real
def test_oversized_upload_returns_413(live_server):
    import requests

    blob = os.urandom((int(MAX_UPLOAD_MB) + 1) * 1024 * 1024)  # exceed the limit
    r = requests.post(
        live_server["base"] + "/editor/beat-sync",
        files={"file": ("big.mp4", blob, "video/mp4")},
        timeout=30,
    )
    assert r.status_code == 413, f"expected 413, got {r.status_code}: {r.text[:200]}"


# ─────────────────────────────────────────────────────────────────────────────
# (d) disallowed extension -> 415
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.real
def test_disallowed_extension_returns_415(live_server):
    import requests

    r = requests.post(
        live_server["base"] + "/editor/beat-sync",
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")},
    )
    assert r.status_code == 415, f"expected 415, got {r.status_code}: {r.text[:200]}"


# ─────────────────────────────────────────────────────────────────────────────
# (e) CORS allow-list rejects arbitrary origins
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.real
def test_cors_origin_allowlist(live_server):
    import requests

    r = requests.options(
        live_server["base"] + "/health",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # A disallowed origin must be rejected (Starlette answers 400 for a
    # non-allowlisted preflight) and must NEVER be reflected in ACAO.
    assert r.status_code in (200, 400), f"unexpected CORS status {r.status_code}"
    acao = r.headers.get("access-control-allow-origin")
    assert acao != "http://evil.example.com", "CORS reflected a disallowed origin"

    # Sanity: an allow-listed origin IS reflected.
    ok = requests.options(
        live_server["base"] + "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"


# ─────────────────────────────────────────────────────────────────────────────
# Direct runner
# ─────────────────────────────────────────────────────────────────────────────
def _run_all() -> int:
    import requests

    results = []

    def check(name, fn):
        try:
            fn()
            print(f"PASS {name}")
            results.append(True)
        except (AssertionError, Exception) as e:  # noqa: BLE001 - surface all
            print(f"FAIL {name}: {e}")
            results.append(False)

    check("test_upload_traversal_stays_in_storage", test_upload_traversal_stays_in_storage)
    check("test_sanitize_filename_strips_separators_and_dotdot", test_sanitize_filename_strips_separators_and_dotdot)

    _provision_venv()
    port = _free_port()
    proc = _start_server(port)
    try:
        _wait_for_health(port)
        base = f"http://127.0.0.1:{port}"
        check("test_download_traversal_returns_404", lambda: _check_404(requests, base))
        check("test_oversized_upload_returns_413", lambda: _check_413(requests, base))
        check("test_disallowed_extension_returns_415", lambda: _check_415(requests, base))
        check("test_cors_origin_allowlist", lambda: _check_cors(requests, base))
    finally:
        _stop_server(proc)

    ok = all(results)
    print(f"\n{('OK' if ok else 'FAILED')} — {sum(results)}/{len(results)} S-003 security checks green")
    return 0 if ok else 1


def _check_404(requests, base):
    r = requests.get(base + "/muscle/download/..%2F..%2Fetc%2Fpasswd")
    assert r.status_code == 404, f"got {r.status_code}"


def _check_413(requests, base):
    blob = os.urandom((int(MAX_UPLOAD_MB) + 1) * 1024 * 1024)
    r = requests.post(base + "/editor/beat-sync", files={"file": ("big.mp4", blob, "video/mp4")}, timeout=30)
    assert r.status_code == 413, f"got {r.status_code}"


def _check_415(requests, base):
    r = requests.post(base + "/editor/beat-sync", files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")})
    assert r.status_code == 415, f"got {r.status_code}"


def _check_cors(requests, base):
    r = requests.options(
        base + "/health",
        headers={"Origin": "http://evil.example.com", "Access-Control-Request-Method": "GET"},
    )
    assert r.status_code in (200, 400)
    assert r.headers.get("access-control-allow-origin") != "http://evil.example.com"
    ok = requests.options(
        base + "/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"


if __name__ == "__main__":
    raise SystemExit(_run_all())
