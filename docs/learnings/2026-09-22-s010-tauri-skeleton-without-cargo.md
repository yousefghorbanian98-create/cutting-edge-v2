# 2026-09-22 — S-010: Tauri skeleton authored in a sandbox without cargo

## What broke
`src-tauri` could not compile for 3 milestones (Tauri-1 `shell-open` feature, no `tauri-build`/icons/capabilities) and nothing could be verified locally: no rustc/cargo, crates.io and static.rust-lang.org unreachable. GitHub token also expired twice mid-step, blocking push.

## Root cause
The step was treated as "needs cargo" instead of being split into a locally provable half and a runner-owned half; icons were expected from `tauri icon` (needs the CLI's native binary) and `Cargo.lock` from a local resolve.

## Rule
- Split cargo-dependent steps: manifest/config/capability/icon contract pinned by pytest locally; compile/bundle/install proven only by `ci / windows` — ledger stays REVIEW until that job is green.
- `tauri::generate_context!()` embeds `frontendDist` at compile time → build the static export before clippy/test, not only before `tauri build`.
- Generate binary assets with a dependency-free deterministic script plus a `--check` gate (`scripts/make_icons.py`) so committed bytes are provably reproducible on both OSes.
- Installer smoke asserts observable facts (exe, HKCU key, `.lnk`, `MainWindowTitle`, orphans, leftovers) and uninstalls in `finally`.
- Lockfiles the sandbox cannot produce are captured from the runner (log group + artifact) and committed next; then enforce `--locked`.
- Commit locally the moment auth fails; retry push later — never leave step work uncommitted.
