# CONTRACT — S-032 — Audio mixdown: track gains, fades, ducking, music bed

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.
> زنجیرهٔ رسانه: probe → typed operation → capability check → safe execute → verify → provenance.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | خروجی موسیقی `-12dB` به‌علاوهٔ گفتار، بلندی یکپارچهٔ `ebur128` برابر `-14 ±1 LUFS` است. | pytest واقعی | `tests/test_audio_mix.py` |
| AC-2 | RMS موسیقی در بازهٔ گفتار حداقل `6dB` کمتر از بازهٔ سکوت است. | pytest واقعی | همان فایل |
| AC-3 | گین، fade in/out، داکینگ `sidechaincompress`، و نرمال‌سازی فقط operationهای allow-list هستند. filter غایب `missing` است و پاس نیست. | pytest واحد + واقعی | `tests/unit/test_export_plan.py` و تست واقعی |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | سوییت SSIM و پخش مرورگر خروجی | شروع نمی‌شود | S-033 |
| NG-2 | UI دیالوگ | مال S-030 است | S-030 |
| NG-3 | عوض کردن آستانهٔ `6dB` یا `±1 LUFS` | شل کردن ممنوع | اگر فیلتر نرسد تست رد می‌شود |

## Forward-knowledge compliance

- Registry IDs: `K-001` و `K-009` فقط به‌صورت allow-list تایپ‌شده، بدون vendor. `K-002` overwrite ناایمن را رد می‌کند و `BUG-18` را باز نگه می‌دارد. `K-003` probe فیلتر را fail-closed می‌کند. `K-007` اعمال نمی‌شود. `K-008` مجوز ادامه نیست. `K-010` و `K-011` وارد runtime نمی‌شوند. `K-012` و `K-013` اینجا اجرا نمی‌شوند. `K-014` گیت دات‌نت اضافه نمی‌کند.
- Open gaps: `missing` برای فیلتر پاس یا skip نیست. `user-gpu` باز است. شکاف‌های نام‌دار UI با این مرحله بسته نمی‌شوند.
- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-028`؛ کارت S-032؛ گیت و معماری و ایندکس و `BUG-18`.
- REVIEWها و architecture updateهای اعمال‌شده: S-032 به S-028 وابسته است، نه به S-031. می‌تواند بعد از compiler با S-029 موازی باشد، ولی integration صدا بعد از عبور static/unit/typecheck همان دامنه است. S-028 هنوز GREEN نیست.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: گین و fade و sidechain و loudnorm operation typed هستند. graph از ops ساخته می‌شود. probe فیلترها capability را تعیین می‌کند. خروجی verify مدت و stream صدا را دارد و provenance فیلترهای استفاده‌شده را ثبت می‌کند.
- Deferred: اعتبار بصری و faststart و sync تصویری سوییت → S-033 که شروع نمی‌شود. license FFmpeg → S-086.
- Negative boundary: رشتهٔ filter از assistant رد می‌شود. `missing` برای `sidechaincompress` یا `loudnorm` یا `ebur128` پاس نیست و skip نمی‌شود. overwrite ناایمن رد می‌شود. نتیجهٔ اندازه‌گرفته‌نشده پاس نیست.
- Evidence plan: واحد allow-list بدون رسانه. pytest واقعی روی Windows. offline یعنی ورودی فقط فایل محلی است. Windows یعنی همان تست در job ویندوز. آستانه‌ها شل نمی‌شوند.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود. S-033 شروع نمی‌شود.
