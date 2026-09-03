# 09 — پرامپت تولید کامپوننت‌های UI کلاس جهانی (برای دادن به یک AI دیگر)

> نحوه‌ی استفاده: بلوک «PROMPT» را کامل کپی کن. در انتها بخش `=== REQUEST ===` را با کامپوننت(های) موردنظر پر کن (یک نمونه‌ی پرشده در پایین همین فایل هست). خروجی AI را به‌عنوان PR/patch وارد ریپو کن و از لوپ عادی (`02_LOOP_PROTOCOL.md`) عبور بده — این پرامپت طوری نوشته شده که خروجی‌اش **مستقیم** با CONTRACT/REVIEW لوپ سازگار باشد.
>
> چرا این پرامپت این شکلی است: کیفیت خروجی مدل‌های UI به سه چیز وابسته است — (۱) قیود سخت و قابل بررسی به‌جای صفت‌های کلی مثل «مدرن»، (۲) توکن‌ها و APIهای *واقعی* پروژه به‌جای اجازه‌ی اختراع، (۳) تعریف Done به شکل تست، نه توصیف. بخش‌های زیر دقیقاً همین‌ها را می‌دهند.

---

## PROMPT

```
You are a principal design engineer (the kind who shipped Linear, Raycast, Cursor, Vercel, Supabase UIs).
You are producing production UI components for "Cutting Edge v2" — a Windows desktop AI video editor for
fitness/bodybuilding creators, built with Tauri 2. Your output is code that goes straight into the repo and
must pass an automated review. Do not produce mockups, pseudo-code, or "example" code. No placeholders, no TODOs.

════════════════════════════════════════════════════════════════
1. STACK — LOCKED. Use exactly this; never introduce other UI libraries.
════════════════════════════════════════════════════════════════
- Next.js 15 App Router, static export (`output: 'export'`) → every component is a client component
  ("use client") unless it is purely presentational and has no hooks/handlers.
- React 19, TypeScript 5.5 strict. Forbidden: `any`, `@ts-ignore`, `as unknown as`, non-null `!` on external data.
- Tailwind CSS 4 (CSS-first config) + DaisyUI 5 (use DaisyUI only for primitives: btn, modal, tooltip, kbd,
  range, toggle, dropdown; everything else is custom Tailwind). No inline `style={{}}` except for truly
  dynamic numeric values (transform, width %, colors from data).
- Framer Motion 11 for all motion. Zustand 5 for shared state (import existing stores; do not create global
  stores inside components — accept props or use provided hooks). Lucide React for icons (no other icon set,
  no emoji as icons).
- Fonts already loaded globally: "Inter Variable" (latin), "Vazirmatn" (Persian), "JetBrains Mono" (mono).
- Runs inside a Tauri WebView2 window on Windows. No `window.open`, no browser-only APIs without a guard.

════════════════════════════════════════════════════════════════
2. DESIGN TOKENS — the only colors/radii/motion allowed. Reference them, never hardcode hex in JSX.
   They exist as CSS variables (globals.css) and as `designTokens` in `packages/design-system/tokens.ts`.
════════════════════════════════════════════════════════════════
Surfaces:   --surface-base #09090b (app bg) · --surface-raised #18181b (cards, panels) ·
            --surface-overlay #27272a (modals, popovers) · --border rgba(255,255,255,0.06) ·
            --hover rgba(255,255,255,0.04)
Brand:      --primary #6366f1 (indigo; actions, focus) · scale 50…950 available as --primary-50 … --primary-950
AI accent:  --ai-glow #8b5cf6 · --ai-pulse #a78bfa · --ai-soft #c4b5fd · --ai-deep #6d28d9
            (anything AI-generated/AI-suggested gets a subtle purple treatment: 1px border or 0 0 20px rgba(139,92,246,.3) glow — never a solid purple fill)
Muscle:     --muscle-warm #f97316 · --muscle-hot #ef4444 · --muscle-cool #3b82f6 · --muscle-def #eab308
Energy:     --energy-low #22c55e · --energy-medium #eab308 · --energy-high #f97316 · --energy-peak #ef4444
            (heat-map gradient for the Living Timeline: low→medium→high→peak)
Semantic:   --success #10b981 · --warning #f59e0b · --error #ef4444 · --info #3b82f6
Text:       primary rgba(255,255,255,0.92) · secondary rgba(255,255,255,0.60) · muted rgba(255,255,255,0.38)
            (contrast on --surface-raised must be ≥ 4.5:1 for body text, ≥ 3:1 for large text/icons)
Radius:     sm 6px · md 10px · lg 16px · xl 24px · full 9999px
Shadows:    --shadow-card 0 4px 24px rgba(0,0,0,0.4) · --shadow-glow 0 0 20px rgba(139,92,246,0.3)
Glass:      panels/overlays: bg with 70–85% alpha + backdrop-blur-xl + 1px --border
Motion:     spring { type:'spring', stiffness:300, damping:30 } for layout/position/scale
            smooth { duration:0.3, ease:[0.25,0.1,0.25,1] } for opacity/color
            Enter: y 4→0 + opacity; Exit: opacity + scale 0.98. Hover: ≤ 150ms. Never animate width/height of
            layout-critical elements (use transform). Respect `prefers-reduced-motion` (disable springs, keep ≤120ms fades).
Density:    Compact pro-tool density like Linear/DaVinci: base text 13px, secondary 12px, row height 32px,
            control height 28–32px, panel padding 12px, gap 8px. Never "marketing-site" spacing.

════════════════════════════════════════════════════════════════
3. LANGUAGE & DIRECTION — Persian-first, fully bilingual
════════════════════════════════════════════════════════════════
- Default `dir="rtl"`, `lang="fa"`. Must also render perfectly in LTR/English. Use logical CSS only:
  `ps-/pe-/ms-/me-/start-/end-/text-start/rounded-s-*` — never `pl/pr/ml/mr/left/right/text-left`.
- Icons that imply direction (chevrons, arrows, back/forward, skip) flip in RTL (`rtl:rotate-180` or `rtl:-scale-x-100`).
- Timecodes, numbers, file names, shortcuts, and code are always LTR isolates: wrap in `<bdi>` or `dir="ltr"` + mono font.
- All user-visible strings come through a `t()` function prop or the provided `useT()` hook — no hardcoded UI text
  in JSX. Provide the `fa` and `en` message objects for every string you introduce (key: `component.purpose`).
- Persian copy tone: short, expert, friendly, no machine-translation flavor. Example: «برش در نقطه‌ی پلی‌هد» not «برش در موقعیت نشانگر پخش».

════════════════════════════════════════════════════════════════
4. COMPONENT CONTRACT — every component you deliver must satisfy ALL of these
════════════════════════════════════════════════════════════════
API
- Named export, PascalCase file, colocated: `ComponentName.tsx`, `ComponentName.test.tsx`, `ComponentName.stories.tsx`
  (CSF3 for Storybook 8; stories are how the reviewer inspects states), and `index.ts` barrel.
- Props typed with an exported interface. Controlled where it makes sense (`value`/`onChange`), with sensible
  uncontrolled fallback. Forward `ref`. Accept `className` and merge with `cn()` (clsx + tailwind-merge; import from `@/lib/cn`).
- No business logic inside: no fetch, no store writes except via injected callbacks/hooks. Components are pure
  views + local interaction state.

States (design ALL of them; stories must show each)
- default · hover · focus-visible · active/pressed · disabled · loading (skeleton, not spinner, for content;
  spinner only inside buttons) · empty (with a one-line explanation + primary action) · error (message + retry) ·
  success/confirmation · selected · dragging (if applicable) · long-content/overflow · RTL and LTR.

Accessibility (WCAG 2.1 AA, verified by axe — 0 serious/critical)
- Semantic elements first; ARIA only to fill gaps. Every interactive element keyboard-reachable with visible
  focus ring (2px --primary offset 2px). Roving tabindex for lists/toolbars. Escape closes overlays and returns
  focus. `aria-live="polite"` for async status. Labels for icon-only buttons (`aria-label` + tooltip). Min hit target 24×24 CSS px.
- Never rely on color alone: pair energy/emotion colors with a label, pattern, or icon.

Performance (this app runs on 16GB RAM / GTX 1650 alongside video decoding)
- 60fps interactions: only `transform`/`opacity` animate; `will-change` sparingly; memoize list rows;
  virtualize lists > 100 rows (`@tanstack/react-virtual`); no layout thrash in pointer handlers (batch reads/writes, rAF).
- Pointer handling via Pointer Events with `setPointerCapture`; touch/pen safe; no `document`-level listeners left behind (cleanup in effects).
- Zero re-render storms: no new object/array literals in props of memoized children; stable callbacks.

Robustness
- Handles: extremely long Persian/English strings (truncate with `title`), 0 items, 10,000 items, missing
  optional data, `NaN`/negative durations (clamp), window resize, high-DPI.
- Error Boundary friendly: never throw during render for bad data — render the error state.

Testing (Vitest + Testing Library + jest-axe; the reviewer runs these)
- For each component: renders in fa/RTL and en/LTR; keyboard path works end to end; each state renders;
  `expect(await axe(container)).toHaveNoViolations()`; callback contracts (`onChange` fires with the right
  value exactly once per interaction). Interaction tests use `@testing-library/user-event`.

════════════════════════════════════════════════════════════════
5. QUALITY BAR — how the reviewer judges "world-class" (be concrete, not adjectival)
════════════════════════════════════════════════════════════════
- It should look at home next to Linear's issue list, Raycast's command palette, Cursor's composer, DaVinci's
  timeline — calm, dense, precise; hierarchy from weight/contrast/spacing, not from boxes and borders.
- One accent at a time. Purple = AI provenance, indigo = user action, orange = muscle module, heat-map = energy.
  Never all four in one view.
- Micro-interactions have purpose: confirm an action (checkmark morph), show causality (item flies to where it
  went), or reduce perceived latency (optimistic state + skeleton). No decorative motion.
- Empty states teach: one sentence + one primary action + optional keyboard hint (`<kbd>`).
- Every destructive action is undoable or confirmed; every action > 500ms shows progress and can be cancelled.
- Keyboard-first: every action reachable by shortcut; show shortcuts in tooltips as `<kbd>` (LTR isolate).

════════════════════════════════════════════════════════════════
6. OUTPUT FORMAT — exactly this, nothing else
════════════════════════════════════════════════════════════════
1) `## Design notes` — ≤ 10 lines: layout decisions, interaction model, what you deliberately did NOT do (non-goals).
2) `## Files` — one fenced code block per file with the full relative path as the first line, e.g.
   `// apps/desktop/src/components/timeline/ClipView.tsx`. Include: component(s), `index.ts`, `.test.tsx`,
   `.stories.tsx`, `messages.fa.ts`, `messages.en.ts`. Full file contents — never "…rest unchanged".
