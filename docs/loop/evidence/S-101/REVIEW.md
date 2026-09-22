# REVIEW — S-101 — round 1 — commit (this commit; see ledger)

> Supervisor as independent reviewer (fresh pass: inputs = CONTRACT.md, EVIDENCE.md, `git diff`, hygiene validator output). Reviewer pushes nothing.

CI: run #3 in flight for the previous commit (S-009 r3); this step's tests are pure-Python unit tests that `ci / ubuntu` executes — no environment dependency.
Evidence re-produced by reviewer: **yes** — `python scripts/loop/hygiene.py` → `9 ADRs, 4 learnings, 0 problem(s)`; `pytest tests/unit/test_repo_hygiene.py -k adr_or_learn` → 4 passed; deleted `## Consequences` from a copy of ADR-0005 in a temp dir → validator names `0005-…: sections must be exactly […]; missing/misordered: ['## Consequences']`; `python scripts/supervise.py` → `C13 ✅ PASS`.

## Summary
Back-fills the seven architectural decisions the project had already taken into MADR-short ADRs (0003–0009), adds a template, and replaces two ad-hoc heuristics (supervise C13 and the test) with one shared validator so ADRs and learnings cannot drift in shape. Handoff prompt and sessions log now point at both directories.

## 1. Must fix before GREEN
- None. AC-1…AC-6 reproduced. Read all seven ADRs against protocol §5, steps.json (S-010/S-060/S-086/S-053/S-063/S-085/S-089) and ADR-0002: no new decision introduced (NG-1). Status dates match when the decision was actually taken in the ledger history.

## 2. Should fix soon (non-blocking)
- `[UX]` ADR README is English while the loop docs are Persian-first; acceptable for machine-readable governance docs, but S-011's ONBOARDING should say so explicitly.
- When S-099 lands, add ADR-0010 "DESIGN.md is the single UI authority" (currently only implied by ADR-0003 follow-ups) — listed in the S-099 contract.
- Hygiene validator accepts any `Superseded by ADR-NNNN`; it does not check that the target exists. Cheap to add when the first supersession happens.

## 3. Verdict
approved — all ACs reproduced; validator proven non-decorative by negative cases; no product decision changed.
