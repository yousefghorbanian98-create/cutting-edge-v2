# DESIGN.md — cutting-edge-v2
> **Hybrid Design System برای AI-Native Generation**
> ترکیب `Linear (dark craft) + Vercel (clean minimal) + Stripe (gradient accent)` — بهینه برای عامل‌های AI کدنویسی
> این فایل در ریشه پروژه قرار دارد تا هر Agent (Claude Code, Cursor, Codex) آن را به عنوان مرجع بصری بخواند.
> منبع الهام: `design-md/DESIGN.linear.md` (548 lines), `DESIGN.vercel.md` (736), `DESIGN.stripe.md` (487) از VoltAgent/awesome-design-md — MIT

---
version: 1.0.0
name: cutting-edge-v2 Design System
description: "AI-Native dark-first system: Linear's near-black canvas (#010102) + Vercel's geometric clarity + Stripe's blurple accent. Built for dashboards, RAG chat, and data-heavy SaaS."
author: cutting-edge-v2 team
basedOn: [linear.app, vercel, stripe]
license: MIT

---

## 1. Brand & Vision
- **Personality:** Precise, technical, quietly luxurious — like Linear's craft but with Stripe's confidence and Vercel's Swiss grid.
- **Promise:** "Cutting edge, but calm." No neon, no glassmorphism gimmicks. Content first, chrome second.
- **Tagline vibe:** `Software that thinks with you`

## 2. Colors
```yaml
# Core palette — dark-first (default)
canvas: "#010102"        # deepest black — Linear
canvas-soft: "#0A0A0B"
surface-1: "#0F1011"      # card bg
surface-2: "#141516"
surface-3: "#18191A"
hairline: "#23252A"       # borders — subtle
hairline-strong: "#34343A"

ink: "#F7F8F8"            # primary text
ink-muted: "#D0D6E0"
ink-subtle: "#8A8F98"
ink-tertiary: "#62666D"

# Accent — single chromatic (Stripe/Vercel inspired)
primary: "#5E6AD2"        # Linear blurple — primary CTA, focus ring
primary-hover: "#828FFF"
primary-strong: "#4C5BCC"
primary-soft: "rgba(94,106,210,0.12)"  # hover bg

# Semantic
success: "#0E9F6E"
warning: "#C27803"
danger: "#E02424"
info: "#5E6AD2"

# Light mode (auto via prefers-color-scheme)
light-canvas: "#FFFFFF"
light-surface: "#F6F8FA"
light-ink: "#0A0A0B"
light-hairline: "#E5E7EB"
```

**Usage rules:**
- فقط یک رنگ accent (primary) — هرگز دو رنگ پررنگ کنار هم نه
- CTA اصلی: `bg-primary text-white`، ثانویه: `bg-surface-2 border-hairline text-ink`
- Focus ring همیشه `ring-2 ring-primary/50` — از `web-interface-guidelines` تبعیت می‌کند

## 3. Typography
```yaml
font-display: "Geist Sans, Inter, SF Pro Display, system-ui"  # Vercel Geist
font-mono: "Geist Mono, JetBrains Mono, monospace"
font-brand: "Linear Display, Geist Sans"

scale:
  display-xl: { size: 72px, weight: 600, lineHeight: 1.05, tracking: -2.5px } # hero
  display-lg: { size: 56px, weight: 600, lineHeight: 1.10, tracking: -1.8px }
  display-md: { size: 40px, weight: 600, lineHeight: 1.15, tracking: -1.0px }
  headline:   { size: 28px, weight: 600, lineHeight: 1.20, tracking: -0.6px }
  title:      { size: 20px, weight: 500, lineHeight: 1.30 }
  body:       { size: 15px, weight: 400, lineHeight: 1.70 }
  body-sm:    { size: 13px, weight: 400, lineHeight: 1.60 }
  caption:    { size: 12px, weight: 500, lineHeight: 1.50, tracking: 0.3px, uppercase: false }
  mono:       { size: 13px, weight: 400, lineHeight: 1.60 }
```

**Rules:**
- Headings با `text-wrap: balance` (Vercel guideline)
- اعداد جدول: `font-variant-numeric: tabular-nums`
- `…` نه `...` ، گیومه فارسی `«»` برای فارسی، curly quotes برای انگلیسی

