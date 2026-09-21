# CONTRACT — S-008 — Toolchain: Biome, Ruff, tsc strict, Turbo 2 tasks, pinned versions, pre-commit, security scans

> نوشته‌شده توسط Builder (این نوبت: سشن ناظر در حالت سازنده — بازبینی توسط اجرای مجدد مستقل در نوبت بعد) در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-008 در `03_STEPS.md` (تقویت‌شده با ADR-0002: bandit، pip-audit، pnpm audit).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | `python scripts/gate.py --stage static` روی درخت تمیز با exit 0 تمام می‌شود و جدول pass/fail/missing/skip چاپ می‌کند؛ هر ابزارِ غایب `MISSING` گزارش می‌شود نه `PASS` (Skip ≠ Pass) | gate.py | `tests/unit/test_gate.py::test_static_stage_green_on_clean_tree` |
| AC-2 | فایلی حاوی `sk-or-v1-TEST…` که stage شود → gate static با exit 1 و نام فایل + شماره‌ی خط | gate.py (secret scan داخلی + gitleaks اگر موجود) | `tests/unit/test_gate.py::test_staged_secret_fails_static` |
| AC-3 | Ruff (lint + format، قوانین E,F,W,I,B,S,UP,SIM) روی `ai-engine/src`, `tests`, `scripts` بدون خطا؛ هر suppress با کامنت دلیل‌دار | `ruff check`, `ruff format --check` | `tests/unit/test_gate.py::test_ruff_clean` |
| AC-4 | Biome (lint + format) روی `apps/desktop/src`, `packages`, `scripts/*.js` بدون خطا؛ `tsc --noEmit` strict روی `apps/desktop` بدون خطا | `biome ci`, `tsc` | `tests/unit/test_gate.py::test_biome_and_tsc_clean` |
| AC-5 | `turbo.json` از `pipeline` به `tasks` (Turbo 2) مهاجرت کرده و `turbo run build --dry=json` موفق است؛ هیچ `latest`/بازه‌ی شناور در هیچ `package.json`/`requirements.txt` نیست (همه پین دقیق) | `turbo --dry`, grep | `tests/unit/test_gate.py::test_no_floating_versions`, `::test_turbo2_tasks` |
| AC-6 | `lefthook.yml` هوک pre-commit با `gate.py --stage static --staged` (سریع: فقط فایل‌های stage‌شده برای lint/secret) و `commit-msg` که شناسه‌ی `S-\d{3}` یا پیشوند `docs/chore/merge/review/supervisor` را الزامی می‌کند | lefthook | `tests/unit/test_gate.py::test_lefthook_config` |
| AC-7 | امنیت پایتون در gate static: `bandit -r ai-engine/src -ll -q` و `pip-audit -r ai-engine/requirements.txt` (خطا = FAIL؛ ابزار غایب = MISSING)؛ `pnpm audit --audit-level=high` برای JS | gate.py | `tests/unit/test_gate.py::test_security_tools_wired` |

## Non-Goals (الزام‌آور)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | بدون تغییر رفتار runtime بک‌اند/فرانت — فقط اصلاح‌های lint (import، bare except → typed except با لاگ، متغیر بلااستفاده) | S-008 ابزار است | — |
| NG-2 | بدون CI (workflow) — فقط ابزار محلی و gate | S-009 | S-009 |
| NG-3 | بدون `gate.py --stage unit/real/e2e/perf/chaos` کامل؛ فقط `static` کامل و اسکلت بقیه با MISSING صریح | S-011 | S-011 |
| NG-4 | بدون `cargo fmt/clippy` واقعی (rustc در سندباکس نیست) → `MISSING` گزارش می‌شود؛ CI windows آن را اجرا می‌کند | S-009/S-010 | S-010 |
| NG-5 | بدون تغییر نسخه‌ی major هیچ وابستگی؛ فقط پین به نسخه‌ای که هم‌اکنون در `pnpm-lock.yaml` حل شده | ریسک رگرسیون | — |

## Reheal layers touched
- هیچ‌کدام. Probe آشوب: N/A (ابزار توسعه).

## Risks / unknowns
- Ruff روی کد قدیمی `reheal/*` و `test_pipeline.py` حدود ۹۰ یافته دارد؛ اصلاح‌ها مکانیکی‌اند (E701/E702 با `ruff format`، F401/F841 حذف، E722 → `except Exception as exc:` + لاگ). هر تغییر معنایی ممنوع (NG-1).
- Biome در سندباکس از طریق `npx` اجرا می‌شود؛ نسخه پین‌شده `1.9.4` در devDependencies ریشه.
- `pnpm` از طریق corepack (v12) در دسترس است؛ `packageManager` در package.json ریشه پین می‌شود.

## U-decisions
- `user: none`.
