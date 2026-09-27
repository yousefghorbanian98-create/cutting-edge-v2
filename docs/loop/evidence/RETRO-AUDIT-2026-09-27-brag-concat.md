# Retrospective audit — brag and Concat — 2026-09-27

This record routes two external references into the knowledge registry. It does not change the ledger, stage status, thresholds, or `BUG-18`. It is not a `REVIEW.md` and it is not implementation clearance.

Inspected:

- `docs/loop/KNOWLEDGE_REGISTRY.md`
- `docs/loop/STYLE_MATCH_ARCHITECTURE.md`
- `docs/loop/FORWARD_KNOWLEDGE_GATE.md`
- `docs/loop/KNOWLEDGE_REFRESH_AUDIT.md`
- `docs/loop/06_BUGS.md` (`BUG-18` remains `OPEN`)
- `ai-engine/src/core/ffmpeg.py`
- `ai-engine/src/export/runner.py`
- CI `36236525859` on `0cc6d8237552afb550e2f13cd3aebb179aff203e` (named annotations and check-run text; zip artifacts not downloaded)

References read for principles only. No source, crate, shader, skill implementation, MCP, or asset was copied.

- brag: MIT. Skill and reference notes inspected. Hyperframes, bundled music/SFX, and provider adapters were not imported.
- Concat: AGPL-3.0-or-later. Architecture headings inspected. No engine file was vendored.

## Disposition

`K-015` and `K-016` are durable index entries. They are not implementation proof. Product schemas for a processing receipt, expanded capability states, a pure frame plan, or a scheduler are deferred to the owners below. Starting those schemas here would be a new stage or a migration, so this batch stops at the proposal.

## Principle mapping

| Reference principle | Native component | Owner | Files today | Required test | Required evidence | Legal / dependency risk | Performance risk |
|---|---|---|---|---|---|---|---|
| source-first inspection | Style signature / future source brief | S-045, S-046 | `STYLE_MATCH_ARCHITECTURE.md` | not started | source surfaces named before claims | brag MIT text is reference only | none until a scanner is added |
| real UI and asset reuse | desktop components, not a copied renderer | S-046 | `apps/desktop/src` | existing Playwright specs | fixture screenshots, not a fabricated UI | do not import brag assets | none |
| entry → action → result | editor journey | S-026 | `apps/desktop/e2e/timeline.spec.ts` | `e2e/timeline.spec.ts` | visual ratio `< 0.001` | none | do not relax the ratio |
| typed storyboard / edit plan | future `EditPlan`; export plan exists only as export | S-046, S-028 | `tests/unit/test_export_plan.py` | export-plan unit tests | schema validation, not chat text | no Concat model copy | none |
| source-backed claims | future claim record | S-046, S-055 | none as a typed claim store | not started | each claim cites a source id | none | none |
| readability budget | timeline/caption text | S-040, S-046 | timeline components | not a new threshold | dwell, overflow, contrast when that stage starts | none | none |
| settled frame and mid-transition QA | sequence and visual specs | S-024, S-026 | `sequence.spec.ts`, `timeline.spec.ts` | those specs | measured gap and visual ratio | none | do not replace `0.001` with SSIM |
| poster and frame zero | future export validation | S-033 | none | not started | frame-zero hash when S-033 starts | none | none |
| timestamped output isolation | CI reports directory; product run dirs not unified | S-074 | `reports/` in CI only | evidence manifest tests | run id in the manifest | none | bounded retention, owner S-074 |
| processing receipt | CI evidence manifest, not a product receipt | S-086 | `scripts/ci/evidence_manifest.py` | `tests/unit/test_evidence_manifest.py` | canonical text plus sidecar sha256 | none | none |
| manifest and checksum | same CI manifest | S-086 | `scripts/ci/verify_evidence_manifest.py` | verifier unit test | sha256 of canonical bytes | none | none |
| secret / PII / hostname exclusion | gitleaks plus future redaction record | S-086 | `.gitleaks.toml`, ubuntu secret scan | gitleaks job | scan pass is not a product privacy pass | none | none |
| voice opt-in | no voice runtime | S-056 | none | not started | capability `denied` or absent until opt-in | no Kokoro/Hyperframes provider | none |
| audio / SFX provenance | beat-sync extract only | S-040, S-086 | `tests/test_beat_sync.py` | `test_ffmpeg_extract_aac` | measured rate and channels | no bundled music import | none |
| optional adapter capability | export encoder probe | S-028, S-086 | `ai-engine/src/export/runner.py` | encoder tests | `available` / `missing` / `unknown`; missing is not pass | no new provider | software fallback is not `user-gpu` |
| one-way layers | Python core vs desktop UI | S-028 | `ai-engine/src/core`, `apps/desktop` | import boundary not yet a fitness test | proposal only | no Concat crate | none |
| core without window or FFmpeg | partial: UI is separate; `run_ffmpeg` still calls FFmpeg | S-028, S-033 | `ai-engine/src/core/ffmpeg.py` | overwrite unit tests | do not pretend core is backend-free | no media-backend copy | none |
| one document, one command path | timeline store actions | S-013–S-032, S-068 | timeline store | history specs | store action, not `setState` bypass | none | none |
| shared UI/CLI/API command path | not present | S-068 | none | not started | proposal only | no Concat API copy | none |
| pure frame plan before decode | not present | S-033, S-024 | `SequencePlayer.tsx` uses the media clock | playback spec | drift `< 1/fps` | no Concat planner copy | a new plan must not add drift |
| shared preview/export semantics | not proven | S-028, S-033 | export runner and preview player are separate | both suites | same timeline resolution when S-033 starts | none | none |
| exact / frame-grid time | playback clock and existing thresholds | S-024 | `SequencePlayer.tsx`, playback spec | `playback.spec.ts` | drift and arrow measurements | none | do not change `< 1/fps` or `< 0.001` |
| reference compositor | not present | S-033 | none | not started | GPU/software parity only with a named oracle | no shader copy | software oracle is not a GPU pass |
| bounded cache | not a product cache policy | S-056, S-074 | none | not started | hit/miss and peak memory when implemented | none | unbounded cache is rejected |
| priority scheduler | not present | S-056 | none | not started | Playback > Filmstrip > Artwork > Proxy only if S-015 budgets hold | none | no validation removal |
| bounded workers | not present | S-056 | none | not started | worker cap in the receipt | none | none |
| proxy policy | future analysis proxy only | S-045, S-056 | architecture note | not started | proxy hash separate from master | none | none |
| hardware detect and software fallback | NVENC probe | S-028 | `export/runner.py` | capability tests | listed encoder is not `user-gpu` | none | fallback must be named |
| stale async discard | not a session-wide rule | S-012, S-037 | job model is S-012 | not retested here | proposal only | none | none |
| effect manifest validation | unknown effect must fail closed | S-048, S-086 | export filter allow-list | filter missing test | unknown graph rejected | no shader import | none |
| resource limits before effect | not a general executor | S-086 | upload limits exist for S-003 | not this batch | proposal only | none | none |
| model manifest / digest / license | not a downloader | S-056, S-086 | architecture note | not started | digest and license before download | no model import | none |
| bounded per-run logs | CI annotations, not product log retention | S-074, S-086 | evidence scripts | manifest tests | no secrets in notices | none | none |
| measured performance table | Playwright/CDP budgets already named | S-015 | `timeline-canvas.spec.ts` | that spec | rendered and drop ratio | none | no budget relaxation |
| local/offline default | no new network renderer | S-056 | none added | not started | external handoff stays denied | no `npx` | none |
| HDR/SDR evidence gate | no color-pipeline claim | S-033, S-068 | none | not started | no HDR pass without measurement | none | none |
| overwrite consent, staging, rollback | `run_ffmpeg` partial publish | S-033, S-086; `BUG-18` stays open | `ffmpeg.py`, `tests/unit/test_ffmpeg_overwrite.py` | three named overwrite tests | refusal, consent, staging, rollback | none | none |
| no `ffmpeg -y` | default path has no `-y` | S-033, S-086 | `ffmpeg.py` | consented replace asserts `-y` absent | named evidence | none | none |

