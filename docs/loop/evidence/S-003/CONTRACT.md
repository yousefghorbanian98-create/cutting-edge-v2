# CONTRACT — S-003 — Security fix: upload/download path traversal, size & type limits, CORS

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-003 در `03_STEPS.md` (goal/files/real_test/done-when).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | آپلود با نام فایل مسیرپیمایشی (`../../../../etc/evil.mp4`) همیشه داخل دایرکتوری ذخیره‌سازی نوشته می‌شود؛ نام روی دیسک یک UUID با پسوند whitelist است و هرگز `..`/separator ندارد؛ مسیر ذخیره‌شده زیر base dir است. | `Storage.save_upload` + `Path.resolve` | `tests/test_security.py::test_upload_traversal_stays_in_storage` |
| AC-2 | دانلود با مسیرپیمایشی (`GET /muscle/download/..%2F..%2Fetc%2Fpasswd` و `../../../etc/passwd`) کد **404** برمی‌گرداند و هیچ فایلی خارج از base dir خوانده نمی‌شود. | زنده uvicorn + `requests` | `tests/test_security.py::test_download_traversal_returns_404` |
| AC-3 | آپلود بیش از حد مجاز (پیش‌فرض 2GB، قابل‌تنظیم با `CE_MAX_UPLOAD_MB`) کد **413** برمی‌گرداند و فایل ناقص پاک می‌شود. | زنده uvicorn + `requests` با payload بزرگ | `tests/test_security.py::test_oversized_upload_returns_413` |
| AC-4 | آپلود با پسوند غیرمجاز (مثلاً `.exe`) کد **415** برمی‌گرداند. | زنده uvicorn + `requests` | `tests/test_security.py::test_disallowed_extension_returns_415` |
| AC-5 | رشته‌ی `sanitize_filename` جداکننده‌ها ( `/` `\`) و `..` را حذف می‌کند و فقط یک نام بی‌خطر برمی‌گرداند. | تست واحد تابع | `tests/test_security.py::test_sanitize_filename_strips_separators_and_dotdot` |
| AC-6 | CORS فقط به `http://localhost:3000`، `http://127.0.0.1:3000`، `tauri://localhost`، `https://tauri.localhost` محدود است و هیچ origin دیگری back-reflect نمی‌شود (پیش‌تر `*` بود). | زنده uvicorn + preflight OPTIONS | `tests/test_security.py::test_cors_origin_allowlist` |

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | هیچ تغییری در منطق/کیفیت خروجی اندپوینت‌های AI یا الگوریتم‌ها؛ فقط سخت‌سازی ورودی/خروجی ذخیره‌سازی (ضد path traversal + حجم/نوع + CORS) | کارت S-003 فقط امنیت است | S-004, S-035… |
| NG-2 | بدون تغییر `.github/workflows/ci.yml` و بدون ابزار کیفیت (Biome/Ruff/tsc) یا `gate.py` | CI = S-009؛ ابزار = S-008/S-011 | S-008, S-009, S-011 |
| NG-3 | بدون جابه‌جایی دایرکتوری کد | جلوگیری از scope creep | — |
| NG-4 | بدون فیلتر محتوای واقعی (اعتبارسنجی magic bytes/SSRF)، بدون پاک‌سازی/بلاکلیست نام‌های خاص، بدون رمزنگاری در rest؛ فقط whitelist پسوند + حجم + path safety | این‌ها در S-086 (audit) و مراحل بعدی | S-086 |
| NG-5 | بدون پیاده‌سازی «استریم آپلود» یا resume؛ فقط محدودیت حجم در-جریان | صف/مدیریت فایل در S-012/S-074 | S-012, S-074 |

## Reheal layers touched

- هیچ‌کدام — این مرحله فقط لایه‌ی ورودی/ذخیره‌سازی را سخت می‌کند؛ هیچ لایه‌ی Reheal (L1–L7) را تغییر نمی‌دهد. Probe آشوب: N/A با دلیل مکتوب (اگرچه 413/415/404 رفتارهای خطا هستند، آن‌ها مسیر عادی خطا هستند، نه بازیابی از کرش؛ در این مرحله هیچ پروسه/state ماندگاری برای آشوب وجود ندارد).

## Risks / unknowns

- ریسک متوسط: تغییر CORS از `*` به allow-list ممکن است فرانت‌اندی را که از origin دیگری (مثلاً پورت dev متفاوت) فراخوانی می‌کند، بشکند. اسکریپت‌های dev روی `localhost:3000` کار می‌کنند؛ این در CONTRACT NG-1 نیست و در صورت نیاز در S-007/فرانت ثبت می‌شود.
- حد حجم قابل‌تنظیم (`CE_MAX_UPLOAD_MB`) برای تست/CI است؛ پیش‌فرض production = 2GB.
- اجرای تست‌های زنده به `ffmpeg` وابسته نیست (این مرحله فقط HTTP/ذخیره‌سازی است)، پس در این sandbox بدون ffmpeg هم قابل اجراست.

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست.
