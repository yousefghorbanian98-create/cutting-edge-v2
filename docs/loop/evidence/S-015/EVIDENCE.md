# S-015 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for the window math. The CDP scroll budget is `unverified:browser`.

| AC | What ran | Result |
| --- | --- | --- |
| AC-2 | `vitest run` window test | 11/11 passed. A 10–12s window of the 200-clip sequence mounts only the overlapping clips. |
| AC-1, AC-3 | Playwright + CDP | not run. Chromium download from `cdn.playwright.dev` still resets. The spec is on the ubuntu job. Not a pass. |

- Renderer: DOM + `translate3d`, ruler and clips virtualized, scroll updates batched to one frame.
- `design_audit --strict`: 0 findings.
- No REVIEW.md.
