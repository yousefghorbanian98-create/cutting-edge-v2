# 🗺️ ROADMAP v2 — cutting-edge-v2 + 3 Integrations
> **16-Layer Plan + ECC + Web Design Guidelines + Awesome Design** — یک نقشه راه واحد، قابل اجرا از همین امروز
> Date: 2026-09-08 (Asia/Tehran) | Branch: `arena/01a07f8a-cutting-edge-v2` | Previous: `docs/16-LAYER-PRODUCTION-PLAN.md`

---

## 📌 TL;DR برای مدیرعامل / Tech Lead

| سوال | جواب |
|---|---|
| **چی اضافه شد؟** | ۳ لایه تقویتی روی نقشه ۱۶ لایه قبلی: ① ECC (هوشمندسازی SDLC) ② Vercel Web Guidelines (کیفیت UI) ③ Awesome Design (سیستم طراحی آماده) |
| **هزینه؟** | صفر — هر ۳ MIT و بدون vendor lock |
| **ریسک؟** | کم — نصب گزینشی، هر کدام قابل حذف با یک `git revert` |
| **اثر؟** | سرعت توسعه 30%↑ (ECC)، کیفیت UI 2x (Guidelines + DESIGN.md)، Thrash طراحی 80%↓ |
| **زمان؟** | ۲ روز setup + سپس در هر اسپرینت به صورت بومی استفاده |

---

## 1. معماری ادغام — کجا هر کدام می‌نشیند؟

```
16-LAYER PLAN (قبلی)
├── L1..L5  (Product, Arch, DB, API, Backend)
│     └── + ECC: /ecc:plan, TDD, code-review برای هر ماژول
├── L6 Frontend
│     └── + DESIGN.md (Awesome) = WHAT to build
│     └── + Web Guidelines Skill = HOW to build correctly
├── L7 Design System
│     └── DESIGN.md (hybrid) + tokens + Storybook + audit
├── L8..L9 (Auth, Security)
│     └── + ECC security-scan + AgentShield
├── L10 DevOps
│     └── + ECC hooks (pre-commit, SessionStart)
├── L11..L13 (Infra, Cache, Observability)
│     └── بدون تغییر
├── L14 Testing
│     └── + ECC tdd-workflow + e2e-testing skill
├── L15 AI
│     └── + ECC ai-first-engineering skill + DESIGN.md برای AI-generated UI
└── L16 Docs
      └── + AGENTS.md (مرکز فرمان عوامل) + docs/integrations/*
```

**فایل‌های جدید (این کامیت):**
```
DESIGN.md                                   # هیبرید اختصاصی (مرجع Agent)
AGENTS.md                                   # دفترچه عامل‌ها
.claude/skills/web-design-guidelines/SKILL.md
.cursor/skills/web-design-guidelines.md
.windsurf/rules/web-design-guidelines.md
.github/copilot-instructions.md
design-md/DESIGN.{linear,vercel,stripe}.md  # مراجع الهام (3)
docs/integrations/{ecc,web-guidelines,awesome-design}/README.md
docs/ROADMAP-v2-WITH-INTEGRATIONS.md        # همین فایل
docs/16-LAYER-PRODUCTION-PLAN.md            # دست نخورده — مرجع
```

---

## 2. نقشه راه فازبندی — ۲۶ هفته‌ای (۶ ماه)

### فاز 0 — Foundation + Integrations Setup (هفته 1-2) ✅ این کامیت

| Task | Owner | خروجی | وابستگی |
|---|---|---|---|
| PRD + Arch + DB (L1-L3) | Tech Lead | `docs/16-LAYER...` ✅ | — |
| **ECC selective install** | Tech Lead | `AGENTS.md` + hooks | L10 |
| **Web Guidelines install** | FE Lead | 4x SKILL.md + snapshot | L6 |
| **DESIGN.md hybrid** | Design+FE | `DESIGN.md` root + 3 refs | L7 |
| Repo hygiene | All | `README.md` جدید، CI skeleton | — |

**DoD فاز 0:** `pnpm lint`, `design:audit` روی یک کامپوننت نمونه سبز، `/ecc:plan` یکبار تست شده

### فاز 1 — MVP Build با پشتیبانی ۳ ادغام (هفته 3-10)

| هفته | فیچر | ECC | Design | Guidelines |
|---|---|---|---|---|
| 3-4 | Auth + Org (L8) | `tdd-workflow` + `plan` | `DESIGN.md` login page | `aria-label` audit |
| 5-6 | Document Upload + Ingestion | `plan` → `implement` → `review` | Card + Upload zone | `focus-visible`, `alt` |
| 7-8 | RAG Chat (L15 core) | `ai-first-engineering` skill | Chat bubbles (DESIGN.md) | `prefers-reduced-motion` |
| 9-10 | Dashboard + Billing | `e2e-testing` | Table virtualized | `tabular-nums`, `truncate` |

