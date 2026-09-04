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
    assert "THE SOFTWARE IS PROVIDED \"AS IS\"" in text
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
    assert result.returncode == 0, (
        f"verify_ledger.py failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "ledger OK" in result.stdout


def _run_all() -> int:
    tests = [
        test_no_python_files_at_repo_root,
        test_license_is_mit,
        test_editorconfig_present_and_complete,
        test_code_of_conduct_present,
        test_docs_tree_and_ledger_intact,
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
