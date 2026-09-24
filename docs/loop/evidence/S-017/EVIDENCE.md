# S-017 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for the snap math. The mouse drag spec is `unverified:browser`.

| AC | What ran | Result |
| --- | --- | --- |
| AC-1 | `vitest run` snap tests | 14/14 passed. A drop 4px from A.end at 100px/s snaps to A.end. 4.5s does not snap to 5.0s at that scale, because 0.5s is 50px, outside the 8px threshold. Shift keeps the raw time. |
| AC-2 | Playwright mouse drag | not run. Chromium download from `cdn.playwright.dev` still resets. The spec is on the ubuntu job. Not a pass. |

- Rejected cross-kind moves show `این کلیپ روی این ترک نمی‌نشیند`.
- `design_audit --strict`: 0 findings.
- No REVIEW.md.
