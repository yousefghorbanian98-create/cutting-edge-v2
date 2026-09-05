import { defineConfig, devices } from '@playwright/test';

/**
 * S-007 — Playwright config for the frontend styling suite.
 *
 * The suite runs against the **static export** (`out/`), not `next dev`, because
 * that is the artifact the card requires ("`next build` emits out/") and the same
 * artifact the Tauri shell loads (S-010 / S-060). `scripts/serve-out.mjs` is a
 * dependency-free static server so the same command works on ubuntu and windows CI.
 *
 * Reports: `playwright-report/` (HTML) + `playwright-report/junit.xml`, both
 * uploaded as CI artifacts by S-009.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: 0,
  timeout: 60_000,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report/html', open: 'never' }],
    ['junit', { outputFile: 'playwright-report/junit.xml' }],
  ],
  use: {
    baseURL: process.env.CE_E2E_BASE_URL ?? 'http://127.0.0.1:4321',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
  ],
  webServer: {
    command: 'node scripts/serve-out.mjs out 4321',
    url: process.env.CE_E2E_BASE_URL ?? 'http://127.0.0.1:4321',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
