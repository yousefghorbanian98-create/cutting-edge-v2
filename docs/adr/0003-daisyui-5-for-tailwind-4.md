# ADR-0003 — DaisyUI 5 (not 4) on Tailwind 4, wired through `@tailwindcss/postcss`

## Status
Accepted — 2026-09-06

## Context
The locked stack says "Tailwind 4 + DaisyUI". The imported UI used DaisyUI-4 idioms while the desktop app pinned Tailwind 4.3. DaisyUI 4 is a Tailwind-3 plugin (`tailwind.config.js` plugin API) and does not load under Tailwind 4's CSS-first `@plugin` model; the page rendered unstyled (BUG-9). Card S-007; protocol §5 "clarifications".

## Decision
Use **DaisyUI 5.7.x** via `@plugin 'daisyui'` in `apps/desktop/src/app/globals.css`, Tailwind 4 via `@tailwindcss/postcss`, tokens declared once in a `@theme static` block and mirrored to `packages/design-system/tokens.ts`. Fonts (Vazirmatn, Inter Variable, JetBrains Mono) are self-hosted through `@fontsource`; no Google Fonts requests. This is a compatibility correction, not a stack change.

## Consequences
- Positive: real styling with one source of truth for tokens; offline-safe fonts; DaisyUI components usable in every later UI card.
- Negative: DaisyUI 5 theme syntax differs from 4 — old snippets in the reference docs must be adapted, not pasted.
- Follow-ups: `apps/desktop/tests/build-artifacts.spec.ts` keeps `tokens.ts` ⇄ `@theme` in sync; S-099 makes `DESIGN.md` describe the same tokens and `scripts/check-design-tokens.js` enforces it in the gate.
