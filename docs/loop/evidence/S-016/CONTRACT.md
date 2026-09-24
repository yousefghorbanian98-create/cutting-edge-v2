# S-016 — Playhead sync, scrubbing, JKL, frame-step, time display

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | Playhead follows the preview video through `requestVideoFrameCallback`. After 3s of playback, playhead x drift vs `video.currentTime` is under one frame. | `apps/desktop/tests/playback.spec.ts` |
| AC-2 | ArrowRight ten times from 0 sets `currentTime` to `10/fps` ± 1ms, at 30fps and 60fps fixtures. | same spec |
| AC-3 | Ruler drag scrubs. J/K/L play reverse, pause, and forward. Timecode is `HH:MM:SS:FF`. | ruler pointer handler, key listener, `src/hooks/__tests__/timecode.test.ts` |

## Out of scope

- Dragging clips, snapping, and trim handles are later cards.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/playback.spec.ts`.
