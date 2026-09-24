# S-018 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for the trim math. The handle drag spec is `unverified:browser`.

| AC | What ran | Result |
| --- | --- | --- |
| AC-1, AC-2 | `vitest run` | 16/16 passed. Out-trim −2000ms ripples the next start by 2000ms. A 50s extend is rejected. Roll moves the cut and both durations. |
| AC-3 | Playwright handle drag | not run. Chromium download from `cdn.playwright.dev` still resets. The spec is on the ubuntu job. Not a pass. |

- Preview canvas redraws from the trim point.
- `design_audit --strict`: 0 findings.
- No REVIEW.md.
