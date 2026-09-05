import { test, expect, type Page } from '@playwright/test';
import { readdirSync, statSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

/**
 * S-007 — real test for the frontend styling fix.
 *
 * Repo state before this step (01_STATE_OF_REPO.md B-4): page.tsx carries 86
 * Tailwind classNames but tailwindcss/postcss/daisyui/globals.css do not exist,
 * so the page renders with **no CSS**; layout.tsx paints the background with an
 * inline style (which proves nothing about the stylesheet) and the fonts are
 * bare font-family strings that are never loaded.
 *
 * Every AC in docs/loop/evidence/S-007/CONTRACT.md has an assertion here.
 * Run: `pnpm --filter cutting-edge-desktop test:e2e` (after `next build`).
 */

const APP_DIR = resolve(__dirname, '..');
const OUT_DIR = join(APP_DIR, 'out');
const EVIDENCE_DIR = resolve(APP_DIR, '../../docs/loop/evidence/S-007');

/** The backend health endpoint page.tsx polls on load (hardcoded in page.tsx). */
const HEALTH_URL = 'http://127.0.0.1:8001/health';
const HEALTH_BODY = JSON.stringify({ status: 'healthy', ram: 41.0, cpu: 7.5, gpu: null });

function walk(dir: string, acc: string[] = []): string[] {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

/** Route the health poll to a local stub so a missing backend cannot produce a
 *  network error that would pollute the "zero console errors" assertion. This
 *  does not fake any styling behaviour — API behaviour has real tests in
 *  tests/test_api_live.py (S-006) and tests/test_jobs.py (S-012). */
async function stubHealthPoll(page: Page): Promise<void> {
  await page.route('http://127.0.0.1:8001/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*' },
      body: HEALTH_BODY,
    }),
  );
}

// ── AC-1 ──────────────────────────────────────────────────────────────────────
test('build emits CSS > 10KB', () => {
  let files: string[] = [];
  try {
    files = walk(OUT_DIR);
  } catch {
    files = [];
  }
  const css = files.filter((f) => f.endsWith('.css'));
  expect(css.length, `no .css found under ${OUT_DIR} — did 'next build' run with output:'export'?`).toBeGreaterThan(0);

  const sized = css.map((f) => ({ f: f.replace(OUT_DIR, 'out'), size: statSync(f).size }));
  const largest = sized.reduce((a, b) => (b.size > a.size ? b : a));
  // Card done-when: "next build emits out/ with CSS > 10KB".
  expect(largest.size, `largest stylesheet ${largest.f} is only ${largest.size} B`).toBeGreaterThan(10 * 1024);
});

// ── shared page setup for the DOM assertions ──────────────────────────────────
async function loadApp(page: Page): Promise<string[]> {
  const consoleErrors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push(`pageerror: ${err.message}`));
  await stubHealthPoll(page);
  await page.goto('/', { waitUntil: 'networkidle' });
  return consoleErrors;
}

// ── AC-2 ──────────────────────────────────────────────────────────────────────
test('body background comes from the stylesheet', async ({ page }) => {
  await loadApp(page);
  const result = await page.evaluate(() => ({
    inline: document.body.style.backgroundColor,
    computed: getComputedStyle(document.body).backgroundColor,
    sheets: document.styleSheets.length,
    rules: Array.from(document.styleSheets).reduce((n, s) => {
      try {
        return n + s.cssRules.length;
      } catch {
        return n;
      }
    }, 0),
  }));
  // The point of the fix: the colour must come from CSS, not an inline style.
  expect(result.inline, 'body still carries an inline background — stylesheet not proven').toBe('');
  expect(result.computed).toBe('rgb(9, 9, 11)');
  expect(result.sheets).toBeGreaterThan(0);
  expect(result.rules).toBeGreaterThan(100);
});

