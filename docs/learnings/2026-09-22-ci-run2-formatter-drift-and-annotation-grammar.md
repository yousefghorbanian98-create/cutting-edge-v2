# 2026-09-22 — S-009 run #2: tests that encode formatter output, and `::error,` is not an annotation

## What broke
- `ci / ubuntu` Playwright: `tokens.ts cssTheme map matches @theme` failed (`typography.mono not found`) and `body background comes from the stylesheet` failed (`79` rules, expected `> 100`) — both green when S-007 was reviewed.
- `ci / loop-audit` failed on C11 because run #1 (an *older* commit) was red — the audit would have stayed red forever after any single red push.
- The round-2 `::error` lines printed in the log but GitHub recorded **no** annotations.

## Root cause
- S-008's Biome format pass rewrote `tokens.ts` quotes/trailing comma; the S-007 test matched the file byte-for-byte, so an unrelated formatter run broke it. The `cssRules.length` count was flat while Tailwind 4 nests utilities under `@layer` — passing locally only because the local Chromium/CSS happened to exceed 100.
- C11 judged *any* run on the branch instead of runs for HEAD.
- Workflow-command grammar is `::error file=…,line=…,title=…::msg`; a leading comma (`::error,title=`) is silently ignored. Nothing checked the emitted shape.

## Rule
- Tests compare **semantics**, never formatter output: normalise quotes/whitespace, count nested CSS rules recursively, and re-run the affected suite after any repo-wide format/lint pass (`biome check --write`, `ruff format`) before calling a step GREEN.
- Audits compare the current HEAD only; history belongs to the ledger (`C11` now reports older red runs as context, not verdict).
- Anything that emits machine-parsed output (`::error`, junit, JSON) gets a unit test on the exact grammar (`test_junit_annotate_emits_valid_workflow_commands`).
- Signed job-log URLs from `gh api …/jobs/<id>/logs` are readable through `fetch_page` even when the sandbox cannot reach blob storage — use that before guessing.
- Splitting one working tree into several commits must keep **each** commit runnable: run #3 (`27e84a4`) failed `loop-audit` only because `supervise.py` imported `scripts/loop/hygiene.py` that landed in the next commit. Stage by dependency, or run the audit against the staged tree before committing.
