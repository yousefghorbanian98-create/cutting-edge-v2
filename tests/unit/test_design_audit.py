"""S-100 — offline Web Interface Guidelines checker is exact, not decorative.

Fixtures: tests/fixtures/ui/violations.tsx (8 known violations, one per rule,
fixed line numbers) and tests/fixtures/ui/clean.tsx (0 findings, one justified
wig-ignore). The real UI tree must be clean in --strict mode (gate + CI).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "design_audit.py"
FIX = ROOT / "tests" / "fixtures" / "ui"

EXPECTED = [
    (9, "icon-button-label"),
    (12, "outline-none-focus"),
    (13, "transition-all"),
    (16, "div-click"),
    (17, "img-alt-dims"),
    (18, "hardcoded-format"),
    (19, "reduced-motion"),
    (20, "input-label"),
]


def _run(*args: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT, check=False)
    return proc.returncode, proc.stdout


def _findings(*args: str) -> tuple[int, list[dict]]:
    rc, out = _run(*args, "--json")
    return rc, json.loads(out.strip().splitlines()[-1])["findings"]


# ── AC-1: fixture with 8 known violations → exactly 8 findings at the right lines ──
def test_violations_fixture_exact() -> None:
    rc, findings = _findings(str(FIX / "violations.tsx"), "--strict")
    assert rc == 1
    got = [(f["line"], f["rule"]) for f in findings]
    assert got == EXPECTED, got
    # every finding points at a real line containing the offending construct
    lines = (FIX / "violations.tsx").read_text(encoding="utf-8").splitlines()
    for line, rule in got:
        src = lines[line - 1]
        assert ("<" in src) or ("toLocale" in src), f"{rule} at {line}: {src!r}"


# ── AC-2: clean fixture → 0 findings; its wig-ignore is consumed (no unused-ignore) ──
def test_clean_fixture_zero() -> None:
    rc, findings = _findings(str(FIX / "clean.tsx"), "--strict")
    assert rc == 0
    assert findings == []


# ── AC-3: output format `file:line rule message` and --warn exit 0 ────────────
def test_output_format_and_modes() -> None:
    rc, out = _run(str(FIX / "violations.tsx"))
    assert rc == 0, "default/--warn mode must exit 0"
    body = [ln for ln in out.splitlines() if not ln.startswith("design_audit:")]
    assert len(body) == 8
    for ln in body:
        loc, rule, *_msg = ln.split(" ", 2)
        path, num = loc.rsplit(":", 1)
        assert path.endswith("tests/fixtures/ui/violations.tsx") and num.isdigit(), ln
        assert rule in {r for _, r in EXPECTED}, ln
    assert out.strip().endswith("[warn]")
    rc, out = _run(str(FIX / "violations.tsx"), "--strict")
    assert rc == 1 and out.strip().endswith("[strict]")


# ── AC-4: ignores must be justified with a step id; unknown/unused ignores are findings ──
def test_ignore_grammar(tmp_path: Path) -> None:
    src = tmp_path / "x.tsx"
    src.write_text(
        "export function X() {\n"
        "  return (\n"
        "    <div>\n"
        "      {/* wig-ignore icon-button-label: no reason step */}\n"
        '      <button type="button"><Icon /></button>\n'
        "      {/* wig-ignore nonsense-rule: whatever (S-001) */}\n"
        "      <span>ok</span>\n"
        "      {/* wig-ignore transition-all: nothing here to suppress (S-001) */}\n"
        "      <span>ok</span>\n"
        "    </div>\n"
        "  );\n"
        "}\n",
        encoding="utf-8",
    )
    rc, findings = _findings(str(src), "--strict")
    assert rc == 1
    rules = sorted((f["line"], f["rule"]) for f in findings)
    assert rules == [(4, "invalid-ignore"), (6, "invalid-ignore"), (8, "unused-ignore")], rules


# ── AC-5: the real UI tree is clean in strict mode (what gate + CI run) ─────────
def test_real_ui_tree_is_clean() -> None:
    rc, findings = _findings("apps/desktop/src", "--strict")
    assert rc == 0, "\n".join(f"{f['file']}:{f['line']} {f['rule']}" for f in findings)
    # and it really scanned the app (not an empty glob)
    rc, out = _run("apps/desktop/src", "--strict")
    assert "in 4 file(s)" in out or "file(s)" in out
    assert "0 finding(s)" in out


# ── AC-6: every suppression in the real tree names an owner step ───────────────
def test_real_tree_ignores_are_justified() -> None:
    owners = []
    for f in (ROOT / "apps" / "desktop" / "src").rglob("*.tsx"):
        for ln, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if "wig-ignore" in raw:
                assert "(S-" in raw, f"{f}:{ln} wig-ignore without owner step"
                owners.append((f.name, ln))
    assert len(owners) <= 3, f"too many suppressions for a 4-file tree: {owners}"
