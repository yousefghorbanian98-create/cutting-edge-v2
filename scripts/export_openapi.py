#!/usr/bin/env python3
"""Write the FastAPI OpenAPI document (S-012). Deterministic key order."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps" / "desktop" / "openapi.json"


def main() -> int:
    sys.path.insert(0, str(ROOT / "ai-engine"))
    from ai_engine.main import app

    doc = app.openapi()
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
