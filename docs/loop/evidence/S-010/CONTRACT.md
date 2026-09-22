# CONTRACT — S-010 — Tauri walking skeleton that compiles and ships a first .exe

> Builder: Supervisor session (autonomous chain). Deps: S-007 GREEN, S-009 GREEN. Closes BUG-10, BUG-16.

## Acceptance Criteria

| # | Criterion | Proof |
|---|-----------|-------|
| AC-1 | `apps/desktop/src-tauri` is a compilable Tauri 2 crate: `tauri-build` + `build.rs`, no Tauri-1 `shell-open` feature, `lib.rs` (`run()`, commands `system_status` / `app_version`, pure `is_healthy`/`status_from` with 5 Rust unit tests) + thin `main.rs`; `cargo fmt --check`, `cargo clippy --all-targets -D warnings`, `cargo test` **hard** on `ci / windows` (`continue-on-error` removed, `xfail` marker in `test_gate.py` deleted) | `tests/unit/test_tauri_skeleton.py::test_cargo_manifest_is_tauri2_shape`, `::test_lib_exposes_the_two_commands_and_health_rule`, `test_ci_workflows.py::test_windows_job_steps`; CI windows job log |
| AC-2 | `tauri.conf.json`: `devUrl` + `beforeDevCommand`, `beforeBuildCommand: pnpm build` + `frontendDist: ../out`, window `main` titled **Cutting Edge** (1400×900, min 1024×640, dark, surface-0 background), `bundle.targets: ["nsis"]`, per-user install, English+Persian with selector, MIT `licenseFile`, icon list incl. `.ico`; version identical in `tauri.conf.json` / `Cargo.toml` / `package.json` | `::test_tauri_conf_wiring`, `::test_bundle_targets_nsis_per_user_with_persian`, `::test_version_is_single_sourced_across_manifests` |
| AC-3 | Capabilities minimal: exactly one file, `windows: ["main"]`, `permissions: ["core:default"]` | `::test_capabilities_minimal` |
| AC-4 | Icon set (`32x32`, `128x128`, `128x128@2x`, `icon.png`, `icon.ico` 16–256) produced by a dependency-free deterministic generator `scripts/make_icons.py`; committed pixels == generator output (`--check`), enforced by gate check `icons`; glyph coherent with DESIGN.md (indigo→violet, ✦) | `::test_icons_regenerate_identically`, `::test_icon_files_have_expected_dimensions_and_alpha`, `::test_make_icons_check_detects_drift`; gate `icons` PASS |
| AC-5 | **Real test on `ci / windows`:** `pnpm exec tauri build` → `*_x64-setup.exe`; `scripts/ci/installer_smoke.ps1` silently installs (`/S`, no UAC), asserts exe + `uninstall.exe` + HKCU uninstall key (`DisplayName = Cutting Edge`) + Start-Menu shortcut, launches the installed exe and waits for `MainWindowTitle == "Cutting Edge"`, checks working set < 400 MB, kills it, asserts no orphan, silently uninstalls and asserts dir/registry/shortcuts gone — every check as a JSON line in `reports/installer-smoke.jsonl` (uploaded) | `::test_installer_smoke_script_covers_the_step_contract`, `::test_installer_smoke_script_parses_in_pwsh` (windows); CI step "Installer smoke"; artifact `windows-evidence/installer-smoke.jsonl` |
| AC-6 | Downloadable `.exe` on every push: artifact `cutting-edge-windows-x64-setup` (30 days) | CI run artifacts list |
| AC-7 | `Cargo.lock` committed (captured from the first green runner build, since the authoring sandbox has no cargo) so builds are reproducible | second commit of this step; `git ls-files apps/desktop/src-tauri/Cargo.lock` |

## Non-Goals
| # | Not in this step | Owner |
|---|------------------|-------|
| NG-1 | Custom titlebar, window-state persistence, drag region | S-058 |
| NG-2 | Native dialogs / opener / fs permissions, CSP | S-059 |
| NG-3 | Python sidecar spawn / health-wait | S-060 |
| NG-4 | Final brand icon, exe metadata polish, version-sync script | S-063 |
| NG-5 | Code signing, updater, release publishing | S-027 / S-098 |
| NG-6 | Frontend calling `invoke()` (still polls FastAPI `/health`) | S-012 / S-076 |

## U-decisions
None (defaults from ADR-0006: product name "Cutting Edge", MIT, fa+en).

## Environment notes
No cargo/rustc in the build sandbox → AC-1/AC-5/AC-6/AC-7 are verified only on `ci / windows`. Ledger stays REVIEW until that job is green on the pushed commit; local half (10 pytest + gate 13/0/0/1) is recorded in EVIDENCE.md.
