"""Write a small text manifest and print it as public annotations.

Zip downloads from this sandbox return EOF against blob.core.windows.net even
when the artifact API lists a size. Check-run annotations are the readable
channel. This script does not treat a missing file as a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

INSTALLER_CHECKS = (
    "install-exit-0",
    "app-still-running",
    "window-title",
    "uninstall-dir-removed",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _notice(title: str, message: str) -> None:
    text = " ".join(message.split())
    print(f"::notice title={title}::{text}")


def _error(title: str, message: str) -> None:
    text = " ".join(message.split())
    print(f"::error title={title}::{text}")


def _meta() -> str:
    platform = os.environ.get("RUNNER_OS", "unknown")
    sha = os.environ.get("GITHUB_SHA", "unknown")
    run = os.environ.get("GITHUB_RUN_ID", "unknown")
    return f"platform={platform} sha={sha} run={run} producer=scripts/ci/evidence_manifest.py"


def _installer_checks(path: Path, lines: list[str]) -> int:
    failed = 0
    found: dict[str, bool] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        item = json.loads(raw)
        name = str(item.get("check", ""))
        if name in INSTALLER_CHECKS:
            found[name] = bool(item.get("ok"))
    prefix = _meta()
    for name in INSTALLER_CHECKS:
        if name not in found:
            _notice("named result", f"{prefix} name={name} result=not-run")
            lines.append(f"check={name} result=not-run")
            continue
        result = "passed" if found[name] else "failed"
        lines.append(f"check={name} result={result}")
        if result == "failed":
            failed += 1
            _error("named result", f"{prefix} name={name} result=failed")
        else:
            _notice("named result", f"{prefix} name={name} result=passed")
    return failed


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--optional", action="append", default=[])
    parser.add_argument("--require-glob", default="")
    parser.add_argument("--glob-outcome", default="")
    parser.add_argument("--note", action="append", default=[])
    args = parser.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [_meta(), "readable-channel=check-run-annotation", "user-gpu=unverified"]
    lines.extend(note.replace("\n", " ") for note in args.note)
    failed = 0

    def record(path: Path, *, required: bool) -> None:
        nonlocal failed
        prefix = _meta()
        if not path.is_file():
            lines.append(f"file={path} result=not-produced")
            if required:
                failed += 1
                _error("evidence manifest", f"{prefix} file={path} result=not-produced")
            else:
                _notice("evidence manifest", f"{prefix} file={path} result=not-produced")
            return
        digest = _sha256(path)
        size = path.stat().st_size
        lines.append(f"file={path} bytes={size} sha256={digest}")
        _notice("evidence manifest", f"{prefix} file={path} bytes={size} sha256={digest}")
        if path.name == "installer-smoke.jsonl":
            failed += _installer_checks(path, lines)
        if path.name == "smoke-gpu-dry.json":
            lines.append("smoke-gpu=dry-run user-gpu=unverified")
            _notice("user-gpu", f"{prefix} unverified dry-run is not a GPU pass")

    for raw in args.require:
        record(Path(raw), required=True)
    for raw in args.optional:
        record(Path(raw), required=False)

    if args.require_glob:
        matches = sorted(Path().glob(args.require_glob))
        outcome = args.glob_outcome or "unknown"
        if not matches:
            lines.append(f"glob={args.require_glob} result=not-produced outcome={outcome}")
            message = f"{_meta()} glob={args.require_glob} result=not-produced outcome={outcome}"
            if outcome == "success":
                failed += 1
                _error("evidence manifest", message)
            else:
                _notice("evidence manifest", message)
        for path in matches:
            record(path, required=True)

    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    digest = _sha256(out)
    _notice(
        "evidence manifest",
        f"{_meta()} file={out} bytes={out.stat().st_size} sha256={digest}",
    )
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as handle:
            handle.write("## Evidence manifest\n\n```text\n")
            handle.write(text)
            handle.write(f"manifest-sha256={digest}\n```\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
