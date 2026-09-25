# Retrospective audit — 2026-09-25

> Process record only. This file does not change the ledger, a verdict, an acceptance threshold, or product code. No stage is GREEN. S-033 is not started. The next implementation batch has not started.

## Scope

- Branch: `arena/01a0c936-cutting-edge-v2`. The fetched index still names `arena/01a06951-cutting-edge-v2`. That name was not checked out.
- Base product SHA before this audit commit: `aea01788d53500172b40f9bd4efc86af099d833b`.
- Overseer docs fetched, and only these files, from `ed0ba8928ee27b944b36f7aec6c5c0d1b48118b2`: `KNOWLEDGE_REGISTRY.md`, `FORWARD_KNOWLEDGE_GATE.md`, `KNOWLEDGE_REFRESH_AUDIT.md`, `STYLE_MATCH_ARCHITECTURE.md`, `00_INDEX.md`.
- Historical path reviewed: S-001 through S-032, the last built stage. S-033 remains `TODO`.
- Registry lenses read: K-001 through K-011.

## Read

- `docs/loop/KNOWLEDGE_REGISTRY.md`
- `docs/loop/FORWARD_KNOWLEDGE_GATE.md`
- `docs/loop/KNOWLEDGE_REFRESH_AUDIT.md`
- `docs/loop/STYLE_MATCH_ARCHITECTURE.md`
- `docs/loop/00_INDEX.md`
- `docs/loop/04_LEDGER.md` rows S-001 through S-033, read only
- `docs/loop/06_BUGS.md`
- stage contracts S-023 through S-032, and reviews present for S-001 through S-022
- `ai-engine/src/core/ffmpeg.py`, `ai-engine/src/export/runner.py`, `tests/helpers/media.py`
- `.github/workflows/ci.yml` action pins
- public CI annotations for run `36136231456` at `aea01788`

## Status after this audit

- No ledger edit.
- No GREEN.
- No threshold change.
- No failure turned into a skip.
- S-023 implementation is not continued in this commit.
- S-033 is not started.

## Findings

