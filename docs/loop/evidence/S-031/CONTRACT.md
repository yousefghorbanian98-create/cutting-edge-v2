# CONTRACT — S-031 — Export progress UI, cancel, open output folder, export history

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | متن پیشرفت زیاد می‌شود. | Playwright | `apps/desktop/tests/export-progress.spec.ts` |
| AC-2 | لغو toast فارسی نشان می‌دهد، وضعیت job برابر `cancelled` است، و فایل خروجی نمی‌ماند. | Playwright برای toast و وضعیت؛ pytest برای نبود فایل | spec و `tests/test_export.py` |
| AC-3 | در وب لینک دانلود فقط وقتی فایل verify شده باشد نشان داده می‌شود. تاریخچهٔ خروجی از نتیجهٔ ساختاریافته پر می‌شود. | Playwright | همان spec |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | opener واقعی Tauri اگر پوسته در Playwright نیست | در وب دانلود است | Tauri opener وقتی `window.__TAURI__` باشد؛ نبودش skip پاس نیست و مسیر وب اثبات می‌شود |
| NG-2 | داکینگ صدا | موازی S-032 | S-032 |
| NG-3 | SSIM خروجی | شروع نمی‌شود | S-033 |

## Forward-knowledge compliance

- Registry IDs: `K-001` لغو را از raw command جدا می‌کند. `K-002` فایل لغوشده را خروجی موفق نمی‌کند و `BUG-18` را باز نگه می‌دارد. `K-004` setState روی sequence را رد می‌کند. `K-006` toast بدون وضعیت واقعی را رد می‌کند. `K-007` اعمال نمی‌شود. `K-008` مجوز ادامه نیست. `K-011` رد می‌شود.
- Open gaps: `unverified:tauri-opener` پاس وب نیست. `user-gpu` باز است.
- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-030`؛ کارت S-031؛ گیت و معماری و ایندکس و `BUG-18`.
- REVIEWها و architecture updateهای اعمال‌شده: لغو از route موجود `/jobs/{id}/cancel` می‌گذرد. UI sequence را با setState عوض نمی‌کند. S-030 هنوز GREEN نیست.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: پیشرفت از هوک job است. فایل لغوشده در UI به‌عنوان خروجی موفق نشان داده نمی‌شود. تاریخچه provenance را نشان می‌دهد، نه یک نام ساختگی.
- Deferred: اندازه‌گیری LUFS → S-032. اعتبار playable/sync/codec فایل → S-033 که شروع نمی‌شود. opener دسکتاپ اگر در این مرورگر نباشد `unverified:tauri-opener` است و پاس وب را جایگزین آن نمی‌کند.
- Negative boundary: toast بدون وضعیت `cancelled` پاس نیست. وجود فایل بعد از لغو پاس نیست. raw command از دکمهٔ لغو ساخته نمی‌شود.
- Evidence plan: Playwright برای متن صعودی و toast. pytest S-028/S-031 برای حذف فایل. هر کدام فقط همان بخش را پاس می‌کند. CI کامل پیش از تحویل.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
