# Coherence audit — 2026-09-26

> This file records an audit. It is not an independent REVIEW. It does not change the ledger, GREEN any stage, loosen a threshold, or turn a failure into a skip. S-033 is not started.

Branch: `arena/01a0c936-cutting-edge-v2`.

Base before this record: `83034045f8bb6ce8bdf3d441be2c479c4575230d`.

Scope read: S-001 through S-032, the last built stage. S-033 remains `TODO`. Lenses: contracts, ledger rows, product code sampled below, tests and fixtures named below, store history, UI tokens and motion, viewport and scroll, accessibility labels present in source, media probe and export, Windows and installer notes, CI evidence policy, security and license, and `K-001` through `K-014`.

## What this commit changed

- Named `K-012`, `K-013`, and `K-014` in the existing `Forward-knowledge compliance` sections of `S-023` through `S-032`.
- No product code change.
- No regression test added. A docs citation is not a behavior fix.
- No ledger edit. No GREEN. No new CONTRACT for an unstarted stage.

## Classification

`no-gap` means the inspected evidence matches the rule. It is not a stage closure.

`must-fix` stays open until named evidence or the owner stage closes it. Absence from a failure annotation is not that evidence.

`deferred` has an owner and a reason. It is not pulled into the current batch.

`blocker` would stop the current batch. None was found that can be fixed inside an owner stage without hiding a threshold, starting `S-033`, or claiming a named pass.

