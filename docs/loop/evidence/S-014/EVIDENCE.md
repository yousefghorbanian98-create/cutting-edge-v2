# S-014 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux for the store snapshot and the static export. Playwright itself is `unverified:browser` here.

| AC | What ran | Result |
| --- | --- | --- |
| AC-3 snapshot | `vitest run` | 10/10 passed, including rename hydrate. Coverage suite 8/8 after the no-op trim fix. |
| AC-1 route | `next build` | static export includes `/editor` (3.1 kB). |
| AC-1..AC-2 browser | Playwright | not run. `pnpm exec playwright install chromium` failed: `cdn.playwright.dev` TLS reset. The spec is in the ubuntu job so CI is the browser proof. Do not treat this row as a pass. |

- Fixtures are base64 in `apps/desktop/tests/fixtures/media-clips.json` (1.0s, 2.0s, 0.5s testsrc). No `.mp4` committed.
- `design_audit --strict` on `apps/desktop/src`: 0 findings.
- No REVIEW.md.
