# EVIDENCE — S-100 — UI guidelines audit gate (offline WIG checker) wired into gate static

Builder: Supervisor session (autonomous chain). Verified on: `local-linux` (Python 3.11, Node 22). Pure-Python text analysis → identical in `ci / ubuntu` and `ci / windows` (no browser, no network).

## Red → Green proof (real, not numeric)

| AC | Red state (before) | Green state (after) | How reproduced |
|----|--------------------|---------------------|----------------|
| AC-1 | no checker; gate `design-audit ⏭️ SKIP` | `violations.tsx` → `[(9, icon-button-label), (12, outline-none-focus), (13, transition-all), (16, div-click), (17, img-alt-dims), (18, hardcoded-format), (19, reduced-motion), (20, input-label)]` — exactly the 8 planted lines | `test_violations_fixture_exact` |
| AC-2 | — | `clean.tsx` → `0 finding(s)`; its `wig-ignore input-label … (S-084)` is consumed (no `unused-ignore`) | `test_clean_fixture_zero` |
| AC-3 | — | lines `tests/fixtures/ui/violations.tsx:9 icon-button-label icon-only <button> needs aria-label …`; `--warn` exit 0, `--strict` exit 1, `--json` `{files, findings[]}` | `test_output_format_and_modes` |
| AC-4 | — | temp file: ignore without `(S-xxx)` → `4 invalid-ignore`; unknown rule → `6 invalid-ignore`; nothing to suppress → `8 unused-ignore` | `test_ignore_grammar` |
| AC-5 | **17 real findings** on `apps/desktop/src` (first run): `page.tsx` — reduced-motion ×1 (toast/panel/chat/muscle-result motion.divs), transition-all ×8, icon-button-label ×2 (SkipBack/SkipForward — and the play/pause toggle once the icon-expression case was added), input-label ×2 (range scrubber, AI chat input), outline-none-focus ×1; `CommandPalette.tsx` — reduced-motion, input-label, outline-none-focus, transition-all, div-click (backdrop) | **0 findings `--strict`**. Fixes in place: `aria-label` on 3 transport buttons (Persian) + `aria-hidden` icons; `aria-label` on range + 2 text inputs; `focus-visible:ring-2` replacements for both `outline-none`; `transition-all` → `transition-colors` / `transition-[color,transform] motion-reduce:transform-none` / `transition-[height,background-color]` (9 sites); `useReducedMotion()` in both files — slides/scales collapse to fades under `prefers-reduced-motion`; `…` instead of `...` in two placeholders; Command-Palette backdrop keeps click-to-dismiss with **one** justified ignore `wig-ignore div-click … (S-084)` and now only dismisses when the backdrop itself is the target (removed the inner `stopPropagation`). Gate: `12 pass / 0 fail / 0 missing / 1 skip` | `test_real_ui_tree_is_clean`, `test_real_tree_ignores_are_justified`, `gate.py --stage static --skip cargo-clippy` |
| AC-6 | gate returned `SKIP` when script absent | returns `MISSING` (fails `--strict-missing` in CI) — Skip ≠ Pass; `pnpm design:audit` added | `gate.py` source; CI run cited in ledger after push |

Regression: `next build` OK; `build-artifacts.spec.ts` 8/8; `biome check` 7 files clean; `tsc --noEmit` clean; `pytest tests/unit` **52 passed / 1 skipped**.

## Checker design notes (for the reviewer)
- Tag extraction is brace/quote-aware (JSX attributes with `{…}` and template literals), so `className={\`… transition-all …\`}` is seen — the first version missed those 4 sites; fixed before the fixture was frozen.
- `icon-button-label` covers three shapes: single self-closing icon child, empty button, and `{cond ? <A/> : <B/>}` icon expressions without any string literal.
- `reduced-motion` is one finding per file (first animation) and ignores `animate-spin` loaders alone; satisfied by `useReducedMotion`, `motion-reduce:` utilities, a `prefers-reduced-motion` media query, or `MotionConfig reducedMotion`.
- `input-label` accepts wrapping `<label>`, `htmlFor`↔`id`, `aria-label`/`aria-labelledby`; `type="hidden"` exempt.

## Reheal / carry
- Future rules (S-084): `autoFocus` justification, `onPaste`+`preventDefault`, `.map()` > 50 without virtualisation (needs data-size knowledge), `user-scalable=no`.
- The remaining `outline-none` usages are paired with `focus-visible:ring-*`; S-084's axe run must confirm the ring is visible on the dark surfaces (contrast of `indigo-500/50` on `#09090b`).


## CI
`7f5618c` → https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35675829105 — `ubuntu` ✅ `windows` ✅ `loop-audit` ✅ (unit junit incl. this step's tests on both OSes; gate `design-tokens` + `design-audit` PASS under `--strict-missing`).
