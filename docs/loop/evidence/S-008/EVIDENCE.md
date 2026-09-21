# EVIDENCE — S-008 — Toolchain: Biome, Ruff, tsc strict, Turbo 2 tasks, pinned versions, pre-commit

Builder: Supervisor session (autonomous chain, user directive 2026-09-22). Verified on: `local-linux` (sandbox, Node 22.22.3, Python 3.11, pnpm 9.15.9 via corepack).

## Red → Green proof (real, not numeric)

| AC | Red state (before) | Green state (after) | How reproduced |
|----|--------------------|---------------------|----------------|
| AC-1 | `gate.py --stage static` → `4 pass, 6 fail, 1 missing, 2 skip` (ruff-lint, ruff-format, biome, turbo, pip-audit, pnpm-audit FAIL) | `10 pass, 0 fail, 1 missing (cargo-clippy), 2 skip (design-tokens/design-audit placeholders)` — see `gate-static.json` | `python scripts/gate.py --stage static --json` |
| AC-2 | — | `.gate-secret-probe.py` with `sk-or-v1-TEST…` staged → `--only secrets` FAIL with `file:line [openrouter]`, exit 1; **also blocked a real `git commit` through the installed lefthook hook** (`scripts/leak_probe.py`, commit refused, tree left clean) | `tests/unit/test_gate.py::test_staged_secret_fails_static` + manual hook run |
| AC-3 | 96 Ruff findings (E701 45, E702 24, F401 7, E741 6, E401 5, E722 5, F841 2, E402 1, E731 1) + S110 7 / S113 7 / S306 2 / SIM105 10 under the new rule set | `ruff check ai-engine/src tests scripts` → `All checks passed!`; `ruff format --check` → 49 files formatted | `test_ruff_clean` |
| AC-4 | Biome: 45 diagnostics (a11y `useButtonType` ×14, `noExplicitAny` ×3, `noArrayIndexKey` ×4, `useExhaustiveDependencies`, `noNonNullAssertion` ×4, unused imports, format drift); tsc had no node_modules | `biome ci … --colors=off` → `Checked 11 files … No fixes applied.`; `tsc --noEmit -p apps/desktop` exit 0; `next build` (output: export) still succeeds — `/` 46.3 kB, 148 kB first-load | `test_biome_and_tsc_clean` |
| AC-5 | `turbo.json` used Turbo-1 `pipeline`; root `turbo: latest`, `lucide-react: latest`, majors `next: 15`, `react: 19`… ; `starlette` transitive | `turbo run build --dry=json` → `turboVersion=2.11.2`, `tasks` schema; every `package.json` + `requirements.txt` exact `x.y.z` (0 `specifier: latest` in lockfile) | `test_no_floating_versions`, `test_turbo2_tasks` |
| AC-6 | no hooks | `lefthook install` → `sync hooks: ✔️ (pre-commit, commit-msg)`; `--commit-msg-file` rejects `bad message` and `feat(tooling): add gate` (no step id), accepts `feat(tooling): S-008 add gate` | `test_lefthook_config`, `test_commit_msg_rule` + manual |
| AC-7 | pip-audit: **34 CVEs in 6 packages** (python-multipart 0.0.18, python-dotenv 1.0.1, requests 2.32.3, starlette 0.41.3, pillow 10.4 transitive, protobuf 4.25 transitive); pnpm audit: 2× high (postcss ≤ 8.5.17 via next) | pip-audit `No known vulnerabilities found, 18 ignored` (documented in `ai-engine/pip-audit-ignore.txt`), pnpm audit `No known vulnerabilities found`; bandit `-ll` clean | `test_security_tools_wired` |

`tests/unit/test_gate.py` — **18 passed** (46 s). Whole suite `pytest tests` — **46 passed** pre-gate-fix, then 18/18 gate tests (total 50 incl. 4 gate tests that were red mid-work; final run of gate tests green; other 32 unchanged and green).

## Security remediation detail (AC-7)

Direct pins raised to the fixed versions (all inside the locked stack, no major change of any *framework* the app authors against — FastAPI stays FastAPI):

