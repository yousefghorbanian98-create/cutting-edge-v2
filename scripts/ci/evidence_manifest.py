"""Write a canonical evidence manifest and a separate sidecar checksum.

Zip downloads from this sandbox return EOF against blob.core.windows.net.
Job-summary markdown is not in the REST API. This script therefore prints the
canonical body and the sidecar as the first check-run annotations, and also
creates a check run whose output.text is the same canonical body.

The sidecar is not part of the hashed bytes. Embedding the manifest's own
sha256 inside the manifest would be circular, so it is not done.

Canonicalization:
  UTF-8, LF, no BOM, exactly one trailing newline.
  File records are sorted by posix path.
  Named records keep the required-name order.
Hash method: SHA-256 over those exact canonical bytes.
Verify: sha256(canonical) == sidecar hex. scripts/ci/verify_evidence_manifest.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

INSTALLER_CHECKS = (
    "install-exit-0",
    "app-still-running",
    "window-title",
    "uninstall-dir-removed",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str:
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


def _display(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def encode_annotation(text: str) -> str:
    """GitHub workflow commands decode %25, %0D, and %0A."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def canonical_bytes(lines: list[str]) -> bytes:
    body = "\n".join(lines).rstrip("\n") + "\n"
    if "\r" in body:
        raise ValueError("canonical manifest must not contain CR")
    return body.encode("utf-8")


def sidecar_bytes(digest: str, display: str) -> bytes:
    return f"{digest}  {display}\n".encode()


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
    for name in INSTALLER_CHECKS:
        if name not in found:
            lines.append(f"name={name} result=not-run")
            continue
        result = "passed" if found[name] else "failed"
        lines.append(f"name={name} result={result}")
        if result == "failed":
            failed += 1
    return failed


def _publish_check_run(name: str, conclusion: str, summary: str, text: str) -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    sha = os.environ.get("GITHUB_SHA", "")
    if os.environ.get("GITHUB_ACTIONS") != "true":
        _notice("evidence check-run", "result=not-run reason=outside-github-actions")
        return "not-run"
    missing = [name for name, value in (("repository", repo), ("token", token), ("sha", sha)) if not value]
    if missing:
        _error("evidence check-run", "result=failed reason=missing-" + "-".join(missing))
        return "failed"
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "name": name,
        "head_sha": sha,
        "status": "completed",
        "conclusion": conclusion,
        "started_at": now,
        "completed_at": now,
        "output": {
            "title": name[:255],
            "summary": summary[:65535],
            "text": text[:65535],
        },
    }
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/check-runs",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "cutting-edge-evidence",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 — GitHub API, not a user URL
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        _error("evidence check-run", f"result=failed status={exc.code} body={detail}")
        return "failed"
    check_id = body.get("id", "unknown")
    _notice("evidence check-run", f"result=published id={check_id} name={name} conclusion={conclusion}")
    return "published"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--optional", action="append", default=[])
    parser.add_argument("--require-glob", default="")
    parser.add_argument("--glob-outcome", default="")
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--junit", action="append", default=[])
    parser.add_argument("--name", action="append", default=[])
    parser.add_argument("--job", default=os.environ.get("GITHUB_JOB", "unknown"))
    args = parser.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sidecar = out.with_suffix(".sha256")
    lines = [
        "schema=evidence-manifest-v1",
        "hash-method=sha256",
        "canonicalization=utf-8-lf-no-bom-single-trailing-newline",
        "circular=false",
        "sidecar-note=sidecar-bytes-are-not-part-of-canonical-bytes",
        f"job={args.job}",
        _meta(),
        "readable-channel=check-run-annotation",
        "user-gpu=unverified",
        "BUG-18=open",
        "S-033=not-started",
        "GREEN=none",
    ]
    lines.extend(f"note={note.replace(chr(10), ' ')}" for note in args.note)
    failed = 0
    file_rows: list[str] = []

    def record(path: Path, *, required: bool) -> None:
        nonlocal failed
        shown = _display(path)
        if not path.is_file():
            file_rows.append(f"file={shown} result=not-produced")
            if required:
                failed += 1
            return
        digest = _file_sha256(path)
        size = path.stat().st_size
        file_rows.append(f"file={shown} bytes={size} sha256={digest}")
        if path.name == "installer-smoke.jsonl":
            failed += _installer_checks(path, file_rows)
        if path.name == "smoke-gpu-dry.json":
            file_rows.append("smoke-gpu=dry-run user-gpu=unverified")

    for raw in args.require:
        record(Path(raw), required=True)
    for raw in args.optional:
        record(Path(raw), required=False)

    if args.require_glob:
        matches = sorted(Path().glob(args.require_glob))
        outcome = args.glob_outcome or "unknown"
        if not matches:
            file_rows.append(f"glob={args.require_glob} result=not-produced outcome={outcome}")
            if outcome == "success":
                failed += 1
        for path in matches:
            record(path, required=True)

    lines.extend(sorted(file_rows))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from junit_annotate import named_records

    named = named_records(args.junit, tuple(args.name))
    for record_item in named:
        lines.append(
            f"named={record_item['name']} result={record_item['result']} "
            f"passed={record_item['passed']} failed={record_item['failed']} {record_item['detail']}"
        )
        if record_item["result"] == "failed":
            failed += 1

    data = canonical_bytes(lines)
    digest = _sha256(data)
    if digest.encode("ascii") in data:
        raise RuntimeError("canonical bytes contain their own sha256; refusing circular manifest")
    side = sidecar_bytes(digest, _display(out))
    out.write_bytes(data)
    sidecar.write_bytes(side)

    prefix = _meta()
    _notice(
        "evidence sha256",
        f"{prefix} job={args.job} file={_display(out)} bytes={len(data)} sha256={digest} "
        "hash-method=sha256 canonicalization=utf-8-lf-no-bom-single-trailing-newline circular=false",
    )
    _notice("evidence sidecar", f"{prefix} job={args.job} {side.decode('utf-8').strip()} hash-method=sha256")
    _notice("evidence canonical", f"{prefix} job={args.job} body={encode_annotation(data.decode('utf-8'))}")
    summary = (
        f"job={args.job} file={_display(out)} bytes={len(data)} sha256={digest} "
        "hash-method=sha256 canonicalization=utf-8-lf-no-bom-single-trailing-newline "
        "circular=false sidecar-is-not-in-canonical-bytes\n"
        "verify=sha256(output.text) == this sha256, after confirming LF and one trailing newline\n"
    )
    published = _publish_check_run(
        f"evidence-manifest-{args.job}",
        "failure" if failed else "success",
        summary,
        data.decode("utf-8"),
    )
    if published == "failed":
        failed += 1
    for row in file_rows:
        kind = "error" if "result=not-produced" in row and any(req in row for req in args.require) else "notice"
        if "result=failed" in row:
            kind = "error"
        print(f"::{kind} title=evidence manifest::{prefix} {row}")
    for record_item in named:
        kind = "error" if record_item["result"] == "failed" else "notice"
        print(
            f"::{kind} title=named result::{prefix} name={record_item['name']} "
            f"result={record_item['result']} {record_item['detail']}"
        )

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with Path(step_summary).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("## Evidence manifest\n\n")
            handle.write("Canonical bytes are hashed. The sidecar is not inside those bytes.\n\n")
            handle.write("```text\n")
            handle.write(data.decode("utf-8"))
            handle.write(f"sidecar-sha256={digest}\n")
            handle.write("```\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
