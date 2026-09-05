import { test, expect } from '@playwright/test';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

/**
 * S-007 — build-artifact assertions over the real `next build` output.
 *
 * These tests need **no browser**, so they run everywhere (including a sandbox
 * or CI runner where `npx playwright install chromium` cannot download). They
 * assert on the actual compiled CSS/HTML that ships in `out/`, which is the same
 * artifact the Tauri shell loads (S-010 / S-060).
 *
 * The DOM-level counterparts (computed style, `document.fonts`, console errors)
 * live in `styling.spec.ts` and are the authoritative AC checks; this file
 * pins the compiled output so a Tailwind/DaisyUI misconfiguration is caught even
 * when no browser is available.
 */

const APP_DIR = resolve(__dirname, '..');
const OUT_DIR = join(APP_DIR, 'out');
const REPO_ROOT = resolve(APP_DIR, '../..');
const GLOBALS_CSS = join(APP_DIR, 'src/app/globals.css');
const LAYOUT_TSX = join(APP_DIR, 'src/app/layout.tsx');
const PAGE_TSX = join(APP_DIR, 'src/app/page.tsx');
const TOKENS_TS = join(REPO_ROOT, 'packages/design-system/tokens.ts');

function walk(dir: string, acc: string[] = []): string[] {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

function compiledCss(): string {
  const files = existsSync(OUT_DIR) ? walk(OUT_DIR).filter((f) => f.endsWith('.css')) : [];
  expect(files.length, `no compiled CSS under ${OUT_DIR} — run 'next build' first`).toBeGreaterThan(0);
  return files.map((f) => readFileSync(f, 'utf8')).join('\n');
}

/** The `@theme static { … }` block of globals.css, as written in source. */
function themeBlock(): string {
  const css = readFileSync(GLOBALS_CSS, 'utf8');
  const m = css.match(/@theme static\s*\{([\s\S]*?)\n\}/);
  expect(m, 'globals.css has no `@theme static { … }` block').not.toBeNull();
  return m![1];
}

// ── AC-1 ──────────────────────────────────────────────────────────────────────
test('out/ contains a real stylesheet (> 10 KB)', () => {
  const css = compiledCss();
  expect(Buffer.byteLength(css, 'utf8')).toBeGreaterThan(10 * 1024);
  // A Tailwind 4 build always starts with its preflight/theme layer.
  expect(css).toContain('--color-surface-base:#09090b');
});

// ── AC-2 (static half) ────────────────────────────────────────────────────────
test('body colour/font come from CSS, not an inline style', () => {
  const layout = readFileSync(LAYOUT_TSX, 'utf8');
  expect(layout).toContain("import './globals.css'");
  // The old layout painted <body> with an inline style; that proves nothing.
  expect(layout).not.toMatch(/<body[^>]*style=/);

  const css = compiledCss();
  expect(css).toMatch(/body\{[^}]*background-color:var\(--color-surface-base\)[^}]*\}/);
  expect(css).toMatch(/body\{[^}]*font-family:var\(--font-sans\)[^}]*\}/);
  expect(css).toMatch(/body\{[^}]*margin:0[^}]*\}/);
});

