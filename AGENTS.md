# AGENTS.md — cutting-edge-v2
> **Agent Operating Manual** — این فایل توسط هر Agent Harness (Claude Code, Cursor, Codex, OpenCode) به صورت خودکار خوانده می‌شود.
> ترکیب ۳ منبع: **ECC + Web Design Guidelines + Awesome Design**

---

## 1. Project Identity
- **Name:** cutting-edge-v2 — AI-Native SaaS Platform (Modular Monolith)
- **Stack:** Next.js 15 (App Router) + NestJS + PostgreSQL + Prisma + pgvector/Qdrant + Redis + BullMQ
- **Design System:** `DESIGN.md` در ریشه (Hybrid Linear/Vercel/Stripe) — **مرجع بصری اجباری**
- **16-Layer Plan:** `docs/16-LAYER-PRODUCTION-PLAN.md` — منبع حقیقت معماری
- **Roadmap v2:** `docs/ROADMAP-v2-WITH-INTEGRATIONS.md` — این ۳ ادغام در نقشه راه

## 2. How to Build
```bash
git clone https://github.com/yousefghorbanian98-create/cutting-edge-v2.git
pnpm install
cp .env.example .env
docker compose up -d   # postgres + redis + qdrant
pnpm dev               # web:3000 api:4000
pnpm test              # coverage ≥80%
```

- **Conventional Commits:** `feat:`, `fix:`, `docs:`, `chore:`
- **Branching:** Trunk-based — شاخه کوتاه `feat/*` ≤2 روز، PR squash
- **Lint/Format:** `pnpm lint` + `pnpm typecheck` باید سبز باشد قبل از PR

## 3. ECC — Agent Harness (Selective)
> منبع: `affaan-m/ECC` — The agent harness performance system (261 skills, MIT)

**نصب گزینشی فعال:**
```bash
npm i -g ecc-universal
# فقط core skills نصب شده — نه کل 261
```

**Skills فعال در این پروژه (از `docs/integrations/ecc/`):**
- `tdd-workflow` — RED → GREEN → REFACTOR اجباری
- `code-review` — هر PR یک review با context تازه
- `security-scan` — OWASP + secrets
- `plan` (`/ecc:plan`) — قبل از کدنویسی، پلن به عنوان artifact
- `build-fix`, `e2e-testing`, `doc-updater`

**Workflow اجباری:**
```
plan -> test -> implement -> review -> verify -> remember -> improve
```
- قبل از هر فیچر: `/ecc:plan "Add X"` → فایل `docs/plan-*.md` → تایید انسانی
- سپس TDD: تست اول، بعد کد
- سپس `/code-review` با agent متفاوت

**Hooks فعال:**
- `SessionStart` — چک `DESIGN.md` و `AGENTS.md` لود شده؟
- `Stop` — خلاصه سشن + پیشنهاد skill جدید
- `PreCommit` — lint + typecheck + secrets scan (trufflehog)

## 4. Web Design Guidelines Skill (Vercel Labs)
> منبع: `vercel-labs/agent-skills` + `vercel-labs/web-interface-guidelines` — MIT

**فایل:** `.claude/skills/web-design-guidelines/SKILL.md` (همچنین در `.cursor/skills/` و `.windsurf/rules/`)

**چه می‌کند:**
- کد UI را با قوانین `command.md` (190 قانون) چک می‌کند: a11y, focus, forms, animation, typography, perf
- منبع زنده: `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`

**Usage:**
- وقتی کاربر گفت `review my UI` / `check a11y` / `audit design` → این Skill را فعال کن
- خروجی: `file:line` تِرس (مثال: `src/Button.tsx:42 - icon button missing aria-label`)

**قوانین طلایی که همیشه رعایت کن:**
- `aria-label` روی icon按钮، `label` روی هر input
- `focus-visible:ring-*` — هرگز `outline-none` بدون جایگزین
- `transform/opacity` فقط برای انیمیشن — هرگز `transition: all`
- `width+height` روی هر `img`، `loading=lazy` below-fold
- `Intl.DateTimeFormat` برای تاریخ — نه hardcode

**CI:** `pnpm design:audit` → این Skill روی `apps/web/**/*.tsx` اجرا می‌شود

## 5. Awesome Design — DESIGN.md
> منبع: `VoltAgent/awesome-design-md` (114K stars, MIT) — 73 DESIGN.md از برندهای واقعی

**فایل‌های مرجع:** `design-md/DESIGN.linear.md`, `DESIGN.vercel.md`, `DESIGN.stripe.md` (هر کدام 500-700 خط)
**فایل مرجع پروژه:** `DESIGN.md` در ریشه — **این فایل برای هر خروجی UI اولویت دارد**

**دستور به Agent:**
> "Use DESIGN.md for all styling. If in doubt, DESIGN.md wins over defaults."
- رنگ‌ها فقط از `DESIGN.md` بخش Colors
- تایپوگرافی فقط `Geist Sans / Linear Display`
- کامپوننت‌ها دقیقاً کلاس‌های بخش Components

**Workflow طراحی:**
1. یک `DESIGN.md` از `design-md/` به عنوان الهام انتخاب کن (پیش‌فرض: Linear)
2. به جای کپی، `DESIGN.md` ریشه را بخوان
3. کامپوننت را با Tailwind + shadcn بساز
4. با Web Design Guidelines Skill خودت را چک کن

## 6. Quality Gates (قبل از هر PR)
- [ ] `pnpm lint && pnpm typecheck` سبز
- [ ] تست‌ها نوشته شده (coverage ≥80% برای ماژول جدید)
- [ ] `DESIGN.md` رعایت شده (رنگ/فاصله/تایپو)
- [ ] `web-design-guidelines` audit بدون خطای a11y
- [ ] `ECC code-review` پاس شده
- [ ] `promptfoo` eval اگر تغییر prompt/RAG

## 7. Security
- هرگز `.env` را کامیت نکن — از `Doppler` / `Vault`
- `npx ecc-agentshield scan --path .` قبل از PRهای حساس
- `trufflehog` در pre-commit

## 8. Prompts & AI
- Promptها در `prompts/*.md` version می‌شوند — هر تغییر با git
- LLM abstraction: `openai` primary, `anthropic` fallback — هرگز مستقیم صدا نزن
- هر خروجی RAG باید citation داشته باشد

## 9. Where to Look
- Architecture: `docs/16-LAYER-PRODUCTION-PLAN.md`
- Roadmap v2: `docs/ROADMAP-v2-WITH-INTEGRATIONS.md`
- ADRs: `docs/adr/`
- Runbooks: `docs/runbooks/`
- Integrations docs: `docs/integrations/{ecc,web-guidelines,awesome-design}/`

---
> این فایل به صورت خودکار توسط Claude Code, Cursor, Codex خوانده می‌شود. آن را به‌روز نگه دار — هر تصمیم جدید را اینجا ثبت کن.
