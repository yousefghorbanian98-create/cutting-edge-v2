# EVIDENCE — S-011 — Loop tooling

Builder. Status: GREEN. Closed after Overseer `approved` r2 @ `4b9c7a3`. CI run 35999861447. `smoke-gpu.ps1 -DryRun` is not a GPU pass.

## What landed

| file | role |
|------|------|
| `scripts/gate.py` | `--stage all` plus real `unit` / `real` runners; `e2e` / `perf` / `chaos` stay MISSING with owner steps |
| `scripts/verify_ledger.py` | `--ledger` / `--steps` / `--skip-render-check` so negative cases do not touch the committed ledger |
| `scripts/smoke-gpu.ps1` | always prints one JSON object (`app_launch`, `backend_health`, `import_ok`, `ok`, `checks`); `-DryRun` exits 0 and does not claim a machine pass; a failed real probe exits 1 after the JSON |
| `.github/workflows/ci.yml` | windows step runs `-DryRun` and rejects a missing key or `ok: true` |
| `tests/unit/test_loop_tooling.py` | AC-1…AC-8 |
| `docs/loop/07_SESSION_HANDOFF.md` | unchanged; the test locks the BATCH BUILDER and OVERSEER prompts |

## Local proof (`local-linux`)

`pytest tests/unit/test_loop_tooling.py tests/unit/test_ci_workflows.py -q`: 20 passed.

Observed `--stage all` rollup on this checkout (cargo skipped):

| stage | status | why |
|-------|--------|-----|
| static | PASS | existing static checks; `cargo-clippy` SKIP (owned by windows) |
| unit | MISSING | `pytest tests/unit -m unit` PASS; `vitest` and `cargo-test` MISSING with a reason, so the stage is not a silent pass |
| real | MISSING | `ModuleNotFoundError: cv2` at collection — not installed in the tooling venv |
| e2e | MISSING | owner S-079 |
| perf | MISSING | owner S-082 |
| chaos | MISSING | owner S-077 |

Negative ledger cases (temp files): GREEN with empty `verified_on` → exit 1; a `steps.json` id with no row → exit 1. Default `verify_ledger.py` still prints `ledger OK`.

## Carried

| item | owner |
|------|-------|
| `pwsh scripts/smoke-gpu.ps1 -DryRun` on a real runner | green windows job [35996988592](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35996988592) @ `273003f`, job `107624150630`. Dry-run succeeded and is not a GPU pass. Pytest 0 failed / 108. Installer smoke 17/17. |
| real GPU probes (`app_launch=true`) | user machine, S-027 / U2 |
| vitest suite | S-013 |
| chaos / perf / tauri-driver | S-077 / S-082 / S-079 |