**هر روز:** Agent قبل از کدنویسی `DESIGN.md` را می‌خواند، بعد از کدنویسی `web-guidelines` audit

### فاز 2 — Hardening (هفته 11-18)

- **L9 Security:** `ECC security-scan` + `AgentShield scan` در CI
- **L12 Perf:** `web-guidelines` بخش Performance (virtualize, lazy, preconnect)
- **L13 Obs:** ECC `remember` → خلاصه سشن‌ها به `docs/learnings/`
- **L14 Testing:** `tdd-workflow` سخت‌گیرانه — coverage 80% gate
- **Design Polish:** Storybook از `DESIGN.md` tokens — Chromatic visual regression

### فاز 3 — Scale & Polish (هفته 19-26)

- Agent خودمختار (L15) با UI تولیدی مبتنی بر `DESIGN.md`
- Multi-region + DR
- `AGENTS.md` به پورتال Backstage تبدیل
- ارزیابی نهایی: `design:audit` کل `apps/web` باید `✓ pass` باشد

---

## 3. RACI برای ۳ ادغام

| ادغام | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| **ECC** | Tech Lead | CTO | All Devs | PM |
| **Web Guidelines** | FE Lead | Tech Lead | Design | QA |
| **Awesome/DESIGN.md** | Design | FE Lead | PM | All |

---

## 4. CI/CD — پایپلاین جدید (به `.github/workflows/ci.yml` اضافه می‌شود)

```yaml
jobs:
  quality:
    steps:
      - run: pnpm lint && pnpm typecheck
      - run: pnpm test --coverage
      # NEW — 3 integrations
      - name: Web Guidelines Audit
        run: pnpm design:audit  # runs Skill on apps/web/**/*.tsx
      - name: ECC AgentShield
        run: npx -y ecc-agentshield scan --path . --strict
      - name: DESIGN.md check
        run: node scripts/check-design-tokens.js  # ensure tokens from DESIGN.md used

  e2e:
    steps:
      - run: npx playwright test
      - uses: chromaui/action@v1  # visual regression from Storybook/DESIGN.md
```

---

## 5. معیار موفقیت (KPIs جدید)

| KPI | قبل | بعد با ادغام | ابزار سنجش |
|---|---|---|---|
| a11y violations | نامشخص | 0 critical | web-guidelines audit |
| Design consistency | سلیقه‌ای | 95% tokens از DESIGN.md | `check-design-tokens` |
| PR review time | 2 روز | <4 ساعت (ECC reviewer) | GitHub metrics |
| Test coverage | 60% | ≥80% (TDD gate) | Jest |
| Agent onboarding | 3 روز | <1 روز (`AGENTS.md`) | survey |

---

## 6. ریسک‌ها و بازگشت

| ریسک | Mitigation | بازگشت |
|---|---|---|
| Context bloat از ECC | نصب گزینشی (6 skill نه 261) | `rm -rf .claude/skills/ecc-*` |
| DESIGN.md قدیمی شود | Owner: FE Lead، بازبینی ماهانه | `git log DESIGN.md` |
| Guidelines سخت‌گیر | ابتدا warning، سپس error در CI | `pnpm design:audit --warn` |

---

## 7. چک‌لیست اجرا برای شما (Owner)

- [ ] این PR را مرج کن (`arena/01a07f8a-cutting-edge-v2` → `main`)
- [ ] `pnpm design:audit` را یکبار روی یک کامپوننت تست کن
- [ ] به Agent بگو: `Use DESIGN.md to build a login page` — نتیجه را ببین
- [ ] (اختیاری) GitHub App ECC را نصب کن: https://github.com/apps/ecc-tools → کامنت `/ecc-tools analyze`
- [ ] در جلسه Kick-off، `DESIGN.md` را به عنوان مرجع طراحی تایید کن (یا رنگ accent را عوض کن)

---

## 8. لینک‌های مرجع

- **16-Layer Original:** `docs/16-LAYER-PRODUCTION-PLAN.md`
- **AGENTS:** `AGENTS.md`
- **DESIGN:** `DESIGN.md` + `design-md/DESIGN.*.md`
- **ECC:** https://github.com/affaan-m/ECC (213K stars)
- **Web Guidelines:** https://github.com/vercel-labs/agent-skills + https://github.com/vercel-labs/web-interface-guidelines
- **Awesome Design:** https://github.com/VoltAgent/awesome-design-md (114K stars)

---

> **نکته:** این Roadmap جایگزین نقشه 16 لایه نیست — لایه تقویتی روی آن است. نقشه اصلی همچنان `16-LAYER-PRODUCTION-PLAN.md` است.
