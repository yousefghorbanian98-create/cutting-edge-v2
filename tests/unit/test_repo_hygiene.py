"""Real test for S-001 — Repo hygiene.

Proves, against the actual git-tracked tree (not mocks):
  AC-1 no Python files (esp. generator scripts) are tracked at repo root
  AC-2 LICENSE is a present, valid MIT license text
  AC-3 .editorconfig exists with sane base rules
  AC-4 CODE_OF_CONDUCT.md exists at the GitHub-standard root location
  AC-5 the docs/loop tree is intact and scripts/verify_ledger.py is green

Runs under pytest and also as a plain script (`python tests/unit/test_repo_hygiene.py`).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOOP = ROOT / "docs" / "loop"

GENERATOR_SCRIPTS = ("build_cutting_edge.py", "extend_cutting_edge_part2.py")
LOOP_DOCS = [f"{i:02d}_" for i in range(12)]  # 00_INDEX … 11_SUPERVISOR


def _git_tracked_python_files_at_root() -> list[str]:
    """Return tracked *.py paths that live directly at the repository root."""
    out = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [p for p in out.stdout.splitlines() if "/" not in p and p.strip()]


def test_no_python_files_at_repo_root() -> None:
    """AC-1: generator scripts removed and nothing replaced them at root."""
    root_py = _git_tracked_python_files_at_root()
    assert root_py == [], f"tracked .py files at repo root: {root_py}"
    for name in GENERATOR_SCRIPTS:
        assert not (ROOT / name).exists(), f"generator script still present: {name}"


def test_license_is_mit() -> None:
    """AC-2: LICENSE exists at root and is recognizably the MIT license."""
    license_path = ROOT / "LICENSE"
    assert license_path.is_file(), "LICENSE missing at repo root"
    text = license_path.read_text(encoding="utf-8")
    assert "MIT License" in text, "LICENSE does not look like MIT"
    assert "Permission is hereby granted, free of charge" in text
    assert 'THE SOFTWARE IS PROVIDED "AS IS"' in text
    assert re.search(r"Copyright \(c\) \d{4} .+", text), "LICENSE lacks a Copyright (c) <year> <holder> line"


def test_editorconfig_present_and_complete() -> None:
    """AC-3: .editorconfig exists with a root marker and a [*] base section."""
    ec = ROOT / ".editorconfig"
    assert ec.is_file(), ".editorconfig missing at repo root"
    text = ec.read_text(encoding="utf-8")
    assert re.search(r"^\s*root\s*=\s*true\b", text, re.MULTILINE), "missing 'root = true'"
    assert "[*]" in text, "missing [*] base section"
    for key in ("end_of_line", "insert_final_newline", "charset"):
        assert re.search(rf"^\s*{key}\s*=", text, re.MULTILINE), f".editorconfig [*] missing {key}"


def test_code_of_conduct_present() -> None:
    """AC-4: CODE_OF_CONDUCT.md exists at root with enforcement/report guidance."""
    coc = ROOT / "CODE_OF_CONDUCT.md"
    assert coc.is_file(), "CODE_OF_CONDUCT.md missing at repo root"
    text = coc.read_text(encoding="utf-8").lower()
    assert "code of conduct" in text
    # report/enforcement channel must be described (en or fa)
    assert "report" in text or "گزارش" in text, "CoC lacks a reporting channel"
    assert "harassment" in text or "آزار" in text, "CoC lacks harassment-free pledge"


def test_docs_tree_and_ledger_intact() -> None:
    """AC-5: docs/loop tree intact and verify_ledger.py exits green."""
    # All loop docs 00..11 present
    loop_md = sorted(p.name for p in LOOP.glob("*.md"))
    for prefix in LOOP_DOCS:
        assert any(n.startswith(prefix) for n in loop_md), f"docs/loop missing doc with prefix {prefix}"
    assert (LOOP / "steps.json").is_file()
    assert (LOOP / "templates" / "CONTRACT.md").is_file()
    assert (LOOP / "templates" / "REVIEW.md").is_file()
    assert (LOOP / "evidence" / "SESSIONS.md").is_file()

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_ledger.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"verify_ledger.py failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    assert "ledger OK" in result.stdout


# ── S-101: ADR log + learnings hygiene ────────────────────────────────────────
def _hygiene():
    sys.path.insert(0, str(ROOT / "scripts" / "loop"))
    import hygiene  # noqa: PLC0415

    return hygiene


def test_adr_or_learnings_adr_format() -> None:
    """S-101 AC-1/AC-3: ≥ 8 ADRs, contiguous numbering, four MADR sections, dated status."""
    h = _hygiene()
    errs = h.validate_adr_dir()
    assert not errs, "\n".join(errs)
    adrs = sorted(p.name for p in h.ADR_DIR.glob("*.md") if p.name not in h.EXEMPT)
    assert len(adrs) >= 8, adrs
    expected_slugs = {
        "0001": "locked-stack",
        "0002": "external-tool-audit-triage",
        "0003": "daisyui-5-for-tailwind-4",
        "0004": "ffmpeg-first-moviepy-fallback",
        "0005": "python-backend-as-pyinstaller-sidecar",
        "0006": "free-cloud-models-and-key-in-keyring",
        "0007": "product-defaults-mit-no-telemetry-fa",
        "0008": "supervisor-builder-loop-with-evidence-ledger",
        "0009": "ci-as-public-evidence",
    }
    for num, slug in expected_slugs.items():
        assert f"{num}-{slug}.md" in adrs, f"ADR {num}-{slug}.md missing"


def test_adr_or_learnings_index_complete() -> None:
    """S-101 AC-2: README lists exactly the ADR files; TEMPLATE exists."""
    h = _hygiene()
    idx = (h.ADR_DIR / "README.md").read_text(encoding="utf-8")
    files = sorted(p.name[:4] for p in h.ADR_DIR.glob("*.md") if p.name not in h.EXEMPT)
    listed = sorted(set(re.findall(r"^\|\s*(\d{4})\s*\|", idx, flags=re.M)))
    assert files == listed, f"files={files} listed={listed}"
    assert (h.ADR_DIR / "TEMPLATE.md").is_file()
    tmpl = (h.ADR_DIR / "TEMPLATE.md").read_text(encoding="utf-8")
    for sec in h.ADR_SECTIONS:
        assert sec in tmpl


def test_adr_or_learnings_learnings_format() -> None:
    """S-101 AC-4: every learnings entry ≤ 20 lines with the three sections."""
    h = _hygiene()
    errs = h.validate_learnings_dir()
    assert not errs, "\n".join(errs)
    entries = [p for p in h.LEARN_DIR.glob("*.md") if p.name not in h.EXEMPT]
    assert len(entries) >= 3, "expected the S-008/S-009 session learnings to exist"


def test_adr_or_learnings_validator_rejects_bad(tmp_path: Path) -> None:
    """S-101 AC-5: the validator is not decorative — malformed inputs fail with the file name."""
    h = _hygiene()
    adr = tmp_path / "adr"
    adr.mkdir()
    (adr / "TEMPLATE.md").write_text("x", encoding="utf-8")
    (adr / "README.md").write_text("| # | Title | Status |\n|---|---|---|\n| 0001 | t | Accepted |\n", encoding="utf-8")
    (adr / "0001-no-consequences.md").write_text(
        "# ADR-0001 — t\n\n## Status\nAccepted — 2026-09-22\n\n## Context\nc\n\n## Decision\nd\n", encoding="utf-8"
    )
    errs = h.validate_adr_dir(adr)
    assert any("0001-no-consequences.md" in e and "Consequences" in e for e in errs), errs

    (adr / "0001-no-consequences.md").write_text(
        "# ADR-0001 — t\n\n## Status\nAccepted\n\n## Context\nc\n\n## Decision\nd\n\n## Consequences\nq\n",
        encoding="utf-8",
    )
    errs = h.validate_adr_dir(adr)
    assert any("Status line" in e for e in errs), errs

    learn = tmp_path / "learn"
    learn.mkdir()
    (learn / "TEMPLATE.md").write_text("x", encoding="utf-8")
    body = "# 2026-09-22 — long\n\n## What broke\n" + "- x\n" * 22 + "\n## Root cause\n- y\n\n## Rule\n- z\n"
    (learn / "2026-09-22-too-long.md").write_text(body, encoding="utf-8")
    errs = h.validate_learnings_dir(learn)
    assert any("too-long.md" in e and "> 20" in e for e in errs), errs
    (learn / "bad name.md").write_text("## What broke\n## Root cause\n## Rule\n", encoding="utf-8")
    errs = h.validate_learnings_dir(learn)
    assert any("bad name.md" in e and "file name" in e for e in errs), errs


def _run_all() -> int:
    tests = [
        test_no_python_files_at_repo_root,
        test_license_is_mit,
        test_editorconfig_present_and_complete,
        test_code_of_conduct_present,
        test_docs_tree_and_ledger_intact,
        test_adr_or_learnings_adr_format,
        test_adr_or_learnings_index_complete,
        test_adr_or_learnings_learnings_format,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except AssertionError as exc:  # real assertions only; no bare except
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
        else:
            print(f"PASS {test.__name__}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
