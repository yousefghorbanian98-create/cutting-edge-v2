# ADR-0008 — Numbered steps executed by a Supervisor/Builder loop with contracts, fresh review and an evidence ledger

## Status
Accepted — 2026-09-04

## Context
The user wants the whole remaining path to a published Windows installer numbered, documented and self-verifying with minimal personal involvement, and insisted on *real* functional testing rather than metrics. Prior generated code claimed "done" without proof. Finn-loop and ECC practices were reviewed for adoptable patterns (`docs/loop/08_FINN_LOOP_ADOPTION.md`).

## Decision
- The plan is a machine-readable list of steps `S-001…S-101` in `docs/loop/steps.json`; `03_STEPS.md` is generated from it; `04_LEDGER.md` records status per step and is verified by `scripts/verify_ledger.py` (GREEN requires evidence dir, an `approved` `REVIEW.md`, and GREEN dependencies).
- Every step runs the same loop: SYNC → CONTRACT (AC-N / NG-N, test first) → BUILD → STATIC gate → TEST-REAL → REHEAL check → DEBUG (≤ 5) → REVIEW by a fresh reviewer → EVIDENCE → COMMIT + PUSH (verified with `git ls-remote`).
- A Supervisor audits the repo each session with `scripts/supervise.py` (C1–C16) and turns every `docs/learnings/` entry into a check, rule or card ("improve"). Only two chats exist for the user; the user is asked only for `user≠none` cards (API key, GPU smoke, final approval).
- "Skip ≠ Pass": a check that could not run is `MISSING`/`unverified:<env>` in evidence, never green.

## Consequences
- Positive: nothing is forgotten (every remaining task has a number), quality is enforced by tooling instead of taste, and a new agent can resume from `docs/ONBOARDING.md` + the ledger alone.
- Negative: process overhead per step (contract + evidence + review ≈ 15–25 % of effort); the reviewer is the same model family when no second chat exists, so independence is procedural (fresh context, diff-only) rather than organisational.
- Follow-ups: S-011 loop tooling, C13/C14 escalate WARN→FAIL once S-101/S-099 are GREEN, learnings per session enforced by C13.