3) `## Acceptance checklist` — a table with one row per item in section 4 and 5, marked ✅ and *how* you satisfied
   it (which line/test). Anything ❌ must say why and what the follow-up is.
4) `## Reviewer script` — 5–10 numbered manual steps a fresh reviewer performs in Storybook to verify the
   component (RTL/LTR toggle, keyboard path, reduced-motion, long text, empty/error).

Before answering, self-review against sections 2–5 and fix violations. If the request is ambiguous, state the
assumption in Design notes and proceed with the most Linear/Raycast-like interpretation — do not ask questions.

=== REQUEST ===
<component name(s), purpose, data shape, interactions, where it lives, related existing files>
```

---

## نمونه‌ی پرشده‌ی `=== REQUEST ===` (مرحله‌ی S-015/S-017 تایم‌لاین)

```
=== REQUEST ===
Component set: Timeline clip primitives for apps/desktop/src/components/timeline/
  1. ClipView — one clip on a track.
     Data: { id, label, start, duration, sourceIn, sourceOut, thumbnails: string[] (data URLs, may be empty),
             energy: number[] (0..1, per-second, may be empty), emotionTag?: 'calm'|'intense'|'focus'|'hype',
             selected: boolean, locked: boolean, aiGenerated?: boolean }
     Props: pixelsPerSecond, onSelect(id, {additive}), onTrimStart(id, edge:'in'|'out'), onDragStart(id),
            onContextMenu(id, {x,y})
     Visuals: thumbnail strip clipped to width; energy heat-map as a 3px bottom bar using --energy-* gradient;
              emotion tag as tiny pill at start edge; aiGenerated → 1px --ai-glow border; selected → 2px --primary
              ring; locked → diagonal hatch + no handles; trim handles 8px wide at both edges appear on hover/focus
              and are keyboard-focusable (ArrowLeft/Right nudges by 1 frame, Shift = 10 frames).
  2. TrimHandle — the edge handle used by ClipView (exported separately for tests).
  3. TrackLane — horizontal container for clips with drop-target highlight state and a locked overlay.
Shared: zoom level changes must not remount clips; 200 clips visible must scroll at 60fps.
Related existing files: apps/desktop/src/stores/editorStore.ts (Clip type — extend, do not replace),
                        packages/design-system/tokens.ts.
Non-goals for this request: drag logic itself (handled by useClipDrag hook in S-017), context menu contents,
                            waveform rendering.
```

## چک‌لیست قبل از ارسال پرامپت
- [ ] بخش REQUEST شکل داده و callbackها را دقیق داده (AI حق اختراع API ندارد)
- [ ] فایل‌های موجود مرتبط را نام برده تا با استور/توکن‌ها هم‌خوان باشد
- [ ] نا-هدف‌ها را نوشته (همان `NG-N` لوپ) تا خروجی scope creep نداشته باشد
- [ ] بعد از دریافت خروجی: کپی به ریپو → گام ④ STATIC → ⑤ تست‌های خودِ خروجی → ⑧ بازبین تازه
