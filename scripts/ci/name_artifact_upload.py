"""Name an upload-artifact outcome.

Upload success is not a client read of the zip. The GitHub artifact digest is
not the SHA-256 of a file inside the archive. A failed upload is not silent.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    outcome = os.environ.get("UPLOAD_OUTCOME", "unknown")
    name = os.environ.get("ARTIFACT_NAME", "unknown")
    prefix = (
        f"platform={os.environ.get('RUNNER_OS', 'unknown')} "
        f"sha={os.environ.get('GITHUB_SHA', 'unknown')} "
        f"run={os.environ.get('GITHUB_RUN_ID', 'unknown')} "
        "producer=scripts/ci/name_artifact_upload.py"
    )
    if outcome == "success":
        print(
            "::notice title=artifact zip::"
            f"{prefix} name={name} result=unverified "
            "reason=upload-success-is-not-a-client-read "
            "artifact-digest-is-not-file-sha256"
        )
        return 0
    print(
        "::error title=artifact zip::"
        f"{prefix} name={name} result=failed outcome={outcome} "
        "upload-failure-is-not-silent"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
