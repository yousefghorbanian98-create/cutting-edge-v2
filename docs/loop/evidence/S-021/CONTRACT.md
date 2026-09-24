# S-021 — Undo/Redo UI and history panel

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | Five edits can undo back to the initial sequence hash and redo to the final hash. | `apps/desktop/src/components/shared/__tests__/history.test.ts` |
| AC-2 | Ctrl+Z / Ctrl+Shift+Z and the history panel are wired. Drag commits once on pointerup, so a drag is one history entry. | `apps/desktop/tests/history.spec.ts` |

## Out of scope

- Mute, solo, and lock are S-022. Zoom is S-023.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/history.spec.ts`.
