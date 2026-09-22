"""S-099 — AGENTS.md / DESIGN.md / harness files are one consistent, machine-checked authority.

Real tests: they run the actual `scripts/check-design-tokens.js` (three-way
DESIGN.md ⇄ globals.css ⇄ tokens.ts) on the clean tree and on mutated copies,
and read the agent-facing files for foreign-stack claims and missing links.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "scripts" / "check-design-tokens.js"
DESIGN = ROOT / "DESIGN.md"
CSS = ROOT / "apps" / "desktop" / "src" / "app" / "globals.css"
TOKENS = ROOT / "packages" / "design-system" / "tokens.ts"

HARNESS = [
    ROOT / ".cursorrules",
    ROOT / ".github" / "copilot-instructions.md",
    ROOT / ".claude" / "skills" / "web-design-guidelines" / "SKILL.md",
    ROOT / ".cursor" / "skills" / "web-design-guidelines.md",
    ROOT / ".windsurf" / "rules" / "web-design-guidelines.md",
]
REQUIRED_LINKS = ("AGENTS.md", "DESIGN.md", "docs/loop/00_INDEX.md")
# Words that describe a different product (generic SaaS from the imported drafts).
FOREIGN = (
    "NestJS",
    "Prisma",
    "shadcn",
    "PostgreSQL",
    "Redis",
    "zod",
    "RAG",
    "Geist",
    "next-themes",
    "apps/web",
    "raw.githubusercontent.com",
)
# Draft-only design values that must not survive in the authority doc.
DRAFT_VALUES = (
    "#010102",
    "#5E6AD2",
    "#0F1011",
    "Geist",
    "Linear Display",
    "next-themes",
    "light-canvas",
    "Chat Bubble",
)

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is required for the token check")


def _run(*args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        ["node", str(CHECK), "--json", *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert proc.returncode in (0, 1), f"checker crashed: rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout.strip().splitlines()[-1])


# ── AC-1 / AC-2 ───────────────────────────────────────────────────────────────
def test_token_check_green_on_clean_tree() -> None:
    rc, rep = _run()
    assert rc == 0, rep["problems"]
    assert rep["ok"] is True
    assert rep["threeWay"] == 27, rep  # every @theme var is documented and equal in all three sources
    assert rep["tsOnly"] >= 16, rep  # primary scale + radius.full + motion + shadows
    assert set(rep["groups"]) >= {"colors", "typography", "radius", "motion", "shadows"}
    assert "placeholder" not in CHECK.read_text(encoding="utf-8").lower()


# ── AC-2 / AC-6: drift in each of the three sources is named ─────────────────
def test_token_check_tolerates_crlf(tmp_path: Path) -> None:
    """Windows checkouts/editors may write CRLF; the check must parse them (CI run 35675177747)."""
    crlf = tmp_path / "DESIGN.md"
    crlf.write_bytes(DESIGN.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
    css = tmp_path / "globals.css"
    css.write_bytes(CSS.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
    ts = tmp_path / "tokens.ts"
    ts.write_bytes(TOKENS.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
    rc, rep = _run("--design", str(crlf), "--css", str(css), "--tokens", str(ts))
    assert rc == 0, rep["problems"]
    assert rep["threeWay"] == 27 and rep["tsOnly"] >= 16


def test_token_check_detects_drift_in_each_source(tmp_path: Path) -> None:
    css = tmp_path / "globals.css"
    css.write_text(
        CSS.read_text(encoding="utf-8").replace("--radius-md: 10px;", "--radius-md: 12px;"), encoding="utf-8"
    )
    rc, rep = _run("--css", str(css))
    assert rc == 1
    assert any(
        p.startswith("--radius-md:") and "globals.css=12px" in p and "DESIGN.md=10px" in p for p in rep["problems"]
    ), rep

    ts = tmp_path / "tokens.ts"
    ts.write_text(
        TOKENS.read_text(encoding="utf-8").replace("success: '#10b981'", "success: '#22c55e'"), encoding="utf-8"
    )
    rc, rep = _run("--tokens", str(ts))
    assert rc == 1
    assert any(p.startswith("--color-success:") and "tokens.ts=#22c55e" in p for p in rep["problems"]), rep

    design = tmp_path / "DESIGN.md"
    text = re.sub(r"```yaml\n# tokens: motion\n[\s\S]*?```", "(removed)", DESIGN.read_text(encoding="utf-8"))
    design.write_text(text, encoding="utf-8")
    rc, rep = _run("--design", str(design))
    assert rc == 1
    assert any("missing `# tokens: motion` block" in p for p in rep["problems"]), rep
    assert any(p.startswith("ts:motion.spring.stiffness:") for p in rep["problems"]), rep

    # A value edited in DESIGN.md alone (doc drifting from code) is caught too.
    design.write_text(
        DESIGN.read_text(encoding="utf-8").replace('--color-ai-glow: "#8b5cf6"', '--color-ai-glow: "#7c3aed"'),
        encoding="utf-8",
    )
    rc, rep = _run("--design", str(design))
    assert rc == 1
    assert any(p.startswith("--color-ai-glow:") and "DESIGN.md=#7c3aed" in p for p in rep["problems"]), rep


# ── AC-1: DESIGN.md is the authority, not the imported draft ─────────────────
def test_design_md_has_no_draft_values() -> None:
    text = DESIGN.read_text(encoding="utf-8")
    assert "IMPORTED DRAFT" not in text
    assert "AUTHORITY" in text
    for bad in DRAFT_VALUES:
        assert bad not in text, f"DESIGN.md still carries draft value {bad!r}"
    for must in (
        "Vazirmatn",
        "Inter Variable",
        "JetBrains Mono",
        "#09090b",
        "#8b5cf6",
        "#6366f1",
        "ADR-0010",
        "check-design-tokens.js",
    ):
        assert must in text, f"DESIGN.md lacks {must!r}"
    # Section skeleton the UI cards cite in their contracts.
    for heading in ("## 2. Colors", "## 3. Typography", "## 5. Motion", "## 6. Components", "## 8. Accessibility"):
        assert heading in text, heading


# ── AC-4: harness files are thin pointers ────────────────────────────────────
@pytest.mark.parametrize("path", HARNESS, ids=lambda p: str(p.relative_to(ROOT)))
def test_harness_files_are_thin_pointers(path: Path) -> None:
    assert path.is_file(), f"{path} missing"
    text = path.read_text(encoding="utf-8")
    for link in REQUIRED_LINKS:
        assert link in text, f"{path.name} does not point at {link}"
    for word in FOREIGN:
        assert (
            re.search(rf"(?<![\w/]){re.escape(word)}(?![\w-])", text) is None
        ), f"{path.name} mentions foreign-stack word {word!r}"
    assert len([ln for ln in text.splitlines() if ln.strip()]) <= 40, f"{path.name} is not thin"
    if "web-design-guidelines" in str(path):
        assert "docs/integrations/web-guidelines/web-interface-guidelines.md" in text
        assert "design_audit.py" in text


# ── AC-5: AGENTS.md is the entry point ────────────────────────────────────────
def test_agents_md_entry_point() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for must in (
        "DESIGN.md",
        "docs/loop/00_INDEX.md",
        "docs/loop/04_LEDGER.md",
        "check-design-tokens.js",
        "design_audit.py",
        "ADR-0010",
        "docs/adr/",
        "docs/learnings/",
    ):
        assert must in text, f"AGENTS.md lacks {must!r}"
    assert (ROOT / "docs" / "adr" / "0010-design-md-single-ui-authority.md").is_file()
    idx = (ROOT / "docs" / "adr" / "README.md").read_text(encoding="utf-8")
    assert re.search(r"^\|\s*0010\s*\|", idx, flags=re.M), "ADR-0010 not indexed"
