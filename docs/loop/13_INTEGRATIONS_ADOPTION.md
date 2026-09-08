# 13 — پذیرش سه ادغام (ECC · Web Interface Guidelines · awesome-design-md)

> ورودی: `docs/ROADMAP-v2-WITH-INTEGRATIONS.md` و `docs/integrations/*` (شاخه‌ی `arena/01a07f8a`).
> اصل: **هر قاعده‌ای که به لوپ اضافه می‌شود باید توسط یک اسکریپت یا تست اجرا شود؛ «توصیه» بدون گیت پذیرفته نمی‌شود.** به همین دلیل بخش بزرگی از سه ادغام به‌جای نصب ابزار خارجی، به مرحله/چک درون‌ریپویی ترجمه شده است.

## 1. ECC (agent harness: plan → test → implement → review → verify → remember → improve)

| مفهوم ECC | قبلاً در لوپ ما | تصمیم | کجا |
|---|---|---|---|
| `plan` قبل از کد | گام ② CONTRACT (AC/NG) | ✅ داشتیم | ۰۲ §1-② |
| `tdd-workflow` RED→GREEN | «تست واقعی اول قرمز» | ✅ داشتیم | ۰۲ §1-② |
| `code-review` با کانتکست تازه | بازبین تازه = ناظر | ✅ داشتیم | ۰۲ §1-⑧، ۱۱ |
| `security-scan` | gitleaks + Ruff S + Bandit + supervise C10 | ✅ داشتیم | S-008, S-086 |
| `build-fix` | حلقه‌ی دیباگ ≤ ۵ تکرار | ✅ داشتیم | ۰۲ §1-⑦ |
| `verify` | گیت‌های gate.py + CI + بازتولید شواهد توسط بازبین | ✅ داشتیم | ۰۲ §1-⑤⑨ |
| **`remember`** (حافظه‌ی بین‌سشنی) | فقط SESSIONS.md پنج‌خطی | ➕ **افزوده شد**: `docs/learnings/<date>-<slug>.md` با قالب ≤ ۲۰ خط (چه شکست / ریشه / قاعده‌ی بعدی)؛ هر سشن سازنده یک ورودی می‌نویسد | S-101، ۰۲ §1-⑩، ۰۷ |
| **`improve`** (تبدیل درس به قاعده) | غیررسمی | ➕ **افزوده شد**: ناظر در هر ممیزی learnings جدید را می‌خواند و به یکی از این‌ها تبدیل می‌کند: چک supervise.py، قاعده در ۰۲، تغییر پرامپت ۰۷، یا کارت steps.json — و در `evidence/SUPERVISOR/` ثبت می‌کند | ۱۱ §7 |
| هوک `SessionStart` | پرامپت شروع سشن با fetch/BASE_OK | ✅ معادل | ۰۷ |
| هوک `PreCommit` | lefthook (S-008) | ✅ داشتیم | S-008 |
| نصب ۲۶۱ skill / GitHub App | — | ✂️ نه: Arena اسکیل‌لودر/هوک ندارد و context را پر می‌کند | — |
| `AGENTS.md` مرکز فرمان | ۰۰_INDEX | ➕ **افزوده شد**: `AGENTS.md` ریشه (نازک، لینک به ۰۰_INDEX و DESIGN.md) + فایل‌های هارنس به‌عنوان اشاره‌گر | S-099 |

## 2. Vercel Web Interface Guidelines (چگونه UI را درست بسازیم)

