"""S-028 / S-032 plan rules. No network and no raw command."""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-engine"))

from ai_engine.export.compiler import PlanRejected, compile_plan  # noqa: E402
from ai_engine.export.runner import CapabilityError, OverwriteRefused, choose_encoder, resolve_encoder  # noqa: E402

pytestmark = pytest.mark.unit


def _request(tmp: Path, **settings: object) -> dict:
    (tmp / "a.mp4").write_bytes(b"not-a-real-file")
    body = {
        "clips": [
            {
                "id": "a",
                "name": "a.mp4",
                "kind": "video",
                "start_ms": 0,
                "duration_ms": 1000,
                "in_ms": 0,
            }
        ],
        "settings": {
            "width": 320,
            "height": 180,
            "fps": 30,
            "codec": "h264",
            "output_name": "out.mp4",
            "overwrite": False,
        },
    }
    body["settings"].update(settings)
    return body


def test_raw_command_and_escape_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(PlanRejected):
        compile_plan({"raw_command": "ffmpeg -i x", "settings": {}, "clips": []}, tmp_path)
    with pytest.raises(PlanRejected):
        compile_plan(_request(tmp_path, output_name="../out.mp4"), tmp_path)
    with pytest.raises(PlanRejected):
        compile_plan(_request(tmp_path, output_name="..\\out.mp4"), tmp_path)


def test_compile_does_not_open_a_socket(tmp_path: Path) -> None:
    def _blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("export compile opened a socket")

    original = socket.create_connection
    socket.create_connection = _blocked  # type: ignore[assignment]
    try:
        plan = compile_plan(_request(tmp_path), tmp_path)
    finally:
        socket.create_connection = original
    assert plan["graph"].startswith("[0:v]trim")
    assert "filter_graph" not in plan


def test_nvenc_capability_is_not_a_pass_when_missing() -> None:
    encoder, state = choose_encoder("h264", ["libx264", "aac"])
    assert encoder == "libx264"
    assert state == "missing"
    encoder, state = choose_encoder("h264", ["h264_nvenc", "libx264"])
    assert encoder == "h264_nvenc"
    assert state == "available"
    with pytest.raises(CapabilityError) as unknown:
        choose_encoder("h264", None)
    assert unknown.value.state == "unknown"
    with pytest.raises(CapabilityError) as missing:
        choose_encoder("h264", ["aac"])
    assert missing.value.state == "missing"


def test_listed_nvenc_that_cannot_open_is_not_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ai_engine.export.runner.encoder_opens", lambda _ffmpeg, _encoder: False)
    encoder, state = resolve_encoder("ffmpeg", "h264", ["h264_nvenc", "libx264"], probe=True)
    assert encoder == "libx264"
    assert state == "missing"


def test_existing_output_without_consent_is_refused(tmp_path: Path) -> None:
    plan = compile_plan(_request(tmp_path), tmp_path)
    target = tmp_path / "out.mp4"
    target.write_bytes(b"keep")
    from ai_engine.export.runner import run_export

    with pytest.raises(OverwriteRefused):
        run_export(plan, tmp_path, encoders=["libx264"], filters={"trim", "scale", "pad", "fps", "concat"})
    assert target.read_bytes() == b"keep"
