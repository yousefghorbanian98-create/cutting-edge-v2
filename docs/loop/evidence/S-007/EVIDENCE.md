# EVIDENCE — S-007 — Frontend styling fix (Tailwind 4 + DaisyUI 5 + offline fonts)

Environment: `local-linux` (Arena sandbox). Date 2026-09-05.

## 1. Versions actually installed (npm registry reachable; everything else pinned)

```
next                15.5.25
react               19.2.8
tailwindcss         4.3.3
@tailwindcss/postcss 4.3.3
daisyui             5.7.28
@fontsource/vazirmatn        5.3.0
@fontsource-variable/inter   5.3.0
@fontsource/jetbrains-mono   5.3.0
@playwright/test    1.63.0
```

## 2. `next build` (`output: 'export'`)

```
   ▲ Next.js 15.5.25
/*! 🌼 daisyUI 5.7.28 */
 ✓ Compiled successfully in 8.8s
 ✓ Generating static pages (4/4)
 ✓ Exporting (2/2)
Route (app)                                 Size  First Load JS
┌ ○ /                                    46.5 kB         149 kB
└ ○ /_not-found                            992 B         104 kB
```

**AC-1 — CSS emitted:** `out/_next/static/css/aff2c50356a38e98.css` = **64 570 bytes** (62.5 KB),
i.e. 6.3× the card's 10 KB bar.

**AC-4 — self-hosted fonts:** 19 `.woff2` files emitted under `out/_next/static/media/`
(`vazirmatn-arabic-400/700`, `vazirmatn-latin-*`, `inter-*`, `jetbrains-mono-*`); all 31 `url(...woff2)`
references in the compiled CSS start with `/_next/static/media/`; zero occurrences of
`fonts.googleapis.com` / `fonts.gstatic.com` in CSS or HTML.

**AC-7 — RTL:** `grep -o '<html[^>]*>' out/index.html` → `<html lang="fa" dir="rtl">`.

## 3. Compiled rules the DOM assertions depend on (extracted from the shipped CSS)

```css
body{background-color:var(--color-surface-base);color:#fff;font-family:var(--font-sans);
     -webkit-font-smoothing:antialiased;text-rendering:optimizelegibility;margin:0}
--color-surface-base:#09090b;                     /* = rgb(9, 9, 11) → AC-2 */
.bg-gradient-to-l{--tw-gradient-position:to left in oklab;
                  background-image:linear-gradient(var(--tw-gradient-stops))}   /* → AC-3 */
.bg-clip-text{-webkit-background-clip:text;background-clip:text}
.text-transparent{color:#0000}                                                  /* = rgba(0,0,0,0) */
@font-face{font-family:Vazirmatn;font-style:normal;font-display:swap;font-weight:400;
           src:url(/_next/static/media/vazirmatn-arabic-400-normal.f37c0063.woff2)…}
.btn{--size:calc(var(--size-field,.25rem) * 10);…display:inline-flex;…}         /* → AC-6 */
--color-base-100:oklch(25.33% .016 252.42);                                     /* DaisyUI 5 theme */
:root{--font-sans:"Inter Variable","Vazirmatn",system-ui,sans-serif;
      --font-mono:"JetBrains Mono",ui-monospace,monospace;…}
```

The Tailwind-3 alias `bg-gradient-to-l` **does** survive Tailwind 4 (it compiles to
`--tw-gradient-position:to left in oklab`), so NG-1 ("do not touch page.tsx") holds.

## 4. Test results

```
$ npx playwright test tests/build-artifacts.spec.ts
Running 8 tests using 1 worker
  ✓ out/ contains a real stylesheet (> 10 KB)
  ✓ body colour/font come from CSS, not an inline style
  ✓ header gradient utilities are compiled
  ✓ fonts are bundled offline (no external font host)
  ✓ daisyui 5 rules and theme tokens are compiled
  ✓ exported HTML is Persian + RTL
  ✓ tokens.ts cssTheme map matches the @theme block exactly
  ✓ out/ is git-ignored (no build artifacts in git)
  8 passed (857ms)
```

Machine-readable copy: `docs/loop/evidence/S-007/build-artifacts.junit.xml`
(`tests="8" failures="0" skipped="0" errors="0"`).

### Red-first proof (executed, not claimed)

Reverting `src/app/globals.css`, `postcss.config.mjs` and `src/app/layout.tsx` to `HEAD` and
rebuilding:

```
=== CSS AFTER REVERT ===        (no output: out/ contains NO .css file at all — exactly B-4)
=== SPEC (expect RED) ===
  6 failed
    › out/ contains a real stylesheet (> 10 KB)
    › body colour/font come from CSS, not an inline style
    › header gradient utilities are compiled
    › fonts are bundled offline (no external font host)
    › daisyui 5 rules and theme tokens are compiled
    › tokens.ts cssTheme map matches the @theme block exactly
  2 passed
```

The two that stay green in both states (`exported HTML is Persian + RTL`, `out/ is git-ignored`)
are deliberately independent of the styling fix. After restoring the change: 8/8 green again.

## 5. `unverified:ci` — what could NOT be run here

`npx playwright install chromium` fails: the sandbox only proxies registry.npmjs.org and PyPI.

```
deb.debian.org 000 · security.debian.org 000 · archive.ubuntu.com 000
cdn.playwright.dev 000 · playwright.azureedge.net 000 · storage.googleapis.com 000
Error: Client network socket disconnected before secure TLS connection was established
```

No system Chromium is installed either. Therefore `apps/desktop/tests/styling.spec.ts`
(computed style, `document.fonts.check/load`, zero console/page errors, screenshot baseline) is
written and committed but **`unverified:ci`**; the S-009 ubuntu job is its gate, and the
screenshot baseline (`docs/loop/evidence/S-007/home-1440x900.png`) will be produced there.
`AC-2…AC-6` are *partially* covered locally by the compiled-CSS assertions above; the DOM-level
half is not.

## 6. Note for S-008 / S-009

* `apps/desktop/package-lock.json` was generated by the local `npm install` used for
  verification. The committed lock source of truth is `pnpm-lock.yaml` (S-008).
* Next.js rewrote `tsconfig.json` during the first build (added `.next/types/**/*.ts` to
  `include`) — that change is committed, it is Next's own recommendation.
* CI must run `npx playwright install --with-deps chromium` on ubuntu for `styling.spec.ts`.
