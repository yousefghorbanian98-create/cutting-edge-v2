# S-022 evidence

Ledger row stays `RED`. This file is not a GREEN record and does not approve the stage.

Target SHA: `d9841c706d397a21ed8e752e0ebbb40cc2631d00`

Overseer review read, not imported by this reconcile: `8d77bc10f7868faccfe13f607e0a8fbb7f848a64`

## Final CI

Run `36099355863` completed `success`.

https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/36099355863

| job | id | conclusion |
| --- | --- | --- |
| ubuntu | `107958369066` | success |
| windows | `107958369326` | success |
| loop-audit | `107958369452` | success |

Public check-run annotations, re-read for this reconcile:

- Ubuntu Playwright: `0 failed / 26 total across 1 report(s)`
- Ubuntu unit: `0 failed / 83 total across 1 report(s)`
- Windows pytest: `0 failed / 112 total across 1 report(s)`
- Installer smoke: `17/17 checks ok`
- Installer: `Cutting Edge_2.0.0_x64-setup.exe` `2.04 MB` sha256 `394F31AFBAF1A70725673F1C764CB65A36DFA89AF0411E3764D2BB156648F9BE`

Windows job steps that completed `success`, not skipped:

- pytest
- cargo fmt --check
- cargo clippy -D warnings
- cargo test
- tauri build NSIS
- installer smoke
- installer upload

The Ubuntu Playwright command at this SHA includes `tests/tracks.spec.ts`. The count `26` is that command, not the earlier `24` that omitted the spec.

Public sources:

- https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/36099355863/job/107958369066
- https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/36099355863/job/107958369326
- https://api.github.com/repos/yousefghorbanian98-create/cutting-edge-v2/check-runs/107958369066/annotations
- https://api.github.com/repos/yousefghorbanian98-create/cutting-edge-v2/check-runs/107958369326/annotations

## Artifact gap

`ubuntu-evidence` id `10848803076` and `windows-evidence` id `10848928303` both failed `gh run download` with `EOF`. The job log endpoint also returned `EOF`. Individual testcase names inside the zip were not read.

## Annotation policy for S-022

The user instruction for this reconcile accepts public CI annotations as the evidence basis for S-022 when the blob artifact cannot be opened. That is the same class of decision already used for S-010 after TLS `EOF`.

Accepted here:

- job conclusion
- completed step names
- public annotation counts and installer sha256

Not accepted as a pass:

- a skipped cargo or installer step
- an upload error caused only by a missing exe
- a Playwright count that does not include `tests/tracks.spec.ts`
- a local pass in place of this CI run

This policy does not GREEN S-022, does not change the ledger, and does not start S-023.

## Earlier runs, not the final claim

- `36097690809`: not a pass. loop-audit failed while S-022 was `TODO`. Playwright `1 failed / 24` was the `حذف` name collision.
- `36098306089`: Ubuntu `0 failed / 24` did not list `tests/tracks.spec.ts`. Windows was cancelled. Not S-022 browser evidence.
- `36098714999`: `1 failed / 26`. The lock and analyser test passed. The second test hit the Next route announcer. The locator was scoped before `d9841c7`. Thresholds were not changed.

## Local, not a CI substitute

- `pnpm exec vitest run` in `apps/desktop`: `28` passed / `28`.
- `pnpm exec tsc --noEmit`: passed.
- Local Playwright Chromium download failed with `ECONNRESET`. That is not a pass.
