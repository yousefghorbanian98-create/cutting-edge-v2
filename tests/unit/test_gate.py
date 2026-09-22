"""S-008 real tests for the static gate (`scripts/gate.py`).

These run the actual gate against the actual tree. They are `unit`-marked
because they need no media/server, but they are not mocked: `gate.py` really
executes ruff / biome / tsc / turbo / bandit / pip-audit when present.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "gate.py"
pytestmark = pytest.mark.unit


def _run_gate(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    e = os.environ.copy()
    e.update(env or {})
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=e,
        timeout=900,
        check=False,
    )


def _report(proc: subprocess.CompletedProcess[str]) -> dict:
    """gate.py prints a JSON report as its last line when --json is given."""
    last = proc.stdout.strip().splitlines()[-1]
    return json.loads(last)


# ── AC-1 ──────────────────────────────────────────────────────────────────────
def test_static_stage_green_on_clean_tree() -> None:
    # cargo-clippy is exercised separately (test_cargo_clippy_green, BUG-16 until S-010):
    # GitHub runners ship cargo, the sandbox does not, and the crate cannot compile yet.
    proc = _run_gate("--stage", "static", "--json", "--skip", "cargo-clippy")
    rep = _report(proc)
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-1000:]
    assert rep["stage"] == "static"
    assert rep["fail"] == 0
    # Skip ≠ Pass: missing tools must be reported explicitly, never counted as pass.
    for chk in rep["checks"]:
        assert chk["status"] in {"PASS", "FAIL", "MISSING", "SKIP"}
    assert any(c["status"] == "PASS" for c in rep["checks"])


# ── AC-2 ──────────────────────────────────────────────────────────────────────
def test_staged_secret_fails_static(tmp_path: Path) -> None:
    probe = ROOT / ".gate-secret-probe.py"
    assert not probe.exists()
    # Assemble the fake key at runtime so no tracked file ever contains a string
    # matching the OpenRouter pattern (gitleaks / supervise C10 / gate secrets).
    fake_key = "sk-or-" + "v1-TEST" + "0" * 58
    probe.write_text(f'OPENROUTER_API_KEY = "{fake_key}"\n')
    try:
        subprocess.run(["git", "add", "-N", str(probe)], cwd=ROOT, check=True, capture_output=True)
        proc = _run_gate("--stage", "static", "--only", "secrets", "--json")
        rep = _report(proc)
    finally:
        subprocess.run(["git", "reset", "-q", "--", str(probe)], cwd=ROOT, check=False, capture_output=True)
        probe.unlink(missing_ok=True)
    assert proc.returncode == 1
    sec = next(c for c in rep["checks"] if c["name"] == "secrets")
    assert sec["status"] == "FAIL"
    assert ".gate-secret-probe.py:1" in sec["detail"]


@pytest.mark.xfail(
    strict=True,
    reason="BUG-16: src-tauri lacks tauri-build/icons/capabilities so clippy cannot compile it; "
    "S-010 (walking skeleton) makes fmt+clippy green and must delete this marker",
)
def test_cargo_clippy_green() -> None:
    # Owned by the `ci / windows` job (Tauri's Linux build needs webkit2gtk system libs
    # that hosted ubuntu runners lack, and the sandbox has no cargo at all).
    if sys.platform != "win32" and not os.environ.get("CE_RUN_CARGO"):
        pytest.skip("cargo-clippy is exercised on the windows CI job (set CE_RUN_CARGO=1 to force)")
    rep = _report(_run_gate("--stage", "static", "--only", "cargo-clippy", "--json"))
    chk = rep["checks"][0]
    if chk["status"] == "MISSING":
        pytest.skip("cargo not installed here — exercised on the windows CI job")
    assert chk["status"] == "PASS", chk["detail"][-1500:]


# ── AC-3 / AC-4 / AC-7 (each tool wired and clean or explicitly missing) ─────
@pytest.mark.parametrize(
    "name",
    ["ruff-lint", "ruff-format", "biome", "tsc", "bandit", "pip-audit", "pnpm-audit", "verify-ledger"],
)
def test_tool_wired(name: str) -> None:
    proc = _run_gate("--stage", "static", "--only", name, "--json")
    rep = _report(proc)
    chk = next(c for c in rep["checks"] if c["name"] == name)
    assert chk["status"] in {"PASS", "MISSING"}, f"{name}: {chk['status']} — {chk['detail'][-800:]}"
    if chk["status"] == "MISSING":
        assert chk["detail"], "MISSING must say which binary/module is absent"


def test_ruff_clean() -> None:
    rep = _report(_run_gate("--stage", "static", "--only", "ruff-lint", "--json"))
    assert rep["checks"][0]["status"] == "PASS", rep["checks"][0]["detail"][-1500:]


def test_biome_and_tsc_clean() -> None:
    rep = _report(_run_gate("--stage", "static", "--only", "biome", "--only", "tsc", "--json"))
    statuses = {c["name"]: c["status"] for c in rep["checks"]}
    assert statuses["biome"] == "PASS", rep
    assert statuses["tsc"] == "PASS", rep


# ── AC-5 ──────────────────────────────────────────────────────────────────────
FLOATING = re.compile(r'"(latest|next|\*|\^[0-9]|~[0-9]|>=?\s*[0-9])')


def _package_jsons() -> list[Path]:
    return [ROOT / "package.json", *ROOT.glob("apps/*/package.json"), *ROOT.glob("packages/*/package.json")]


def test_no_floating_versions() -> None:
    offenders: list[str] = []
    for pj in _package_jsons():
        data = json.loads(pj.read_text(encoding="utf-8"))
        for section in ("dependencies", "devDependencies"):
            for name, spec in data.get(section, {}).items():
                if spec.startswith("workspace:"):
                    continue
                if not re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?", spec):
                    offenders.append(f"{pj.relative_to(ROOT)}: {name}={spec}")
    req = (ROOT / "ai-engine" / "requirements.txt").read_text(encoding="utf-8")
    for line in req.splitlines():
        line = line.split("#", 1)[0].strip()
        if line and "==" not in line:
            offenders.append(f"requirements.txt: {line}")
    assert not offenders, "\n".join(offenders)


def test_turbo2_tasks() -> None:
    turbo = json.loads((ROOT / "turbo.json").read_text(encoding="utf-8"))
    assert "pipeline" not in turbo, "Turbo 1 key `pipeline` must be migrated to `tasks`"
    assert "tasks" in turbo and "build" in turbo["tasks"]
    rep = _report(_run_gate("--stage", "static", "--only", "turbo", "--json"))
    assert rep["checks"][0]["status"] in {"PASS", "MISSING"}, rep


# ── AC-6 ──────────────────────────────────────────────────────────────────────
def test_lefthook_config() -> None:
    text = (ROOT / "lefthook.yml").read_text(encoding="utf-8")
    assert "pre-commit:" in text and "gate.py --stage static --staged" in text
    assert "commit-msg:" in text and "S-\\d{3}" in text or "S-[0-9]{3}" in text


def test_commit_msg_rule() -> None:
    ok = _run_gate("--commit-msg-check", "feat(tooling): S-008 gate")
    assert ok.returncode == 0
    ok2 = _run_gate("--commit-msg-check", "docs(loop): record session")
    assert ok2.returncode == 0
    bad = _run_gate("--commit-msg-check", "wip stuff")
    assert bad.returncode == 1


# ── AC-7 ──────────────────────────────────────────────────────────────────────
def test_security_tools_wired() -> None:
    rep = _report(
        _run_gate("--stage", "static", "--only", "bandit", "--only", "pip-audit", "--only", "pnpm-audit", "--json")
    )
    names = {c["name"] for c in rep["checks"]}
    assert {"bandit", "pip-audit", "pnpm-audit"} <= names
    assert rep["fail"] == 0, rep
