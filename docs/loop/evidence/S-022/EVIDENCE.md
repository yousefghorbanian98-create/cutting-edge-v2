# S-022 evidence

Ledger row stays `TODO`. This file is not a GREEN record.

## Local

- `pnpm exec vitest run` in `apps/desktop`: 28 passed / 28.
- `pnpm exec tsc --noEmit`: passed.
- `design_audit.py --strict` on the timeline components: 0 findings.
- Playwright Chromium did not install. `cdn.playwright.dev` returned `ECONNRESET`. AC-3 and AC-4 are not locally passed.
- CI run `36097690809` is not a pass. loop-audit failed because S-022 was still `TODO` after a commit named it. Ubuntu Playwright was 1 failed / 24: `media-bin.spec.ts` strict-mode collision on the button name `حذف`. The track control is now `برداشتن`. Thresholds were not loosened.

## Not claimed

- Ubuntu Playwright is not passed until CI says so.
- Windows pytest, cargo, Tauri, and installer smoke are not passed until that job runs them.
- A skipped or missing browser step is not a pass.
