# 2026-09-22 — S-009 first real CI run: Skip ≠ Pass, in both directions

## What broke
- `ci / ubuntu` and `ci / windows` failed at the pytest step on run #1 although the same tests were green in the sandbox and in a fresh local clone.
- Job logs/artifacts could not be read: the sandbox GitHub token expired mid-run (401), and logs require auth.

## Root cause
- `test_static_stage_green_on_clean_tree` ran the full gate; in the sandbox `cargo-clippy` was `MISSING` (accepted), on GitHub runners cargo exists so the check *ran* against a crate that cannot compile before S-010 → FAIL. The sandbox's "green" was a MISSING masquerading as pass — the exact trap the gate was built to expose, this time in the test harness itself.
- Windows tests used `bash` + `os.killpg`; never exercised before because no Windows runner existed.
- Diagnostics depended on authenticated log access.

## Rule
- A test that tolerates `MISSING` locally must pin the same behaviour in CI: either `--skip` the check it does not own (and give that check its own owner-job test) or force it in both places. Never let environment presence decide pass/fail silently.
- Every OS-specific branch in tests (`bash`, signals, paths) gets exercised by the job that owns that OS before the step is GREEN; `unverified:windows` must be listed explicitly until then.
- CI failures must surface as **public** check-run annotations (`scripts/ci/junit_annotate.py`, gate `::error`) so the loop can self-diagnose without a token; token expiry is a known Arena failure mode (2nd occurrence).
