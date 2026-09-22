# DESIGN.md — Cutting Edge v2

> **STATUS: AUTHORITY (S-099, 2026-09-22).** This file is the single visual reference for every agent and human.
> The fenced `# tokens:` blocks below are **machine-checked** against the code on every commit and in CI:
> `node scripts/check-design-tokens.js` (gate `design-tokens`, supervisor C14) compares
> `DESIGN.md ⇄ apps/desktop/src/app/globals.css (@theme static) ⇄ packages/design-system/tokens.ts` three ways.
> To change a token: edit all three in one commit (the check names the variable and the two values otherwise).
> Decision record: ADR-0010 — `docs/adr/0010-design-md-single-ui-authority.md`.

> **Persian-first, dark-only, offline.** A Windows desktop editor for sports / fitness creators.
> Inspirations were Linear (dark craft), Vercel (Swiss clarity) and Stripe (one confident accent) — see
> `design-md/DESIGN.*.md` for the sources — but **only the values below exist in this product.**

---
version: 2.0.0
name: cutting-edge-v2 Design System
description: "Dark-only, RTL-first desktop editor: near-black zinc surfaces, indigo primary, violet AI accent, fitness heat/energy scales. Inter Variable + Vazirmatn + JetBrains Mono, all self-hosted."
license: MIT
sources: [apps/desktop/src/app/globals.css, packages/design-system/tokens.ts]
---

## 1. Brand & Vision
- **Personality:** Precise, technical, calm. The video is the hero; chrome stays quiet until the AI acts — then it glows violet.
- **Promise:** "Cutting edge, but calm." No neon, no glassmorphism gimmicks, no light theme (ADR-0003 / ADR-0007).
- **Audience:** Persian-speaking coaches and athletes on a mid-range Windows laptop (16 GB, GTX 1650). Every screen must read at 1366×768 in RTL.

## 2. Colors

All colours are Tailwind-4 theme variables (`--color-*` → utilities such as `bg-surface-raised`, `text-ai-glow`, `border-surface-border`).
The `primary` scale is JS-only today (`designTokens.colors.primary`) and is consumed through DaisyUI's `primary` theme colour; it becomes a `--color-primary-*` set when a UI card needs the utilities (owner: S-013).

```yaml
# tokens: colors
# surfaces — zinc near-black, three elevations + two white overlays
--color-surface-base: "#09090b"        # app canvas
--color-surface-raised: "#18181b"      # panels, cards, timeline lanes
--color-surface-overlay: "#27272a"     # popovers, menus, tooltips
--color-surface-border: "rgb(255 255 255 / 0.06)"   # hairline on dark
--color-surface-hover: "rgb(255 255 255 / 0.04)"    # row / clip hover

# AI accent — violet; only the AI features use it (Style Match, Assistant, Enhancer)
--color-ai-glow: "#8b5cf6"
--color-ai-pulse: "#a78bfa"
--color-ai-soft: "#c4b5fd"
--color-ai-deep: "#6d28d9"

# status
--color-success: "#10b981"
--color-warning: "#f59e0b"
--color-error: "#ef4444"
--color-info: "#3b82f6"

# muscle enhancer heat map (overlay legend only — never applied to the athlete's skin)
--color-muscle-warm: "#f97316"
--color-muscle-hot: "#ef4444"
--color-muscle-cool: "#3b82f6"
--color-muscle-def: "#eab308"

# beat-sync energy scale (timeline / waveform)
--color-energy-low: "#22c55e"
--color-energy-medium: "#eab308"
--color-energy-high: "#f97316"
--color-energy-peak: "#ef4444"

# primary — indigo scale (tokens.ts only; DaisyUI `primary` = 500)
ts:colors.primary.50: "#eef2ff"
ts:colors.primary.100: "#e0e7ff"
ts:colors.primary.200: "#c7d2fe"
ts:colors.primary.300: "#a5b4fc"
ts:colors.primary.400: "#818cf8"
ts:colors.primary.500: "#6366f1"
ts:colors.primary.600: "#4f46e5"
ts:colors.primary.700: "#4338ca"
ts:colors.primary.800: "#3730a3"
ts:colors.primary.900: "#312e81"
ts:colors.primary.950: "#1e1b4b"
```

