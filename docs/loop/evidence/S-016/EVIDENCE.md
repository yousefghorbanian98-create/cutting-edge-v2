# S-016 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for the timecode formatter. The sync spec is `unverified:browser`.

| AC | What ran | Result |
| --- | --- | --- |
| AC-3 format | `vitest run` | 12/12 passed. `10/30` and `10/60` format as `00:00:00:10`. |
| AC-1, AC-2 | Playwright | not run. Chromium download from `cdn.playwright.dev` still resets. The spec is on the ubuntu job. Not a pass. |

- Playhead position is written in the video frame callback, not on the next React commit.
- `design_audit --strict`: 0 findings.
- No REVIEW.md.
