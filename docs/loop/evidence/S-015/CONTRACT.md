# S-015 — Timeline canvas: ruler, tracks, virtualized clips, 60fps rendering

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | Timeline shows a time ruler, track headers, and clips with a thumbnail strip and a deterministic waveform. Clips are positioned with `translate3d`. | `apps/desktop/tests/timeline-canvas.spec.ts` |
| AC-2 | Horizontal virtualization: a 200-clip sequence does not mount every clip. | same spec (`data-rendered` < 40) and `src/components/timeline/__tests__/window.test.ts` |
| AC-3 | While scrolling, CDP tracing reports no `RunTask` longer than 50ms, and dropped frames stay under 5%. | same Playwright spec |

## Decision

DOM + transform, not Canvas. The visible window is a few clips, so a full canvas redraw is unnecessary. The scroll trace is the proof.

## Out of scope

- Playhead, JKL, drag, trim, and zoom UI are later cards.
- No Style Match model and no `submit_inference()`.

## Behavior change

Ubuntu CI Playwright also runs `tests/timeline-canvas.spec.ts`.

Scroll no longer reads `clientWidth` inside the scroll event. Viewport comes from `ResizeObserver`. The `< 0.05` budget is unchanged. Run `36136231456` received `0.06`. That gap stays open until a later annotation or opened junit names this test as passed.
