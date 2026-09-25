"""Real tests for S-009 — CI overhaul.

These parse the actual workflow files (PyYAML) and assert the contract in
docs/loop/evidence/S-009/CONTRACT.md. They do not mock anything; a
mis-typed job id or an unpinned action fails here before it fails on GitHub.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"
CI = WF / "ci.yml"
CODEQL = WF / "codeql.yml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
GITLEAKS = ROOT / ".gitleaks.toml"

SHA_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./-]+)?@[0-9a-f]{40}$")


def _load(p: Path) -> dict:
    assert p.exists(), f"{p.relative_to(ROOT)} missing"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{p.name} is not a mapping"
    return data


def _on(data: dict) -> dict:
    # PyYAML parses the bare key `on` as boolean True.
    return data.get("on") or data.get(True) or {}


def _steps(job: dict) -> list[dict]:
    return [s for s in job.get("steps", []) if isinstance(s, dict)]


def _runs(job: dict) -> str:
    return "\n".join(str(s.get("run", "")) for s in _steps(job))


def _uses(job: dict) -> list[str]:
    return [str(s["uses"]) for s in _steps(job) if "uses" in s]


# ── AC-1 ─────────────────────────────────────────────────────────────────────
def test_triggers_and_job_ids():
    ci = _load(CI)
    assert ci.get("name") == "ci", "workflow name must be `ci` so checks read `ci / ubuntu`"
    on = _on(ci)
    push = on.get("push", {}) or {}
    branches = push.get("branches", [])
    assert "main" in branches and "arena/**" in branches, branches
    assert "pull_request" in on
    jobs = ci["jobs"]
    for jid in ("ubuntu", "windows", "loop-audit"):
        assert jid in jobs, f"job `{jid}` missing (branch protection names depend on it)"
    assert jobs["ubuntu"]["runs-on"].startswith("ubuntu")
    assert jobs["windows"]["runs-on"].startswith("windows")
    assert "concurrency" in ci, "cancel superseded runs on the same ref"


# ── AC-2 ─────────────────────────────────────────────────────────────────────
def test_ubuntu_job_steps():
    job = _load(CI)["jobs"]["ubuntu"]
    runs = _runs(job)
    uses = " ".join(_uses(job))
    assert "pnpm/action-setup" in uses
    assert "actions/setup-node" in uses and "cache: pnpm" in yaml.safe_dump(job)
    assert "actions/setup-python" in uses and "cache: pip" in yaml.safe_dump(job)
    assert re.search(r"scripts/gate\.py --stage static.*--json.*--strict-missing", runs), runs
    assert "pytest" in runs and "tests/unit" in runs
    assert re.search(r"pnpm (run )?build", runs)
    assert "playwright install" in runs and "chromium" in runs
    assert "playwright test" in runs
    assert "tests/tracks.spec.ts" in runs
    dump = yaml.safe_dump(job)
    assert "actions/upload-artifact" in uses
    for artefact in ("junit", "playwright-report", "home-1440x900.png"):
        assert artefact in dump, f"artifact `{artefact}` not uploaded"
    assert "if-no-files-found: error" in dump or "if-no-files-found: 'error'" in dump


# ── AC-3 ─────────────────────────────────────────────────────────────────────
def test_windows_job_steps():
    job = _load(CI)["jobs"]["windows"]
    runs = _runs(job)
    uses = " ".join(_uses(job))
    dump = yaml.safe_dump(job)
    assert "python-version: '3.11'" in dump or 'python-version: "3.11"' in dump or "python-version: 3.11" in dump
    assert "requirements.txt" in runs
    assert re.search(r"pytest .*-m ['\"]not gpu['\"]", runs), "GPU tests must be excluded on hosted runners"
    assert "--junitxml" in runs or "--junit-xml" in runs
    assert "dtolnay/rust-toolchain" in uses
    assert "Swatinem/rust-cache" in uses
    assert "cargo fmt" in runs and "--check" in runs
    assert "cargo clippy --locked" in runs and "-D warnings" in runs
    assert "cargo test --locked" in runs
    assert "tauri build --ci --verbose -- --locked" in runs
    assert "src-tauri" in dump
    assert "actions/upload-artifact" in uses
    # S-010: cargo checks are hard (BUG-16 closed) and every push ships an installer.
    for step in _steps(job):
        if "cargo" in str(step.get("run", "")):
            assert not step.get("continue-on-error"), f"cargo step is advisory again: {step.get('name')}"
    assert "tauri build" in runs
    assert "scripts/ci/installer_smoke.ps1" in runs
    assert "scripts/smoke-gpu.ps1 -DryRun" in runs, "S-011: windows must execute the smoke contract"
    assert "scripts/ci/publish_cargo_lock.ps1" in runs
    assert "make_icons.py --check" in runs
    # BUG-17: only this job may write, and only to commit the runner lockfile.
    assert (job.get("permissions") or {}).get("contents") == "write"
    assert "_x64-setup.exe" in dump, "installer artifact must be uploaded"
    order = [str(s.get("name", "")) for s in _steps(job)]
    i_front = next(i for i, n in enumerate(order) if n.startswith("Frontend build"))
    i_clippy = next(i for i, n in enumerate(order) if n.startswith("cargo clippy"))
    i_build = next(i for i, n in enumerate(order) if n.startswith("tauri build"))
    i_smoke = next(i for i, n in enumerate(order) if n.startswith("Installer smoke"))
    assert i_front < i_clippy < i_build < i_smoke, order


# ── AC-4 ─────────────────────────────────────────────────────────────────────
def test_loop_audit_job():
    job = _load(CI)["jobs"]["loop-audit"]
    runs = _runs(job)
    assert "scripts/verify_ledger.py" in runs
    assert "scripts/supervise.py" in runs
    assert "--write" not in runs, "CI must never write supervisor reports"
    assert job["runs-on"].startswith("ubuntu")


# ── AC-5 ─────────────────────────────────────────────────────────────────────
def test_gitleaks_wired():
    job = _load(CI)["jobs"]["ubuntu"]
    assert any(u.startswith("gitleaks/gitleaks-action@") for u in _uses(job))
    dump = yaml.safe_dump(job)
    assert "fetch-depth: 0" in dump, "gitleaks needs full history"
    assert GITLEAKS.exists()
    toml = GITLEAKS.read_text(encoding="utf-8")
    assert "sk-or-v1-" in toml, "OpenRouter key rule missing"
    assert "nvapi-" in toml, "Nvidia NIM key rule missing"
    assert "sk-or-v1-TEST" in toml, "test probe pattern must be allow-listed"
    assert "[allowlist]" in toml or "[[rules]]" in toml


# ── AC-6 ─────────────────────────────────────────────────────────────────────
def test_codeql_and_dependabot():
    cq = _load(CODEQL)
    on = _on(cq)
    assert "push" in on and "pull_request" in on and "schedule" in on
    dump = yaml.safe_dump(cq)
    assert "python" in dump and "javascript-typescript" in dump
    assert "github/codeql-action" in dump
    assert "security-events: write" in dump

    db = _load(DEPENDABOT)
    assert db.get("version") == 2
    ecosystems = {(u["package-ecosystem"], u["directory"]) for u in db["updates"]}
    assert ("pip", "/ai-engine") in ecosystems
    assert ("npm", "/") in ecosystems
    assert ("cargo", "/apps/desktop/src-tauri") in ecosystems
    assert ("github-actions", "/") in ecosystems
    for u in db["updates"]:
        assert u["schedule"]["interval"] == "weekly", u
        assert "groups" in u, f"{u['package-ecosystem']}: group minor/patch to keep PR noise low"


# ── AC-7 ─────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("wf", sorted(WF.glob("*.yml")), ids=lambda p: p.name)
def test_actions_pinned_by_sha_and_permissions(wf: Path):
    data = _load(wf)
    text = wf.read_text(encoding="utf-8")
    perms = data.get("permissions")
    assert perms is not None, f"{wf.name}: top-level `permissions:` missing"
    assert perms.get("contents") == "read", f"{wf.name}: top-level contents must be read-only"
    for jid, job in data["jobs"].items():
        for u in _uses(job):
            if u.startswith("./"):
                continue
            assert SHA_RE.match(u), f"{wf.name}/{jid}: `{u}` is not pinned to a 40-char commit SHA"
            # human-readable version comment must sit on the same line
            line = next(ln for ln in text.splitlines() if u in ln)
            assert re.search(r"#\s*v?\d", line), f"{wf.name}/{jid}: `{u}` lacks a `# vX` comment"


# ── AC-8 ─────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("wf", sorted(WF.glob("*.yml")), ids=lambda p: p.name)
def test_referenced_paths_exist(wf: Path):
    data = _load(wf)
    for jid, job in data["jobs"].items():
        for step in _steps(job):
            base = ROOT / str(step.get("working-directory", "."))
            for m in re.finditer(
                r"(?<![\w/.-])((?:scripts|tests|apps|ai-engine|docs)/[\w./-]+)", str(step.get("run", ""))
            ):
                path = m.group(1).rstrip(".,;:)")
                if "*" in path or "$" in path or "/.venv/" in path or "/reports/" in path:
                    continue  # created during the run
                if (
                    path.endswith(("/out", "/out/", "playwright-report", ".xml", ".png", ".json", ".log"))
                    and not (base / path).exists()
                ):
                    continue  # build outputs are produced during the run
                assert (base / path).exists(), f"{wf.name}/{jid}: `{path}` (cwd {base.relative_to(ROOT)}) not in tree"


# ── AC-9 (round 3): annotations must be well-formed workflow commands ─────────
def test_junit_annotate_emits_valid_workflow_commands(tmp_path: Path):
    """CI run #2 printed `::error,title=…` (leading comma) — GitHub silently dropped
    every annotation. Lock the exact `::error file=…,line=…,title=…::msg` grammar."""
    import subprocess  # noqa: PLC0415
    import sys  # noqa: PLC0415

    junit = tmp_path / "j.xml"
    junit.write_text(
        '<testsuites><testsuite name="s">'
        '<testcase classname="styling.spec.ts" name="body, bg::x"><failure message="m">d</failure></testcase>'
        '<testcase classname="t.py" name="ok" file="tests/unit/t.py" line="7"><error message="e">b</error></testcase>'
        '<testcase classname="a" name="pass"/>'
        "</testsuite></testsuites>",
        encoding="utf-8",
    )
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "junit_annotate.py"), str(junit)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    errors = [ln for ln in out if ln.startswith("::error")]
    assert len(errors) == 2, out
    cmd = re.compile(r"^::error (?:file=[^,]+,(?:line=\d+,)?)?title=[^,:]+(?: › [^,:]+)*::.+$")
    for ln in errors:
        assert cmd.match(ln), f"malformed workflow command: {ln}"
    assert "file=tests/unit/t.py,line=7," in errors[1]
    assert any(ln.startswith("::notice title=junit summary::2 failed / 3 total") for ln in out), out
