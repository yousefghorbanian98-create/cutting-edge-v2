# CONTRACT — S-009 — CI overhaul: matrix (ubuntu lint/unit/e2e + windows heavy/tauri), caching, artifacts, all branches

> Builder: Supervisor session (autonomous chain). Card: `docs/loop/steps.json#S-009`. Deps: S-008 GREEN.

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| # | Criterion | Where | Proof |
|---|-----------|-------|-------|
| AC-1 | `.github/workflows/ci.yml` triggers on `push` to `main` + `arena/**` and on `pull_request`; job ids `ubuntu`, `windows`, `loop-audit` exist so branch protection can require `ci / ubuntu` and `ci / windows` | ci.yml | `tests/unit/test_ci_workflows.py::test_triggers_and_job_ids` |
| AC-2 | `ubuntu` job: pnpm (from `packageManager`) + pip caches; runs `python scripts/gate.py --stage static --json --strict-missing` (skipping only `cargo-clippy`, which the windows job owns), `pytest tests/unit`, `pnpm build`, Playwright chromium (`build-artifacts.spec.ts` + `styling.spec.ts`), and uploads `junit.xml`, `playwright-report/`, and `home-1440x900.png` as artifacts | ci.yml | `::test_ubuntu_job_steps` |
| AC-3 | `windows` job: Python 3.11 + full `requirements.txt` (pip cache), FFmpeg available (imageio-ffmpeg binary), `pytest -m "not gpu" tests` with junit upload; Rust stable + `Swatinem/rust-cache`; `cargo fmt --check` + `cargo clippy -D warnings` in `apps/desktop/src-tauri` (marked `continue-on-error: false`); step names contain `cargo` | ci.yml | `::test_windows_job_steps` |
| AC-4 | `loop-audit` job: `python scripts/verify_ledger.py` and `python scripts/supervise.py` (read-only, no `--write`) run on ubuntu and fail the job on exit ≠ 0 | ci.yml | `::test_loop_audit_job` |
| AC-5 | Secret scanning in CI: `gitleaks/gitleaks-action` step (full history `fetch-depth: 0`) in the ubuntu job, plus `.gitleaks.toml` with the OpenRouter/NIM/GitHub token rules and allow-list for the test probe pattern `sk-or-v1-TEST` | ci.yml, .gitleaks.toml | `::test_gitleaks_wired` |
| AC-6 | `.github/workflows/codeql.yml` analyses `python` and `javascript-typescript` on push/PR/weekly schedule; `.github/dependabot.yml` covers `pip` (ai-engine), `npm` (root), `cargo` (src-tauri), `github-actions`, weekly, with grouped minor/patch updates | codeql.yml, dependabot.yml | `::test_codeql_and_dependabot` |
| AC-7 | Every third-party action is pinned to a full commit SHA with a `# vX` comment (supply-chain rule); `permissions:` block is least-privilege at workflow top (`contents: read`) with job-level elevation only where required (CodeQL `security-events: write`) | all workflows | `::test_actions_pinned_by_sha_and_permissions` |
| AC-8 | Workflows are valid YAML and every `run:` referencing a repo script/path points at a file that exists in the tree (`scripts/gate.py`, `scripts/verify_ledger.py`, `scripts/supervise.py`, `tests/unit`, `apps/desktop`) | all workflows | `::test_referenced_paths_exist` |
| AC-9 | After push: the `ci` workflow run for the S-009 commit is visible via `gh run list --branch arena/01a06951-cutting-edge-v2` and its `ubuntu` + `loop-audit` jobs conclude `success` (the `windows` job is observed and its result recorded honestly — heavy pytest may need a follow-up hotfix card, not a silent skip) | GitHub Actions | `EVIDENCE.md` run URL + `gh run view` output |

## Non-Goals (الزام‌آور)

| # | Not in this step | Why | Owner |
|---|------------------|-----|-------|
| NG-1 | No `release.yml` publishing an installer — there is no installer yet; `release.yml` lands with S-027 (tag → build → pre-release) once S-010 makes `tauri build` succeed | walking skeleton first | S-010 / S-027 |
| NG-2 | No changes to application code (`ai-engine/src`, `apps/desktop/src`); only workflows, `.gitleaks.toml`, `.github/dependabot.yml`, tests, docs, and the small `scripts/dev-backend.*` pin sync from S-008 | scope | — |
| NG-3 | No `tauri build` in CI yet (Cargo.toml lacks `tauri-build`/icons/capabilities) — windows job runs `cargo fmt/clippy` on the crate only; if the crate does not compile without the Tauri context, the step is `continue-on-error: true` **with an explicit `::warning`** and a BUG card, never silently green | S-010 owns the crate | S-010 |
| NG-4 | No branch-protection API changes (token lacks admin scope) — `done_when` is satisfied by stable job ids | permissions | user (U-decision when publishing) |
| NG-5 | No GPU tests in CI (`-m "not gpu"`); GPU smoke stays on the user's machine (`smoke-gpu.ps1`, S-027) | hardware | S-027 |

## Reheal layers touched
L7 (CI as the outer self-check): every push produces machine-readable evidence (junit, gate JSON, screenshots) that the ledger can cite.

## Risks / unknowns
- Windows runner: `pip install -r requirements.txt` pulls mediapipe/faster-whisper (~1.5 GB) — mitigated by pip cache keyed on `requirements.txt` hash; first run may be 10–15 min.
- Playwright on ubuntu needs `npx playwright install --with-deps chromium` (~150 MB, cached by `~/.cache/ms-playwright` key).
- `styling.spec.ts` was never executed in a browser (sandbox lacked Chromium) — the first CI run is its real red/green moment; a failure reopens S-007 as RED per the addendum.
- `gh` token in the sandbox may lack `actions:read` — AC-9 evidence then falls back to the public Actions URL recorded in EVIDENCE.md and verified next session.

## U-decisions
None (`user: none`).
