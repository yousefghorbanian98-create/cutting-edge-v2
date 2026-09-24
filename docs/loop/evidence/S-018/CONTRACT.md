# S-018 — Trim handles (in/out), ripple & roll trim

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | Ripple out-trim of 2s shortens the clip by exactly 2s and moves the next clip by 2s. Extending past the source is rejected. | `apps/desktop/src/domain/__tests__/trim.test.ts` |
| AC-2 | Roll trim keeps the cut and changes both durations, within source in-points. | same file |
| AC-3 | Dragging the out handle updates duration, and the preview canvas pixels change. | `apps/desktop/tests/trim.spec.ts` |

## Out of scope

- Split and ripple delete shortcuts are S-019.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/trim.spec.ts`. Alt ripple, Shift roll.
