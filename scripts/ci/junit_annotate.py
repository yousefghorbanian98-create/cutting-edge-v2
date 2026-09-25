"""Emit GitHub Actions annotations for failed junit test cases (S-009).

Why: job logs and artifacts need an authenticated token, but check-run
annotations are public. Running this `if: always()` after pytest/Playwright
makes the first failures visible to the loop even when logs are not.

Usage: python scripts/ci/junit_annotate.py reports/junit-unit.xml [more.xml ...]
Exit code is always 0 (the test step already failed the job).
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_ANNOTATIONS = 10  # GitHub keeps at most 10 error annotations per step
# Named result notices are evidence for open gaps only. A missing name is not a pass.
NAMED_GAPS = (
    "timeline-canvas.spec.ts",
    "zoom.spec.ts",
    "playback.spec.ts",
    "e2e/timeline.spec.ts",
    "timeline.spec.ts",
    "test_ffmpeg_overwrite.py",
)


def _one_line(s: str, limit: int = 900) -> str:
    s = " ".join(s.split())
    return s[:limit] + ("…" if len(s) > limit else "")


def _params(tc: ET.Element, name: str) -> str:
    """Workflow-command parameters: `::error file=…,line=…,title=…::msg`.

    A leading comma (`::error,title=…`) is silently ignored by GitHub — CI run #2
    proved it: the errors printed but no annotation was recorded. Build the list
    and join with commas so the shape is right with or without `file`.
    """
    parts = []
    file_attr = tc.get("file") or ""
    if file_attr:
        parts.append(f"file={file_attr}")
        line = tc.get("line") or ""
        if line.isdigit():
            parts.append(f"line={line}")
    # `::` and `,` inside a title terminate the parameter parser — strip them.
    title = name[:120].replace("::", " › ").replace(",", " ")
    parts.append(f"title={title}")
    return ",".join(parts)


def main(paths: list[str]) -> int:
    emitted = 0
    total = failed = 0
    named = {gap: [0, 0] for gap in NAMED_GAPS}
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            print(f"::notice title=junit_annotate::{p} not found (step may have been skipped)")
            continue
        root = ET.parse(p).getroot()  # noqa: S314 — junit written by our own pytest/Playwright run, not untrusted input
        for tc in root.iter("testcase"):
            total += 1
            problems = list(tc.findall("failure")) + list(tc.findall("error"))
            identity = f"{tc.get('classname', '')} {tc.get('file', '')} {tc.get('name', '')}"
            gap = next((item for item in NAMED_GAPS if item in identity), "")
            if problems:
                failed += 1
                if gap:
                    named[gap][1] += 1
                if emitted >= MAX_ANNOTATIONS:
                    continue
                name = f"{tc.get('classname', '')}::{tc.get('name', '')}"
                msg = problems[0].get("message") or ""
                body = problems[0].text or ""
                print(f"::error {_params(tc, name)}::{_one_line(msg + ' | ' + body)}")
                emitted += 1
                continue
            if gap:
                named[gap][0] += 1
    for gap, (passed, broken) in named.items():
        if passed or broken:
            print(f"::notice title=named result::{gap}: {passed} passed, {broken} failed")
    print(f"::notice title=junit summary::{failed} failed / {total} total across {len(paths)} report(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
