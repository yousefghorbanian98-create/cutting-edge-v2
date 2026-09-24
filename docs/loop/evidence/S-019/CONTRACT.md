# S-019 — Split at playhead (Ctrl+B), delete, ripple delete

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | A 10s clip split at 4.5s becomes [0, 4.5] and [4.5, 10], with continuous source in/out. | `apps/desktop/src/domain/__tests__/split.test.ts` |
| AC-2 | Ripple delete of the first half moves the second clip to 0. | same file |
| AC-3 | Ctrl+B uses the playhead time. Delete and Shift+Delete remove the selection. | `apps/desktop/src/lib/shortcuts.ts` and `apps/desktop/tests/split.spec.ts` |

## Out of scope

- Marquee selection is S-020.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/split.spec.ts`.
