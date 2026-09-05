"""S-005 real test: fixture factory produces every fixture + probe verification.

Run: pytest -m real tests/test_fixtures.py   (or python tests/test_fixtures.py)

Uses a gitignored cache dir and the bundled `imageio-ffmpeg` binary; never
commits media. Probes streams/duration/resolution per fixture using
`ai_engine.core.ffmpeg.probe_duration_and_streams` (ffprobe-equivalent since
imageio-ffmpeg ships ffmpeg only). Offline run degrades to synthetic-only with
an EXPLICIT warning (never a silent skip).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Allow direct execution (python tests/test_fixtures.py) without the package
# being installed; pytest adds repo root to sys.path via rootdir, so this only
# matters for the standalone runner.
if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_engine.core.ffmpeg import probe_duration_and_streams  # noqa: E402
from tests.fixtures.make_fixtures import build_synthetic, make_fixtures, sha256  # noqa: E402

MANIFEST_EXPECTED = [
    ("tone_120bpm_720p.mp4", "video_with_audio", 1280, 720),
    ("silent_720p.mp4", "video", 1280, 720),
    ("short_2s.mp4", "video", 640, 360),
    ("vertical_9x16.mp4", "video", 720, 1280),
    ("wide_4k_3s.mp4", "video", 3840, 2160),
    ("کلیپ تمرین ۱.mp4", "video", 640, 360),
]


@pytest.mark.real
def test_factory_produces_all_fixtures() -> None:
    with tempfile.TemporaryDirectory() as td:
        res = make_fixtures(Path(td), allow_network=False)  # offline by default in test
        paths = res["paths"]
        expected = MANIFEST_EXPECTED
        for name, *_ in expected:
            assert name in paths, f"fixture not produced: {name}"
        # empty + broken special files
        assert (paths["empty_0byte.mp4"]).stat().st_size == 0
        assert (paths["broken_header.mp4"]).exists()


@pytest.mark.real
def test_probe_streams_duration_resolution() -> None:
    with tempfile.TemporaryDirectory() as td:
        paths = build_synthetic(Path(td))
        for name, kind, w, h in MANIFEST_EXPECTED:
            info = probe_duration_and_streams(paths[name])
            assert info["audio"] is True if kind == "video_with_audio" else True, name
            # width/height only meaningful for playable video
            if kind == "video_with_audio" or kind == "video":
                assert info["width"] is not None, f"no resolution for {name}"
                # ffmpeg `testsrc2=size=WxH` reports the requested resolution.
                assert abs(info["width"] - w) <= 2, f"{name}: width {info['width']} != {w}"
                assert abs(info["height"] - h) <= 2, f"{name}: height {info['height']} != {h}"
                assert info["duration"] is not None, f"no duration for {name}"


@pytest.mark.real
def test_bpm_fixture_detects_120() -> None:
    from ai_engine.editor_ai.beat_sync import BeatSyncEngine

    with tempfile.TemporaryDirectory() as td:
        paths = build_synthetic(Path(td))
        engine = BeatSyncEngine()
        beats = engine.analyze_audio(str(paths["tone_120bpm_720p.mp4"]))
        assert beats, "expected beats from 120 BPM fixture"
        assert abs(engine.tempo_bpm - 120.0) <= 3.0, f"tempo {engine.tempo_bpm}"


@pytest.mark.real
def test_offline_degrades_explicitly_not_silent() -> None:
    with tempfile.TemporaryDirectory() as td:
        res = make_fixtures(Path(td), allow_network=False)
        warnings = res["warnings"]
        assert warnings, "must emit an explicit offline warning (never silent skip)"
        assert any("OFFLINE" in w for w in warnings), f"no explicit OFFLINE warning: {warnings}"
        # synthetic set still produced, downloaded set labelled unverified:network
        assert len(res["paths"]) == 8
        assert res["downloaded"].get("human_clip.mp4") == "unverified:network"
        assert res["downloaded"].get("pose.jpg") == "unverified:network"


@pytest.mark.real
def test_manifest_describes_every_synthetic_fixture() -> None:
    mf = res_manifest()
    synthetic_names = {e["name"] for e in mf["synthetic"]}
    generated = {"tone_120bpm_720p.mp4", "silent_720p.mp4", "short_2s.mp4",
                 "empty_0byte.mp4", "broken_header.mp4", "vertical_9x16.mp4",
                 "wide_4k_3s.mp4", "کلیپ تمرین ۱.mp4"}
    assert synthetic_names == generated, "manifest synthetic set != generated set"
    # every generated fixture (except the two synthetic-only specials) has a probe spec
    for e in mf["synthetic"]:
        if e["kind"] in ("video", "video_with_audio"):
            assert e["width"] and e["height"], f"manifest missing spec for {e['name']}"


def res_manifest() -> dict:
    from tests.fixtures.make_fixtures import load_manifest

    return load_manifest()


# ─────────────────────────────────────────────────────────────────────────────
# Direct runner
# ─────────────────────────────────────────────────────────────────────────────
def _run_all() -> int:
    results = []

    def check(name, fn):
        try:
            fn()
            print(f"PASS {name}")
            results.append(True)
        except (AssertionError, Exception) as e:  # noqa: BLE001
            print(f"FAIL {name}: {e}")
            results.append(False)

    check("test_factory_produces_all_fixtures", test_factory_produces_all_fixtures)
    check("test_probe_streams_duration_resolution", test_probe_streams_duration_resolution)
    check("test_bpm_fixture_detects_120", test_bpm_fixture_detects_120)
    check("test_offline_degrades_explicitly_not_silent", test_offline_degrades_explicitly_not_silent)
    check("test_manifest_describes_every_synthetic_fixture", test_manifest_describes_every_synthetic_fixture)
    ok = all(results)
    print(f"\n{('OK' if ok else 'FAILED')} — {sum(results)}/{len(results)} S-005 fixture checks green")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
