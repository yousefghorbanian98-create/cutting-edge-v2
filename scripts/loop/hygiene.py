"""Shared validators for docs/adr and docs/learnings (S-101).

Used by tests/unit/test_repo_hygiene.py (hard) and scripts/supervise.py C13 (audit)
so both agree on what a well-formed ADR / learnings entry is.

    python scripts/loop/hygiene.py            # validate the repo, exit 1 on problems
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADR_DIR = ROOT / "docs" / "adr"
LEARN_DIR = ROOT / "docs" / "learnings"

ADR_SECTIONS = ("## Status", "## Context", "## Decision", "## Consequences")
ADR_FILE_RE = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ADR_STATUS_RE = re.compile(
    r"^(Proposed|Accepted|Deprecated|Superseded by ADR-\d{4})\s+—\s+\d{4}-\d{2}-\d{2}\b",
)
LEARN_SECTIONS = ("## What broke", "## Root cause", "## Rule")
LEARN_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
LEARN_MAX_LINES = 20
EXEMPT = {"README.md", "TEMPLATE.md"}


def _section_order(text: str, sections: tuple[str, ...]) -> list[str]:
    found = []
    for line in text.splitlines():
        s = line.strip()
        if s in sections:
            found.append(s)
    return found


def validate_adr_file(path: Path) -> list[str]:
    errs: list[str] = []
    name = path.name
    m = ADR_FILE_RE.match(name)
    if not m:
        return [f"{name}: file name must be NNNN-kebab-slug.md"]
    num = m.group(1)
    text = path.read_text(encoding="utf-8")
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    if not first.startswith(f"# ADR-{num} —"):
        errs.append(f"{name}: H1 must start with `# ADR-{num} —`")
    order = _section_order(text, ADR_SECTIONS)
    if order != list(ADR_SECTIONS):
        missing = [s for s in ADR_SECTIONS if s not in order]
        errs.append(
            f"{name}: sections must be exactly {list(ADR_SECTIONS)} in order; missing/misordered: {missing or order}"
        )
    if "## Status" in text:
        after = text.split("## Status", 1)[1].strip().splitlines()
        status_line = after[0].strip() if after else ""
        if not ADR_STATUS_RE.match(status_line):
            errs.append(
                f"{name}: Status line must be `<Proposed|Accepted|Deprecated|Superseded by ADR-NNNN> — YYYY-MM-DD`, got {status_line!r}"
            )
    return errs


def validate_adr_dir(adr_dir: Path = ADR_DIR) -> list[str]:
    errs: list[str] = []
    files = sorted(p for p in adr_dir.glob("*.md") if p.name not in EXEMPT)
    nums = []
    for p in files:
        errs += validate_adr_file(p)
        m = ADR_FILE_RE.match(p.name)
        if m:
            nums.append(int(m.group(1)))
    if nums != list(range(1, len(nums) + 1)):
        errs.append(f"ADR numbers must be contiguous from 0001, got {nums}")
    if not (adr_dir / "TEMPLATE.md").exists():
        errs.append("docs/adr/TEMPLATE.md missing")
    readme = adr_dir / "README.md"
    if not readme.exists():
        errs.append("docs/adr/README.md missing")
    else:
        idx = readme.read_text(encoding="utf-8")
        listed = set(re.findall(r"^\|\s*(\d{4})\s*\|", idx, flags=re.M))
        present = {f"{n:04d}" for n in nums}
        for n in sorted(present - listed):
            errs.append(f"README.md: ADR {n} not listed")
        for n in sorted(listed - present):
            errs.append(f"README.md lists ADR {n} which has no file")
    return errs


def validate_learning_file(path: Path) -> list[str]:
    errs: list[str] = []
    name = path.name
    if not LEARN_FILE_RE.match(name):
        errs.append(f"{name}: file name must be YYYY-MM-DD-kebab-slug.md")
    text = path.read_text(encoding="utf-8")
    n = len([ln for ln in text.splitlines() if ln.strip()])
    if n > LEARN_MAX_LINES:
        errs.append(f"{name}: {n} non-empty lines > {LEARN_MAX_LINES} (keep learnings short)")
    order = _section_order(text, LEARN_SECTIONS)
    if order != list(LEARN_SECTIONS):
        errs.append(f"{name}: sections must be exactly {list(LEARN_SECTIONS)} in order, got {order}")
    return errs


def validate_learnings_dir(learn_dir: Path = LEARN_DIR) -> list[str]:
    errs: list[str] = []
    files = sorted(p for p in learn_dir.glob("*.md") if p.name not in EXEMPT)
    for p in files:
        errs += validate_learning_file(p)
    if not (learn_dir / "TEMPLATE.md").exists():
        errs.append("docs/learnings/TEMPLATE.md missing")
    return errs


def main() -> int:
    errs = validate_adr_dir() + validate_learnings_dir()
    adrs = len([p for p in ADR_DIR.glob("*.md") if p.name not in EXEMPT])
    learns = len([p for p in LEARN_DIR.glob("*.md") if p.name not in EXEMPT])
    for e in errs:
        print(f"- {e}")
    print(f"hygiene: {adrs} ADRs, {learns} learnings, {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