## 4. Spacing & Grid
```yaml
base: 4px
scale: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96]
radius:
  sm: 6px
  md: 10px
  lg: 16px
  xl: 24px
  full: 9999px
shadow:
  soft: "0 4px 20px rgba(0,0,0,0.06)"
  card: "0 1px 3px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.08)"
  focus: "0 0 0 3px rgba(94,106,210,0.32)"
grid:
  maxWidth: 1280px
  columns: 12
  gutter: 24px
  breakpoints: { sm: 640, md: 768, lg: 1024, xl: 1280, 2xl: 1536 }
```

**Layout:** Flex/Grid only — never JS measurement (Vercel rule). Container queries برای کارت‌ها.

## 5. Components
### Button
- Primary: `h-9 px-4 bg-primary text-white rounded-md font-medium hover:bg-primary-hover focus-visible:ring-2`
- Ghost: `h-9 px-4 bg-transparent border border-hairline text-ink hover:bg-surface-2`
- Icon-only: حتماً `aria-label` + `aria-hidden` روی svg (web-guideline)

### Card
- `bg-surface-1 border border-hairline rounded-xl p-6 shadow-card`
- Hover: `border-hairline-strong` + subtle lift `translate-y-[-1px]`

### Input
- `h-10 px-3 bg-surface-2 border border-hairline rounded-md focus:border-primary focus:ring-2 focus:ring-primary/20`
- `autocomplete` + `name` معنادار + `spellCheck={false}` روی email/code (Vercel form rules)

### Chat Bubble (core for RAG)
- User: `bg-primary text-white rounded-2xl rounded-br-sm ml-auto max-w-[80%]`
- Assistant: `bg-surface-2 border border-hairline rounded-2xl rounded-bl-sm max-w-[80%]` + citation badges `[1][2]`

### Table
- Header: `text-caption text-ink-subtle uppercase tracking-wide bg-surface-2`
- Row: `border-b border-hairline hover:bg-surface-2/50`
- Virtualize اگر >50 rows (Vercel perf rule)

## 6. Motion
```yaml
duration: { fast: 150ms, base: 200ms, slow: 300ms }
easing: { enter: "cubic-bezier(0.16,1,0.3,1)", exit: "cubic-bezier(0.4,0,1,1)" }
respect: "prefers-reduced-motion: reduce → disable or reduce to 150ms"
 animateOnly: ["transform", "opacity"]  # never `transition: all`
```

- Message stream: `opacity 0→1 + translateY 4px` per token chunk
- Modal: `scale 0.98→1 + opacity` with `overscroll-behavior: contain`

## 7. Dark / Light
- Default: **dark** (`color-scheme: dark` on html) — مطابق Linear
- Toggle via `next-themes`, ذخیره در localStorage, no FOUC
- `<meta name="theme-color" content="#010102">` (dark) / `#ffffff` (light)

## 8. Accessibility (from web-interface-guidelines)
- `aria-label` روی icon buttons, `label` روی هر input
- `focus-visible:ring-*` — هرگز `outline-none` بدون جایگزین
- Keyboard: `onKeyDown` برای هر `onClick` روی div
- Color contrast ≥ 4.5:1 (ink on canvas = 19:1 ✅)
- `scroll-margin-top` برای heading anchors

## 9. Performance Budgets
- Bundle JS <200KB gz, CSS <30KB
- Image: `width+height` + `loading=lazy` below fold, `priority` above fold
- List >50 → virtualize (`virtua` / `content-visibility: auto`)

## 10. Agent Instructions
> **به عامل AI:** هر صفحه/کامپوننت جدید را با این DESIGN.md بساز. اگر بین این فایل و رفتار پیش‌فرض مرددی، این فایل اولویت دارد. قبل از تحویل، خودت را با `web-design-guidelines` Skill چک کن (aria, focus, ...).

---
**Preview:** برای دیدن کاتالوگ بصری، فایل‌های `design-md/DESIGN.*.md` را باز کن — هر کدام `preview.html` هم دارند (در ریپو اصلی VoltAgent).
