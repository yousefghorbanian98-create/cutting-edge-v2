# EVIDENCE — S-010 — Tauri walking skeleton that compiles and ships a first `.exe`

Builder: this chat (Builder). Local half: `local-linux` (no cargo). Runner half: `ci / windows` on `arena/01a06951-cutting-edge-v2`.

## Commits
| sha | what |
|-----|------|
| `4f0c628` … `5c16396` | crate (`Cargo.toml`, `build.rs`, `lib.rs`, `main.rs`), `tauri.conf.json`, capability, icons + `scripts/make_icons.py`, gate check `icons`, `installer_smoke.ps1`, windows job hardening (fmt/clippy/test hard, `tauri build`, smoke, artifacts), `test_tauri_skeleton.py` |
| `fadbe2d` | NSIS locale fix: `languages: ["English","Farsi"]` + `customLanguageFiles.Farsi = nsis/Farsi.nsh` (tauri's NSIS has `Farsi.nlf`, no `Persian.nlf`) |
| `2193db9` | evidence made API-readable: installer-smoke table + installer sha256 + Cargo.lock digest as public check-run annotations / job summary |

## CI
| run | commit | ubuntu | windows | loop-audit |
|-----|--------|--------|---------|------------|
| [35707003767](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35707003767) | `5c16396` | ✅ | ❌ step 17 `tauri build`: `Error in macro MUI_LANGUAGEEX` — `Persian.nlf` missing in tauri's bundled NSIS | ✅ |
| [35708714699](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35708714699) | `fadbe2d` | ✅ | ✅ job `106683814048` — steps 12–21 all success | ✅ |
| [35711041909](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35711041909) | `2193db9` | ✅ (65 unit + 15 Playwright, junit `0 failed`) | ✅ job `106691418725` (10 m 7 s) — 92 pytest, fmt, clippy, cargo test, icons, tauri build, smoke **17/17** | ✅ (verify_ledger, supervise, steps drift) |

### `ci / windows` step → acceptance-criterion map (job 106691418725, all `success`)
| # | step | proves |
|---|------|--------|
| 10–11 | pytest (real media + live uvicorn, no GPU) → junit; annotation `0 failed / 92 total` | regression guard — unchanged behaviour of the backend on Windows |
| 12 | Frontend build (Turbo → `next build` export) | `frontendDist: ../out` exists before `generate_context!()` |
| 13 | `cargo fmt --check` (hard) | AC-1 |
| 14 | `cargo clippy --all-targets -D warnings` (hard, no `continue-on-error`) | AC-1, closes BUG-16 |
| 15 | `cargo test` (5 unit tests: `is_healthy` / `status_from` rules) | AC-1 |
| 16 | `scripts/make_icons.py --check` | AC-4 on a second OS (byte-identical icons) |
| 17 | `pnpm exec tauri build` → `Cutting Edge_2.0.0_x64-setup.exe` | AC-2, AC-5, closes BUG-10 |
| 18 | Cargo.lock → annotation `114995 bytes sha256 01B0A06DCC1724B91A5C27F60CD98A5BD1EEFB53ECFD37ED81C96BAE4E6E34A6` + gzip/base64 in job summary | AC-7 (capture) |
| 19 | Installer smoke (`scripts/ci/installer_smoke.ps1`) | AC-5 |
| 20 | annotations: `installer smoke: 17/17 checks ok`; `installer: Cutting Edge_2.0.0_x64-setup.exe 2.02 MB sha256 6C75AB20927CFD430F1570D3599E95750DB246DD4DB8FA97FCB4E054AEBE9E96` | AC-5 evidence readable without a token |
| 21 | upload `cutting-edge-windows-x64-setup` (2,095,337 B, 30 days) | AC-6 |
| 22 | upload `windows-evidence` (junit + `installer-smoke.jsonl`, 29.2 KB) | AC-5 evidence archive |

Public sources (no token needed): `https://api.github.com/repos/yousefghorbanian98-create/cutting-edge-v2/check-runs/106691418725/annotations`, `…/actions/runs/35711041909/jobs`.

### The 17 installer-smoke checks (all `ok: true`)
`installer-exists` · `installer-version-info` (ProductName `Cutting Edge`, FileVersion `2.0.0`) · `install-exit-0` (`/S`, no UAC — `RequestExecutionLevel user`) · `installed-exe` (`%LOCALAPPDATA%\Cutting Edge\Cutting Edge.exe`) · `uninstaller-present` · `uninstall-registry-key` (`HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Cutting Edge`) · `registry-display-name` · `start-menu-shortcut` · `exe-version-info` · `app-still-running` · `window-title` (`MainWindowTitle == "Cutting Edge"`) · `shell-working-set-lt-400mb` · `no-orphan-process` · `uninstall-dir-removed` · `uninstall-registry-removed` · `uninstall-shortcut-removed` · `uninstall-desktop-shortcut-removed`.

Artifacts of run 35711041909: `cutting-edge-windows-x64-setup` (2 MB, digest `sha256:4283704c…c319` of the zip), `windows-evidence` (29.2 KB), `ubuntu-evidence` (230 KB), `gitleaks-results.sarif`.

## Local half (this sandbox, `local-linux`)
- `tests/unit/test_tauri_skeleton.py` — 10 passed, 1 skipped (`test_installer_smoke_script_parses_in_pwsh` is windows-only). Covers AC-1 (manifest/lib shape), AC-2 (conf wiring, NSIS block: `currentUser`, `["English","Farsi"]`, `customLanguageFiles`, selector, MIT licence, icons, single-sourced version 2.0.0), AC-3 (one capability, `core:default`), AC-4 (icons regenerate identically, dimensions/alpha, `--check` detects drift), AC-5 (smoke script covers the contract), and the Farsi language file: 27 `LangString` keys == tauri-bundler `English.nsh` key set, no handlebars.
- `tests/unit/test_ci_workflows.py` — 11 passed (windows job order: frontend build → clippy → tauri build → smoke; cargo steps not advisory; SHA-pinned actions; referenced paths exist).
- `tests/unit/test_gate.py` — `xfail` marker for `cargo-clippy` deleted; the check is owned by `ci / windows` (skip with owner elsewhere).
- `scripts/gate.py --stage static` — 13 pass / 0 fail / 0 missing / 1 skip (`cargo-clippy`, owner windows job); new `icons` check PASS.

## Decisions taken inside the step
- **Persian installer UI kept** (not deferred): NSIS's language name for Persian is `Farsi` (`Farsi.nlf`); tauri-bundler ships no `Farsi.nsh`, so `apps/desktop/src-tauri/nsis/Farsi.nsh` provides the 27 strings with `${PRODUCTNAME}` placeholders (custom files are not handlebars-rendered).
- Identifier `com.cuttingedge.app` unchanged — tauri prints a non-fatal `.app` suffix warning; renaming would touch ADR-0007 and is a P6 polish item (S-063).
- Evidence path: blob-hosted logs/artifacts are unreachable from the sandbox and the per-job log endpoint needs admin rights once the app token rotates, so every fact needed for review is emitted as a public check-run annotation or job-summary block.

## Carried / open
| item | owner |
|------|-------|
| AC-7 second half: commit `apps/desktop/src-tauri/Cargo.lock` (sha256 `01B0A06D…34A6`, 114995 B — identical to run 35711041909) | committed by ci/windows via contents API as `40efd7b` (blob + job-summary body unreachable from the sandbox). `--locked` is the follow-up commit; proof is the next `ci / windows` clippy/test/tauri build. BUG-17 stays OPEN until that run is green. |
| `.app` identifier warning | S-063 |
| Node-20 action pin deprecation warnings (checkout/setup-node/setup-python/upload-artifact/pnpm) | Dependabot → S-009 follow-up |
