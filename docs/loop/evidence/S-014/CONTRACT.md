# S-014 — Media Bin: multi-file import, metadata probe, thumbnails, rename/delete

**Status:** REVIEW (not GREEN). Builder does not self-approve.

## Acceptance criteria

| ID | Criterion | Real test |
| --- | --- | --- |
| AC-1 | `/editor` has a media bin. Drop and the file dialog both import files. Probe uses `HTMLVideoElement` for duration, size, and canvas thumbnails. | `apps/desktop/tests/media-bin.spec.ts` |
| AC-2 | Three fixture files become three cards. Durations match the container duration ±0.1s. Thumbnails are not blank (pixel variance > 0). A Persian filename imports. | same spec |
| AC-3 | Rename survives a page reload of the store snapshot. Search and delete work. | same spec, plus `src/stores/__tests__/mediaStore.test.ts` for the snapshot round-trip |

## Out of scope

- Timeline canvas, playhead, and drag onto tracks are S-015 onward.
- No Style Match model and no `submit_inference()`.

## Behavior change

- Ubuntu CI Playwright now also runs `tests/media-bin.spec.ts`. The home-page specs are unchanged.
- A no-op trim in `domain/timeline.ts` returns the same object. The coverage run found a flaky undo mismatch when a same-duration trim still allocated a new sequence.
