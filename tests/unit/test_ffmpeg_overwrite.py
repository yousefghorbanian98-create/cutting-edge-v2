"""BUG-18: run_ffmpeg must not replace an existing file without consent."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-engine"))

from ai_engine.core.ffmpeg import OverwriteRefused, file_sha256, run_ffmpeg, staged_output  # noqa: E402

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
    assert list(tmp_path.glob("out.*.partial.wav")) == []
    print("EVIDENCE concept=refusal concept=no-overwrite ffmpeg-called=false dest-unchanged=true partial-absent=true")


def test_failed_consented_replace_rolls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"keep")
    monkeypatch.setattr("ai_engine.core.ffmpeg.find_ffmpeg", lambda: "ffmpeg")

    class Proc:
        returncode = 1
        stderr = "boom"

    def fake_run(cmd, **_kwargs):
        partial = Path(cmd[-1])
        assert partial.name.endswith(".partial.wav")
        assert partial.name != "out.wav"
        partial.write_bytes(b"torn")
        return Proc()

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", fake_run)
    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        run_ffmpeg(["-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"keep"
    assert list(tmp_path.glob("out.*.partial.wav")) == []
    print("EVIDENCE concept=explicit-consent concept=rollback dest-unchanged=true partial-absent=true")


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
        partial = Path(cmd[-1])
        assert ".partial.wav" in partial.name
        partial.write_bytes(b"new")
        return Proc()

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", fake_run)
    run_ffmpeg(["-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"new"
    assert list(tmp_path.glob("out.*.partial.wav")) == []
    digest = file_sha256(dest)
    print(
        "EVIDENCE concept=explicit-consent concept=staging "
        f"partial-unique=true published-after-success=true dash-y-absent=true "
        f"receipt=sha256:{digest} bytes={dest.stat().st_size}"
    )


def test_raw_dash_y_cannot_bypass_consent(tmp_path: Path) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"keep")
    with pytest.raises(OverwriteRefused, match="raw -y"):
        run_ffmpeg(["-y", "-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"keep"
    print("EVIDENCE concept=raw-args-bypass refused=true ffmpeg-called=false dest-unchanged=true")


def test_unique_staging_names_differ(tmp_path: Path) -> None:
    dest = tmp_path / "out.wav"
    first = staged_output(dest)
    second = staged_output(dest)
    assert first != second
    assert first.name.endswith(".partial.wav")
    assert second.name.endswith(".partial.wav")
    print(f"EVIDENCE concept=unique-staging first={first.name} second={second.name} distinct=true")


def test_interrupt_preserves_previous_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"keep")
    monkeypatch.setattr("ai_engine.core.ffmpeg.find_ffmpeg", lambda: "ffmpeg")

    class Stop(BaseException):
        pass

    def fake_run(cmd, **_kwargs):
        Path(cmd[-1]).write_bytes(b"torn")
        raise Stop

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", fake_run)
    with pytest.raises(Stop):
        run_ffmpeg(["-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"keep"
    assert list(tmp_path.glob("out.*.partial.wav")) == []
    print("EVIDENCE concept=interruption dest-unchanged=true partial-absent=true")


def test_empty_staged_output_is_not_published(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "out.wav"
    dest.write_bytes(b"keep")
    monkeypatch.setattr("ai_engine.core.ffmpeg.find_ffmpeg", lambda: "ffmpeg")

    class Proc:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **_kwargs):
        Path(cmd[-1]).write_bytes(b"")
        return Proc()

    monkeypatch.setattr("ai_engine.core.ffmpeg.subprocess.run", fake_run)
    with pytest.raises(RuntimeError, match="validation"):
        run_ffmpeg(["-i", "in.mp4", str(dest)], overwrite=True)
    assert dest.read_bytes() == b"keep"
    assert list(tmp_path.glob("out.*.partial.wav")) == []
    print("EVIDENCE concept=validate-before-replace dest-unchanged=true partial-absent=true")
