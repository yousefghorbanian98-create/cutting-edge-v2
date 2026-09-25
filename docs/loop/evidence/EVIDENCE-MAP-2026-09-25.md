# Evidence map — 2026-09-25

> This map records evidence events. It does not change the ledger, close a gap, or GREEN any stage. It is not an independent REVIEW.

Overseer process-audit review imported from `60827107400f5127123714d186ebdbf913b3c01b`:

```text
docs/loop/evidence/RETRO-AUDIT-2026-09-25-REVIEW.md
```

Verdict of that file: accepted as a process audit only. Not a clearance to continue implementation and not a GREEN.

## Rules that stay open

- Absence from a failure annotation is not a named pass.
- A junit count of `0 failed` is a summary of that report. It does not name each test title as passed.
- A later successful run does not erase an earlier named failure.
- Ubuntu evidence and Windows evidence are different scopes. One does not clear the other.
- Public annotations are not a readable evidence zip. `K-007` stays limited to S-022.
- `BUG-18` stays open. `run_ffmpeg()` still always passes `-y`.
- `user-gpu` stays unverified. `smoke-gpu.ps1` dry-run is not a GPU pass. No tag. No pre-release.
- S-033 is not started.

## Open gaps until named evidence

| owner | gap | last named failure | what would close it | current state |
|---|---|---|---|---|
| S-015 | scroll frame budget `< 0.05` | run `36136231456`, `tests/timeline-canvas.spec.ts`, received `0.06` | a later CI annotation or opened junit that names this test as passed, without loosening `0.05` | open |
| S-023 | cursor lock `<= 1` and fit `scrollWidth <= clientWidth + 1` | runs `36113514991`, `36125925821`, `36128799735`, `36133043615` named `tests/zoom.spec.ts` | a later annotation or opened junit that names this test as passed, without loosening either bound | open. Run `36139485294` did not name it. |
| S-024 | playhead drift `< 1/60` | run `36136231456`, `tests/playback.spec.ts`, received `0.018207077636719138` against `< 0.016666666666666666`. Earlier run `36120355492` received `0.02593685791015643`. | a later annotation or opened junit that names this test as passed, without widening the frame tolerance | open |
| S-026 | three-run visual diff `< 0.001` | run `36113514991`, `e2e/timeline.spec.ts`, ratio `0.002446338383838384` | a later annotation or opened junit that names this test as passed, without loosening `0.001` | open. Run `36139485294` did not name it. |
| S-028 / S-033 / S-086 | BUG-18 overwrite | `ai-engine/src/core/ffmpeg.py` still prefixes `-y` | a named test that refuses an existing output without consent, plus the owner-stage closure | open |
| S-027 | user GPU | no user machine JSON | `smoke-gpu.ps1` on the user GPU, not a dry-run | unverified |

## Evidence event E-2026-09-25-01

This event is separate from the audit and from the failed product run.

| field | value |
|---|---|
| run | `36139485294` |
| url | `https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/36139485294` |
| SHA | `4609ed50729925ea08405f8c1e488b1f1fce1897` |
| commit kind | docs-only audit commit on top of product SHA `aea01788d53500172b40f9bd4efc86af099d833b` |
| conclusion | `success` for Ubuntu, Windows, and `loop-audit` |
| what it is not | not a GREEN, not a named pass list, not a zip the builder opened |

### Ubuntu scope

Command source: `.github/workflows/ci.yml` on that SHA.

- Secret scan, static gate, frontend export build.
- `pytest tests/unit` only. Annotation: `0 failed / 88`. This is not `pytest tests`.
- `pnpm exec vitest run --coverage` in `apps/desktop`. No vitest count was in the annotations read for this event. The step succeeded. That is not a named test list.
- Playwright command, and only these files:

```text
tests/build-artifacts.spec.ts
tests/styling.spec.ts
tests/media-bin.spec.ts
tests/timeline-canvas.spec.ts
tests/playback.spec.ts
tests/clip-drag.spec.ts
tests/trim.spec.ts
tests/split.spec.ts
tests/selection.spec.ts
tests/history.spec.ts
tests/tracks.spec.ts
tests/zoom.spec.ts
tests/sequence.spec.ts
tests/shortcuts.spec.ts
tests/export-dialog.spec.ts
tests/export-progress.spec.ts
e2e/timeline.spec.ts
```

Annotation: `0 failed / 32` across 1 report. The annotation did not list the 32 titles. Therefore this event does not name `tests/timeline-canvas.spec.ts`, `tests/playback.spec.ts`, `tests/zoom.spec.ts`, or `e2e/timeline.spec.ts` as passed.

### Windows scope

Different job. It did not run Playwright.

- `smoke-gpu.ps1` dry-run. Contract check only. Not a GPU pass.
- `pytest tests -m "not gpu"`. Annotation: `0 failed / 124`. GPU-marked tests were excluded.
- `cargo fmt --check`, `cargo clippy -D warnings`, `cargo test` in `src-tauri`. Those steps succeeded. No separate test-name list was retrieved.
- `tauri build` NSIS installer.
- Installer smoke annotation: `17/17`.
- Installer annotation, not an opened zip: `Cutting Edge_2.0.0_x64-setup.exe`, sha256 `5DD537B76F3B0AFC60BA090229B834E513C282F613FC9636FEAB7DD7EA327DB6`.
- Cargo.lock annotation sha256 `01B0A06DCC1724B91A5C27F60CD98A5BD1EEFB53ECFD37ED81C96BAE4E6E34A6`.

### Artifact readability

The counts and checksum above were read from public check-run annotations. Earlier zip downloads of `ubuntu-evidence` and `windows-evidence` returned EOF. This event does not claim those zips were opened. `K-007` is not extended beyond S-022.

### Ubuntu versus Windows

| proof | Ubuntu `36139485294` | Windows `36139485294` |
|---|---|---|
| Playwright files listed above | step succeeded; junit `0 failed / 32`; titles not named as passed | not run |
| `pytest tests/unit` | `0 failed / 88` | not this command |
| `pytest tests -m "not gpu"` | not this command | `0 failed / 124` |
| installer smoke and NSIS | not this job | `17/17`; checksum from annotation |
| user GPU | not run | dry-run only; unverified |

Windows success does not clear an Ubuntu failure, and Ubuntu success does not clear a Windows gap. The previous Ubuntu failure remains a historical fact.

## Historical failure that this event does not rewrite

Run `36136231456` at `aea01788d53500172b40f9bd4efc86af099d833b` concluded `failure`.

- Ubuntu Playwright junit: `2 failed / 32`.
- Named: `tests/timeline-canvas.spec.ts` drop ratio `0.06` against `< 0.05`.
- Named: `tests/playback.spec.ts` drift `0.018207077636719138` against `< 0.016666666666666666`.
- Windows on that run succeeded. That did not clear Ubuntu.
- Installer annotation sha256 on that failed run: `63571B9610060EC1EA88FBD7CE3A1CB77B5D6CF0E6DE3096AB0492A2A5EC9235`.

Those named failures stay in the record even though a later run of the same Playwright command reported `0 failed / 32`.
