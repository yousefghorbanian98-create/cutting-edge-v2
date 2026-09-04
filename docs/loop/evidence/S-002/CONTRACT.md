# CONTRACT — S-002 — Backend boot fix: package imports, dotenv, dev scripts

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-002 در `03_STEPS.md` (goal/files/real_test/done-when).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | بک‌اند به‌صورت پکیج اجرا می‌شود: `from ai_engine.main import app` بدون خطای import (حل کرش `attempted relative import` سند B-1). | `python -c "from ai_engine.main import app"` در venv | `tests/real/test_backend_boot.py::test_package_import` |
| AC-2 | `scripts/dev-backend.sh` سرور را روی یک پورت تصادفی بالا می‌آورد و `/health` در **≤ 2s** کد 200 با JSON شامل فیلدهای `ram`، `cpu`، `gpu_mem` برمی‌گرداند. | اسکریپت واقعی + `requests.get` با تایماوت اندک | `tests/real/test_backend_boot.py::test_health_within_2s` |
| AC-3 | سرور پس از **60s** بیکاری زنده می‌ماند و دوباره `/health` کد 200 با همان فیلدها می‌دهد (مقدار idle به‌صورت متغیر `CE_IDLE_SECONDS` قابل تنظیم است؛ پیش‌فرض 60). | اسکریپت + sleep + درخواست دوم | `tests/real/test_backend_boot.py::test_survives_60s_idle` |
| AC-4 | `python-dotenv` بارگذاری می‌شود و فایل `ai-engine/.env.example` با کلید `OPENROUTER_API_KEY=` وجود دارد؛ سرور بدون فایل `.env` هم بوت می‌شود (پیکربندی اختیاری). | اجرای اسکریپت بدون `.env` + تست فایل | `tests/real/test_backend_boot.py::test_dotenv_and_env_example` |
| AC-5 | `ai-engine/requirements.txt` نسخه‌ها را pin می‌کند (هر خط اسم+`==`نسخه) و `ai-engine/pyproject.toml` با metadata پکیج (name/version/deps/package mapping) وجود دارد. | پارس فایل‌ها | `tests/real/test_backend_boot.py::test_pinned_requirements_and_pyproject` |
| AC-6 | `scripts/dev-backend.ps1` (Windows) وجود دارد و فراخوانی `uvicorn ai_engine.main:app` با همان پورت/هاست دارد. | پارس محتوای فایل | `tests/real/test_backend_boot.py::test_dev_backend_ps1_present` |

> AC-6 را تنها می‌توان به‌صورت ایستا در Linux تأیید کرد؛ اجرای واقعی اسکریپت PowerShell روی Windows انجام می‌شود → در دفترچه `unverified:windows` ثبت می‌شود.

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | هیچ تغییری در رفتار/منطق اندپوینت‌های API یا الگوریتم‌های می‌کننده‌های AI (`editor_ai`، `muscle`، `style_match`، …) — فقط بسته‌بندی/بوت | کارت S-002 فقط رفع بوت و پکیج‌بندی است؛ تضمین کیفیت خروجی‌های AI در مراحل بعدی | S-004, S-035… |
| NG-2 | بدون تغییر `.github/workflows/ci.yml` (حتی اجرا روی این برنچ) و بدون ابزار کیفیت (Biome/Ruff/tsc) یا `gate.py` | بازطراحی CI = S-009؛ ابزار = S-008/S-011 | S-008, S-009, S-011 |
| NG-3 | بدون جابه‌جایی دایرکتوری کد (ساختار `ai-engine/src/` حفظ می‌شود؛ فقط mapping پکیج در pyproject) | جلوگیری از scope creep / refactor فرصت‌طلبانه | — |
| NG-4 | بدون سخت‌سازی CORS، پاک‌سازی path traversal یا محدودیت اندازه/نوع آپلود | کار صریح امنیت S-003 است | S-003 |
| NG-5 | نصب کامل پشته‌ی سنگین AI (whisper/mediapipe/… از `requirements.txt`) در این مرحله اجباری نیست؛ اسکریپت dev فقط وابستگی‌های لازم برای بوت را نصب می‌کند و نصب کامل = CI/کاربر نهایی | `requirements.txt` کامل pin شده است؛ این مرحله تنها بوت/سلامت را اثبات می‌کند | CI و `smoke-gpu.ps1` |

## Reheal layers touched

- هیچ‌کدام — این مرحله فقط بسته‌بندی/بوت/اسکریپت dev را لمس می‌کند، هیچ لایه‌ی Reheal (L1–L7) را تغییر نمی‌دهد. Probe آشوب: N/A با دلیل مکتوب (بدون مسیر داده‌ی runtime جدید برای آشوب‌پروب؛ «بقا در 60s بیکاری» با AC-3 اثبات می‌شود).

## Risks / unknowns

- ریسک متوسط: تغییر بسته‌بندی می‌تواند importهای نسبی را به‌هم بزند اگر subpackage‌ای import absolute داشته باشد — با `grep` بررسی شد: تمام importهای داخل پکیج نسبی هستند (فقط main.py از `.editor_ai` و mood_dna.py از `..analyzer`).
- اسکریپت dev برای بوت فقط وابستگی‌های سبک را نصب می‌کند؛ مسیر نصب کامل (برای تولید/CI) به `requirements.txt` وابسته است و جداگانه تأیید می‌شود.
- `.ps1` روی این sandbox (Linux) قابل اجرا نیست → AC-6 به‌صورت ایستا و با `unverified:windows` رکورد می‌شود.

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست.
