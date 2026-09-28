"""Evidence notices must name a result. A count or a dry-run is not a pass."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(script: str, args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / script), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_manifest_prints_sha256_and_names_a_missing_file(tmp_path: Path) -> None:
    present = tmp_path / "junit.xml"
    present.write_text("<ok/>", encoding="utf-8")
    out = tmp_path / "evidence-manifest.txt"
    proc = _run(
        "evidence_manifest.py",
        ["--out", str(out), "--require", str(present), "--require", str(tmp_path / "missing.xml")],
        {"RUNNER_OS": "Linux", "GITHUB_SHA": "abc", "GITHUB_RUN_ID": "9"},
    )
    assert proc.returncode == 1, proc.stderr
    digest = hashlib.sha256(present.read_bytes()).hexdigest()
    assert f"sha256={digest}" in proc.stdout
    assert "missing.xml result=not-produced" in proc.stdout
    text = out.read_text(encoding="utf-8")
    assert "user-gpu=unverified" in text
    assert "official-playback-drift=lt-1/60" in text
    assert "historical-printed-1/30-was-reporting-defect" in text
    assert "playback-drift-assertion=lt-1/60" in text
    assert "S-024=open" in text
    assert "playback-expect-not-rewritten" not in text
    assert "S-026=open" in text
    assert "pixelDiffRatio-is-not-visual-diff" in text
    assert "printed-threshold-1/fps-is-not-official-when-fps-is-not-60" not in text


def test_installer_check_absent_is_not_run(tmp_path: Path) -> None:
    report = tmp_path / "installer-smoke.jsonl"
    report.write_text(json.dumps({"check": "install-exit-0", "ok": True}) + "\n", encoding="utf-8")
    out = tmp_path / "evidence-manifest.txt"
    proc = _run(
        "evidence_manifest.py",
        ["--out", str(out), "--optional", str(report)],
        {"RUNNER_OS": "Windows", "GITHUB_SHA": "abc", "GITHUB_RUN_ID": "9"},
    )
    assert proc.returncode == 0, proc.stdout
    assert "name=install-exit-0 result=passed" in proc.stdout
    assert "name=window-title result=not-run" in proc.stdout
    assert "name=app-still-running result=not-run" in proc.stdout
    assert "name=uninstall-dir-removed result=not-run" in proc.stdout


def test_smoke_gpu_success_is_not_a_gpu_pass() -> None:
    proc = _run(
        "name_steps.py",
        [],
        {
            "RUNNER_OS": "Windows",
            "GITHUB_SHA": "abc",
            "GITHUB_RUN_ID": "9",
            "CE_NOTE_USER_GPU": "unverified",
            "CE_NAMED_STEPS": "smoke-gpu.ps1 dry-run|success\ncargo fmt --check|skipped\n",
        },
    )
    assert proc.returncode == 0, proc.stderr
    assert "name=smoke-gpu.ps1 dry-run result=contract-dry-run user-gpu=unverified" in proc.stdout
    assert "name=cargo fmt --check result=not-run" in proc.stdout
    assert "result=passed" not in proc.stdout


def test_required_gap_missing_from_junit_is_not_run(tmp_path: Path) -> None:
    junit = tmp_path / "j.xml"
    junit.write_text(
        '<testsuites><testsuite name="s"><testcase classname="tests/zoom.spec.ts" name="fit">'
        "<system-out>EVIDENCE scrollWidth=10 clientWidth=10</system-out>"
        "</testcase></testsuite></testsuites>",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "junit_annotate.py"), str(junit)],
        capture_output=True,
        text=True,
        check=True,
        env={
            **os.environ,
            "CE_EVIDENCE_REQUIRE": "zoom.spec.ts,sequence.spec.ts",
            "GITHUB_SHA": "deadbeef",
            "RUNNER_OS": "Linux",
            "GITHUB_RUN_ID": "9",
            "PYTHONUTF8": "1",
        },
    )
    out = proc.stdout
    assert "zoom.spec.ts: 1 passed, 0 failed" in out
    assert "name=fit result=passed" in out
    assert "scrollWidth=10" in out
    assert "sequence.spec.ts: 0 passed, 0 failed result=not-run" in out
    assert "count is not a named pass" in out
    assert "run=36194558289" in out


def test_canonical_sidecar_is_not_circular(tmp_path: Path) -> None:
    present = tmp_path / "junit.xml"
    present.write_text("<ok/>", encoding="utf-8")
    out = tmp_path / "evidence-manifest.txt"
    proc = _run(
        "evidence_manifest.py",
        ["--out", str(out), "--require", str(present), "--job", "unit"],
        {"RUNNER_OS": "Windows", "GITHUB_SHA": "abc", "GITHUB_RUN_ID": "9"},
    )
    assert proc.returncode == 0, proc.stderr
    canonical = out.read_bytes()
    sidecar = out.with_suffix(".sha256").read_text(encoding="utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    assert digest.encode("ascii") not in canonical
    assert canonical.endswith(b"\n") and not canonical.endswith(b"\n\n")
    assert b"\r" not in canonical
    assert sidecar == f"{digest}  {out.as_posix()}\n" or sidecar.startswith(f"{digest}  ")
    assert "circular=false" in canonical.decode("utf-8")
    assert "hash-method=sha256" in proc.stdout
    assert f"sha256={digest}" in proc.stdout
    assert "body=" in proc.stdout
    verify = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ci" / "verify_evidence_manifest.py"),
            "--canonical",
            str(out),
            "--sidecar",
            str(out.with_suffix(".sha256")),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify.returncode == 0, verify.stderr
    assert "result=passed" in verify.stdout


def test_overwrite_concepts_and_extract_measurement_come_from_junit(tmp_path: Path) -> None:
    junit = tmp_path / "j.xml"
    junit.write_text(
        "<testsuites><testsuite name='s'>"
        "<testcase classname='tests.unit.test_export_plan' "
        "name='test_existing_output_without_consent_is_refused'>"
        "<system-out>not evidence</system-out>"
        "</testcase>"
        "<testcase classname='tests.unit.test_ffmpeg_overwrite' "
        "name='test_existing_output_without_consent_is_refused'>"
        "<system-out>EVIDENCE concept=refusal concept=no-overwrite ffmpeg-called=false</system-out>"
        "</testcase>"
        "<testcase classname='tests.unit.test_ffmpeg_overwrite' "
        "name='test_failed_consented_replace_rolls_back'>"
        "<system-out>EVIDENCE concept=explicit-consent concept=rollback dest-unchanged=true</system-out>"
        "</testcase>"
        "<testcase classname='tests.unit.test_ffmpeg_overwrite' "
        "name='test_consented_replace_publishes_only_after_success'>"
        "<system-out>EVIDENCE concept=explicit-consent concept=staging partial-name=out.partial.wav</system-out>"
        "</testcase>"
        "<testcase classname='tests.test_beat_sync' name='test_ffmpeg_extract_aac'>"
        "<system-out>EVIDENCE measured-rate=22050 measured-channels=1 measured-frames=9</system-out>"
        "</testcase>"
        "</testsuite></testsuites>",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "junit_annotate.py"), str(junit)],
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "CE_EVIDENCE_REQUIRE": (
                "tests.unit.test_ffmpeg_overwrite::test_existing_output_without_consent_is_refused,"
                "refusal,no-overwrite,explicit-consent,staging,rollback,"
                "test_ffmpeg_extract_aac,sequence.spec.ts"
            ),
            "GITHUB_SHA": "abc",
            "RUNNER_OS": "Windows",
            "GITHUB_RUN_ID": "9",
            "PYTHONUTF8": "1",
        },
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert (
        "tests.unit.test_ffmpeg_overwrite::test_existing_output_without_consent_is_refused: 1 passed, 0 failed" in out
    )
    assert "test_export_plan" not in out
    assert "refusal: 1 passed, 0 failed" in out
    assert "no-overwrite: 1 passed, 0 failed" in out
    assert "explicit-consent: 2 passed, 0 failed" in out
    assert "staging: 1 passed, 0 failed" in out
    assert "rollback: 1 passed, 0 failed" in out
    assert "measured-rate=22050" in out
    assert "measured-channels=1" in out
    assert "measured-frames=9" in out
    assert "expected=wav=22050 channels=1" in out
    assert "measured=not-in-junit wav=22050" not in out
    assert "sequence.spec.ts: 0 passed, 0 failed result=not-run" in out


def test_playback_annotation_names_official_drift_not_one_over_fps(tmp_path: Path) -> None:
    spec = (ROOT / "apps/desktop/tests/playback.spec.ts").read_text(encoding="utf-8")
    assert "official-threshold=<1/60" in spec
    assert "assertion-bound=<1/60" in spec
    assert "STRICT_PLAYHEAD_FPS" in spec
    assert "const STRICT_PLAYHEAD_FPS" not in spec
    assert "threshold=${1 / fixture.fps}" not in spec
    assert "toBeLessThan(1 / fixture.fps)" not in spec
    assert "toBeLessThan(1 / STRICT_PLAYHEAD_FPS)" in spec
    assert "toBeLessThan(0.001)" in spec
    assert "arrow-interval=file-fps" in spec
    assert "test.skip" not in spec
    junit = tmp_path / "j.xml"
    junit.write_text(
        "<testsuites><testsuite name='s'>"
        "<testcase classname='playback.spec.ts' name='playhead'>"
        "<system-out>EVIDENCE drift=live official-threshold=&lt;1/60</system-out>"
        "</testcase></testsuite></testsuites>",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "junit_annotate.py"), str(junit)],
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "CE_EVIDENCE_REQUIRE": "playback.spec.ts",
            "GITHUB_SHA": "abc",
            "RUNNER_OS": "Linux",
            "GITHUB_RUN_ID": "9",
            "PYTHONUTF8": "1",
        },
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "expected=official-drift<1/60" in out
    assert "assertion-bound=<1/60" in out
    assert "historical-printed-1/30-was-reporting-defect" in out
    assert "measured-values-not-rewritten" in out
    assert "expect-not-rewritten" not in out
    assert "drift<1/fps" not in out
    assert "threshold=0.03333333333333333" not in out


def test_s026_annotation_names_visual_diff_not_byte_ratio(tmp_path: Path) -> None:
    spec = (ROOT / "apps/desktop/e2e/timeline.spec.ts").read_text(encoding="utf-8")
    assert "visualDiffRatio" in spec
    assert "pixelDiffRatio(" not in spec
    assert "pixelDiffRatio-is-not-this-metric=true" in spec
    assert "toBeLessThan(0.001)" in spec
    assert "test.skip" not in spec
    junit = tmp_path / "j.xml"
    junit.write_text(
        "<testsuites><testsuite name='s'>"
        "<testcase classname='e2e/timeline.spec.ts' name='journey'>"
        "<system-out>EVIDENCE metric=visual-diff threshold=0.001 undo-visual-diff=0 split-visual-diff=0"
        "</system-out></testcase></testsuite></testsuites>",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "junit_annotate.py"), str(junit)],
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "CE_EVIDENCE_REQUIRE": "e2e/timeline.spec.ts",
            "GITHUB_SHA": "abc",
            "RUNNER_OS": "Linux",
            "GITHUB_RUN_ID": "9",
            "PYTHONUTF8": "1",
        },
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "expected=visual-diff<0.001" in out
    assert "pixelDiffRatio-is-not-visual-diff" in out
    assert "ssim-is-not-visual-diff" in out
    assert "visual-ratio<0.001" not in out


def test_visual_diff_names_are_not_a_count(tmp_path: Path) -> None:
    junit = tmp_path / "j.xml"
    junit.write_text(
        "<testsuites><testsuite name='s'>"
        "<testcase classname='tests/pngDiff.test.ts' "
        "name='direct visual diff &gt; visual-diff one changed pixel among 1000 fails lt 0.001'>"
        "<system-out>EVIDENCE metric=visual-diff fixture=synthetic-rgba-40x25 "
        "baseline=one-channel-of-one-pixel measured=0.001 threshold=&lt;0.001 "
        "condition-result=failed</system-out></testcase>"
        "<testcase classname='tests/pngDiff.test.ts' "
        "name='direct visual diff &gt; visual-diff identical images is 0'>"
        "<system-out>EVIDENCE metric=visual-diff measured=0 condition-result=passed</system-out>"
        "</testcase></testsuite></testsuites>",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "junit_annotate.py"), str(junit)],
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "CE_EVIDENCE_REQUIRE": (
                "visual-diff one changed pixel among 1000 fails lt 0.001,"
                "visual-diff identical images is 0,"
                "visual-diff alpha-only change"
            ),
            "GITHUB_SHA": "abc",
            "RUNNER_OS": "Linux",
            "GITHUB_RUN_ID": "9",
            "PYTHONUTF8": "1",
        },
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "visual-diff one changed pixel among 1000 fails lt 0.001: 1 passed, 0 failed" in out
    assert "measured=0.001" in out
    assert "condition-result=failed" in out
    assert "junit-pass-is-not-threshold-pass" in out
    assert "visual-diff identical images is 0: 1 passed, 0 failed" in out
    assert "measured=0" in out
    assert "visual-diff alpha-only change: 0 passed, 0 failed result=not-run" in out
    assert "0 failed / 2 total" in out
    assert "count is not a named pass" in out
