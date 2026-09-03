#!/usr/bin/env python3
"""Render docs/loop/03_STEPS.md and (idempotently) docs/loop/04_LEDGER.md from docs/loop/steps.json.

Usage:
    python scripts/loop/render_steps.py            # regenerate 03_STEPS.md, add missing ledger rows
    python scripts/loop/render_steps.py --check    # exit 1 if 03_STEPS.md is stale or ledger misses steps

The ledger is append-only per step: existing rows are preserved, new steps get a `TODO` row.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOOP = ROOT / "docs" / "loop"
STEPS_JSON = LOOP / "steps.json"
STEPS_MD = LOOP / "03_STEPS.md"
LEDGER_MD = LOOP / "04_LEDGER.md"

LEDGER_HEADER = """# 04 — Ledger (دفترچه‌ی وضعیت)

> **ماشین‌خوان است.** هر ردیف یک مرحله از `steps.json`. فقط ستون‌های `status`, `iter`, `verified_on`, `evidence`, `notes` را ویرایش کنید.
> `python scripts/verify_ledger.py` این فایل را در CI بررسی می‌کند.
>
> **status ∈ {TODO, RED, REVIEW, AMBER, GREEN, BLOCKED}**
> - `TODO` شروع نشده
> - `RED` در حال کار، تست واقعی قرمز
> - `REVIEW` کد و تست Builder سبز؛ منتظر verdict بازبین تازه (`evidence/S-xxx/REVIEW.md`)
> - `AMBER` کد کامل، منتظر تأیید کاربر (U1/U2/U3) یا تست خارجی
> - `GREEN` تست واقعی سبز + REVIEW approved + شواهد ثبت‌شده (`verified_on` الزامی)
> - `BLOCKED` وابستگی خارجی؛ دلیل در notes
>
> **verified_on** لیستی با کاما از: `ci-ubuntu`, `ci-windows`, `local-linux`, `user-gpu` (ماشین کاربر با GTX 1650).
> **evidence** لینک/مسیر: CI run URL، فایل junit، اسکرین‌شات، JSON خروجی smoke-gpu.ps1.

| id | title | status | iter | verified_on | evidence | notes |
|----|-------|--------|------|-------------|----------|-------|
"""


def load() -> dict:
    return json.loads(STEPS_JSON.read_text(encoding="utf-8"))


def render_steps_md(data: dict) -> str:
    phases = {p["id"]: p for p in data["phases"]}
    codes = data["user_intervention_codes"]
    out: list[str] = []
    out.append("# 03 — Numbered Steps (تولیدشده‌ی خودکار — ویرایش نکنید)\n")
    out.append(f"> منبع: `docs/loop/steps.json` — {len(data['steps'])} مرحله در {len(data['phases'])} فاز. "
               "برای تغییر، JSON را ویرایش و `python scripts/loop/render_steps.py` را اجرا کنید.\n")
    out.append("## کدهای دخالت کاربر\n")
    for k, v in codes.items():
        out.append(f"- **{k}** — {v}")
    out.append("")

    # Summary table
    out.append("## نقشه‌ی کلی\n")
    out.append("| فاز | نسخه | هدف | مراحل |")
    out.append("|-----|------|-----|-------|")
    for p in data["phases"]:
        ids = [s["id"] for s in data["steps"] if s["phase"] == p["id"]]
        out.append(f"| {p['id']} {p['name']} | {p['version']} | {p['goal']} | {ids[0]} → {ids[-1]} ({len(ids)}) |")
    out.append("")

    # Ordered steps
    cur = None
    for s in data["steps"]:
        if s["phase"] != cur:
            cur = s["phase"]
            p = phases[cur]
            out.append(f"\n---\n\n## {p['id']} — {p['name']} → v{p['version']}\n")
            out.append(f"_{p['goal']}_\n")
        out.append(f"### {s['id']} — {s['title']}\n")
        out.append(f"**هدف:** {s['goal']}\n")
        out.append("**فایل‌ها:** " + ", ".join(f"`{f}`" for f in s["files"]) + "\n")
        out.append(f"**تست واقعی (نه فقط عدد):** {s['real_test']}\n")
        out.append(f"**Done when:** {s['done_when']}\n")
        user = s.get("user", "none")
        line = f"**دخالت کاربر:** `{user}`"
        if s.get("decision_default"):
            line += f" — پیش‌فرض در سکوت: _{s['decision_default']}_"
        out.append(line + "\n")
        if s.get("bugs"):
            out.append("**باگ‌های بسته‌شونده:** " + ", ".join(s["bugs"]) + "\n")
        out.append("**وابستگی‌ها:** " + (", ".join(s["deps"]) if s["deps"] else "—") + "\n")
    out.append("")
    return "\n".join(out)


def parse_ledger_ids(text: str) -> set[str]:
    return set(re.findall(r"^\|\s*(S-\d{3})\s*\|", text, flags=re.M))


def ledger_row(s: dict) -> str:
    return f"| {s['id']} | {s['title']} | TODO | 0 |  |  |  |"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    data = load()
    ids = [s["id"] for s in data["steps"]]
    if len(ids) != len(set(ids)):
        print("duplicate step ids in steps.json", file=sys.stderr)
        return 1
    known = set(ids)
    for s in data["steps"]:
        for d in s["deps"]:
            if d not in known:
                print(f"{s['id']} depends on unknown {d}", file=sys.stderr)
                return 1
            if ids.index(d) >= ids.index(s["id"]):
                print(f"{s['id']} depends on later/equal step {d}", file=sys.stderr)
                return 1

    steps_md = render_steps_md(data)
    existing_ledger = LEDGER_MD.read_text(encoding="utf-8") if LEDGER_MD.exists() else LEDGER_HEADER
    missing = [s for s in data["steps"] if s["id"] not in parse_ledger_ids(existing_ledger)]

    if args.check:
        stale = (not STEPS_MD.exists()) or STEPS_MD.read_text(encoding="utf-8") != steps_md
        if stale:
            print("03_STEPS.md is stale — run scripts/loop/render_steps.py", file=sys.stderr)
        if missing:
            print("04_LEDGER.md missing rows: " + ", ".join(s["id"] for s in missing), file=sys.stderr)
        return 1 if (stale or missing) else 0

    LOOP.mkdir(parents=True, exist_ok=True)
    STEPS_MD.write_text(steps_md, encoding="utf-8")
    new_ledger = existing_ledger.rstrip("\n") + "\n" + "\n".join(ledger_row(s) for s in missing) + ("\n" if missing else "")
    LEDGER_MD.write_text(new_ledger, encoding="utf-8")
    print(f"rendered {STEPS_MD.relative_to(ROOT)} ({len(ids)} steps); ledger rows added: {len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