| مفهوم | تصمیم | کجا |
|---|---|---|
| Skill که هر بار `command.md` را از اینترنت می‌گیرد | ✂️ نه (شبکه ندارد؛ غیرقطعی) | — |
| Snapshot قوانین (`docs/integrations/web-guidelines/web-interface-guidelines.md`) | ✅ نگه داشته شد به‌عنوان منبع قوانین | — |
| ممیزی `file:line` | ➕ **افزوده شد** به‌صورت اسکریپت آفلاین و قطعی `scripts/design_audit.py` روی TSX، با fixture نقض/تمیز، حالت `--warn`/`--strict`، suppress دلیل‌دار `wig-ignore` | S-100 |
| اجرا در CI (`design:audit`) | ➕ داخل `gate.py --stage static` و جاب ubuntu | S-100, S-009 |
| قوانین طلایی (aria-label، focus-visible، transform/opacity، Intl، reduced-motion) | ➕ به چک‌لیست کلاس جهانی ۰۲ §4 و AGENTS.md §5 اضافه شد؛ قابل سنجش با S-100 | ۰۲ §4 |
| بستن نقض‌های موجود page.tsx | S-100 آن‌ها را یا رفع می‌کند یا با ارجاع به S-084 مستند می‌کند؛ S-084 همه را می‌بندد | S-100, S-084 |

## 3. awesome-design-md (چه چیزی بسازیم — DESIGN.md)

| مفهوم | تصمیم | کجا |
|---|---|---|
| `DESIGN.md` در ریشه به‌عنوان مرجع بصری اجباری | ✅ پذیرفته شد — اما فایل وارداتی با توکن‌های واقعی S-007 تعارض دارد (Geist/blurple/چت RAG در برابر Inter+Vazirmatn/بنفش AI) | S-099 آن را با `@theme` و `tokens.ts` یکی می‌کند |
| سه فایل الهام (`design-md/DESIGN.{linear,vercel,stripe}.md`) | ✅ نگه داشته شد فقط به‌عنوان مرجع الهام؛ هیچ‌کدام مستقیم به کد نمی‌آید | — |
| `scripts/check-design-tokens.js` | فعلاً placeholder است → ➕ در S-099 چک واقعی سه‌طرفه DESIGN.md ⇄ globals.css ⇄ tokens.ts و ورود به gate static | S-099 |
| KPI «۹۵٪ رنگ‌ها از توکن» | ➕ به S-087 اضافه شد (اسکریپت شمارش hex خام) | S-087 |
| Storybook/Chromatic | ✂️ نه؛ Playwright visual regression در S-081 | — |
| ادعاهای استک بیگانه در `.cursorrules`/copilot (NestJS, Prisma, shadcn) | ➕ S-099 آن‌ها را به اشاره‌گر نازک به AGENTS.md تبدیل می‌کند و تست `test_agent_docs.py` واژه‌های ممنوع را قرمز می‌کند | S-099 |

## 4. تغییرات ساختاری در خود لوپ (این کامیت)
1. `AGENTS.md` ریشه ساخته شد (نقطه‌ی ورود هر ایجنت؛ در S-099 تست می‌شود).
2. `DESIGN.md` با بنر «پیش‌نویس وارداتی — مرجع فعلی توکن‌های کد است» علامت خورد تا تا S-099 هیچ رنگی از آن وارد کد نشود.
3. سه مرحله‌ی جدید در P0: S-099 (DESIGN/AGENTS/token gate)، S-100 (design_audit)، S-101 (ADR + learnings).
4. چهار کارت تقویت شد: S-009 (چک‌های طراحی در CI)، S-053 (پرامپت نسخه‌دار + eval آفلاین)، S-084 (KPI صفر نقض)، S-087 (۹۵٪ توکن).
5. گام ⑩ لوپ: هر سشن سازنده یک ورودی `docs/learnings/` می‌نویسد (remember)؛ ناظر در ممیزی آن را به قاعده تبدیل می‌کند (improve) — ۱۱ §7.
6. گام ① لوپ: **گیت پوش** — قبل از شروع مرحله‌ی جدید، `git ls-remote` باید HEAD مرحله‌ی قبل را روی GitHub نشان دهد (درس از انقضای توکن در S-008).
7. `supervise.py`: چک C13 (ورودی learnings برای هر سشن سازنده — از S-101) و C14 (drift توکن: `check-design-tokens.js` — از S-099).
