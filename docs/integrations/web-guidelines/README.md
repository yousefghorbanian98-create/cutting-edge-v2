# Web Design Guidelines Integration

> **Source:** `vercel-labs/agent-skills` (Skill) + `vercel-labs/web-interface-guidelines` (Rules) — MIT
> Raw: https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md (190 rules)

## چیست؟
یک Agent Skill سبک از Vercel Labs که کد UI شما را با 40+ قانون حرفه‌ای (a11y, focus, forms, animation, typography, perf, hydration) چک می‌کند و خروجی `file:line` می‌دهد. منبع قوانینش هر بار به صورت زنده fetch می‌شود، پس همیشه آپدیت است.

## کجا نصب شد؟
```
.claude/skills/web-design-guidelines/SKILL.md  (Claude Code)
.cursor/skills/web-design-guidelines.md        (Cursor)
.windsurf/rules/web-design-guidelines.md       (Windsurf)
.github/copilot-instructions.md                (Copilot)
docs/integrations/web-guidelines/SKILL.md     (archive)
docs/integrations/web-guidelines/web-interface-guidelines.md (190 rules — snapshot 2026-09-08)
```

## چگونه استفاده می‌شود؟
- **دستی:** به Agent بگو `review my UI` / `check a11y` / `audit design` → Skill فعال می‌شود، فایل‌ها را می‌خواند، با قوانین می‌سنجد، `file:line` گزارش می‌دهد
- **CI (پیشنهادی):** `pnpm design:audit` روی `apps/web/**/*.tsx`

مثال خروجی:
```
src/components/Button.tsx:42 - icon button missing aria-label
src/components/Input.tsx:18 - input lacks label
src/components/Card.tsx:55 - animation missing prefers-reduced-motion
```

## قوانین کلیدی (از command.md)
- `aria-label` روی icon button، `label` روی هر input
- `focus-visible:ring-*` — هرگز `outline-none` بدون جایگزین
- `transform/opacity` فقط برای انیمیشن — هرگز `transition: all`
- `width`+`height` روی `img` + `loading=lazy` below-fold
- `Intl.DateTimeFormat` برای تاریخ — نه hardcode

## ارتباط با DESIGN.md
`DESIGN.md` می‌گوید **چی** بساز (رنگ/تایپو)، این Skill می‌گوید **چگونه درست** بساز (a11y/perf). هر کامپوننت جدید باید هر دو را پاس کند — چک در `AGENTS.md` بخش 6.

## آپدیت
چون Skill هر بار `command.md` را fetch می‌کند، نیازی به آپدیت دستی نیست. snapshot در `web-interface-guidelines.md` فقط برای آفلاین/مرجع است.
