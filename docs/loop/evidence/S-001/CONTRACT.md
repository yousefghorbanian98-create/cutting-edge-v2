# CONTRACT — S-001 — Repo hygiene: remove generator scripts, add LICENSE/.editorconfig/docs tree

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-001 در `03_STEPS.md` (goal/files/real_test/done-when).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | هیچ فایل پایتونی در ریشه‌ی ریپو ردیابی نشده است (`git ls-files '*.py'` در ریشه خروجی خالی می‌دهد) — به‌طور خاص `build_cutting_edge.py` و `extend_cutting_edge_part2.py` حذف شده‌اند و هیچ جایگزین/کپی‌ای از آن‌ها اضافه نشده است | `git ls-files` + `Path.glob` در تست پایتون | `tests/unit/test_repo_hygiene.py::test_no_python_files_at_repo_root` |
| AC-2 | فایل `LICENSE` در ریشه وجود دارد، متن پروانه‌ی MIT است (شامل عبارت `MIT License` و بند `Permission is hereby granted`) و سال/دارنده‌ی حق‌نشر دارد | تست پایتون (خواندن فایل + regex) | `tests/unit/test_repo_hygiene.py::test_license_is_mit` |
| AC-3 | فایل `.editorconfig` در ریشه وجود دارد و حداقل بخش ریشه (`root = true`) و یک الگوی `[*]` با تعریف `end_of_line`, `insert_final_newline`, `charset` دارد | تست پایتون (parse ساده‌ی ini) | `tests/unit/test_repo_hygiene.py::test_editorconfig_present_and_complete` |
| AC-4 | `CODE_OF_CONDUCT.md` در ریشه وجود دارد (مکان استاندارد GitHub) و شامل بخش‌های قابل گزارش تخلف (contact/report) و تعهد به محیط آزارندیدن است | تست پایتون (جست‌وجوی کلیدواژه‌های en/fa) | `tests/unit/test_repo_hygiene.py::test_code_of_conduct_present` |
| AC-5 | ساختار `docs/` درخت لوپ را دست‌نخورده نگه می‌دارد: تمام فایل‌های `docs/loop/*.md` (00–11)، `steps.json`، `templates/` و `evidence/SESSIONS.md` موجود می‌مانند و `python scripts/verify_ledger.py` سبز است (دفترچه ۹۸ ردیف، صفر خطا) | `subprocess` اجرای verify_ledger در تست + شمارش فایل‌ها | `tests/unit/test_repo_hygiene.py::test_docs_tree_and_ledger_intact` |

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | هیچ تغییری در کد بک‌اند (`ai-engine/`)، فرانت (`apps/`)، `packages/`، یا تست‌های موجود (`tests/test_pipeline.py`) — فقط حذف اسکریپت‌های ریشه و افزودن فایل‌های متنی/تست بهداشت | کارت S-001 فقط بهداشت ریپو است؛ بوت بک‌اند S-002، امنیت S-003 | S-002, S-003, … |
| NG-2 | هیچ تغییری در `.github/workflows/ci.yml` (حتی برای اجرا روی این برنچ) | بازطراحی CI ماتریکسی کار صریح S-009 است | S-009 |
| NG-3 | نصب/پیکربندی ابزارهای کیفیت (Biome/Ruff/tsc/Turbo 2/pre-commit) یا افزودن `gate.py` | کار صریح S-008/S-011؛ در S-001 تنها «تست واقعی» موجودِ قابل اجرا = verify_ledger + تست بهداشت است | S-008, S-011 |
| NG-4 | افزودن محتوای مستندات کاربر/توسعه‌دهنده (README جدید، docs/user و…) — فقط فایل‌های Community-standard خواسته‌شده (LICENSE/.editorconfig/CODE_OF_CONDUCT) و درخت موجود docs/loop | مستندات کاربر S-092، بازنویسی README S-093 | S-092, S-093 |
| NG-5 | حذف یا جابه‌جایی چیزی جز دو اسکریپت مولد؛ هیچ فایل ردیابی‌شده‌ی دیگری حذف نمی‌شود | جلوگیری از scope creep / refactor فرصت‌طلبانه | — |

## Reheal layers touched

- هیچ‌کدام — این مرحله فقط فایل‌های ریپو/مستندات را لمس می‌کند، هیچ کد اجرایی، پروسه، یا مسیر داده‌ای تغییر نمی‌کند. Probe آشوب: N/A با دلیل مکتوب (بدون رفتار runtime برای آشوب‌پروب؛ بهداشت استاتیک با تست‌های AC-1…AC-5 اثبات می‌شود).

## Risks / unknowns

- ریسک پایین: اسکریپت‌های مولد ممکن است توسط چیزی فراخوانی شوند — بررسی شد (`grep` کل ریپو): هیچ ارجاعی در کد/CI/config ندارند؛ فقط در مستندات ممیزی/کارت مرحله ذکر شده‌اند.
- محل `CODE_OF_CONDUCT.md`: کارت می‌گوید «CODE_OF_CONDUCT کوتاه» بدون مسیر؛ استاندارد GitHub = ریشه‌ی ریپو. در ریشه گذاشته می‌شود (هم برای شناسایی خودکار GitHub، هم انطباق با «ساختار docs/»).

## U-decisions

- U3: License choice → پیش‌فرض کارت اعمال شد: **MIT** (سکوت کاربر = پیش‌فرض). ثبت در `docs/DECISIONS.md`.
