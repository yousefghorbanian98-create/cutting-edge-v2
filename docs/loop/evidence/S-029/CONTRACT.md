# CONTRACT — S-029 — WebSocket progress channel /ws/jobs/{id} (BUG 6) + frontend hook

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.
> `BUG-6` تا verdict مستقل در `06_BUGS.md` بسته نمی‌شود.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | در یک export واقعی، WebSocket حداقل `10` پیام percent صعودی می‌فرستد. | pytest واقعی | `tests/test_ws.py` |
| AC-2 | قطع WebSocket وسط کار باعث fallback به polling می‌شود و job تمام می‌شود. | pytest + vitest | `tests/test_ws.py` و `useJob.test.ts` |
| AC-3 | پیام شامل percent و fps و eta و stage و log است. reconnect در هوک هست. | vitest | `useJob.test.ts` |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | دیالوگ پریست | کارت بعدی | S-030 |
| NG-2 | بستن `BUG-6` در دفتر باگ پیش از verdict | ناظر باید ببندد | بعد از review |
| NG-3 | میکس صدا | موازی بعد از S-028 | S-032 |

## Forward-knowledge compliance

- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-028`؛ کارت S-029؛ REVIEW مرحلهٔ `S-012`؛ `BUG-6`؛ گیت و معماری و ایندکس.
- REVIEWها و architecture updateهای اعمال‌شده: پیشرفت از job manager موجود خوانده می‌شود. هوک endpoint را دست‌نویس نمی‌کند؛ بعد از افزودن route، کلاینت OpenAPI بازتولید می‌شود. S-028 هنوز GREEN نیست.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: پیام ساختاریافته است. قطع سوکت خطا را به پاس تبدیل نمی‌کند؛ polling ادامه می‌دهد. capability سوکت اگر برقرار نشود `missing` است و فقط fallback ثبت می‌شود.
- Deferred: دیالوگ → S-030. نوار UI و toast لغو → S-031. داکینگ → S-032. S-033 شروع نمی‌شود.
- Negative boundary: درصد ساختگی برای رسیدن به عدد `10` ممنوع است. پیام‌ها از پیشرفت واقعی ffmpeg می‌آیند. raw command از سوکت اجرا نمی‌شود.
- Evidence plan: pytest روی Windows با export واقعی. vitest هوک بدون ادعای جایگزین CI. اگر کمتر از `10` پیام بیاید تست رد می‌شود و skip نمی‌شود.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