## Historical path

| Historical path | New lens | Result | Evidence inspected | Severity | Owner | Action |
|---|---|---|---|---|---|---|
| S-004 / `run_ffmpeg` | brag `ffmpeg -y` rejection; Concat atomic export | Gap remains open. Default refusal, staging, and rollback are tested. That does not close the bug. | CI `36236525859` named overwrite results | deferred | `BUG-18`, S-033, S-086 | no status change |
| S-015 canvas | Concat performance table | No gap in the current budget. No new scheduler was added, so there is no before/after delta. | `timeline-canvas.spec.ts` on `36236525859`: rendered=8, drop-ratio=0 | informational | S-015, S-056 | do not add a scheduler in this batch |
| S-023 zoom | brag settled frame; cursor lock | No gap in the current spec. | cursor-lock-px=0, scrollWidth=1406, clientWidth=1406 | informational | S-023 | no threshold change |
| S-024 playback | Concat exact time; media clock | No gap in the current clock tests. A shared frame-plan type does not exist. | playback drift and arrow lines on `36236525859` | deferred | S-024, S-033 | proposal only for a shared plan |
| S-026 visual | brag settled visual QA | Measured visual ratios are 0 and map to `< 0.001`. SSIM is not a substitute. | `e2e/timeline.spec.ts` undo-ratio=0 split-ratio=0 | informational | S-026 | do not replace the ratio |
| sequence regression | historical `36194558289` | Historical failure stays. This run passed a different named assertion. | sequence ssim=0.975, gap-ms=13.200000000011642; historical notice present | informational | S-024 | do not rewrite the old failure |
| S-028 export | Concat one media boundary; brag receipt | Encoder capability exists. A product processing receipt does not. | `export/runner.py` capability states | deferred | S-028, S-086 | do not expand states in this batch |
| Windows installer | manifest/checksum | Named smoke checks passed. Zip not read here. | installer sha256 in check-run text | informational | S-010 | zip EOF remains a readability limit |
| `user-gpu` | Concat software fallback | Still unverified. Dry-run is not a pass. | `smoke-gpu.ps1` contract-dry-run | deferred | S-027 | no GPU claim |

## Proposals that stop here

1. A typed processing receipt with schema version, commit, tool versions, input hashes, redactions, capabilities, named results, thresholds, output hashes, licenses, consent, staging, and final status. Owner: S-086, with export fields owned by S-033. Not started.
2. Capability states beyond `available` / `missing` / `unknown`. Owner: S-028 and S-086. Not started. `user-gpu` stays `unverified`.
3. A pure frame plan shared by preview and export, with rational time. Owner: S-024 and S-033. Not started, because it can move drift and needs its own contract.
4. Bounded cache, worker cap, and Playback > Filmstrip > Artwork > Proxy. Owner: S-056 and S-015. Not started. No before/after measurement exists because no code changed.
5. Effect manifest with fail-closed unknown executors. Owner: S-048 and S-086. Not started.

## Explicit non-actions

- no stage `GREEN`
- `S-033` not started
- `BUG-18` not closed
- ledger not edited
- thresholds not changed
- no failure converted to skip
- no Concat or HotClip runtime dependency
- no Hyperframes dependency
- no unpinned `npx`
- `K-012`, `K-013`, and `K-014` are not implementation proof
- `K-015` and `K-016` are not implementation proof
