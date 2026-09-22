# EVIDENCE — S-101 — ADR log + session learnings (ECC remember/improve) with hygiene tests

Builder: Supervisor session (autonomous chain). Verified on: `local-linux` (sandbox, Python 3.11). No environment-dependent AC → no `unverified:*` carry.

## Red → Green proof (real, not numeric)

| AC | Red state (before) | Green state (after) | How reproduced |
|----|--------------------|---------------------|----------------|
| AC-1 | `docs/adr/` had 0001, 0002 only → `test_adr_or_learnings_adr_format` FAIL (`0003-daisyui-5-for-tailwind-4.md missing`) | 9 ADRs 0001–0009, `python scripts/loop/hygiene.py` → `9 ADRs, 4 learnings, 0 problem(s)` | `pytest tests/unit/test_repo_hygiene.py -k adr_or_learn` |
| AC-2 | README listed 2 rows; no `TEMPLATE.md` → `test_adr_or_learnings_index_complete` FAIL | README rows == files (set equality both ways); `docs/adr/TEMPLATE.md` (MADR short) | same |
| AC-3 | decisions lived only in protocol §5 / steps.json / chat | ADR-0003 DaisyUI 5 · 0004 FFmpeg-first · 0005 PyInstaller sidecar · 0006 `:free` models + keyring · 0007 product defaults (MIT / name / fa / no telemetry) · 0008 Supervisor/Builder loop · 0009 CI as public evidence — each links the enforcing check/card in *Consequences* | files + README |
| AC-4 | learnings validated only by a private ≤ 24-line heuristic in supervise.py | shared `validate_learnings_dir()` (≤ 20 non-empty lines, sections in order, dated kebab filename); 4 entries pass | `test_adr_or_learnings_learnings_format` |
| AC-5 | — | temp tree: ADR without `## Consequences` → error names the file + section; undated `Status` → `Status line` error; 25-line learnings → `> 20`; `bad name.md` → `file name` error | `test_adr_or_learnings_validator_rejects_bad` (tmp_path, 4 negative cases) |
| AC-6 | C13 used its own heuristic; handoff prompt mentioned learnings only | C13 imports `scripts/loop/hygiene.py` (learnings **and** ADR dirs) → `supervise.py` shows `C13 ✅ PASS`; 07_SESSION_HANDOFF names both templates + validator; SESSIONS.md header links both dirs; dead expression `ROOT / "docs" / "learnings"` removed | `python scripts/supervise.py` + grep |

`pytest tests/unit/test_repo_hygiene.py` → **9 passed**; whole `tests/unit` → 37 passed / 1 skipped (cargo, owned by windows job). `ruff check scripts tests` clean; gate static `10 pass / 0 fail / 0 missing / 3 skip`.

## Non-goals respected
- NG-1: no decision invented — every ADR cites the step/protocol section where it was taken (dates = when taken, not today).
- NG-2: `docs/DECISIONS.md` untouched; ADR-0007 points at its rows.
- NG-3: C13 stays WARN until this row is GREEN in the ledger (then `enforced=True` flips it to FAIL automatically — no code change needed).

## Reheal / carry
- `supervise.py` C13 escalation happens on the ledger flip in this same commit; first audit after commit must show C13 PASS (it does: verified pre-commit).
- Future ADR authoring cost: copy TEMPLATE, add README row, run `python scripts/loop/hygiene.py` — < 5 min; documented in ADR README + handoff prompt.