| stage/path | knowledge or rule | observed mismatch | evidence | severity | owner | action | regression or CI proof |
|---|---|---|---|---|---|---|---|
| S-001..S-005, S-007..S-011, S-099..S-101 | K-008 | Historical GREEN rows were not re-run here. | Ledger rows and existing REVIEW files. | no-gap | none | Do not reopen from this audit. | Not re-run. |
| S-001..S-021 contracts | K-008 routing | No `Forward-knowledge compliance` section. These contracts predate the registry. | `docs/loop/evidence/S-001/CONTRACT.md` through `S-021/CONTRACT.md`. | deferred | next reopen of that stage | Do not rewrite GREEN contracts in this audit. | None. |
| S-004 `run_ffmpeg()` | K-001, K-002 | Always prefixes `-y`. | `ai-engine/src/core/ffmpeg.py` lines that build `[ffmpeg, "-y", *args]`. | deferred | S-028, S-033, S-086 / BUG-18 | Do not remove `-y` here. Do not close BUG-18. Do not start S-033. | Existing open bug row. Not closed. |
| S-006 probe | K-003 | Expected width and height fail when the probe returns `None`. Status stays REVIEW. | `tests/helpers/media.py` `assert_playable`. Ledger S-006. | no-gap for the helper; status not closed | S-006 | Do not GREEN. | Helper assertion, not a new test. |
| S-012 job model | K-009, K-011 | Held REVIEW because S-006 is REVIEW. No forbidden runtime stack found. | Ledger S-012. `requirements.txt` search. | no-gap for the hold | S-012 | Do not GREEN. Do not add MLflow, Celery, Kafka, or `ffmpeg-python`. | None new. |
| S-013 store path | K-004 | Direct `useTimelineStore.setState` is banned by test. | `apps/desktop/src/stores/__tests__/history-path.test.ts`. `timelineStore.ts` uses zundo actions. | no-gap for the static ban | S-013 | Do not bypass zundo. | Existing unit test. Not a new pass. |
| S-014..S-021 browser specs | K-005, K-007 | Ledger still says browser proof was unverified when the rows were written. A later junit count is not a named pass. | Ledger notes. Evidence map `36139485294`. | must-fix | S-014..S-021 | Do not GREEN from a missing failure name. | No named pass annotation. |
| S-015 scroll budget | K-006, K-014 fitness rule | Named failure remains. Candidate change does not close it. | Run `36136231456`: `tests/timeline-canvas.spec.ts` drop ratio `0.06` against `< 0.05`. Commit `691e5f9` removed the scroll-time `clientWidth` read. Run `36179227873` job success did not name this test as passed. | must-fix | S-015 | Do not loosen `0.05`. Do not skip. | Threshold unchanged. No new test. |
| S-022 | K-004, K-007 | Contract prose states the store path, but it does not name registry IDs. Annotation exception stays S-022 only. | `docs/loop/evidence/S-022/CONTRACT.md`. REVIEW at `165c6d8`. | deferred | next S-022 contract touch | Do not rewrite the approved review. Do not generalize K-007. | None. |
| S-023 zoom and fit | K-005, K-006 | Historical named failures are not cleared by absence. | Runs `36113514991`, `36125925821`, `36128799735`, `36133043615` named `tests/zoom.spec.ts`. Later runs did not name a pass. Bounds stay `<= 1` and `scrollWidth <= clientWidth + 1`. | must-fix | S-023 | Do not change the selector or the bound. | No named pass. |
| S-024 playhead | K-006 | Media-clock change is a candidate, not closure. | REVIEW `b6b91b6` on target `80155f3`. Runs `36120355492` and `36136231456` named drift above `1/60`. Run `36179227873` succeeded as a job only. | must-fix | S-024 | Do not widen `1/60`. Do not GREEN. | `playbackSync.test.ts` locks the half-frame cap. It is not Playwright proof. |
| S-025 shortcuts | K-006 | No named pass and no named failure in the annotations read for this audit. | Contract and ledger. Playwright file is in the Ubuntu command. | must-fix | S-025 | Absence is not a pass. | None. |
| S-026 visual diff | K-005, K-006 | Named ratio remains above the bound. | Run `36113514991`: `e2e/timeline.spec.ts` ratio `0.002446338383838384` against `< 0.001`. Later runs did not name a pass. | must-fix | S-026 | Do not loosen `0.001`. | No new test. |
| S-027 installer and GPU | K-001, K-014 | No tag. Dry-run is not a GPU pass. No fixed installer-size ceiling was added. | Ledger S-027. `smoke-gpu.ps1` contract note. | deferred | S-027 | `user-gpu` stays unverified. | Windows smoke counts are job events, not user-GPU proof. |
| S-028 export consent | K-001, K-002 | Export refuses an existing final file when overwrite is false, then writes a partial. `run_ffmpeg()` still always passes `-y`. A listed encoder is not GPU available. | `ai-engine/src/export/runner.py` `OverwriteRefused` and `_argv`. `choose_encoder` / `resolve_encoder`. | deferred for BUG-18; must-fix for GPU claim | S-028, S-033, S-086 | Do not close BUG-18. Do not treat an encoder list as available. | Existing local notes are not CI closure. |
| S-029 progress socket | K-001, K-006 | BUG-6 is still OPEN in `06_BUGS.md`. Ledger says local socket evidence, not a named CI pass. | Ledger S-029. Bug table. | must-fix | S-029 / BUG-6 | Do not close the bug from this audit. | None new. |
| S-030, S-031 dialog and progress UI | K-006 | Specs are in the Ubuntu command. No named pass was retrieved. | Contracts and ledger. | must-fix | S-030, S-031 | Do not treat junit `0 failed` as a named pass. | None. |
| S-032 mixdown | K-001, K-003 | Local loudness note is not a named CI pass. `missing` filter is not a skip. | Ledger S-032. Contract. | must-fix | S-032 | Do not skip a missing filter. | None new. |
| UI motion and accessibility | K-006 | Some controls have `aria-label`. `prefers-reduced-motion` is honored in `page.tsx` and `CommandPalette.tsx`. Timeline zoom has no separate reduced-motion proof. | Source search. No new browser run. | must-fix | S-023..S-026 | Do not claim responsive or motion acceptance. | None. |
| Design tokens | K-006 | Three-way token check was not re-run as a new proof here. Prior gate notes said drift `0`. | `packages/design-system/tokens.ts` exists. This audit did not rerun `design_audit.py`. | no-gap for "no token edit"; evidence not refreshed | S-007, S-100 | Do not claim a new token pass. | Not re-run. |
| Iris, anti-slop, HotClip, ffmpeg-skill | K-005, K-006, K-009, K-012, K-013 | No runtime import or vendor copy found. | Registry, architecture doc, requirements search. | no-gap | reference only | Do not vendor. Do not add AGPL code. | None. |
| K-014 .NET proposal | K-014 | Not imported as a tool or CI gate. | Registry row at `8303404`. No `ArchUnitNET`, `Roslyn`, `BenchmarkDotNet`, or `OpenCover` dependency found. | no-gap | future architecture stage, only with a CONTRACT | Do not add a universal Service interface, sealed Codec, warning-as-error, `16ms` without a fixture, or installer size ceiling. | None. |
| CI evidence policy | K-007 | Artifact zip downloads previously returned EOF. Job success is not an opened junit. | Evidence map. This audit did not open a zip. | must-fix | evidence policy; S-009 for readability | Do not extend K-007 past S-022. | No readable zip in this audit. |
| Ubuntu versus Windows | K-007 | The jobs have different commands. | `.github/workflows/ci.yml`: Ubuntu Playwright file list and `pytest tests/unit`; Windows `pytest tests -m "not gpu"`, cargo, NSIS, installer smoke. | no-gap for the split; not a cross-clear | S-009 | One job does not clear the other. | Run `36179227873` is a successful job event only. |
| Action pins | security | Inspected uses are SHA-pinned. | `.github/workflows/ci.yml`. | no-gap | S-009 | Do not float actions to `latest`. | Inspection only. |
| Bug table versus closed rows | evidence hygiene | BUG-7, BUG-8, BUG-13, and BUG-14 remain OPEN in `06_BUGS.md` while ledger notes describe related fixes. | `06_BUGS.md` and ledger S-002 and S-003. | deferred | docs owner, not a product reopen | Do not edit the bug table here. Do not reopen GREEN rows. | None. |
| BUG-3, BUG-5, BUG-12 | later owners | Still OPEN. Not in the current batch. | `06_BUGS.md`. | deferred | S-035, S-074, S-037 | Do not pull them into S-023..S-032. | None. |
| `00_INDEX.md` branch line | handoff | Index can still name a stale branch. This session stays on `arena/01a0c936-cutting-edge-v2`. | Prior audit note. Not switched. | deferred | index owner | Do not switch branches. | None. |
| S-033 | K-012, K-013 | Not started. Receipt, verification, stream consistency, and staging stay with this future owner. | Ledger status `TODO`. | deferred | S-033 | Do not start. | None. |

