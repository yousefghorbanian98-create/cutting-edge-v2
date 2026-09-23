#!/usr/bin/env python3
"""Cutting Edge v2 — quality gate runner (S-008: `static`; other stages S-011).

Usage:
    python scripts/gate.py --stage static [--staged] [--only <check>]... [--json]
    python scripts/gate.py --stage all [--json]
    python scripts/gate.py --commit-msg-check "<subject>"
    python scripts/gate.py --list

Principles (02_LOOP_PROTOCOL.md §1-④/⑤):
  * Every check ends in exactly one of PASS / FAIL / MISSING / SKIP.
  * A tool that is not installed is MISSING, never PASS (Skip ≠ Pass). MISSING does
    not fail the gate locally, but CI (S-009) installs every tool so MISSING there
    is treated as FAIL via --strict-missing.
  * `--json` prints a machine-readable report as the LAST stdout line so tests and
    the supervisor can parse it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / "ai-engine"
DESKTOP = ROOT / "apps" / "desktop"
IS_WIN = os.name == "nt"

# ── secrets ───────────────────────────────────────────────────────────────────
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("openrouter", re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}")),
    ("openai", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("nvidia-nim", re.compile(r"\bnvapi-[A-Za-z0-9_-]{20,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("aws", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("env-assignment", re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][^'\"\s]{16,}['\"]")),
]
SECRET_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    ".next",
    "out",
    "target",
    "__pycache__",
    ".turbo",
    ".cache",
}
SECRET_SKIP_FILES = {"pnpm-lock.yaml", "package-lock.json", "Cargo.lock"}
SECRET_ALLOW_PATH_PARTS = ("scripts/gate.py",)  # only the pattern definitions themselves

COMMIT_RE = re.compile(
    r"^(feat|fix|test|chore|docs|refactor|perf|build|ci|style|review|supervisor|merge)(\([a-z0-9._/-]+\))?!?: .+"
)
STEP_ID = re.compile(r"\bS-\d{3}\b")
NO_STEP_PREFIXES = ("docs", "chore", "merge", "review", "supervisor", "ci", "build")


@dataclass
class Check:
    name: str
    status: str = "SKIP"
    detail: str = ""
    seconds: float = 0.0


@dataclass
class Report:
    stage: str
    checks: list[Check] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        c = {"pass": 0, "fail": 0, "missing": 0, "skip": 0}
        for ch in self.checks:
            c[ch.status.lower()] += 1
        return c

    def to_json(self) -> str:
        return json.dumps(
            {"stage": self.stage, **self.counts, "checks": [asdict(c) for c in self.checks]}, ensure_ascii=False
        )


# ── helpers ───────────────────────────────────────────────────────────────────
def _venv_bin(name: str) -> str | None:
    """Prefer the ai-engine venv tool, then PATH."""
    cand = AI / ".venv" / ("Scripts" if IS_WIN else "bin") / (f"{name}.exe" if IS_WIN else name)
    if cand.exists():
        return str(cand)
    return shutil.which(name)


def _npx() -> list[str]:
    return ["npx.cmd" if IS_WIN else "npx", "--yes", "--prefer-offline"]


def _run(cmd: list[str], cwd: Path = ROOT, timeout: int = 600, env: dict[str, str] | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            env=env,
        )  # explicit UTF-8: Windows runners default to cp1252 and the tools print Persian/emoji
        return p.returncode, (p.stdout + p.stderr)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s: {' '.join(cmd)}"


def _staged_files() -> list[Path]:
    rc, out = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    if rc != 0:
        return []
    return [ROOT / line.strip() for line in out.splitlines() if line.strip()]


def _tracked_and_intended() -> list[Path]:
    rc, out = _run(["git", "ls-files", "--cached", "--others", "--exclude-standard"])
    files = [ROOT / line.strip() for line in out.splitlines() if line.strip()] if rc == 0 else []
    return files


# ── checks ────────────────────────────────────────────────────────────────────
def check_secrets(staged: bool) -> Check:
    files = _staged_files() if staged else _tracked_and_intended()
    hits: list[str] = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        if any(part in SECRET_SKIP_DIRS for part in f.parts) or f.name in SECRET_SKIP_FILES:
            continue
        if any(rel.startswith(p) or p in rel for p in SECRET_ALLOW_PATH_PARTS):
            continue
        if not f.is_file() or f.stat().st_size > 2_000_000:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for ln, line in enumerate(text.splitlines(), 1):
            for label, pat in SECRET_PATTERNS:
                if pat.search(line):
                    hits.append(f"{rel}:{ln} [{label}]")
                    break
    gl = shutil.which("gitleaks")
    extra = ""
    if gl:
        rc, out = _run([gl, "protect" if staged else "detect", "--no-banner", "--redact", "-v"], timeout=300)
        if rc != 0:
            hits.append("gitleaks: " + out.strip()[-600:])
        extra = " (+gitleaks)"
    if hits:
        return Check("secrets", "FAIL", "\n".join(hits))
    return Check("secrets", "PASS", f"{len(files)} files scanned{extra}")


def check_ruff(kind: str, staged: bool) -> Check:
    ruff = _venv_bin("ruff")
    name = f"ruff-{kind}"
    if not ruff:
        return Check(name, "MISSING", "ruff not found (pip install ruff==0.8.4 into ai-engine/.venv)")
    targets = ["ai-engine/src", "tests", "scripts"]
    if staged:
        py = [str(p.relative_to(ROOT)) for p in _staged_files() if p.suffix == ".py" and p.exists()]
        if not py:
            return Check(name, "SKIP", "no staged .py files")
        targets = py
    cmd = [ruff, "check", *targets] if kind == "lint" else [ruff, "format", "--check", *targets]
    rc, out = _run(cmd)
    return Check(name, "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def check_biome(staged: bool) -> Check:
    targets = ["apps/desktop/src", "apps/desktop/tests", "packages", "scripts"]
    if staged:
        roots = tuple((ROOT / t).resolve() for t in targets)
        js = [
            str(p.relative_to(ROOT))
            for p in _staged_files()
            if p.suffix in {".ts", ".tsx", ".js", ".mjs", ".json"}
            and p.exists()
            and "node_modules" not in p.parts
            and any(p.resolve().is_relative_to(r) for r in roots)  # same scope as the full gate
        ]
        if not js:
            return Check("biome", "SKIP", "no staged TS/JS files")
        targets = js
    biome_local = ROOT / "node_modules" / ".bin" / ("biome.cmd" if IS_WIN else "biome")
    cmd = [str(biome_local)] if biome_local.exists() else [*_npx(), "@biomejs/biome@1.9.4"]
    rc, out = _run([*cmd, "ci", "--colors=off", *targets], timeout=600)
    if rc == 127 or "could not determine executable" in out:
        return Check("biome", "MISSING", out.strip()[-500:])
    return Check("biome", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def check_tsc() -> Check:
    tsc_local = DESKTOP / "node_modules" / ".bin" / ("tsc.cmd" if IS_WIN else "tsc")
    if not tsc_local.exists():
        return Check("tsc", "MISSING", "apps/desktop/node_modules missing — run pnpm install")
    rc, out = _run([str(tsc_local), "--noEmit", "-p", "tsconfig.json"], cwd=DESKTOP, timeout=600)
    return Check("tsc", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def check_turbo() -> Check:
    turbo_local = ROOT / "node_modules" / ".bin" / ("turbo.cmd" if IS_WIN else "turbo")
    cmd = [str(turbo_local)] if turbo_local.exists() else [*_npx(), "turbo@2.11.2"]
    rc, out = _run([*cmd, "run", "build", "--dry=json"], timeout=600)
    if rc == 127:
        return Check("turbo", "MISSING", out[-500:])
    ver = ""
    if "{" in out:
        try:  # stdout carries the JSON document; stderr ("• turbo 2.x") may be appended after it
            data, _end = json.JSONDecoder().raw_decode(out[out.index("{") :])
            ver = str(data.get("turboVersion", ""))
        except (ValueError, json.JSONDecodeError, AttributeError):
            ver = ""
    ok = rc == 0 and ver.startswith("2.")
    detail = f"turboVersion={ver or '?'}"
    if not ok:
        detail += "\n" + out.strip()[-1500:]
    return Check("turbo", "PASS" if ok else "FAIL", detail)


def check_bandit() -> Check:
    b = _venv_bin("bandit")
    if not b:
        return Check("bandit", "MISSING", "bandit not found (pip install bandit==1.8.0 into ai-engine/.venv)")
    rc, out = _run([b, "-r", "ai-engine/src", "-ll", "-q", "-c", "ai-engine/bandit.yaml"])
    return Check("bandit", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def check_pip_audit() -> Check:
    pa = _venv_bin("pip-audit")
    if not pa:
        return Check("pip-audit", "MISSING", "pip-audit not found (pip install pip-audit==2.7.3 into ai-engine/.venv)")
    ignore_file = AI / "pip-audit-ignore.txt"
    ignores: list[str] = []
    for line in ignore_file.read_text(encoding="utf-8").splitlines() if ignore_file.exists() else []:
        line = line.strip()
        if line and not line.startswith("#"):
            ignores += ["--ignore-vuln", line.split()[0]]
    rc, out = _run(
        [pa, "-r", "ai-engine/requirements.txt", "--progress-spinner", "off", "--strict", *ignores], timeout=900
    )
    if ignores:
        out += f"\n({len(ignores)//2} documented exceptions in ai-engine/pip-audit-ignore.txt)"
    if rc != 0 and (
        "Connection" in out or "Temporary failure" in out or "Max retries" in out or "timed out" in out.lower()
    ):
        return Check("pip-audit", "MISSING", "no network to the vulnerability DB:\n" + out.strip()[-600:])
    return Check("pip-audit", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def check_pnpm_audit() -> Check:
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
    if not pnpm:
        return Check("pnpm-audit", "MISSING", "pnpm not found (corepack enable)")
    rc, out = _run([pnpm, "audit", "--audit-level=high", "--prod"], timeout=600)
    if rc != 0 and ("ENOTFOUND" in out or "ECONNREFUSED" in out or "ETIMEDOUT" in out or "fetch failed" in out):
        return Check("pnpm-audit", "MISSING", "no network to the npm advisory DB:\n" + out.strip()[-600:])
    return Check("pnpm-audit", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def _frontend_export_missing(name: str) -> Check | None:
    """generate_context!() embeds frontendDist at compile time.

    Pytest on ci/windows runs before `pnpm build`, so invoking cargo there fails
    the job and skips tauri build, installer smoke, and the .exe artifact.
    Those steps, after the export, are the AC-1 proof. MISSING ≠ PASS.
    """
    if (DESKTOP / "out").is_dir():
        return None
    return Check(
        name,
        "MISSING",
        "apps/desktop/out missing — generate_context! needs the frontend export; "
        "ci/windows cargo fmt/clippy/test run after pnpm build (S-010)",
    )


def check_cargo() -> Check:
    cargo = shutil.which("cargo")
    if not cargo:
        return Check("cargo-clippy", "MISSING", "cargo not found — CI windows job runs fmt/clippy (S-009/S-010)")
    blocked = _frontend_export_missing("cargo-clippy")
    if blocked:
        return blocked
    tauri = DESKTOP / "src-tauri"
    rc1, out1 = _run([cargo, "fmt", "--check"], cwd=tauri)
    if rc1 != 0:
        # S-010: report rustfmt on its own — the clippy compile log would otherwise bury the diff.
        return Check("cargo-clippy", "FAIL", "cargo fmt --check failed:\n" + out1.strip()[-4000:])
    rc2, out2 = _run([cargo, "clippy", "--locked", "--all-targets", "--", "-D", "warnings"], cwd=tauri, timeout=1800)
    return Check("cargo-clippy", "PASS" if rc2 == 0 else "FAIL", ("cargo clippy:\n" + out2.strip())[-4000:])


def check_icons() -> Check:
    script = ROOT / "scripts" / "make_icons.py"
    if not script.exists():
        return Check("icons", "MISSING", "scripts/make_icons.py absent")
    # S-010: committed src-tauri/icons/* must be byte-for-pixel what the generator emits.
    rc, out = _run([sys.executable, str(script), "--check"])
    return Check("icons", "PASS" if rc == 0 else "FAIL", out.strip()[-2000:])


def check_verify_ledger() -> Check:
    rc, out = _run([sys.executable, "scripts/verify_ledger.py"])
    return Check("verify-ledger", "PASS" if rc == 0 else "FAIL", out.strip()[-2000:])


def check_design_tokens() -> Check:
    script = ROOT / "scripts" / "check-design-tokens.js"
    if not script.exists():
        return Check("design-tokens", "MISSING", "scripts/check-design-tokens.js absent")
    if shutil.which("node") is None:
        return Check("design-tokens", "MISSING", "node not on PATH")
    # S-099: real three-way check DESIGN.md ⇄ globals.css @theme ⇄ tokens.ts (exit 2 = parse error).
    rc, out = _run(["node", str(script)])
    return Check("design-tokens", "PASS" if rc == 0 else "FAIL", out.strip()[-2000:])


def check_openapi_client(staged: bool) -> Check:
    """S-012: committed OpenAPI schema + generated TS client must match a fresh run."""
    script = ROOT / "scripts" / "check_openapi_client.py"
    if not script.exists():
        return Check("openapi-client", "MISSING", "scripts/check_openapi_client.py absent")
    py = _venv_bin("python") or _venv_bin("python3") or sys.executable
    rc, out = _run([py, str(script)], timeout=180)
    if rc == 2:
        return Check("openapi-client", "MISSING", out.strip()[-2000:] or "generator or FastAPI missing")
    return Check("openapi-client", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


def check_design_audit() -> Check:
    script = ROOT / "scripts" / "design_audit.py"
    if not script.exists():
        return Check("design-audit", "MISSING", "scripts/design_audit.py absent")
    rc, out = _run([sys.executable, str(script), "apps/desktop/src", "--strict"])
    return Check("design-audit", "PASS" if rc == 0 else "FAIL", out.strip()[-4000:])


STATIC_CHECKS: dict[str, object] = {
    "secrets": lambda staged: check_secrets(staged),
    "ruff-lint": lambda staged: check_ruff("lint", staged),
    "ruff-format": lambda staged: check_ruff("format", staged),
    "biome": lambda staged: check_biome(staged),
    "tsc": lambda staged: check_tsc(),
    "turbo": lambda staged: check_turbo(),
    "bandit": lambda staged: check_bandit(),
    "pip-audit": lambda staged: check_pip_audit(),
    "pnpm-audit": lambda staged: check_pnpm_audit(),
    "cargo-clippy": lambda staged: check_cargo(),
    "verify-ledger": lambda staged: check_verify_ledger(),
    "design-tokens": lambda staged: check_design_tokens(),
    "design-audit": lambda staged: check_design_audit(),
    "icons": lambda staged: check_icons(),
    "openapi-client": lambda staged: check_openapi_client(staged),
}
# checks that are slow/network-bound and irrelevant for a per-commit hook
STAGED_SKIP = {"tsc", "turbo", "pip-audit", "pnpm-audit", "cargo-clippy", "bandit", "icons"}

STAGES = {
    "static": "static analysis, secrets, versions, ledger (S-008)",
    "unit": "vitest + pytest -m unit + cargo test (S-011)",
    "real": "pytest -m real against a live uvicorn (S-011)",
    "e2e": "playwright / tauri-driver (S-079; web e2e already in ci/ubuntu, S-009)",
    "perf": "budgets on GTX 1650 / CI CPU (S-082)",
    "chaos": "reheal probes (S-077)",
    "all": "every stage, each reported PASS/FAIL/MISSING (S-011)",
}
STAGE_ORDER = ("static", "unit", "real", "e2e", "perf", "chaos")
# Stages that are intentionally not a pass until a later step owns them.
STAGE_OWNERS = {
    "e2e": "S-079",
    "perf": "S-082",
    "chaos": "S-077",
}


# ── commit-msg ────────────────────────────────────────────────────────────────
def commit_msg_ok(subject: str) -> tuple[bool, str]:
    subject = subject.strip().splitlines()[0] if subject.strip() else ""
    if not COMMIT_RE.match(subject):
        return False, "subject must be Conventional Commits: type(scope): description"
    if subject.startswith(NO_STEP_PREFIXES):
        return True, "ok (meta commit)"
    if not STEP_ID.search(subject):
        return False, "step commits must carry the step id, e.g. `feat(timeline): S-018 …`"
    return True, "ok"


# ── main ──────────────────────────────────────────────────────────────────────
def _strict(chk: Check, strict_missing: bool) -> Check:
    if strict_missing and chk.status == "MISSING":
        chk.status = "FAIL"
        chk.detail = "[strict-missing] " + chk.detail
    return chk


def _rollup(checks: list[Check]) -> str:
    """PASS only when something actually passed and nothing failed or is missing."""
    statuses = {c.status for c in checks}
    if "FAIL" in statuses:
        return "FAIL"
    if not checks or "MISSING" in statuses or statuses <= {"SKIP"}:
        return "MISSING"
    if "PASS" in statuses and statuses <= {"PASS", "SKIP"}:
        return "PASS"
    return "MISSING"


def _pytest_marker(marker: str, paths: list[str]) -> Check:
    name = f"pytest-{marker}"
    probe, _ = _run([sys.executable, "-c", "import pytest"], timeout=30)
    if probe != 0:
        return Check(name, "MISSING", "pytest is not installed")
    env = os.environ.copy()
    env["CE_INSIDE_GATE"] = "1"  # nested unit tests must not re-enter --stage all
    # tests/unit only: `pytest -m unit` still imports real modules (cv2) at collection.
    rc, out = _run(
        [sys.executable, "-m", "pytest", *paths, "-m", marker, "-q", "-p", "no:cacheprovider", "--tb=line"],
        timeout=900,
        env=env,
    )
    tail = out.strip()[-1500:]
    if rc == 0:
        return Check(name, "PASS", tail or f"pytest -m {marker}")
    if rc == 5:
        return Check(name, "MISSING", f"pytest -m {marker} collected no tests")
    if "FAILED" not in out and ("ModuleNotFoundError" in out or "ImportError" in out):
        missing = "not installed"
        found = re.search(r"No module named '([^']+)'", out)
        if found:
            missing = f"ModuleNotFoundError: {found.group(1)} not installed"
        return Check(name, "MISSING", missing + "\n" + tail)
    return Check(name, "FAIL", tail or f"pytest -m {marker} exit {rc}")


def check_vitest() -> Check:
    pkg_text = ""
    for pkg in (DESKTOP / "package.json", ROOT / "package.json"):
        if pkg.exists():
            pkg_text += pkg.read_text(encoding="utf-8")
    if "vitest" not in pkg_text:
        return Check(
            "vitest",
            "MISSING",
            "vitest is not a dependency and no script runs it; pytest -m unit is the unit runner until a vitest suite lands",
        )
    local = ROOT / "node_modules" / ".bin" / ("vitest.cmd" if IS_WIN else "vitest")
    cmd = [str(local), "run"] if local.exists() else ["pnpm", "exec", "vitest", "run"]
    rc, out = _run(cmd, timeout=600)
    if rc == 127:
        return Check("vitest", "MISSING", out.strip()[-500:] or "vitest binary not found")
    return Check("vitest", "PASS" if rc == 0 else "FAIL", out.strip()[-1500:])


def check_cargo_test() -> Check:
    cargo = shutil.which("cargo")
    if not cargo:
        return Check("cargo-test", "MISSING", "cargo not found — cargo test --locked runs on ci/windows (S-010)")
    blocked = _frontend_export_missing("cargo-test")
    if blocked:
        return blocked
    rc, out = _run([cargo, "test", "--locked", "--all-targets"], cwd=DESKTOP / "src-tauri", timeout=1800)
    return Check("cargo-test", "PASS" if rc == 0 else "FAIL", out.strip()[-1500:])


def check_e2e() -> Check:
    return Check(
        "playwright",
        "MISSING",
        "S-079 owns tauri-driver; web e2e already runs in ci/ubuntu (S-009). gate does not launch browsers",
    )


def check_perf() -> Check:
    return Check("budgets", "MISSING", "S-082 owns performance budgets; none are wired, so this stage is not a pass")


def check_chaos() -> Check:
    return Check("reheal", "MISSING", "S-077 owns chaos probes; none are wired, so this stage is not a pass")


def _run_named(stage: str, staged: bool, only: list[str], skip: list[str]) -> list[Check]:
    import time

    if stage == "static":
        checks: list[Check] = []
        names = only or list(STATIC_CHECKS)
        for name in names:
            if name not in STATIC_CHECKS:
                checks.append(Check(name, "FAIL", f"unknown check; known: {', '.join(STATIC_CHECKS)}"))
                continue
            if staged and name in STAGED_SKIP and not only:
                checks.append(Check(name, "SKIP", "skipped in --staged mode (runs in full gate / CI)"))
                continue
            if name in skip:
                checks.append(Check(name, "SKIP", "skipped by --skip (owned by another CI job)"))
                continue
            t0 = time.monotonic()
            chk = STATIC_CHECKS[name](staged)  # type: ignore[operator]
            chk.seconds = round(time.monotonic() - t0, 2)
            checks.append(chk)
        return checks
    if stage == "unit":
        return [_pytest_marker("unit", ["tests/unit"]), check_vitest(), check_cargo_test()]
    if stage == "real":
        return [_pytest_marker("real", ["tests"])]
    if stage == "e2e":
        return [check_e2e()]
    if stage == "perf":
        return [check_perf()]
    if stage == "chaos":
        return [check_chaos()]
    return [Check(stage, "FAIL", f"unknown stage; known: {', '.join(STAGES)}")]


def run_stage(stage: str, staged: bool, only: list[str], strict_missing: bool, skip: list[str] | None = None) -> Report:
    skip = skip or []
    if stage == "all":
        rep = Report("all")
        for name in STAGE_ORDER:
            children = [
                _strict(c, strict_missing) for c in _run_named(name, staged, only if name == "static" else [], skip)
            ]
            status = _rollup(children)
            bits = ", ".join(f"{c.name}={c.status}" for c in children) or "no checks"
            detail = f"{STAGE_OWNERS[name]} — {bits}" if name in STAGE_OWNERS else bits
            rep.checks.append(Check(f"stage:{name}", status, detail))
            rep.checks.extend(children)
        return rep
    rep = Report(stage)
    rep.checks.extend(_strict(c, strict_missing) for c in _run_named(stage, staged, only, skip))
    return rep


def print_table(rep: Report) -> None:
    icon = {"PASS": "✅", "FAIL": "❌", "MISSING": "⚠️ ", "SKIP": "⏭️ "}
    print(f"gate — stage {rep.stage}")
    for c in rep.checks:
        print(
            f"  {icon[c.status]} {c.status:<7} {c.name:<15} {c.seconds:>6.1f}s  {c.detail.splitlines()[0][:90] if c.detail else ''}"
        )
    for c in rep.checks:
        if c.status == "FAIL" and c.detail:
            print(f"\n--- {c.name} ---\n{c.detail}\n")
    k = rep.counts
    print(f"summary: {k['pass']} pass, {k['fail']} fail, {k['missing']} missing, {k['skip']} skip")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=list(STAGES))
    ap.add_argument("--staged", action="store_true", help="only staged files, fast subset (pre-commit)")
    ap.add_argument("--only", action="append", default=[], help="run only this check (repeatable)")
    ap.add_argument(
        "--skip",
        action="append",
        default=[],
        help="skip this check, reported as SKIP with the reason (repeatable; CI uses it for cargo-clippy on non-Windows)",
    )
    ap.add_argument("--json", action="store_true", help="print JSON report as the last line")
    ap.add_argument("--strict-missing", action="store_true", help="treat MISSING as FAIL (CI)")
    ap.add_argument("--commit-msg-check", metavar="SUBJECT")
    ap.add_argument("--commit-msg-file", metavar="PATH")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list:
        for k, v in STAGES.items():
            print(f"{k:<8} {v}")
        print("static checks:", ", ".join(STATIC_CHECKS))
        return 0
    if a.commit_msg_check is not None or a.commit_msg_file:
        subject = (
            a.commit_msg_check
            if a.commit_msg_check is not None
            else Path(a.commit_msg_file).read_text(encoding="utf-8")
        )
        ok, why = commit_msg_ok(subject)
        print(("OK: " if ok else "REJECTED: ") + why)
        return 0 if ok else 1
    if not a.stage:
        ap.error("--stage is required")

    rep = run_stage(a.stage, a.staged, a.only, a.strict_missing, a.skip)
    print_table(rep)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        # Public check-run annotations: visible even when job logs need a token.
        for chk in rep.checks:
            if chk.status == "FAIL":
                detail = " ".join(chk.detail.split())[:900]
                print(f"::error title=gate {chk.name}::{detail}")
    if a.json:
        print(rep.to_json())
    return 1 if rep.counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
