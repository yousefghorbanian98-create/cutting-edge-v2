"""BUG-18: run_ffmpeg must not replace an existing file without consent."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-engine"))

from ai_engine.core.ffmpeg import OverwriteRefused, run_ffmpeg  # noqa: E402

pytestmark = pytest.mark.unit


def test_existing_output_without_consent_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"keep")
    called = False

    def boom(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("ffmpeg must not run")

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", boom)
    with pytest.raises(OverwriteRefused):
        run_ffmpeg(["-i", "in.mp4", str(dest)])
    assert dest.read_bytes() == b"keep"
    assert called is False
    assert not (tmp_path / "out.partial.wav").exists()
    print(
        "EVIDENCE concept=refusal concept=no-overwrite " "ffmpeg-called=false dest-unchanged=true partial-absent=true"
    )


def test_failed_consented_replace_rolls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"keep")
    monkeypatch.setattr("ai_engine.core.ffmpeg.find_ffmpeg", lambda: "ffmpeg")

    class Proc:
        returncode = 1
        stderr = "boom"

    def fake_run(cmd, **_kwargs):
        partial = Path(cmd[-1])
        assert partial.name == "out.partial.wav"
        partial.write_bytes(b"torn")
        return Proc()

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", fake_run)
    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        run_ffmpeg(["-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"keep"
    assert not (tmp_path / "out.partial.wav").exists()
    print("EVIDENCE concept=explicit-consent concept=rollback " "dest-unchanged=true partial-absent=true")


def test_consented_replace_publishes_only_after_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"old")
    monkeypatch.setattr("ai_engine.core.ffmpeg.find_ffmpeg", lambda: "ffmpeg")

    class Proc:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **_kwargs):
        assert cmd[0] == "ffmpeg"
        assert "-y" not in cmd
        Path(cmd[-1]).write_bytes(b"new")
        return Proc()

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", fake_run)
    run_ffmpeg(["-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"new"
    assert not (tmp_path / "out.partial.wav").exists()
    print(
        "EVIDENCE concept=explicit-consent concept=staging "
        "partial-name=out.partial.wav published-after-success=true dash-y-absent=true"
    )
