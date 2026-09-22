"""S-011 — loop tooling is executable, never silently OK.

Negative ledger cases use temp files (the committed ledger stays green).
`gate.py --stage all` is invoked as a subprocess. The gate sets CE_INSIDE_GATE
when it spawns pytest, and this module skips that nested call so the unit
stage does not recurse.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "gate.py"
VERIFY = ROOT / "scripts" / "verify_ledger.py"
SMOKE = ROOT / "scripts" / "smoke-gpu.ps1"
HANDOFF = ROOT / "docs" / "loop" / "07_SESSION_HANDOFF.md"
pytestmark = pytest.mark.unit

STAGES = ("static", "unit", "real", "e2e", "perf", "chaos")


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=900,
        check=False,
    )


def _gate(*args: str) -> subprocess.CompletedProcess[str]:
    return _run(GATE, *args)


def _report(proc: subprocess.CompletedProcess[str]) -> dict:
    last = proc.stdout.strip().splitlines()[-1]
    return json.loads(last)


@pytest.fixture(autouse=True)
def _no_nested_gate() -> None:
    if os.environ.get("CE_INSIDE_GATE"):
        pytest.skip("nested gate invocation")


def test_green_without_verified_on_exits_1(tmp_path: Path) -> None:
    steps = tmp_path / "steps.json"
    ledger = tmp_path / "ledger.md"
    steps.write_text(
        json.dumps({"steps": [{"id": "S-001", "deps": [], "user": "none"}]}),
        encoding="utf-8",
    )
    ledger.write_text(
        "| id | title | status | iter | verified_on | evidence | notes |\n"
        "| S-001 | t | GREEN | 1 |  | docs/loop/evidence/S-001 | note |\n",
        encoding="utf-8",
    )
    proc = _run(VERIFY, "--steps", str(steps), "--ledger", str(ledger), "--skip-render-check")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "verified_on" in proc.stdout


def test_missing_step_id_exits_1(tmp_path: Path) -> None:
    steps = tmp_path / "steps.json"
    ledger = tmp_path / "ledger.md"
    steps.write_text(
        json.dumps(
            {
                "steps": [
                    {"id": "S-001", "deps": [], "user": "none"},
                    {"id": "S-002", "deps": ["S-001"], "user": "none"},
                ]
            }
        ),
        encoding="utf-8",
    )
    ledger.write_text(
        "| id | title | status | iter | verified_on | evidence | notes |\n" "| S-001 | t | TODO | 0 |  |  |  |\n",
        encoding="utf-8",
    )
    proc = _run(VERIFY, "--steps", str(steps), "--ledger", str(ledger), "--skip-render-check")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "S-002" in proc.stdout


def test_stage_all_reports_every_stage() -> None:
    proc = _gate("--stage", "all", "--json", "--skip", "cargo-clippy")
    rep = _report(proc)
    assert rep["stage"] == "all"
    assert rep["checks"], "empty report is silently OK"
    for name in STAGES:
        roll = next(c for c in rep["checks"] if c["name"] == f"stage:{name}")
        assert roll["status"] in {"PASS", "FAIL", "MISSING"}, roll
        assert roll["detail"].strip(), f"{name} has an empty detail"
    # A FAIL anywhere must not be swallowed.
    if any(c["status"] == "FAIL" for c in rep["checks"]):
        assert proc.returncode == 1


def test_unit_stage_runs_pytest_and_names_missing_tools() -> None:
    proc = _gate("--stage", "unit", "--json")
    rep = _report(proc)
    by_name = {c["name"]: c for c in rep["checks"]}
    assert by_name["pytest-unit"]["status"] in {"PASS", "FAIL"}
    assert by_name["pytest-unit"]["status"] == "PASS", by_name["pytest-unit"]["detail"][-800:]
    for missing in ("vitest", "cargo-test"):
        assert by_name[missing]["status"] == "MISSING"
        assert by_name[missing]["detail"].strip()


def test_real_stage_is_not_silent() -> None:
    proc = _gate("--stage", "real", "--json")
    rep = _report(proc)
    chk = next(c for c in rep["checks"] if c["name"] == "pytest-real")
    assert chk["status"] in {"PASS", "FAIL", "MISSING"}
    assert chk["detail"].strip()
    if chk["status"] == "MISSING":
        assert "ModuleNotFoundError" in chk["detail"] or "not installed" in chk["detail"]


def test_future_stages_are_missing_with_owner() -> None:
    proc = _gate("--stage", "all", "--json", "--skip", "cargo-clippy")
    rep = _report(proc)
    owners = {
        "stage:e2e": "S-079",
        "stage:perf": "S-082",
        "stage:chaos": "S-077",
    }
    for name, owner in owners.items():
        roll = next(c for c in rep["checks"] if c["name"] == name)
        assert roll["status"] == "MISSING", roll
        assert owner in roll["detail"]


def test_smoke_gpu_script_contract() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    for key in ("app_launch", "backend_health", "import_ok", "dry_run", "ConvertTo-Json"):
        assert key in text, key
    assert "-DryRun" in text or "DryRun" in text
    # A failed probe must still emit JSON before exiting.
    assert "exit 1" in text or "exit $failures" in text or "exit 1" in text.lower()


def test_handoff_template_present() -> None:
    text = HANDOFF.read_text(encoding="utf-8")
    assert "BATCH BUILDER" in text
    assert "OVERSEER" in text
    assert "Scope Ledger" in text


def test_verify_ledger_default_still_green() -> None:
    proc = _run(VERIFY)
    assert proc.returncode == 0, proc.stdout
    assert "ledger OK" in proc.stdout
