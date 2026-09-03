#!/usr/bin/env python3
"""Verify docs/loop/04_LEDGER.md against docs/loop/steps.json.

Rules enforced (exit 1 on any violation):
  1. Every step id in steps.json has exactly one ledger row (and no unknown rows).
  2. status ∈ {TODO, RED, REVIEW, AMBER, GREEN, BLOCKED}.
  3. GREEN requires non-empty `verified_on` AND non-empty `evidence` AND
     docs/loop/evidence/S-xxx/CONTRACT.md AND REVIEW.md whose verdict line says `approved`
     (fresh-reviewer gate, see 08_FINN_LOOP_ADOPTION.md).
  4. GREEN for a step with user == U2 requires `user-gpu` in verified_on.
  5. A step may not be GREEN while any dependency is not GREEN.
  6. BLOCKED requires a note.
  7. iter is a non-negative integer.
  7b. Watchdog (warnings, non-fatal): RED with iter >= 3, REVIEW with iter >= 2.
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
VALID = {"TODO", "RED", "REVIEW", "AMBER", "GREEN", "BLOCKED"}
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
            ev_dir = LOOP / "evidence" / sid
            if not (ev_dir / "CONTRACT.md").exists():
                errors.append(f"{p}: GREEN without evidence/{sid}/CONTRACT.md")
            rv = ev_dir / "REVIEW.md"
            if not rv.exists():
                errors.append(f"{p}: GREEN without evidence/{sid}/REVIEW.md (fresh reviewer)")
            elif not re.search(r"^\s*approved\b", rv.read_text(encoding="utf-8").split("## 3. Verdict")[-1], re.M):
                errors.append(f"{p}: GREEN but REVIEW.md verdict is not 'approved'")
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

    warnings = []
    for sid, r in rows.items():
        it = int(r["iter"]) if r["iter"].isdigit() else 0
        if r["status"] == "RED" and it >= 3:
            warnings.append(f"{sid}: RED after {it} iterations — consider BLOCKED + blockers/{sid}.md")
        if r["status"] == "REVIEW" and it >= 2:
            warnings.append(f"{sid}: 2 review rounds reached — next changes-requested means BLOCKED")
    for w in warnings:
        print("WATCHDOG: " + w)

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
