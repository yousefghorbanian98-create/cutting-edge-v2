#!/usr/bin/env python3
"""Supervisor audit for the Cutting Edge v2 delivery loop.

Run by the SUPERVISOR session (not Builder, not Reviewer). Produces a verdict + action list
based on evidence in git, the ledger, evidence dirs and CI — never on chat claims.

    python scripts/supervise.py                 # audit since last supervisor checkpoint
    python scripts/supervise.py --since <sha>   # audit a specific range
    python scripts/supervise.py --write         # also write docs/loop/evidence/SUPERVISOR/<date>.md
                                                # and move the checkpoint to HEAD

Checks (each yields PASS / WARN / FAIL):
  C1  ledger integrity            verify_ledger.py exit code
  C2  clean tree                  git status --porcelain empty
  C3  commit↔ledger consistency   every commit mentioning S-xxx has a ledger row not TODO;
                                  every non-TODO row has ≥1 commit mentioning it
  C4  one step per commit         a commit must not change status of >1 ledger row
  C5  evidence completeness       REVIEW/GREEN rows have evidence/S-xxx/CONTRACT.md; GREEN also REVIEW.md approved
  C6  scope ledger in commits     commits for a step carry "AC-" and "Other behavior changes"
  C7  test weakening              net removal of assert/expect lines in tests/ or *.test.* within range
  C8  locked stack                forbidden deps in package.json / requirements / Cargo.toml
  C9  repo hygiene                tracked files > 5 MB or forbidden extensions (mp4, exe, pt, onnx, bin)
  C10 secrets                     OpenRouter / generic key patterns in tracked files
  C11 CI status                   latest GitHub Actions run for this branch (via gh; WARN if unavailable)
  C12 stall watchdog              RED iter>=3, REVIEW iter>=2, AMBER older than 72h (by git blame of the row)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "docs" / "loop"
LEDGER = LOOP / "04_LEDGER.md"
CHECKPOINT = LOOP / "evidence" / "SUPERVISOR" / "checkpoint.json"
ROW = re.compile(r"^\|\s*(S-\d{3})\s*\|(.*?)\|\s*(\w+)\s*\|\s*(\d*)\s*\|(.*?)\|(.*?)\|(.*?)\|\s*$")
STEP_RE = re.compile(r"\bS-\d{3}\b")

FORBIDDEN_JS = ["redux", "@reduxjs", "@mui/", "antd", "chakra", "electron", "styled-components", "@emotion", "vue", "svelte", "angular", "bootstrap", "jquery", "mobx", "recoil", "jotai", "shadcn"]
FORBIDDEN_PY = ["ollama", "flask", "django", "transformers>=", "torch==2.5", "tensorflow"]
FORBIDDEN_EXT = {".mp4", ".mov", ".exe", ".msi", ".pt", ".pth", ".onnx", ".bin", ".safetensors", ".zip", ".7z"}
SECRET_PATTERNS = [r"sk-or-v1-[A-Za-z0-9]{20,}", r"nvapi-[A-Za-z0-9_-]{20,}", r"ghp_[A-Za-z0-9]{30,}", r"AKIA[0-9A-Z]{16}"]


def sh(*args: str, check: bool = False) -> str:
    r = subprocess.run(list(args), cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


class Report:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str, list[str]]] = []  # (id, level, title, details)

    def add(self, cid: str, level: str, title: str, details: list[str] | None = None) -> None:
        self.items.append((cid, level, title, details or []))

    @property
    def verdict(self) -> str:
        levels = {lvl for _, lvl, _, _ in self.items}
        if "FAIL" in levels:
            return "STOP — fix before next Builder session"
        if "WARN" in levels:
            return "ATTENTION — proceed, but resolve warnings"
        return "OK — loop is healthy"

    def render(self, since: str, head: str) -> str:
        out = [f"# Supervisor audit — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "",
               f"Range: `{since[:8]}..{head[:8]}`  ", f"**Verdict: {self.verdict}**", "",
               "| # | result | check | details |", "|---|--------|-------|---------|"]
        for cid, lvl, title, det in self.items:
            icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[lvl]
            cell = "<br>".join(d.replace("|", "\\|") for d in det) or "—"
            out.append(f"| {cid} | {icon} {lvl} | {title} | {cell} |")
        actions = [f"- [{cid}] {d}" for cid, lvl, _, det in self.items if lvl != "PASS" for d in (det or ["see check"])]
        out += ["", "## Actions for next session", *(actions or ["- none"]), ""]
        return "\n".join(out)


def read_ledger() -> dict[str, dict]:
    rows = {}
    for ln, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        m = ROW.match(line)
        if m:
            sid, title, status, it, ver, ev, notes = (g.strip() for g in m.groups())
            rows[sid] = {"title": title, "status": status, "iter": int(it or 0), "verified": ver, "evidence": ev, "notes": notes, "ln": ln, "line": line}
    return rows


def ledger_rows_at(rev: str) -> dict[str, str]:
    txt = sh("git", "show", f"{rev}:docs/loop/04_LEDGER.md")
    return {m.group(1): m.group(3).strip() for m in (ROW.match(l) for l in txt.splitlines()) if m}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    head = sh("git", "rev-parse", "HEAD").strip()
    if a.since:
        since = a.since
    elif CHECKPOINT.exists():
        since = json.loads(CHECKPOINT.read_text())["head"]
    else:
        since = sh("git", "merge-base", "HEAD", "origin/main").strip() or sh("git", "rev-list", "--max-parents=0", "HEAD").strip()
    if not sh("git", "cat-file", "-t", since).strip():
        since = sh("git", "rev-list", "--max-parents=0", "HEAD").strip()

    R = Report()
    rows = read_ledger()

    # C1 ledger integrity
    r = subprocess.run([sys.executable, "scripts/verify_ledger.py"], cwd=ROOT, capture_output=True, text=True)
    watchdog = [l.replace("WATCHDOG: ", "") for l in r.stdout.splitlines() if l.startswith("WATCHDOG")]
    R.add("C1", "PASS" if r.returncode == 0 else "FAIL", "Ledger integrity (verify_ledger.py)",
          [] if r.returncode == 0 else [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("-")])

    # C2 clean tree
    dirty = [l for l in sh("git", "status", "--porcelain").splitlines() if l.strip()]
    R.add("C2", "PASS" if not dirty else "WARN", "Working tree clean", dirty[:10])

    # commits in range
    log = sh("git", "log", "--format=%H%x1f%s%x1f%b%x1e", f"{since}..{head}")
    commits = []
    for chunk in log.split("\x1e"):
        if chunk.strip():
            h, s, b = (chunk.strip("\n").split("\x1f") + ["", ""])[:3]
            commits.append({"sha": h, "subject": s, "body": b, "steps": sorted(set(STEP_RE.findall(s)))})

    # C3 commit↔ledger
    det = []
    is_meta = lambda c: c["subject"].startswith(("docs", "review", "chore(loop)", "supervisor"))
    mentioned = {s for c in commits if not is_meta(c) for s in c["steps"]}
    for s in sorted(mentioned):
        if s not in rows:
            det.append(f"{s} referenced in commits but missing from ledger")
        elif rows[s]["status"] == "TODO":
            det.append(f"{s} has commits but ledger still TODO")
    all_log = sh("git", "log", "--format=%s")
    for s, row in rows.items():
        if row["status"] not in ("TODO", "BLOCKED") and s not in all_log:
            det.append(f"{s} is {row['status']} but no commit mentions it")
    R.add("C3", "PASS" if not det else "FAIL", "Commit ↔ ledger consistency", det)

    # C4 one step per commit + C6 scope ledger
    det4, det6 = [], []
    for c in commits:
        if "docs/loop/04_LEDGER.md" in sh("git", "show", "--name-only", "--format=", c["sha"]):
            before = ledger_rows_at(f"{c['sha']}^") if sh("git", "rev-parse", "--verify", "-q", f"{c['sha']}^").strip() else {}
            after = ledger_rows_at(c["sha"])
            changed = [s for s in after if before.get(s, "TODO") != after[s] and s in before]
            if len(changed) > 1:
                det4.append(f"{c['sha'][:8]} changed status of {len(changed)} rows: {', '.join(changed)}")
        if c["steps"] and not c["subject"].startswith(("docs", "review", "chore(loop)")):
            body = c["body"]
            if "AC-" not in body or "Other behavior changes" not in body:
                det6.append(f"{c['sha'][:8]} {c['subject'][:60]} — missing scope ledger (AC-n / Other behavior changes)")
    R.add("C4", "PASS" if not det4 else "FAIL", "One step per commit", det4)
    R.add("C6", "PASS" if not det6 else "WARN", "Scope ledger present in step commits", det6)

    # C5 evidence completeness
    det = []
    for s, row in rows.items():
        d = LOOP / "evidence" / s
        if row["status"] in ("REVIEW", "AMBER", "GREEN") and not (d / "CONTRACT.md").exists():
            det.append(f"{s} {row['status']} without evidence/{s}/CONTRACT.md")
        if row["status"] == "GREEN":
            rv = d / "REVIEW.md"
            if not rv.exists():
                det.append(f"{s} GREEN without REVIEW.md")
            elif "approved" not in rv.read_text(encoding="utf-8").split("## 3. Verdict")[-1][:200]:
                det.append(f"{s} GREEN but REVIEW.md verdict not approved")
            if not row["evidence"]:
                det.append(f"{s} GREEN with empty evidence column")
    R.add("C5", "PASS" if not det else "FAIL", "Evidence completeness (CONTRACT / REVIEW / artifacts)", det)

    # C7 test weakening
    det = []
    for c in commits:
        diff = sh("git", "show", "--format=", "--unified=0", c["sha"], "--", "tests", "apps/desktop/e2e", "*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx", "test_*.py")
        removed = len(re.findall(r"^-\s*(assert\b|expect\()", diff, re.M))
        added = len(re.findall(r"^\+\s*(assert\b|expect\()", diff, re.M))
        skips = len(re.findall(r"^\+.*(pytest\.mark\.skip|\bit\.skip\(|\btest\.skip\(|\bdescribe\.skip\(|\bxit\(|\bxdescribe\(|\bxtest\()", diff, re.M))
        if removed > added:
            det.append(f"{c['sha'][:8]} removed {removed - added} net assertions — verify not weakening")
        if skips:
            det.append(f"{c['sha'][:8]} added {skips} skip markers — must be 'unverified:<reason>' in ledger notes")
    R.add("C7", "PASS" if not det else "WARN", "Test weakening / added skips", det)

    # C8 locked stack
    det = []
    for pj in ROOT.rglob("package.json"):
        if "node_modules" in pj.parts:
            continue
        txt = pj.read_text(encoding="utf-8", errors="ignore").lower()
        for f in FORBIDDEN_JS:
            if f'"{f}' in txt:
                det.append(f"{pj.relative_to(ROOT)} contains forbidden dependency '{f}'")
    for req in list(ROOT.rglob("requirements*.txt")) + list(ROOT.rglob("pyproject.toml")):
        if ".venv" in req.parts or "node_modules" in req.parts:
            continue
        txt = req.read_text(encoding="utf-8", errors="ignore").lower()
        for f in FORBIDDEN_PY:
            if f in txt:
                det.append(f"{req.relative_to(ROOT)} contains forbidden dependency '{f}'")
    R.add("C8", "PASS" if not det else "FAIL", "Locked stack (no foreign UI/state/runtime libs)", det)

    # C9 hygiene
    det = []
    for line in sh("git", "ls-files", "-z").split("\0"):
        if not line:
            continue
        p = ROOT / line
        if Path(line).suffix.lower() in FORBIDDEN_EXT:
            det.append(f"tracked binary: {line}")
        elif p.exists() and p.stat().st_size > 5 * 1024 * 1024:
            det.append(f"tracked file > 5MB: {line} ({p.stat().st_size // 1_048_576} MB)")
    R.add("C9", "PASS" if not det else "FAIL", "Repo hygiene (no media/binaries/large files in git)", det[:10])

    # C10 secrets
    det = []
    tracked = sh("git", "ls-files", "-z").split("\0")
    for line in tracked:
        if not line or Path(line).suffix.lower() in FORBIDDEN_EXT:
            continue
        p = ROOT / line
        if not p.exists() or p.stat().st_size > 2_000_000 or line == "scripts/supervise.py":
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for pat in SECRET_PATTERNS:
            if re.search(pat, txt):
                det.append(f"possible secret in {line} ({pat[:12]}…)")
    R.add("C10", "PASS" if not det else "FAIL", "No secrets in tracked files", det)

    # C11 CI
    branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
    ci = subprocess.run(["gh", "run", "list", "--branch", branch, "--limit", "3", "--json", "status,conclusion,name,headSha,url"], cwd=ROOT, capture_output=True, text=True)
    if ci.returncode != 0 or not ci.stdout.strip():
        R.add("C11", "WARN", "CI status", ["gh unavailable or no runs for this branch — until S-009 lands, CI evidence is absent (Skip ≠ Pass)"])
    else:
        runs = json.loads(ci.stdout)
        bad = [f"{r['name']}: {r['conclusion'] or r['status']} {r['url']}" for r in runs if r.get("conclusion") not in ("success", None) or r.get("status") not in ("completed",)]
        head_runs = [r for r in runs if r["headSha"] == head]
        det = bad[:3]
        if not head_runs:
            det.append("no CI run for HEAD yet — CI evidence absent (Skip ≠ Pass)")
        R.add("C11", "FAIL" if bad else ("WARN" if not head_runs else "PASS"), "CI status (latest runs on branch)", det)

    # C12 stall watchdog
    det = list(watchdog)
    now = time.time()
    for s, row in rows.items():
        if row["status"] in ("AMBER", "REVIEW"):
            blame = sh("git", "blame", "-L", f"{row['ln']},{row['ln']}", "--porcelain", "docs/loop/04_LEDGER.md")
            m = re.search(r"^committer-time (\d+)", blame, re.M)
            if m and now - int(m.group(1)) > 72 * 3600:
                det.append(f"{s} has been {row['status']} for > 72h — {'ask user for U2/U1' if row['status']=='AMBER' else 'run a Reviewer session'}")
    R.add("C12", "PASS" if not det else "WARN", "Stall watchdog", det)

    # Next step suggestion
    nxt = next((s for s, r_ in rows.items() if r_["status"] in ("TODO", "RED")), None)
    rev = [s for s, r_ in rows.items() if r_["status"] == "REVIEW"]
    text = R.render(since, head)
    text += "\n## Queue\n"
    text += f"- Steps awaiting fresh Reviewer: {', '.join(rev) if rev else 'none'}\n"
    text += f"- Next Builder step: {nxt or 'none'}\n"
    green = sum(1 for r_ in rows.values() if r_["status"] == "GREEN")
    text += f"- Progress: {green}/{len(rows)} GREEN\n"
    print(text)

    if a.write:
        out_dir = LOOP / "evidence" / "SUPERVISOR"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M')}.md").write_text(text, encoding="utf-8")
        CHECKPOINT.write_text(json.dumps({"head": head, "at": datetime.now(timezone.utc).isoformat()}, indent=2))
    return 1 if "STOP" in R.verdict else 0


if __name__ == "__main__":
    raise SystemExit(main())
