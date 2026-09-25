# CONTRACT — S-027 — MILESTONE v0.3.0: regression, tag, CI installer, pre-release, user smoke test

> نوشته‌شده پیش از implementation. این مرحله `U2` است. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`. `verified_on` شامل `user-gpu` نمی‌شود مگر کاربر خودش smoke را اجرا کند.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | CHANGELOG نسخهٔ `0.3.0` نوشته می‌شود و صریحاً می‌گوید تگ و pre-release تا user-gpu منتشر نشده‌اند. | فایل | `CHANGELOG.md` |
| AC-2 | dry-run اسکریپت smoke پاس ماشین نیست. | CI Windows موجود | `scripts/smoke-gpu.ps1 -DryRun` |
| AC-3 | کاربر installer را روی Windows/GTX 1650 اجرا کند و JSON شامل `app_launch=true` و `backend_health=true` و `import_ok=true` باشد. | ماشین کاربر | تا اجرا نشود `unverified:user-gpu` است و پاس نیست |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | ساخت تگ `v0.3.0` یا GitHub pre-release بدون user-gpu | Done when به `user-gpu` بسته است | بعد از U2 و verdict |
| NG-2 | GREEN کردن S-023 تا S-026 | verdict مستقل لازم است | بعد از ناظر |
| NG-3 | export pipeline | P2 | S-028 |

## Forward-knowledge compliance

- Registry IDs: `K-001` یعنی `missing` و `unverified` پاس نیستند. `K-007` استثنای S-022 است و checksum نصب‌کننده را پاس ماشین کاربر نمی‌کند. `K-008` مجوز تگ نیست. `K-011` رد می‌شود. `K-005` و `K-006` پذیرش installer را عوض نمی‌کنند.
- Open gaps: `user-gpu` باز است. dry-run پاس GPU نیست. تگ و pre-release نیست. تفاوت شواهد Ubuntu و Windows حفظ می‌شود. خوانده‌نشدن zip مصنوع پاس نیست.
- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-026`؛ کارت S-027؛ REVIEW مرحلهٔ `S-010` و `S-011`؛ گیت و معماری و ایندکس و باگ‌ها.
- REVIEWها و architecture updateهای اعمال‌شده: dry-run موجود در CI ادعای GPU نیست. این مرحله آن را پاس ماشین حساب نمی‌کند. S-026 هنوز GREEN نیست.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: مایلستون بدون شاهد کاربر بسته نمی‌شود. installer checksum وقتی CI کامل batch تمام شد در evidence ثبت می‌شود، نه به‌عنوان user-gpu.
- Deferred: اجرای `smoke-gpu.ps1` روی GTX 1650 → کاربر، owner همین S-027، تا آن زمان `unverified:user-gpu`. تگ و pre-release → همین مرحله بعد از U2، نه این commit. S-033 شروع نمی‌شود.
- Negative boundary: `user-gpu` ساختگی ممنوع است. dry-run برابر پاس نیست. GREEN ممنوع است.
- Evidence plan: CHANGELOG در همین batch. نتیجهٔ dry-run از CI Windows نقل می‌شود و پاس ماشین شمرده نمی‌شود. AC-3 تا اجرای کاربر باز می‌ماند.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