// ── AC-3 (static half) ────────────────────────────────────────────────────────
test('header gradient utilities are compiled', () => {
  const page = readFileSync(PAGE_TSX, 'utf8');
  // NG-1: page.tsx must stay untouched, so the Tailwind-3 gradient alias has to
  // keep working under Tailwind 4. This asserts it actually does.
  expect(page).toContain('bg-gradient-to-l from-indigo-400 to-purple-400 bg-clip-text text-transparent');

  const css = compiledCss();
  expect(css).toMatch(/\.bg-gradient-to-l\{[^}]*background-image:linear-gradient\(/);
  expect(css).toMatch(/\.from-indigo-400\{/);
  expect(css).toMatch(/\.to-purple-400\{/);
  expect(css).toMatch(/\.bg-clip-text\{[^}]*-webkit-background-clip:text[^}]*\}/);
  expect(css).toMatch(/\.text-transparent\{color:#0000\}/);
  expect(css).toMatch(/\.font-bold\{/);
});

// ── AC-4 (static half) ────────────────────────────────────────────────────────
test('fonts are bundled offline (no external font host)', () => {
  const css = compiledCss();
  const html = readFileSync(join(OUT_DIR, 'index.html'), 'utf8');

  for (const family of ['Vazirmatn', 'Inter Variable', 'JetBrains Mono']) {
    expect(css, `no @font-face / token for '${family}'`).toContain(family);
  }
  expect(css).toMatch(/@font-face\{font-family:Vazirmatn;[^}]*font-weight:400/);
  expect(css).toMatch(/@font-face\{font-family:Vazirmatn;[^}]*font-weight:700/);

  // Self-hosted: the woff2 files must exist inside the export.
  const woff2 = walk(OUT_DIR).filter((f) => f.endsWith('.woff2'));
  expect(woff2.length, 'no woff2 emitted — @fontsource import missing').toBeGreaterThan(0);
  for (const family of ['vazirmatn', 'inter', 'jetbrains-mono']) {
    expect(woff2.some((f) => f.includes(family)), `no bundled woff2 for ${family}`).toBe(true);
  }
  // Every font URL in the CSS must be a local, hashed bundle path.
  const urls = [...css.matchAll(/url\(([^)]*woff2?)\)/g)].map((m) => m[1]);
  expect(urls.length).toBeGreaterThan(0);
  for (const u of urls) expect(u.startsWith('/_next/static/media/'), `non-local font url: ${u}`).toBe(true);

  // No external font host anywhere in the shipped CSS/HTML.
  expect(css + html).not.toMatch(/fonts\.(googleapis|gstatic)\.com/);
});

// ── AC-6 (static half) ────────────────────────────────────────────────────────
test('daisyui 5 rules and theme tokens are compiled', () => {
  const css = compiledCss();
  // DaisyUI 4 is a Tailwind 3 plugin and cannot compile here at all.
  expect(css).toMatch(/\.btn\{[^}]*\}/);
  expect(css).toMatch(/\.btn\{[^}]*display:inline-flex/);
  expect(css).toMatch(/--color-base-100:/);
  expect(css).toMatch(/--color-base-content:/);
});

// ── AC-7 (static half) ────────────────────────────────────────────────────────
test('exported HTML is Persian + RTL', () => {
  const html = readFileSync(join(OUT_DIR, 'index.html'), 'utf8');
  expect(html).toMatch(/<html lang="fa" dir="rtl">/);
});

// ── design-system sync (packages/design-system/tokens.ts ↔ globals.css) ──────
test('tokens.ts cssTheme map matches the @theme block exactly', () => {
  const tokens = readFileSync(TOKENS_TS, 'utf8');
  const mapBlock = tokens.match(/export const cssTheme = \{([\s\S]*?)\n\} as const;/);
  expect(mapBlock, 'tokens.ts has no `export const cssTheme` map').not.toBeNull();

  const mapped = [...mapBlock![1].matchAll(/'(--[a-z0-9-]+)'/g)].map((m) => m[1]);
  expect(mapped.length).toBeGreaterThan(20);

  const declared = [...themeBlock().matchAll(/^\s*(--[a-z0-9-]+):/gm)].map((m) => m[1]);
  // Bijective: no orphan CSS variable and no map entry pointing at nothing.
  expect([...mapped].sort()).toEqual([...declared].sort());

  // The compiled bundle must actually expose every token at runtime
  // (`@theme static` is what guarantees this).
  const css = compiledCss();
  for (const name of mapped) {
    expect(css, `${name} is missing from the compiled CSS`).toContain(`${name}:`);
  }

  // Font stacks must be byte-identical between the TS tokens and the CSS.
  const sans = tokens.match(/sans:\s*"([^"]+)"\s*,?\s*\n?\s*mono/);
  const mono = tokens.match(/mono:\s*"([^"]+)"\s*\n\s*\}/);
  expect(sans, 'tokens.ts typography.sans not found').not.toBeNull();
  expect(mono, 'tokens.ts typography.mono not found').not.toBeNull();
  const block = themeBlock();
  expect(block).toContain(`--font-sans: ${sans![1]}`);
  expect(block).toContain(`--font-mono: ${mono![1]}`);
});

// ── guard: the export must not be committed ──────────────────────────────────
test('out/ is git-ignored (no build artifacts in git)', () => {
  const gitignore = readFileSync(join(REPO_ROOT, '.gitignore'), 'utf8');
  expect(gitignore.split('\n').map((l) => l.trim())).toContain('out/');
  // Sanity: the artifact we just asserted on really is there.
  expect(statSync(OUT_DIR).isDirectory()).toBe(true);
});