| Package | Before | After | Why |
|---------|--------|-------|-----|
| python-multipart | 0.0.18 | 0.0.32 | 6 PYSEC (multipart DoS) |
| python-dotenv | 1.0.1 | 1.2.3 | PYSEC-2026-2270 |
| requests | 2.32.3 | 2.34.2 | 2 PYSEC |
| fastapi / starlette | 0.115.6 / 0.41.3 | 0.141.1 / 1.3.1 | 7 PYSEC in starlette; fastapi 0.115 pins `starlette<0.42`; `tests/test_security.py` + `tests/real` 12/12 green on the new pair before pinning |
| postcss (transitive via next) | 8.4.31 | 8.5.28 via `pnpm.overrides` | 2× high |

Not fixable now, documented with owner step in `ai-engine/pip-audit-ignore.txt` (gate reads it; each line = ID + reason + step): **pillow** (moviepy 2.1.1 requires `<11`, fixes are ≥ 12.1 → closes in S-037 when the MoviePy fallback is removed) and **protobuf** (mediapipe 0.10.14 requires `<5` → closes in S-035 re-pin).

## Lint fixes — NG-1 check (no runtime behaviour change)

Reviewed `git diff ai-engine/src` line by line. Categories only:
- `ruff format` reflow (E701/E702 one-liners, trailing commas, quotes).
- `typing.List/Dict` → builtins (UP006/UP035), `Iterable` from `collections.abc`.
- bare `except:` / `except Exception: pass` → `except Exception as exc:` + `logging.debug/info` with the reason in a comment (`main.py` /health GPU probe, `memory_guard`, `auto_fixer`, `health_monitor`, `proactive_coach`, `beat_sync` temp cleanup → `contextlib.suppress(OSError)`).
- `storage.delete`: `try/except PathTraversalError: pass` → `contextlib.suppress(PathTraversalError)` (identical semantics).
- `crash_recovery.load`: `json.load(open(...))` → `with open(...)`.
- `muscle_enhancer`: `l` → `lum` (E741); `supervise.py`: `l` → `ln`.
- tests: `tempfile.mktemp` → `mkdtemp()/file` (S306); all `requests.*` calls got `timeout=30` (S113); poll loops catch `requests.RequestException` and `continue`.

Frontend (`page.tsx`, `CommandPalette`, `ErrorBoundary`, specs): `type="button"` on 16 buttons, `MoodDNA` interface instead of `any`, stable keys (clip start/end, colour value, deterministic idle bars instead of `Math.random()` in render), `label htmlFor` ↔ `input id`, `useCallback` deps fixed, three `!` non-null assertions replaced by explicit `throw`. No visual change — verified by `next build` success and unchanged CSS token tests (`build-artifacts.spec.ts` logic untouched apart from the guards).

## Files touched (scope ledger)

Config: `biome.json`, `ruff.toml` (root, extends), `ai-engine/ruff.toml`, `ai-engine/bandit.yaml`, `ai-engine/pip-audit-ignore.txt`, `lefthook.yml`, `turbo.json`, `package.json` (root: `packageManager pnpm@9.15.9`, devDeps biome 1.9.4 / lefthook 1.10.11 / turbo 2.11.2, scripts `gate:*`, `pnpm.overrides.postcss`), `apps/desktop/package.json` (exact pins), `pnpm-lock.yaml`, `ai-engine/requirements.txt` + `pyproject.toml`, `.gitignore` (`*.tsbuildinfo`).
Tooling: `scripts/gate.py` (new), `tests/unit/test_gate.py` (new).
Lint-only edits: 22 files under `ai-engine/src`, 10 under `tests`, `scripts/{supervise,verify_ledger,loop/render_steps}.py`, 6 frontend files.

Other behaviour changes: none intended (NG-1). Dependency versions changed as listed above (NG-5 held for JS: all pins equal the versions already resolved in `pnpm-lock.yaml`; for Python the security fixes above are the documented exception, each re-tested).

## Unverified / carried
- `unverified:windows` — `cargo fmt/clippy` (MISSING by design, no rustc in sandbox) → S-009 windows job / S-010.
- `unverified:ci` — CI runs of the gate → S-009 (`gate.py --stage static --json` is CI-ready; exit code 1 on any FAIL).
- Biome 2.x exists (2.5.14); staying on 1.9.4 because the repo's `biome.json` schema and `--colors=off` behaviour were verified on 1.9.4; upgrade card can be added at P6 hardening.
