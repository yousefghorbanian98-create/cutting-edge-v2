# Cutting Edge v2 — Delivery Loop (نقطه‌ی شروع)

> **هدف این پوشه:** کاربر کمترین دخالت را داشته باشد و هیچ‌چیز تا انتشار نصب‌کننده‌ی ویندوز (`.exe`) نسخه‌ی ۱.۰ فراموش نشود.
> هر سشن AI از همین فایل شروع می‌کند.

## فایل‌ها به ترتیب خواندن
| # | فایل | چیست |
|---|------|------|
| 00 | `00_INDEX.md` | همین فایل |
| 01 | `01_STATE_OF_REPO.md` | ممیزی واقعی کد (۲۰۲۶-۰۹-۰۳): چه هست، چه شکسته، چرا پیشرفت واقعی ~۱۲–۱۵٪ است |
| 02 | `02_LOOP_PROTOCOL.md` | **لوپ ۱۰ گامی** (Builder + بازبین تازه) برای هر مرحله + لوپ مایلستون + تعریف «تست واقعی» + چک‌لیست کلاس جهانی + سه نقطه‌ی دخالت کاربر |
| 03 | `03_STEPS.md` | **۱۰۱ مرحله‌ی شماره‌دار** (S-001 … S-101؛ سه مرحله‌ی S-099…S-101 در P0 بعد از S-012 اجرا می‌شوند) در ۸ فاز تا v1.0 — تولیدشده از `steps.json` |
| 04 | `04_LEDGER.md` | وضعیت هر مرحله؛ ماشین‌خوان؛ `scripts/verify_ledger.py` در CI آن را چک می‌کند |
| 05 | `05_REHEAL_MATRIX.md` | ۷ لایه‌ی Reheal × مرحله‌ی ساخت × probe آشوب × معیار بازیابی |
| 06 | `06_BUGS.md` | ۱۵ باگ شناخته‌شده (۶ قدیمی + ۹ کشف‌شده در ممیزی) با تست اثبات |
| 07 | `07_SESSION_HANDOFF.md` | پرامپت آماده برای سشن بعدی (نقش Builder / نقش Reviewer) |
| 08 | `08_FINN_LOOP_ADOPTION.md` | بررسی Finn-loop: چه گرفتیم (بازبین تازه، AC/NG، scope ledger) و چه نگرفتیم (merge انسانی، Linear) |
| 09 | `09_UI_COMPONENT_PROMPT.md` | پرامپت آماده برای دادن به یک AI دیگر جهت تولید کامپوننت‌های UI کلاس جهانی |
| 10 | `10_OPERATING_GUIDE.md` | راهنمای **شما** برای اجرای لوپ با کمترین خطا: راه‌اندازی یک‌باره، یک سشن = یک نقش = یک مرحله، پیام‌های آماده، چک ۶۰ ثانیه‌ای، نشانه‌های انحراف |
| 11 | `11_SUPERVISOR.md` | نقش سوم: ناظر روند ساخت (این سشن Arena) — `scripts/supervise.py` با ۱۴ چک، verdict OK/ATTENTION/STOP؛ §7 حلقه‌ی improve |
| 12 | `12_SIXTEEN_LAYER_MAP.md` | نگاشت نقشه‌ی ۱۶ لایه‌ی تولید روی این محصول: کدام لایه در کدام مرحله؛ چه چیزی عمداً حذف شد |
| 13 | `13_INTEGRATIONS_ADOPTION.md` | سه ادغام (ECC، Web Interface Guidelines، awesome-design-md): چه پذیرفته شد، چگونه گیت شد، چه رد شد |
| — | `../../AGENTS.md` | نقطه‌ی ورود هر ایجنت (ریشه‌ی ریپو) — به این پوشه لینک می‌دهد |
| — | `../../DESIGN.md` | مرجع بصری (پیش‌نویس وارداتی تا S-099؛ سپس گیت‌شده) |
| — | `../adr/`, `../learnings/` | تصمیم‌های معماری و درس‌های سشن‌ها (از S-101) |
| — | `templates/` | `CONTRACT.md` (AC/NG هر مرحله) و `REVIEW.md` (verdict بازبین) |
| — | `steps.json` | منبع حقیقت مراحل (ویرایش این؛ سپس `python scripts/loop/render_steps.py`) |
| — | `evidence/` | هر مرحله: `S-xxx/CONTRACT.md`, `REVIEW.md`, artifacts + `SESSIONS.md` |
| — | `blockers/` | گزارش انسداد بعد از ۵ تکرار ناموفق |

## نقشه‌ی راه در یک نگاه
```
P0 Foundation Repair   S-001…S-012 + S-099…S-101  v0.2.1   ← build/test/ship‌پذیر + DESIGN/AGENTS/ADR/learnings گیت‌شده
P1 Timeline Real       S-013…S-027  v0.3.0
P2 Export Pipeline     S-028…S-034  v0.4.0
P3 AI Full Integration S-035…S-057  v0.5.0   ← هر ۱۶ قابلیت
P4 Tauri Desktop       S-058…S-067  v0.6.0   ← نصب‌کننده‌ی NSIS + آپدیتر + sidecar پایتون
P5 Project & Stability S-068…S-078  v0.7.0   ← ۷ لایه‌ی Reheal + تست آشوب
P6 Testing & Polish    S-079…S-090  v0.8.0   ← RC1
P7 Release             S-091…S-098  v1.0.0   ← GitHub Release + SHA256 + latest.json
```

## دخالت کاربر — کل پروژه
- **U1** یک‌بار: کلید OpenRouter (قبل از S-053).
- **U2** ۸ بار: پایان هر مایلستون، نصب exe + اجرای `scripts/smoke-gpu.ps1` (~۱۰ دقیقه) و چسباندن JSON.
- **U3** اختیاری: تصمیم‌های محصولی؛ سکوت = پیش‌فرض ثبت‌شده در کارت.

## دستورات روزمره
```bash
python scripts/verify_ledger.py            # سلامت دفترچه (در CI اجرا می‌شود)
python scripts/supervise.py --write        # ممیزی ناظر: ۱۲ چک + گزارش در evidence/SUPERVISOR/
python scripts/loop/render_steps.py        # بعد از ویرایش steps.json
python scripts/loop/render_steps.py --check
python scripts/gate.py --stage static|unit|real|e2e|perf|chaos|all   # از S-011
pwsh scripts/smoke-gpu.ps1                 # روی ماشین کاربر، از S-011
```

## مرحله‌ی بعدی
اولین ردیف `TODO` در `04_LEDGER.md` که همه‌ی وابستگی‌هایش GREEN یا REVIEW-در-همین-دسته هستند. ترتیب توصیه‌شده‌ی باقی‌مانده‌ی P0: S-008 → S-009 → S-101 → S-099 → S-100 → S-010 → S-011 → S-012.
