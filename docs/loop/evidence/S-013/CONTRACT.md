# S-013 — Timeline domain model + Zustand store with undo history (zundo) + vitest

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | `apps/desktop/src/domain/timeline.ts` models sequence, video/audio/text tracks, clips (start, duration, source in/out, transform, effects), and markers. Time is integer milliseconds. | `apps/desktop/src/domain/__tests__/timeline.test.ts` |
| AC-2 | Split, trim, move, and ripple-delete keep clips on one track non-overlapping. A rejected edit returns the same object. | same file, including the fast-check property |
| AC-3 | `apps/desktop/src/stores/timelineStore.ts` uses Zustand + immer + zundo. `undo(n)` restores the exact prior sequence and id counter. | same file, store undo test + property |
| AC-4 | Line coverage of `domain/timeline.ts` is at least 90%. | `pnpm exec vitest run --coverage` in `apps/desktop` |

## Out of scope

- No editor UI, media bin, or Playwright spec. Those are S-014 onward.
- `primary` stays tokens.ts-only. Promoting it would break the S-099 lock `threeWay == 27`. DaisyUI `primary` is enough until a later card needs the scale utilities.
- No Style Match model and no `submit_inference()`.

## Behavior change

The ubuntu CI job now also runs `pnpm exec vitest run --coverage` so this suite is not skipped. Existing pytest and Playwright commands are unchanged.