// ── AC-3 ──────────────────────────────────────────────────────────────────────
test('header gradient text is real', async ({ page }) => {
  await loadApp(page);
  const header = page.locator('h1').first();
  await expect(header).toBeVisible();
  const style = await header.evaluate((el) => {
    const cs = getComputedStyle(el);
    return {
      backgroundImage: cs.backgroundImage,
      webkitClip: cs.webkitBackgroundClip,
      color: cs.color,
      fontWeight: cs.fontWeight,
    };
  });
  expect(style.backgroundImage).toContain('linear-gradient');
  expect(style.webkitClip).toBe('text');
  expect(style.color).toBe('rgba(0, 0, 0, 0)');
  // Tailwind's `font-bold` must also resolve — proof utilities are compiled.
  expect(Number(style.fontWeight)).toBeGreaterThanOrEqual(700);
});

// ── AC-4 ──────────────────────────────────────────────────────────────────────
test('fonts are self-hosted and resolved', async ({ page }) => {
  const externalFontRequests: string[] = [];
  page.on('request', (req) => {
    const url = req.url();
    if (/fonts\.(googleapis|gstatic)\.com/.test(url) || /\.(woff2?|ttf|otf)(\?|$)/.test(url)) {
      if (!url.startsWith('http://127.0.0.1:4321/')) externalFontRequests.push(url);
    }
  });
  await loadApp(page);

  const families = [
    { face: '400 16px Vazirmatn', name: 'Vazirmatn' },
    { face: '400 16px "Inter Variable"', name: 'Inter Variable' },
    { face: '400 16px "JetBrains Mono"', name: 'JetBrains Mono' },
  ];
  for (const { face, name } of families) {
    const loaded = await page.evaluate((f) => document.fonts.load(f).then((r) => r.length), face);
    expect(loaded, `no FontFace matched '${face}' — @fontsource import missing`).toBeGreaterThan(0);
    const check = await page.evaluate((f) => document.fonts.check(f), face);
    expect(check, `document.fonts.check('${face}') is false`).toBe(true);
    void name;
  }

  // Offline: every font must be served from the export itself.
  expect(externalFontRequests, `external font requests: ${externalFontRequests.join(', ')}`).toEqual([]);
});

// ── AC-5 ──────────────────────────────────────────────────────────────────────
test('zero console/page errors', async ({ page }) => {
  const consoleErrors = await loadApp(page);
  expect(consoleErrors, `console errors during load:\n${consoleErrors.join('\n')}`).toEqual([]);
});

// ── AC-6 ──────────────────────────────────────────────────────────────────────
test('daisyui 5 is compiled', async ({ page }) => {
  await loadApp(page);
  const btn = await page.evaluate(() => {
    const el = document.createElement('button');
    el.className = 'btn';
    document.body.appendChild(el);
    const cs = getComputedStyle(el);
    const out = { display: cs.display, borderRadius: cs.borderRadius, cursor: cs.cursor };
    el.remove();
    return out;
  });
  // DaisyUI 4 cannot compile against Tailwind 4, so a resolved .btn proves v5.
  expect(btn.display, '.btn did not resolve — DaisyUI plugin not compiled').toBe('inline-flex');
  expect(btn.borderRadius).not.toBe('0px');

  const token = await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--color-base-100'));
  expect(token.trim(), 'DaisyUI theme token --color-base-100 missing').not.toBe('');
});

// ── AC-7 ──────────────────────────────────────────────────────────────────────
test('rtl + screenshot baseline', async ({ page }) => {
  await loadApp(page);
  const attrs = await page.evaluate(() => ({
    lang: document.documentElement.lang,
    dir: document.documentElement.dir,
    fontFamily: getComputedStyle(document.body).fontFamily,
  }));
  expect(attrs.lang).toBe('fa');
  expect(attrs.dir).toBe('rtl');
  expect(attrs.fontFamily).toContain('Vazirmatn');

  mkdirSync(EVIDENCE_DIR, { recursive: true });
  await page.screenshot({ path: join(EVIDENCE_DIR, 'home-1440x900.png'), fullPage: false });
  expect(statSync(join(EVIDENCE_DIR, 'home-1440x900.png')).size).toBeGreaterThan(10 * 1024);
});
