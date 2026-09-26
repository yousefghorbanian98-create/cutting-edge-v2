"""Emit GitHub Actions annotations for failed junit test cases (S-009).

Why: job logs and artifacts need an authenticated token, but check-run
annotations are public. Running this `if: always()` after pytest/Playwright
makes the first failures visible to the loop even when logs are not.

Usage: python scripts/ci/junit_annotate.py reports/junit-unit.xml [more.xml ...]
Exit code is always 0 (the test step already failed the job).

GitHub keeps the first 10 annotations of a step. Named results are therefore
one notice each, and the required names are printed before the count line.
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
    "test_existing_output_without_consent_is_refused",
    "test_failed_consented_replace_rolls_back",
    "test_consented_replace_publishes_only_after_success",
    "test_ffmpeg_extract_aac",
)

# Real thresholds already in the specs. This map does not change them.
# These strings are expected contracts, never a substitute for a measured value.
THRESHOLDS = {
    "timeline-canvas.spec.ts": "drop-ratio<0.05 rendered<40 seed=none",
    "zoom.spec.ts": "cursor-lock<=1px fit=scrollWidth<=clientWidth+1 seed=none",
    "playback.spec.ts": "drift<1/fps arrow-threshold=0.001 clock=video.currentTime seed=none",
    "e2e/timeline.spec.ts": "visual-ratio<0.001 fixture=wide.mp4 baseline=previous-journey-shot seed=none",
    "sequence.spec.ts": "ssim>0.9 gap<100ms clock=sequence-input seed=none",
    "test_ffmpeg_extract_aac": "wav=22050 channels=1",
}

# Concept tokens are named only when the owning test's stdout says so.
# A passing owner without the token is not a concept pass. Running these
# tests does not close BUG-18.
CONCEPT_SOURCES = {
    "refusal": ("tests.unit.test_ffmpeg_overwrite::test_existing_output_without_consent_is_refused",),
    "no-overwrite": ("tests.unit.test_ffmpeg_overwrite::test_existing_output_without_consent_is_refused",),
    "rollback": ("tests.unit.test_ffmpeg_overwrite::test_failed_consented_replace_rolls_back",),
    "staging": ("tests.unit.test_ffmpeg_overwrite::test_consented_replace_publishes_only_after_success",),
    "explicit-consent": (
        "tests.unit.test_ffmpeg_overwrite::test_failed_consented_replace_rolls_back",
        "tests.unit.test_ffmpeg_overwrite::test_consented_replace_publishes_only_after_success",
    ),
}


def _one_line(s: str, limit: int = 3500) -> str:
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


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def collect_cases(paths: list[str]) -> tuple[list[dict[str, str]], list[str], int, int]:
    """Return cases, missing report paths, failure count, and total cases."""
    cases: list[dict[str, str]] = []
    missing: list[str] = []
    failed = total = 0
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            missing.append(str(path))
            continue
        root = ET.parse(path).getroot()  # noqa: S314 — junit from our pytest/Playwright, not untrusted input
        for tc in root.iter("testcase"):
            total += 1
            problems = list(tc.findall("failure")) + list(tc.findall("error"))
            if problems:
                failed += 1
            evidence = _evidence(tc) or "measured=not-in-junit"
            cases.append(
                {
                    "identity": f"{tc.get('classname', '')} {tc.get('file', '')} {tc.get('name', '')}",
                    "classname": tc.get("classname", ""),
                    "name": tc.get("name", ""),
                    "result": "failed" if problems else "passed",
                    "evidence": evidence,
                    "problem": _one_line((problems[0].get("message") or "") + " | " + (problems[0].text or ""))
                    if problems
                    else "",
                    "file": tc.get("file") or "",
                    "line": tc.get("line") or "",
                }
            )
    return cases, missing, failed, total


def _qualified(case: dict[str, str], key: str) -> bool:
    """Match `suite::function` so a same-named test in another file is not counted."""
    if "::" not in key:
        return key == case["name"] or key in case["identity"]
    suite, func = key.split("::", 1)
    return suite in case["identity"] and case["name"] == func


def _owns(case: dict[str, str], source: str) -> bool:
    return _qualified(case, source)


def _identity_match(case: dict[str, str], key: str) -> bool:
    if key in CONCEPT_SOURCES:
        return False
    return _qualified(case, key)


def named_records(paths: list[str], required: tuple[str, ...]) -> list[dict[str, str]]:
    """One record per required name. Absence is not-run, never a pass."""
    cases, _missing, _failed, _total = collect_cases(paths)
    records: list[dict[str, str]] = []
    for name in required:
        if name in CONCEPT_SOURCES:
            owned = [case for case in cases if any(_owns(case, source) for source in CONCEPT_SOURCES[name])]
            passed = [case for case in owned if case["result"] == "passed" and f"concept={name}" in case["evidence"]]
            broken = [case for case in owned if case["result"] == "failed"]
            if not owned:
                result = "not-run"
            elif broken and not passed:
                result = "failed"
            elif passed and not broken:
                result = "passed"
            elif passed and broken:
                result = "failed"
            else:
                result = "not-run"
            detail = " | ".join(f"source={case['name']} result={case['result']} {case['evidence']}" for case in owned)
            records.append(
                {
                    "name": name,
                    "result": result,
                    "passed": str(len(passed)),
                    "failed": str(len(broken)),
                    "detail": detail or "measured=not-in-junit",
                }
            )
            continue
        matched = [case for case in cases if _identity_match(case, name)]
        if not matched:
            records.append(
                {"name": name, "result": "not-run", "passed": "0", "failed": "0", "detail": "measured=not-in-junit"}
            )
            continue
        broken = [case for case in matched if case["result"] == "failed"]
        result = "failed" if broken else "passed"
        detail = " | ".join(
            f"suite={case['classname']} name={case['name']} result={case['result']} {case['evidence']}"
            for case in matched
        )
        records.append(
            {
                "name": name,
                "result": result,
                "passed": str(len(matched) - len(broken)),
                "failed": str(len(broken)),
                "detail": detail,
            }
        )
    return records


def main(paths: list[str]) -> int:
    _configure_stdio()
    emitted = 0
    cases, missing, failed, total = collect_cases(paths)
    context = _context()
    for path in missing:
        print(f"::notice title=junit_annotate::{path} not found (step may have been skipped)")
    required = _required()
    for record in named_records(paths, required):
        name = record["name"]
        result = record["result"]
        if result == "not-run":
            print(f"::notice title=named result::{name}: 0 passed, 0 failed result=not-run {context}")
            continue
        passed = record["passed"]
        broken = record["failed"]
        threshold = THRESHOLDS.get(name)
        expected = f" expected={threshold}" if threshold else ""
        print(
            "::notice title=named result::"
            + _one_line(f"{name}: {passed} passed, {broken} failed {context} {record['detail']}{expected}")
        )
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
    for case in cases:
        if case["result"] != "failed" or emitted >= MAX_ANNOTATIONS:
            continue
        title = f"{case['classname']}::{case['name']}"
        fake = ET.Element("testcase", {"file": case["file"], "line": case["line"]})
        print(f"::error {_params(fake, title)}::{case['problem']}")
        emitted += 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
