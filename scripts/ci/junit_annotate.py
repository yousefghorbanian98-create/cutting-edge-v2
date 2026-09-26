"""Emit GitHub Actions annotations for failed junit test cases (S-009).

Why: job logs and artifacts need an authenticated token, but check-run
annotations are public. Running this `if: always()` after pytest/Playwright
makes the first failures visible to the loop even when logs are not.

Usage: python scripts/ci/junit_annotate.py reports/junit-unit.xml [more.xml ...]
Exit code is always 0 (the test step already failed the job).
"""

from __future__ import annotations

import os
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
    "sequence.spec.ts",
    "test_ffmpeg_overwrite.py",
    "test_ffmpeg_extract_aac",
)

# Real thresholds already in the specs. This map does not change them.
THRESHOLDS = {
    "timeline-canvas.spec.ts": "drop-ratio<0.05 rendered<40 seed=none",
    "zoom.spec.ts": "cursor-lock<=1px fit=scrollWidth<=clientWidth+1 seed=none",
    "playback.spec.ts": "drift<1/fps arrow-threshold=0.001 clock=video.currentTime seed=none",
    "e2e/timeline.spec.ts": "visual-ratio<0.001 fixture=wide.mp4 baseline=previous-journey-shot seed=none",
    "sequence.spec.ts": "ssim>0.9 gap<100ms clock=sequence-input seed=none",
    "test_ffmpeg_extract_aac": "wav=22050 channels=1",
}


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


def _context() -> str:
    platform = os.environ.get("RUNNER_OS", "unknown")
    sha = os.environ.get("GITHUB_SHA", "unknown")
    run = os.environ.get("GITHUB_RUN_ID", "unknown")
    return f"platform={platform} sha={sha} run={run}"


def _required() -> tuple[str, ...]:
    raw = os.environ.get("CE_EVIDENCE_REQUIRE", "")
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def _evidence(tc: ET.Element) -> str:
    chunks: list[str] = []
    for tag in ("system-out", "system-err"):
        node = tc.find(tag)
        if node is not None and node.text:
            chunks.append(node.text)
    lines = [part.strip() for part in " ".join(chunks).splitlines() if "EVIDENCE " in part]
    return " | ".join(lines)


def main(paths: list[str]) -> int:
    emitted = 0
    total = failed = 0
    named = {gap: [0, 0] for gap in NAMED_GAPS}
    details: dict[str, list[str]] = {gap: [] for gap in NAMED_GAPS}
    context = _context()
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
            evidence = _evidence(tc) or "measured=not-in-junit"
            if problems:
                failed += 1
                if gap:
                    named[gap][1] += 1
                    details[gap].append(
                        f"suite={tc.get('classname', '')} name={tc.get('name', '')} result=failed {evidence}"
                    )
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
                details[gap].append(
                    f"suite={tc.get('classname', '')} name={tc.get('name', '')} result=passed {evidence}"
                )
    required = _required()
    for gap, (passed, broken) in named.items():
        if gap not in required and not passed and not broken:
            continue
        if not passed and not broken:
            print(f"::notice title=named result::{gap}: 0 passed, 0 failed result=not-run {context}")
            continue
        print(f"::notice title=named result::{gap}: {passed} passed, {broken} failed {context}")
        threshold = THRESHOLDS.get(gap, "threshold=see-spec")
        for line in details[gap]:
            print(f"::notice title=named result::{_one_line(context + ' ' + line + ' ' + threshold)}")
    if "sequence.spec.ts" in required:
        print(
            "::notice title=historical failure::"
            "run=36194558289 sequence.spec.ts sequence-text not found expected عنوان; "
            "historical only; this run is the named result line; absence is not a pass"
        )
    print(
        "::notice title=junit summary::"
        f"{failed} failed / {total} total across {len(paths)} report(s); count is not a named pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
