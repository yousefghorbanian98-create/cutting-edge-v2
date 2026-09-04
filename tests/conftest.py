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

# fixtures are built into a gitignored temp dir (never committed media).
_default_cache = Path(os.environ.get("CE_FIXTURES_DIR", tempfile.mkdtemp(prefix="ce_fixtures_")))


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Build (or reuse) the fixture set and return the cache dir."""
    from tests.fixtures.make_fixtures import make_fixtures

    workdir = _default_cache
    # Reuse if already built.
    if (workdir / "tone_120bpm_720p.mp4").exists():
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