| historical stage/path | new knowledge or reference | observed gap or no-gap | evidence inspected | severity | owner stage or bug | required action |
|---|---|---|---|---|---|---|
| S-023..S-032 batch, started before this audit existed | K-008 | gap | `KNOWLEDGE_REFRESH_AUDIT.md` requires this audit before continuing S-023. Ledger already shows S-023..S-032 as `REVIEW`. No `REVIEW.md` in those evidence dirs. | blocker | process gate, before any next implementation batch | Stop. Do not continue S-023 or start a new stage until the independent overseer accepts this record. Do not rewrite the existing REVIEW rows. |
| S-023..S-032 contracts | K-001..K-011 routing rule | gap | `S-023/CONTRACT.md` has `Forward-knowledge compliance` but does not name registry IDs. The same heading exists in S-024..S-032 contracts. | must-fix | next contract update, not a silent code edit | Before any further implementation, name the applicable registry IDs in the stage CONTRACT. Do not treat the old section as ID compliance. |
| S-004 `run_ffmpeg()` | K-001, K-002 | gap | `ai-engine/src/core/ffmpeg.py` builds `[ffmpeg, "-y", *args]`. `06_BUGS.md` BUG-18 is OPEN. Ledger keeps S-004 GREEN and assigns overwrite to S-028, S-033, S-086. | deferred | S-028, S-033, S-086 / BUG-18 | Do not reopen S-004. Do not widen S-028 to close S-033. Do not remove `-y` in this audit. |
| S-006 probe | K-003 | no-gap for the fail-closed helper; status gap remains | `tests/helpers/media.py` asserts `info["width"] is not None` and `info["height"] is not None` when an expected size is passed. `ffmpeg.py` uses ffprobe JSON first and textual `ffmpeg -i` only after ffprobe is missing. Ledger S-006 is REVIEW, not GREEN. | informational | S-006 | Do not GREEN S-006 from this audit. |
| S-028 encoder selection | K-001 | gap | `choose_encoder()` returns `available` when `h264_nvenc` is merely listed. `resolve_encoder()` downgrades to `libx264` / `missing` only when `probe=True` and `encoder_opens()` fails. A listed encoder is not a GPU pass. `user-gpu` is unverified. | must-fix | S-028, S-027 | Keep the open-probe fallback. Do not treat an encoder list, a Windows job success, or `smoke-gpu.ps1` dry-run as GPU available. |
| S-028 export overwrite | K-002 | gap | BUG-18 is OPEN. S-028 ledger says local overwrite evidence exists and the row is REVIEW. `run_ffmpeg()` still always passes `-y`. | deferred | S-028 share only for its own export path; S-033 and S-086 remain owners of the rest | Do not mark BUG-18 closed. Do not start S-033. |
| S-013..S-022 timeline mutations | K-004 | no-gap for the static ban; gap for UI proof | `apps/desktop/src/stores/__tests__/history-path.test.ts` rejects `useTimelineStore.setState`. S-014..S-021 ledger notes still say browser specs were unverified when those rows were written. Later CI is not a named pass for those specs. | must-fix | S-014..S-021 | Do not bypass zundo. Do not GREEN those rows from a later Windows job label. |
| S-023 zoom and fit | K-005, viewport/scroll geometry | gap | Run `36113514991`: zoom pixel error `95.99999999999997` against `<= 1`. Runs `36125925821` and `36128799735` / `36133043615`: fit `scrollWidth` `1582` then `1617` against `<= 1407`. Run `36136231456` did not name `zoom.spec.ts` in the failure annotations. That absence is not a named pass. Thresholds stay. | must-fix | S-023 | Do not loosen `<= 1` or `scrollWidth <= clientWidth + 1`. Do not continue the fix in this audit commit. |
| S-015 scroll budget | K-005, frame budget | gap | Run `36136231456`, Ubuntu job `108074857498`: `tests/timeline-canvas.spec.ts` received `0.06`, expected `< 0.05`. Junit: `2 failed / 32`. | must-fix | S-015, with S-023 layout as the recent suspect | Do not loosen `0.05`. Do not turn the failure into a skip. |
| S-024 playback sync | K-005, playhead versus media clock | gap | Run `36120355492`: drift `0.02593685791015643` against `< 1/60`. Run `36136231456`: drift `0.018207077636719138` against `< 0.016666666666666666` in `tests/playback.spec.ts`. | must-fix | S-024 | Do not widen the one-frame tolerance. Do not hide a `60` versus display-rate miss. |
| S-026 three-run visual diff | K-005, K-006 | gap | Run `36113514991`: `pixelDiffRatio` `0.002446338383838384` against `< 0.001`. Later runs did not name `e2e/timeline.spec.ts`. That absence is not a named pass. | must-fix | S-026 | Do not loosen `0.001`. Do not seed waveforms from `crypto.randomUUID()` again. |
| S-022 / S-024 selector collision | K-006, real interaction | gap | Run `36110782834` named strict-mode `پخش` versus `پخش سکانس` in `tracks.spec.ts` and `playback.spec.ts`. Current specs use `exact: true`. Later runs did not name that strict-mode failure. That is not a named pass. | deferred | S-022, S-024 | Do not change the selector to hide a failure. Do not claim those specs passed. |
| UI references Iris and anti-slop | K-005, K-006 | no-gap | Search outside `docs/loop` found no Iris, anti-slop, or Hypit runtime import. They are not in `requirements.txt` or `ai-engine/requirements.txt`. | informational | reference only | Do not vendor either repository. Do not replace Playwright, CDP, CI, or installer evidence with a visual camera. |
| S-022 evidence exception | K-007 | no-gap for S-022; gap if reused | S-022 REVIEW and ledger accept public annotations only for that stage after artifact EOF. Runs `36110782834`, `36113514991`, `36120355492`, `36125925821`, `36128799735`, `36133043615`, and `36136231456` were also read from annotations because zip downloads returned EOF. | must-fix | evidence policy; S-023..S-032 | Do not generalize K-007. Annotation text is a failure record, not a pass, and not a substitute for a readable evidence zip. |
| S-001..S-012, S-099..S-101 historical GREEN rows | K-008 | no-gap against rewriting verdicts | Ledger and existing REVIEW files. This audit did not re-run those stages. | informational | none | Do not reopen a GREEN row from this audit alone. Carried bugs stay with their named owners. |
| S-009 / S-010 Windows installer | Windows/installer lens | no-gap for the latest job steps that are named; gap for user GPU and zip readability | Run `36136231456`: Windows job succeeded. Pytest annotation `0 failed / 124`. Installer smoke `17/17`. Installer annotation sha256 `63571B9610060EC1EA88FBD7CE3A1CB77B5D6CF0E6DE3096AB0492A2A5EC9235`. Cargo.lock annotation sha256 `01B0A06DCC1724B91A5C27F60CD98A5BD1EEFB53ECFD37ED81C96BAE4E6E34A6`. Ubuntu conclusion is `failure`. Artifact zip download previously returned EOF. | deferred | S-027 for `user-gpu`; S-009 for artifact readability | Windows success does not clear the Ubuntu failure. No tag. No pre-release. `user-gpu` stays unverified. |
| S-027 milestone | K-001 capability, installer proof | gap | Ledger `verified_on` is empty. No tag. `smoke-gpu.ps1` dry-run is contract-only. | deferred | S-027 | Do not tag. Do not call a dry-run a GPU pass. |
| S-012 job model and Style Match | K-009, K-010 | no-gap for current runtime | S-023 contract says `submit_inference()` is not called here. No Hypit or video-editing-skill package is imported. S-012 stays REVIEW as the approved non-blocking job model. | informational | S-046, S-048, S-056 for the future typed graph; S-012 stays the job model | Do not install Hypit, Ollama, PySide6, Gradio, or Ultralytics. The first Style Match model must later call `submit_inference()`. Not in S-013..S-032. |
| Monitoring reference stack | K-011 | no-gap | `requirements.txt` and `ai-engine/requirements.txt` do not name MLflow, W&B, Celery, Kafka, RabbitMQ, or `ffmpeg-python`. | informational | future observability stage only | Do not add that stack. Do not create a parallel supervisor. |
| CI supply chain | security lens | no-gap for action pins | `.github/workflows/ci.yml` pins checkout, setup-node, setup-python, upload-artifact, gitleaks, pnpm, rust-toolchain, and rust-cache to commit SHAs. Secret scan is a step before Playwright. The failing step on `36136231456` was Playwright, not the secret scan. | informational | S-009 | Do not float third-party actions to `latest`. |
| `06_BUGS.md` versus closed ledger rows | evidence hygiene | gap | BUG-8 and BUG-14 are still marked OPEN in `06_BUGS.md`, while S-003 ledger notes describe the traversal and CORS fixes as closed. This audit did not edit the bug table. | informational | `06_BUGS.md`, not a product reopen | Do not reopen S-003 from this inconsistency. Reconcile the bug table only under an explicit docs instruction. |
| `00_INDEX.md` branch line | handoff | gap | Fetched index says the builder branch is `arena/01a06951-cutting-edge-v2`. This session is `arena/01a0c936-cutting-edge-v2`. | informational | index owner | Do not switch branches. Do not treat the index branch line as authority for this session. |

## CI fact used above

Run `36136231456` at `aea01788d53500172b40f9bd4efc86af099d833b` concluded `failure`.

- Ubuntu: `failure`. Playwright junit `2 failed / 32`. Unit junit `0 failed / 88`.
- Named Playwright failures: `tests/timeline-canvas.spec.ts` drop ratio `0.06` against `< 0.05`; `tests/playback.spec.ts` drift `0.018207077636719138` against `< 0.016666666666666666`.
- Windows: `success`. This does not clear Ubuntu.
- `loop-audit`: `success`.
- CodeQL analyze jobs for that SHA succeeded. That is not a product pass.

## Not done

- No product edit.
- No ledger edit.
- No threshold edit.
- No skip.
- No GREEN.
- No `REVIEW.md`.
- No S-033.
- No continuation of the S-023 fix.