**Usage rules**
- Exactly **two** chromatic accents may appear on one screen: `primary` (indigo) for the user's own actions and `ai-glow` (violet) for anything the AI produced or is producing. Never both on the same control.
- Text on `surface-base`: white at 100 % (headings), 80 % (body), 40 % (secondary), 20 % (disabled/hints). Contrast of `#ffffff/80` on `#09090b` ≈ 15:1; 40 % ≈ 6.5:1 — still AA for body text; never go below 40 % for readable copy.
- `error`/`success`/`warning` colour is never the only signal — pair with icon + text (WIG, S-084).
- Status colours are shared with the heat/energy scales by value (`#ef4444` appears three times) on purpose: one red, one orange, one yellow across the product.

## 3. Typography

```yaml
# tokens: typography
--font-sans: "Inter Variable, Vazirmatn, system-ui, sans-serif"
--font-mono: "JetBrains Mono, ui-monospace, monospace"
```

- **Self-hosted only** (`@fontsource-variable/inter`, `@fontsource/vazirmatn` 400/700, `@fontsource/jetbrains-mono` 400) — the app must render identically with no network. The Playwright suite fails on any `fonts.googleapis.com` / `fonts.gstatic.com` request.
- `html[lang="fa"][dir="rtl"]` is the default; Vazirmatn resolves for Persian glyphs, Inter for Latin, both from the same `--font-sans` stack — do not switch font-family per language.
- Scale (Tailwind defaults, no custom scale until S-013 introduces the timeline typography): `text-xs` 12 px captions/mono readouts · `text-sm` 14 px controls · `text-base` 16 px body · `text-lg` 18 px panel titles · `text-2xl`+ page header (gradient `from-indigo-400 to-purple-300`, `bg-clip-text`).
- Numbers in timecodes, BPM, sizes: `font-mono tabular-nums`; Persian digits only inside prose, Latin digits in technical readouts (S-085 decides per string).
- `…` not `...`; Persian quotes `«»`; `text-wrap: balance` on headings.

## 4. Radius, Spacing & Shadows

```yaml
# tokens: radius
--radius-sm: "6px"      # chips, inputs, small buttons
--radius-md: "10px"     # buttons, list rows, thumbnails
--radius-lg: "16px"     # cards, panels
--radius-xl: "24px"     # modals, feature tiles
ts:radius.full: "9999px"
```

```yaml
# tokens: shadows
ts:shadows.glow: "0 0 20px rgba(139,92,246,0.3)"   # AI activity halo (ai-glow at 30 %)
ts:shadows.card: "0 4px 24px rgba(0,0,0,0.4)"      # raised panels on base
```

- Spacing: Tailwind's 4 px scale (`1`=4 px … `6`=24 px … `12`=48 px). Panel padding `p-6`, control gaps `gap-2`/`gap-3`, section gaps `gap-6`.
- Layout is Flex/Grid only; never measure with JS for layout. Editor shell = CSS grid `media-bin | preview | inspector` over `timeline`; timeline rows virtualised (S-015).
- Borders use `border-surface-border`; hover lifts to `bg-surface-hover`, not a stronger border.

## 5. Motion

```yaml
# tokens: motion
ts:motion.spring.type: "spring"
ts:motion.spring.stiffness: "300"
ts:motion.spring.damping: "30"
ts:motion.smooth.duration: "0.3"
ts:motion.smooth.ease: "[0.25, 0.1, 0.25, 1]"
```

- Framer Motion 11 with `designTokens.motion.spring` for layout/position changes (clips, panels) and `motion.smooth` (300 ms, ease-out) for opacity/reveal.
- Animate **only** `transform` and `opacity`; `transition: all` is a lint failure (S-100 `design_audit.py`).
- `prefers-reduced-motion: reduce` → springs become instant, reveals ≤ 150 ms; the AI glow pulse stops (static halo).
- Progress for anything > 500 ms: determinate bar when the backend reports `%`, otherwise an indeterminate bar + cancel; never a spinner alone.

