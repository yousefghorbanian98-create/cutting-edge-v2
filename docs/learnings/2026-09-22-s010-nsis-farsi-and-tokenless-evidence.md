# 2026-09-22 — S-010: NSIS locale name and evidence that survives token rotation

Steps: S-010 · Branch: arena/01a06951-cutting-edge-v2 · Commits: fadbe2d, 2193db9

## What broke
- Run 35707003767 `tauri build`: `Error in macro MUI_LANGUAGEEX` — `bundle.windows.nsis.languages: ["Persian"]` has no `Persian.nlf` in tauri's bundled NSIS.
- Run 35708714699 went green, but the sandbox token rotated before the smoke JSONL / Cargo.lock could be read: `gh api …/jobs/<id>/logs` → 401/403, artifact zip → 0 bytes (blob storage unreachable).

## Root cause
- NSIS names Persian `Farsi` (`Contrib\Language files\Farsi.nlf`); tauri-bundler ships `English.nsh` etc. but no `Farsi.nsh`, so the locale needs both the NSIS name and a `customLanguageFiles` entry (plain `${PRODUCTNAME}` strings, not handlebars).
- Job logs and artifacts are auth-gated; only check-run annotations and the run page are public. Evidence emitted only inside the log is lost to the loop whenever the app token expires.

## Rule
- Persian installer = `languages: ["English","Farsi"]` + `customLanguageFiles.Farsi: nsis/Farsi.nsh` whose key set equals tauri's `English.nsh` (locked by `test_tauri_skeleton.py`).
- Every fact a reviewer needs (smoke pass count, installer name/size/sha256, lockfile digest) must be a `::notice`/`::error` annotation or job-summary block, never only a log line — windows job steps 18 and 20 in `ci.yml`; read via `api.github.com/repos/…/check-runs/<job>/annotations`.
