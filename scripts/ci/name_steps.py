"""Name step outcomes. A skipped step is not-run, never a pass.

smoke-gpu.ps1 dry-run stays unverified even when the contract step succeeds.
"""

from __future__ import annotations

import os


def result_for(label: str, outcome: str) -> str:
    if "smoke-gpu" in label:
        return "contract-dry-run user-gpu=unverified"
    if outcome == "success":
        return "passed"
    if outcome == "failure":
        return "failed"
    return "not-run"


def main() -> int:
    platform = os.environ.get("RUNNER_OS", "unknown")
    sha = os.environ.get("GITHUB_SHA", "unknown")
    run = os.environ.get("GITHUB_RUN_ID", "unknown")
    prefix = f"platform={platform} sha={sha} run={run}"
    for raw in os.environ.get("CE_NAMED_STEPS", "").splitlines():
        if "|" not in raw:
            continue
        label, outcome = raw.split("|", 1)
        label = " ".join(label.split())
        result = result_for(label, outcome.strip())
        kind = "error" if result == "failed" else "notice"
        print(f"::{kind} title=named result::{prefix} name={label} result={result}")
    if os.environ.get("CE_NOTE_USER_GPU") == "unverified":
        print(f"::notice title=user-gpu::{prefix} unverified dry-run is not a GPU pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
