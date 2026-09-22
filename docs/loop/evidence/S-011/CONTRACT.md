# CONTRACT — S-011 — Loop tooling: gate stages, ledger verifier, smoke-gpu.ps1, handoff template

> Builder. Deps: S-008 GREEN. Makes the loop executable. Does not mark any step GREEN.

## Acceptance Criteria

| # | Criterion | Proof |
|---|-----------|-------|
| AC-1 | `verify_ledger.py` exits 1 when a step is GREEN with an empty `verified_on` | `tests/unit/test_loop_tooling.py::test_green_without_verified_on_exits_1` |
| AC-2 | `verify_ledger.py` exits 1 when a `steps.json` id has no ledger row | `::test_missing_step_id_exits_1` |
| AC-3 | `python scripts/gate.py --stage all --json` reports every stage (`static`, `unit`, `real`, `e2e`, `perf`, `chaos`) as exactly one of PASS / FAIL / MISSING, with a non-empty detail. A stage is never silently OK (no empty report, no status outside that set, SKIP-only rolls up to MISSING) | `::test_stage_all_reports_every_stage` |
| AC-4 | `unit` actually runs `pytest tests/unit -m unit` (PASS/FAIL). The unit tree is scoped so collection does not import real-media modules. `vitest` and `cargo test --locked` are MISSING with a reason when the tool is absent, never omitted | `::test_unit_stage_runs_pytest_and_names_missing_tools` |
| AC-5 | `real` runs `pytest -m real` when the stack imports; a collection `ModuleNotFoundError` is MISSING (named module), an assertion failure is FAIL | `::test_real_stage_is_not_silent` |
| AC-6 | `e2e` / `perf` / `chaos` are MISSING with the owner step (S-009/S-079, S-082, S-077) until those stages exist. They are not PASS | `::test_future_stages_are_missing_with_owner` |
| AC-7 | `scripts/smoke-gpu.ps1` always prints one JSON object with `app_launch`, `backend_health`, `import_ok`, `ok`, `checks`. `-DryRun` exits 0 and sets `dry_run: true` (does not claim the machine passed). A failed real probe exits 1 after printing JSON | `::test_smoke_gpu_script_contract`; `ci / windows` step `smoke-gpu.ps1 -DryRun` |
| AC-8 | Session handoff template remains `docs/loop/07_SESSION_HANDOFF.md` and still contains the BATCH BUILDER and OVERSEER prompts | `::test_handoff_template_present` |

## Non-Goals

| # | Not in this step | Owner |
|---|------------------|-------|
| NG-1 | GPU tests inside CI (`-m "not gpu"` stays). `smoke-gpu.ps1` real probes run on the user machine | S-027 / U2 |
| NG-2 | Chaos probes | S-077 |
| NG-3 | Performance budgets | S-082 |
| NG-4 | Playwright browser install or tauri-driver | S-009 (web e2e already in CI) / S-079 |
| NG-5 | Product code, UI, or stack changes | — |
| NG-6 | Marking S-011 GREEN | Overseer `approved` |

## U-decisions

None.

## Environment notes

No `pwsh` and no cargo in the authoring sandbox. AC-7 execution is `ci / windows` (`-DryRun`). Local proof is the script contract test. `unverified:pwsh` on local-linux until that job is green.
