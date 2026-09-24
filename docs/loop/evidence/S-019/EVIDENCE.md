# S-019 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for the split math. Ctrl+B in the browser is `unverified:browser`.

| AC | What ran | Result |
| --- | --- | --- |
| AC-1, AC-2 | `vitest run` | 17/17 passed. Split at 4500ms on a 10000ms clip with inPoint 100 yields inPoint 4600 on the right half. Ripple delete returns the remainder to 0. |
| AC-3 | Playwright Ctrl+B | not run. Chromium download from `cdn.playwright.dev` still resets. The spec is on the ubuntu job. Not a pass. |

- `design_audit --strict`: 0 findings.
- No REVIEW.md.
