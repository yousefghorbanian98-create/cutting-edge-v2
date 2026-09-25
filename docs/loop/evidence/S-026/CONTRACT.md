# CONTRACT — S-026 — E2E journey v0.3: import → arrange → trim → split → undo → preview

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | سفر import، چیدن روی تایم‌لاین، trim، split، undo و preview سه بار پشت سر هم پاس می‌شود. | Playwright | `apps/desktop/e2e/timeline.spec.ts` |
| AC-2 | اختلاف پیکسلی snapshotهای بصری همان سفر کمتر از `0.1%` است. | Playwright | همان فایل، `maxDiffPixelRatio` برابر `0.001` |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | تگ و pre-release و user-gpu | مایلستون U2 | S-027 |
| NG-2 | شل کردن `0.1%` برای تفاوت فونت بین ماشین‌ها | آستانه ثابت است | snapshot داخل همان اجرا مقایسه می‌شود |
| NG-3 | export فایل | P2 | S-028 |

## Forward-knowledge compliance

- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-025`؛ کارت S-026؛ REVIEWهای `S-014` و `S-018` و `S-019` و `S-021`؛ گیت و معماری و ایندکس و باگ‌ها.
- REVIEWها و architecture updateهای اعمال‌شده: چیدن کلیپ از store action `addClip` است. undo از `undoTimeline` است، نه setState. S-025 هنوز GREEN نیست.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: سفر از UI واقعی می‌گذرد، نه helper خالص. سه تکرار پشت سر هم flake check است و retry پیکربندی Playwright برای پنهان کردن flake زیاد نمی‌شود.
- Deferred: تگ `v0.3.0` و installer user-gpu → S-027. خروجی FFmpeg → S-028. S-033 شروع نمی‌شود.
- Negative boundary: mutation مستقیم sequence ممنوع است. تفاوت بصری بالای `0.001` پاس نیست و شل نمی‌شود. موج کلیپ از id تصادفی ساخته نمی‌شود. skip شدن یک گام سفر پاس نیست.
- Evidence plan: spec بعد از integration به دستور Playwright در CI Ubuntu اضافه می‌شود. پیش از تحویل، CI کامل. local pass جایگزین CI نیست.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
