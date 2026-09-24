# 2026-09-24 — live enhance still expected 200

Steps: S-012 · Branch: arena/01a0c936-cutting-edge-v2

## What broke
- `ci / windows` run 35986178547 failed one test: `test_muscle_enhance_live_http` got `202`, expected `200`.
- Cargo, installer smoke, and the `.exe` upload were skipped after that pytest failure.

## Root cause
- S-012 moved `/muscle/enhance` to a job, and beat-sync was updated, but `_enhance_over_http` still read the POST body. Ubuntu does not run that real test, so the miss stayed invisible until Windows.

## Rule
- When a route becomes `202`, update every live caller in the same commit. The proof is `pytest -m "not gpu"` on `ci / windows`, not the ubuntu unit job.
