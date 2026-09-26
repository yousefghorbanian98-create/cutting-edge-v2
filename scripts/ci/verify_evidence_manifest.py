"""Verify a canonical evidence manifest against its sidecar.

The sidecar is not inside the hashed bytes. Verification is:

  SHA-256(canonical file bytes) == hex in the sidecar

Canonical bytes are UTF-8, LF, no BOM, one trailing newline. This script does
not rewrite the file. A mismatch exits 1. It does not treat a missing file as
a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sidecar_digest(text: str) -> tuple[str, str]:
    line = text.strip().splitlines()[0]
    if "  " not in line:
        raise ValueError(f"sidecar is not sha256sum format: {line[:80]}")
    digest, name = line.split("  ", 1)
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("sidecar digest is not 64 lowercase hex characters")
    return digest, name


def verify(canonical: bytes, sidecar_text: str) -> str:
    if canonical.startswith(b"\xef\xbb\xbf") or b"\r" in canonical:
        raise ValueError("canonical bytes have a BOM or CR; refusing to normalize")
    if not canonical.endswith(b"\n") or canonical.endswith(b"\n\n"):
        raise ValueError("canonical bytes must end with exactly one LF")
    digest, name = sidecar_digest(sidecar_text)
    computed = sha256(canonical)
    if computed != digest:
        raise ValueError(f"mismatch computed={computed} sidecar={digest} name={name}")
    if computed.encode("ascii") in canonical:
        raise ValueError("canonical bytes contain their own digest; circular manifest")
    return digest


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--sidecar", required=True)
    args = parser.parse_args(argv)
    canonical_path = Path(args.canonical)
    sidecar_path = Path(args.sidecar)
    if not canonical_path.is_file() or not sidecar_path.is_file():
        print("result=not-produced", file=sys.stderr)
        return 1
    try:
        digest = verify(canonical_path.read_bytes(), sidecar_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"result=failed {exc}", file=sys.stderr)
        return 1
    print(f"result=passed sha256={digest} bytes={canonical_path.stat().st_size} hash-method=sha256 circular=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