## 6. Components (DaisyUI 5, theme `dark`)

DaisyUI 5 is compiled through `@plugin 'daisyui' { themes: dark --default; }`. Use its classes (`btn`, `card`, `input`, `menu`, `modal`, `tooltip`, `progress`) and recolour with the tokens above — do not hand-roll a second button system.

- **Button** — `btn btn-primary` (indigo) for user actions; `btn` + `bg-ai-glow text-white hover:bg-ai-pulse shadow-[var(--shadow-glow)]` for AI actions; `btn btn-ghost` for secondary. Icon-only buttons carry `aria-label`; the icon `aria-hidden`.
- **Card / Panel** — `bg-surface-raised border border-surface-border rounded-lg p-6` (+ `shadow-card` via tokens.ts for floating panels).
- **Input / Select** — DaisyUI `input input-bordered bg-surface-overlay rounded-md focus-visible:ring-2 focus-visible:ring-primary/50`; every input has a visible `<label>` (Persian) and `name`; `spellCheck={false}` on paths, codes, keys.
- **Timeline clip** — `rounded-md` block, energy colour as a 2 px bottom edge (`border-b-2 border-energy-*`), selected = `ring-2 ring-primary`, AI-generated = `ring-ai-glow`.
- **Preview** — 16:9 `bg-black` stage with `rounded-xl` overflow hidden; the HTML `<video>` gets a `<track kind="captions">` from S-047 (until then the Biome a11y ignore is documented).
- **Muscle Enhancer overlay** — heat legend uses the `muscle-*` tokens on a translucent `surface-overlay` chip; the athlete's pixels are never tinted (ADR-0007 product rule, "100 % natural").
- **Toasts / Errors** — Persian sentence + what to do next; `error` colour + icon + text; never only red.

## 7. Dark only
- `html { color-scheme: dark }`; there is no light theme and no theme toggle (ADR-0003). `<meta name="theme-color" content="#09090b">`.
- Do not add a theme-switching library or DaisyUI light themes; `supervise.py` C15 flags them.

## 8. Accessibility (Web Interface Guidelines snapshot — `docs/integrations/web-guidelines/`)
- `aria-label` on icon-only buttons; a `<label>` for every input; `<button>` for actions (never `div onClick`).
- Focus: `focus-visible:ring-2 ring-primary/50` everywhere; `outline-none` only with that replacement.
- Keyboard: every action reachable by keyboard and listed in the Command Palette (S-022); `Esc` closes, `Enter` confirms, arrow keys move the playhead.
- RTL: logical properties (`ms-*`, `pe-*`, `text-start`), never `ml/mr` for layout; icons that imply direction (play, next) are mirrored in RTL.
- Contrast ≥ 4.5:1 for text (see §2); `scroll-margin-top` on anchors; `overscroll-behavior: contain` inside modals and lists.
- Enforced offline by `python scripts/design_audit.py apps/desktop/src --strict` (S-100) and by axe in Playwright (S-084).

## 9. Performance budgets (desktop WebView2)
- First load of the static export: JS < 200 KB gz, CSS < 80 KB raw (S-007 baseline 64.6 KB with all DaisyUI dark theme rules).
- 60 fps timeline scrub on a GTX 1650 laptop; lists > 50 rows virtualised; thumbnails `width`+`height` set, `loading="lazy"` off-screen.
- No layout thrash: read → write batching in scrub handlers; `content-visibility: auto` for off-screen media-bin sections.

## 10. Agent instructions
> **To the agent:** before any UI work read this file, then `AGENTS.md` §5. Use only the tokens above (Tailwind utilities generated from them, or `designTokens` in TS). Adding a colour, font or radius means editing `globals.css`, `tokens.ts` **and** this file in the same commit — `node scripts/check-design-tokens.js` and the CI job will name the variable you forgot. After the UI change run `python scripts/design_audit.py apps/desktop/src --strict` (S-100) and the Playwright styling suite.
