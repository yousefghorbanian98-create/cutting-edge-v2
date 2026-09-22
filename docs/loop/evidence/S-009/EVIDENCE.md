# EVIDENCE — S-009 — CI overhaul (in progress: round 2 awaiting push)

Builder: Supervisor session (autonomous chain). Local: `local-linux`. Real runs: GitHub Actions on `arena/01a06951-cutting-edge-v2`.

## Run #1 — commit `e966162` — https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35658637512

| Job | Result | What it proved |
|-----|--------|----------------|
| `loop-audit` | ✅ success (8 s) | AC-4: `verify_ledger.py`, `supervise.py` (read-only), `03_STEPS.md` drift check all green on a hosted runner |
| `ubuntu` | ❌ failure at step 10 "Unit tests (tests/unit)" (job 1 m 38 s) | AC-2 partially: gitleaks ✅ (whole history clean), pnpm/Node/Python setup ✅, `pnpm install --frozen-lockfile` ✅, tooling venv ✅, **static gate ✅ with `--strict-missing`** (21 s). Unit tests failed; Playwright steps skipped as a consequence; `ubuntu-evidence` artifact uploaded (gate log + junit) |
| `windows` | ❌ failure at step 5 "pytest (real media + live server, no GPU)" (job 6 m) | AC-3 partially: Python 3.11 + full `requirements.txt` installed in **75 s** (pip cache cold) — the "1.5 GB / 15 min" risk did not materialise; `imageio_ffmpeg` binary present. pytest failed; Rust steps were skipped because they were ordered after pytest; `windows-evidence` junit uploaded |
| `codeql` (separate workflow) | started | AC-6 trigger confirmed |

**Root-cause analysis without logs** (the sandbox GitHub token expired mid-run, so job logs/artifacts — which need auth — could not be read; annotations are public and were read):
1. `tests/unit/test_gate.py::test_static_stage_green_on_clean_tree` ran the *full* gate including `cargo-clippy`. On GitHub runners `cargo` exists, so the check ran `cargo fmt --check` + `cargo clippy` on `src-tauri`, which cannot compile before S-010 (no `tauri-build`, no icons/capabilities) and whose `main.rs` was not rustfmt-formatted → FAIL → test failed on both runners. In the sandbox the same check was `MISSING` (no cargo) and therefore green — a classic Skip≠Pass trap, now recorded as a learning.
2. Windows additionally: the `real` tests launched `bash scripts/dev-backend.sh` with `start_new_session` / `os.killpg`, which do not exist on Windows.

**Round-2 fixes (commit `325b5a1`, local, push blocked by expired token):**
- `test_static_stage_green_on_clean_tree` runs with `--skip cargo-clippy`; new `test_cargo_clippy_green` is `xfail(strict=True)` on Windows and skipped elsewhere (BUG-16, S-010 deletes the marker). `main.rs` reformatted to rustfmt layout.
- Windows: tests boot `python -m uvicorn ai_engine.main:app` directly and use `terminate()`; Rust toolchain + cache moved *before* pytest so fmt/clippy always report; windows job gets pnpm + `node_modules` so `tsc/biome/turbo/pnpm-audit` are real there too.
- `.gitattributes` `eol=lf` (Windows autocrlf would break `ruff format --check`/`biome ci`).
- `scripts/ci/junit_annotate.py` + gate `::error` lines: failures become **public check-run annotations**, so the loop can diagnose CI even when logs need a token.
- `gate.py` subprocess decoding forced to UTF-8 (Windows cp1252 vs Persian/emoji output).
- Playwright reporters come from `playwright.config.ts` (the inline `--reporter` flag would have dropped the configured junit path).

## Local proofs (this sandbox)
- `tests/unit/test_ci_workflows.py` — 10/10 (AC-1, AC-2 shape, AC-3 shape, AC-4, AC-5, AC-6, AC-7 SHA pins + `# vX` comments + least-privilege permissions, AC-8 referenced paths exist).
- Fresh clone at `e966162` + CI-identical install → `gate.py --stage static --json --strict-missing --skip cargo-clippy` = 10 pass / 0 fail / 0 missing / 3 skip; `pytest tests/unit` = 33 passed.
- `tests/test_security.py` + `tests/real` + `tests/unit` after the Windows refactor = 45 passed (Linux path unchanged).

## Open for GREEN (AC-9)
Run #2 (`325b5a1`) must show `ubuntu` ✅ (incl. `styling.spec.ts` in real Chromium + `home-1440x900.png` artifact — this also finalises S-007) and `windows` ✅ (pytest real-media on Windows + cargo advisory warning). Any new failure → round 3 via public annotations.
