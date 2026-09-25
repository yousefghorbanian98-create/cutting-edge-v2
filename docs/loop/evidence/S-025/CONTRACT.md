# CONTRACT — S-025 — Keyboard shortcuts registry + in-app cheat sheet (?)

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | هر شورتکات ثبت‌شده عملش را دقیقاً یک بار اجرا می‌کند. | Playwright | `apps/desktop/tests/shortcuts.spec.ts` |
| AC-2 | `?` و `؟` مودال را باز می‌کنند و تعداد ردیف‌ها با رجیستری یکی است. | Playwright | همان فایل |
| AC-3 | Ctrl+B مال برش تایم‌لاین می‌ماند و Command Palette همان chord را دوباره bind نمی‌کند. | vitest + Playwright | `shortcuts.test.ts` و spec |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | سفر کامل import تا preview | کارت بعدی | S-026 |
| NG-2 | تغییر معنی Ctrl+B که تست S-019 به آن بسته است | شل کردن تست ممنوع | همان برش می‌ماند |
| NG-3 | export | زنجیرهٔ جدا | S-028 |

## Forward-knowledge compliance

- Registry IDs: `K-004` چون عمل شورتکات از store action می‌گذرد. `K-006` برای تعامل واقعی و RTL. `K-005` مرجع دیداری است، نه پذیرش. `K-007` اعمال نمی‌شود. `K-008` مجوز ادامه نیست. `K-011` رد می‌شود. `K-001` تا `K-003` و `K-009` و `K-010` اینجا اجرا نمی‌شوند.
- Open gaps: شکاف‌های `S-015` و `S-023` و `S-024` و `S-026` با این مرحله بسته نمی‌شوند. `BUG-18` و `user-gpu` باز می‌مانند.
- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-024`؛ کارت S-025؛ REVIEW مرحلهٔ `S-019` و `S-021`؛ گیت و معماری Style Match و ایندکس و باگ‌ها.
- REVIEWها و architecture updateهای اعمال‌شده: رجیستری مالک واحد chordهاست. Palette فقط Ctrl+K را از همان تابع می‌خواند. S-024 هنوز GREEN نیست و این مرحله آن را سبز نمی‌کند.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: عمل شورتکات از store action می‌گذرد. مودال RTL است و chordها `dir=ltr` می‌مانند تا در فارسی وارونه نشوند.
- Deferred: سفر سه‌باره و snapshot → S-026. مایلستون و user-gpu → S-027. کانال WebSocket → S-029.
- Negative boundary: listener دوم برای همان chord ممنوع است. `useTimelineStore.setState` ممنوع است. شورتکات خام فرمان shell یا FFmpeg نمی‌سازد.
- Evidence plan: vitest برای عدم تداخل chord. Playwright بعد از integration. failure به skip تبدیل نمی‌شود.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