## Fixed in this audit

- Contract citations only: `S-023` through `S-032` now name `K-012`, `K-013`, and `K-014` as not executed here, or as a rejection of the .NET gate.
- No product mismatch was fixed. The open named failures stay open.

## Deferred

- BUG-18 and `run_ffmpeg()` `-y`: `S-028`, `S-033`, `S-086`.
- HotClip principles: `S-033`, `S-037`, `S-040`, `S-045`, `S-046`, `S-048`, `S-056`, `S-068`, `S-074`, `S-086`.
- K-014 fitness functions that need a new measurement: future architecture stage, only with a CONTRACT, a fixture, a recorded threshold, and CI evidence.
- `user-gpu`: `S-027`.
- BUG-3: `S-035`. BUG-5: `S-074`. BUG-12: `S-037`.
- Historical contracts `S-001` through `S-021`, and the S-022 ID citation: next contract touch, not this commit.
- Bug-table reconciliation for BUG-7, BUG-8, BUG-13, and BUG-14.

## No-gap

- Fail-closed probe helper for expected dimensions.
- Static ban on direct timeline `setState`.
- No Iris, anti-slop, HotClip, or .NET tool in the runtime.
- Export path raises `OverwriteRefused` when overwrite is false. This does not close BUG-18.
- CI action pins inspected are SHA-pinned.
- Ubuntu and Windows commands are different scopes.
- S-033 is not started.
- No threshold was loosened and no failure was skipped.

## Still without named evidence

- `tests/timeline-canvas.spec.ts` drop ratio.
- `tests/zoom.spec.ts` cursor lock and fit.
- `tests/playback.spec.ts` drift.
- `e2e/timeline.spec.ts` three-run visual diff.
- `tests/shortcuts.spec.ts`, `tests/export-dialog.spec.ts`, and `tests/export-progress.spec.ts` as named passes.
- S-014 through S-021 browser specs as named passes.
- Opened junit zip for run `36179227873` and run `36139485294`.
- `user-gpu`.

## Regression tests added

None.

## CI runs that are proof

None in this audit. These remain separate events, not named passes and not GREEN:

- `36136231456` failed. Named drop ratio and playback drift.
- `36139485294` succeeded as a job. Junit counts were not a named pass list.
- `36179227873` succeeded as a job on `80155f3`. Ubuntu, Windows, and `loop-audit` success is not a named playback pass. The S-024 review already says so.

## Evidence plan

1. Keep S-015, S-023, S-024, and S-026 open until an annotation or an opened junit names the test as passed, without changing the bound.
2. Do not read a missing failure name as a pass.
3. Do not start S-033 until its own CONTRACT names `K-012`, `K-013`, and the still-open BUG-18 share.
4. Any new fitness function needs a real fixture, a recorded threshold, and CI evidence. A universal `16ms` rule or installer size ceiling is not added here.
5. Independent review of this file is required before it is treated as accepted. This session does not write that REVIEW.
