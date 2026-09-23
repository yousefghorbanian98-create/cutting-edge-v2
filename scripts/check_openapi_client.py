#!/usr/bin/env python3
"""S-012 drift check: committed OpenAPI client must match a fresh generation.

Exit 0 = match. Exit 1 = drift. Exit 2 = generator or FastAPI missing (MISSING, not PASS).
"""

from __future__ import annotations

import filecmp
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "apps" / "desktop"
SPEC = DESKTOP / "openapi.json"
CLIENT = DESKTOP / "src" / "lib" / "openapi"
ENTRY = DESKTOP / "src" / "lib" / "api.ts"
PAGE = DESKTOP / "src" / "app" / "page.tsx"
BARREL = "/** Generated entry for the OpenAPI client. Do not edit. Do not hand-type endpoints. */\nexport * from './openapi';\n"


def _missing(msg: str) -> int:
    print(msg)
    return 2


def _generator() -> Path | None:
    name = "openapi-ts.cmd" if os.name == "nt" else "openapi-ts"
    cand = DESKTOP / "node_modules" / ".bin" / name
    return cand if cand.exists() else None


def _fresh_spec() -> dict:
    sys.path.insert(0, str(ROOT / "ai-engine"))
    from ai_engine.main import app

    return app.openapi()


def _diff_tree(left: Path, right: Path) -> list[str]:
    cmp = filecmp.dircmp(left, right)
    problems: list[str] = []

    def walk(node: filecmp.dircmp, rel: str) -> None:
        for name in node.diff_files:
            problems.append(f"differs: {rel}{name}")
        for name in node.left_only:
            problems.append(f"only in fresh: {rel}{name}")
        for name in node.right_only:
            problems.append(f"only in committed: {rel}{name}")
        for name, child in node.subdirs.items():
            walk(child, f"{rel}{name}/")

    walk(cmp, "")
    return problems


def main() -> int:
    gen = _generator()
    if gen is None:
        return _missing("openapi-ts not installed (pnpm install; @hey-api/openapi-ts is a desktop devDependency)")
    if not SPEC.exists() or not CLIENT.is_dir() or not ENTRY.exists():
        print("committed OpenAPI client is missing")
        return 1
    try:
        fresh = _fresh_spec()
    except ImportError as exc:
        return _missing(f"cannot import the API to export OpenAPI: {exc}")
    committed = json.loads(SPEC.read_text(encoding="utf-8"))
    if committed != fresh:
        print("apps/desktop/openapi.json drifted from FastAPI app.openapi()")
        return 1
    if ENTRY.read_text(encoding="utf-8") != BARREL:
        print("apps/desktop/src/lib/api.ts is not the generated barrel")
        return 1
    page = PAGE.read_text(encoding="utf-8")
    if "from '@/lib/api'" not in page or "pollJob" not in page or "fetch(" in page:
        print("apps/desktop/src/app/page.tsx does not poll through the generated client")
        return 1
    with tempfile.TemporaryDirectory(prefix="ce-openapi-") as tmp:
        out = Path(tmp) / "client"
        rc = subprocess.run(
            [str(gen), "-f", str(DESKTOP / "openapi-ts.config.ts"), "-i", str(SPEC), "-o", str(out), "--no-log-file"],
            cwd=DESKTOP,
            check=False,
        ).returncode
        if rc != 0 or not out.is_dir():
            print(f"openapi-ts failed (exit {rc})")
            return 1
        problems = _diff_tree(out, CLIENT)
    if problems:
        print("generated client drifted:")
        print("\n".join(problems))
        return 1
    print("openapi client matches FastAPI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
