# S-020 — Selection (click/shift/marquee), copy/paste/duplicate

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | A marquee over the first three of five clips selects those three. | `apps/desktop/src/stores/__tests__/selection.test.ts` |
| AC-2 | Paste at 20s keeps relative offsets. Duplicate places copies after the selection. | same file |
| AC-3 | Ctrl+C / Ctrl+V / Ctrl+D and the marquee gesture are wired. Selected clips use the info border token. | `apps/desktop/tests/selection.spec.ts` |

## Out of scope

- Undo buttons are S-021. Mute/solo/lock are S-022.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/selection.spec.ts`.
