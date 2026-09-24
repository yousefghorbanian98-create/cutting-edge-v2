# S-020 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for selection math. The marquee gesture is `unverified:browser`.

| AC | What ran | Result |
| --- | --- | --- |
| AC-1, AC-2 | `vitest run` | 19/19 passed. Marquee over 0–5.2s selects c0, c1, c2. Paste at 20000ms keeps 0 / 1500 / 3000 offsets. |
| AC-3 | Playwright marquee | not run. Chromium download from `cdn.playwright.dev` still resets. The spec is on the ubuntu job. Not a pass. |

- `design_audit --strict`: 0 findings.
- No REVIEW.md.
