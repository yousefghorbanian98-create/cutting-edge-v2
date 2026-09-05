"""S-005/006 test harness shared fixtures.

`fixtures_dir` builds the real-media fixture set once per session (into a
gitignored cache dir) and the `fixture` helper resolves a fixture by name.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys_path_ok = str(REPO_ROOT)  # noqa: F841 - keep root importable if needed

# Fixtures are built into a gitignored cache dir (never committed media).
# Default is tests/fixtures/.cache/ (already in .gitignore) so local reruns and
# the CI cache actually hit; CE_FIXTURES_DIR overrides it.
DEFAULT_CACHE_DIR = REPO_ROOT / "tests" / "fixtures" / ".cache"
_default_cache = Path(os.environ.get("CE_FIXTURES_DIR") or DEFAULT_CACHE_DIR)

# Every synthetic fixture the factory must produce (see manifest.json).
_EXPECTED_SYNTHETIC = (
    "tone_120bpm_720p.mp4",
    "silent_720p.mp4",
    "short_2s.mp4",
    "empty_0byte.mp4",
    "broken_header.mp4",
    "vertical_9x16.mp4",
    "wide_4k_3s.mp4",
    "کلیپ تمرین ۱.mp4",
)


def _cache_is_complete(workdir: Path) -> bool:
    """True when every expected synthetic fixture is already present."""
    return all((workdir / name).exists() for name in _EXPECTED_SYNTHETIC)


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Build (or reuse) the fixture set and return the cache dir."""
    from tests.fixtures.make_fixtures import make_fixtures

    workdir = _default_cache
    # Reuse only a *complete* cache — a stale/partial dir (e.g. one built before
    # the fixture (h) rename) must be regenerated, never silently reused.
    if _cache_is_complete(workdir):
        return workdir
    res = make_fixtures(workdir, allow_network=os.getenv("CE_FIXTURE_OFFLINE", "0") != "1")
    for w in res["warnings"]:
        # Explicit (never silent) degradation warning.
        import warnings as _w

        _w.warn(w, stacklevel=2)
    return workdir


@pytest.fixture
def fixture(fixtures_dir: Path):
    """Return a name→path resolver for the generated fixtures."""

    def _get(name: str) -> Path:
        p = fixtures_dir / name
        if not p.exists():
            raise FileNotFoundError(f"fixture not built: {name}")
        return p

    return _get


# ── live uvicorn server (S-006) ───────────────────────────────────────────────
@pytest.fixture(scope="session")
def live_api(fixtures_dir: Path):
    """Boot a real uvicorn server on a free port for the live API tests."""
    import os
    import signal
    import socket
    import subprocess
    import time

    import requests

    def _free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    venv = Path(os.environ.get("CE_TEST_VENV", str(REPO_ROOT / "ai-engine" / ".venv")))
    py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    port = _free_port()
    env = os.environ.copy()
    env["CE_HOST"] = "127.0.0.1"
    env["CE_PORT"] = str(port)

    log_f = tempfile.NamedTemporaryFile(delete=False, suffix=".log", mode="w")
    proc = subprocess.Popen(
        [str(py), "-m", "uvicorn", "ai_engine.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(REPO_ROOT / "ai-engine"),
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 20
    ok = False
    while time.monotonic() < deadline:
        try:
            if requests.get(base + "/health", timeout=1.0).status_code == 200:
                ok = True
                break
        except Exception:
            pass
        time.sleep(0.1)
    if not ok:
        proc.kill()
        raise RuntimeError(f"live server did not come up: {(log_f.name)}")
    yield {"base": base, "port": port}
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

