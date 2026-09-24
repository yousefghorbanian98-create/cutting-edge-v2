# S-017 — Clip drag/move/reorder across tracks with snapping

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | Dropping a clip 4px from another clip's end snaps exactly to that end. Shift disables snap. The threshold is 8px. | `apps/desktop/src/domain/__tests__/snap.test.ts` |
| AC-2 | A video clip dragged onto the audio track is rejected and the UI says so. | `apps/desktop/tests/clip-drag.spec.ts` |
| AC-3 | The move goes through the timeline store, so undo still restores it. | store `moveClip` used by `useClipDrag` |

## Out of scope

- Trim handles and roll trim are S-018.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/clip-drag.spec.ts`.
