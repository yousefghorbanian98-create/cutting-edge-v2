#!/usr/bin/env python3
"""Verify docs/loop/04_LEDGER.md against docs/loop/steps.json.

Rules enforced (exit 1 on any violation):
  1. Every step id in steps.json has exactly one ledger row (and no unknown rows).
  2. status ∈ {TODO, RED, AMBER, GREEN, BLOCKED}.
  3. GREEN requires non-empty `verified_on` AND non-empty `evidence`.
  4. GREEN for a step with user == U2 requires `user-gpu` in verified_on.
  5. A step may not be GREEN while any dependency is not GREEN.
  6. BLOCKED requires a note.
  7. iter is a non-negative integer.
  8. 03_STEPS.md is not stale (delegates to render_steps.py --check).

Used by: scripts/gate.py --stage static, CI static job, and the loop protocol (docs/loop/02_LOOP_PROTOCOL.md).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "docs" / "loop"
VALID = {"TODO", "RED", "AMBER", "GREEN", "BLOCKED"}
ROW = re.compile(r"^\|\s*(S-\d{3})\s*\|(.*?)\|\s*(\w+)\s*\|\s*(\d*)\s*\|(.*?)\|(.*?)\|(.*?)\|\s*$")


def main() -> int:
    data = json.loads((LOOP / "steps.json").read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in data["steps"]}
    text = (LOOP / "04_LEDGER.md").read_text(encoding="utf-8")

    rows: dict[str, dict] = {}
    errors: list[str] = []
    for ln, line in enumerate(text.splitlines(), 1):
        m = ROW.match(line)
        if not m:
            continue
        sid, _title, status, it, verified, evidence, notes = (g.strip() for g in m.groups())
        if sid in rows:
            errors.append(f"L{ln}: duplicate row {sid}")
        rows[sid] = {"status": status, "iter": it, "verified": verified, "evidence": evidence, "notes": notes, "ln": ln}

    for sid in steps:
        if sid not in rows:
            errors.append(f"missing ledger row for {sid}")
    for sid in rows:
        if sid not in steps:
            errors.append(f"ledger row {sid} not in steps.json")

    for sid, r in rows.items():
        if sid not in steps:
            continue
        s = steps[sid]
        p = f"L{r['ln']} {sid}"
        if r["status"] not in VALID:
            errors.append(f"{p}: invalid status '{r['status']}'")
            continue
        if r["iter"] == "" or not r["iter"].isdigit():
            errors.append(f"{p}: iter must be integer")
        if r["status"] == "GREEN":
            if not r["verified"]:
                errors.append(f"{p}: GREEN without verified_on")
            if not r["evidence"]:
                errors.append(f"{p}: GREEN without evidence")
            if s.get("user") == "U2" and "user-gpu" not in r["verified"]:
                errors.append(f"{p}: milestone/U2 step GREEN without user-gpu verification")
            for d in s["deps"]:
                if rows.get(d, {}).get("status") != "GREEN":
                    errors.append(f"{p}: GREEN but dependency {d} is {rows.get(d, {}).get('status', 'missing')}")
        if r["status"] == "BLOCKED" and not r["notes"]:
            errors.append(f"{p}: BLOCKED without a note")

    chk = subprocess.run([sys.executable, str(ROOT / "scripts" / "loop" / "render_steps.py"), "--check"],
                         capture_output=True, text=True)
    if chk.returncode != 0:
        errors.append("render_steps --check failed: " + (chk.stderr.strip() or chk.stdout.strip()))

    if errors:
        print("LEDGER VERIFY FAILED")
        for e in errors:
            print("  - " + e)
        return 1

    done = sum(1 for r in rows.values() if r["status"] == "GREEN")
    print(f"ledger OK — {done}/{len(steps)} GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
