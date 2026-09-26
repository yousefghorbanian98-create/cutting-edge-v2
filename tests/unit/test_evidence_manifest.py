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
    assert "user-gpu=unverified" in out.read_text(encoding="utf-8")


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
