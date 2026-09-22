# 2026-09-22 — S-010: building a Tauri skeleton in a sandbox that has no cargo

## Context
The authoring sandbox cannot install rustc/cargo (no apt, static.rust-lang.org and crates.io blocked),
yet S-010 must produce a compiling crate, an NSIS installer and a real install/launch/uninstall test.

## What worked
- Split the step into a **local half** (manifest/config/capabilities/icon contract pinned by
  `tests/unit/test_tauri_skeleton.py`, 10 tests) and a **runner half** (`ci / windows`: cargo fmt →
  clippy `-D warnings` → `cargo test` → `tauri build` → `installer_smoke.ps1`). Ledger stays REVIEW
  until the runner half is green — never GREEN on the local half alone.
- `tauri::generate_context!()` embeds `frontendDist` at compile time: the **static export must be
  built before clippy/test**, not only before `tauri build`.
- Icons: a ~150-line dependency-free rasteriser (`scripts/make_icons.py`) with a `--check` mode
  gives deterministic PNG/ICO bytes on Linux *and* Windows → gate check `icons` proves the committed
  binaries match the generator. No Pillow, no `tauri icon`, no binary drift.
- The installer smoke asserts *observable* facts (exe on disk, HKCU uninstall key, Start-Menu
  `.lnk`, `MainWindowTitle`, orphan processes, leftovers) and always runs the uninstall in `finally`
  so a red run never poisons the runner.
- `Cargo.lock` cannot be produced locally: the runner prints it gzip+base64 in a log group and
  uploads it as an artifact; the follow-up commit adds it and switches to `--locked`.

## Pitfalls
- Tauri-1 feature `shell-open` on `tauri = "2"` fails resolution — v2 uses plugins.
- Lints under `-D warnings`: `assert_eq!` on `f32` is `clippy::float_cmp`; unused deps are not a
  clippy error but were pruned anyway (`serde_json` → dev-dependency, `tokio`/`thiserror` dropped).
- GitHub token expired mid-step twice; commit locally first, push when auth returns.
