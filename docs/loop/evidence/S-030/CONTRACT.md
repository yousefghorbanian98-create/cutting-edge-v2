# CONTRACT — S-030 — Export dialog: resolution/fps/codec/bitrate/presets/destination

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | انتخاب پریست Reels بدنهٔ درخواست `{w:1080,h:1920,fps:30,codec:h264}` می‌سازد. | Playwright | `apps/desktop/tests/export-dialog.spec.ts` |
| AC-2 | 4K روی منبع غیر 4K هشدار بزرگ‌نمایی نشان می‌دهد. | Playwright | همان فایل |
| AC-3 | گزینه‌های 720p و 1080p و 4K، فریم‌ریت `24/30/60`، کدک H.264/H.265، بیت‌ریت یا CRF، نام فایل، مقصد، و تخمین حجم وجود دارند. | vitest + Playwright | `exportPresets.test.ts` و spec |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | نوار پیشرفت و لغو و تاریخچه | کارت بعدی | S-031 |
| NG-2 | اجرای واقعی encode داخل دیالوگ | موتور مال S-028 است | دیالوگ فقط درخواست typed می‌فرستد |
| NG-3 | سوییت کیفیت خروجی | شروع نمی‌شود | S-033 |

## Forward-knowledge compliance

- Registry IDs: `K-001` بدنه را typed می‌کند. `K-002` overwrite پیش‌فرض را false نگه می‌دارد و `BUG-18` را نمی‌بندد. `K-006` هشدار 4K را پنهان نمی‌کند. `K-007` اعمال نمی‌شود. `K-008` مجوز ادامه نیست. `K-011` رد می‌شود.
- Open gaps: evidence نام‌دار دیالوگ هنوز این مرحله را نمی‌بندد. `user-gpu` باز است.
- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-029`؛ کارت S-030؛ گیت و معماری و ایندکس و `BUG-18`.
- REVIEWها و architecture updateهای اعمال‌شده: بدنه فقط operation typed است. پریست filter graph نمی‌فرستد. S-029 هنوز GREEN نیست.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: مقصد از نام امن ساخته می‌شود. تخمین حجم با `Intl.NumberFormat` است. هشدار 4K وقتی عرض منبع کمتر از `3840` است نشان داده می‌شود و پنهان نمی‌شود.
- Deferred: UI پیشرفت و باز کردن پوشه → S-031. میکس LUFS → S-032. verify فایل → S-033 که شروع نمی‌شود.
- Negative boundary: `raw_command` و `filter_graph` در بدنه ممنوع‌اند. overwrite پیش‌فرض false است. capability ضمنی پاس نیست.
- Evidence plan: vitest پریست‌ها. Playwright بعد از integration بدنهٔ واقعی request را می‌خواند، نه فقط یک attribute. CI کامل پیش از تحویل.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
