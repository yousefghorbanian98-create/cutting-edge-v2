# CONTRACT — S-101 — ADR log + session learnings (ECC remember/improve) with hygiene tests

> Builder: Supervisor session (autonomous chain). Deps: S-001 GREEN.

## Acceptance Criteria

| # | Criterion | Proof |
|---|-----------|-------|
| AC-1 | `docs/adr/` holds ≥ 8 ADRs `NNNN-<slug>.md`, unique zero-padded numbers, contiguous from 0001; each has exactly the four MADR-short sections `## Status`, `## Context`, `## Decision`, `## Consequences` (in that order) plus an H1 starting `# ADR-NNNN —`; Status line ∈ {Proposed, Accepted, Superseded by ADR-NNNN, Deprecated} with an ISO date | `tests/unit/test_repo_hygiene.py::test_adr_or_learnings_adr_format` |
| AC-2 | `docs/adr/README.md` table lists every ADR file (number + title + status) and nothing else; `docs/adr/TEMPLATE.md` exists (MADR short, from joelparkerhenderson/architecture-decision-record) | `::test_adr_or_learnings_index_complete` |
| AC-3 | Back-filled decisions cover: locked stack (0001), external audit triage (0002), Tailwind 4 → DaisyUI 5 (0003), FFmpeg-first / MoviePy fallback (0004), Python backend as PyInstaller sidecar (0005), only OpenRouter `:free` models + NIM, key in OS keyring never in git (0006), no telemetry + MIT + "Cutting Edge" + fa default (0007), Supervisor/Builder loop with fresh reviewer and evidence ledger (0008), CI as public evidence: SHA-pinned actions, Skip≠Pass, annotations (0009) | file presence + `README.md` |
| AC-4 | Every `docs/learnings/YYYY-MM-DD-<slug>.md` is ≤ 20 non-empty lines, has the three sections `## What broke`, `## Root cause`, `## Rule`, and a date-prefixed filename; `TEMPLATE.md`/`README.md` exempt | `::test_adr_or_learnings_learnings_format` |
| AC-5 | Negative proof: writing a temp ADR without `## Consequences` (or a learnings file with 25 lines) into a copy of the tree makes the same validator fail with the file name in the message | `::test_adr_or_learnings_validator_rejects_bad` (validator factored into `scripts/loop/hygiene.py`, used by both pytest and supervise C13) |
| AC-6 | `docs/loop/07_SESSION_HANDOFF.md` and `docs/loop/evidence/SESSIONS.md` reference `docs/learnings/` and `docs/adr/`; `supervise.py` C13 uses the shared validator (so a malformed learnings entry is WARN in the audit) | grep + `python scripts/supervise.py` output |

## Non-Goals
| # | Not in this step | Owner |
|---|------------------|-------|
| NG-1 | No new product decisions — ADRs only record decisions already made in steps.json / protocol §5 / DECISIONS.md / ADR-0002 | — |
| NG-2 | No change to `DECISIONS.md` semantics (product defaults table stays; ADRs link to it) | S-099 |
| NG-3 | No escalation of C13 WARN→FAIL yet (done when S-099 also GREEN, per 11_SUPERVISOR §7) | supervisor |

## U-decisions
None.
