# CONTRACT — S-028 — FFmpeg export engine: timeline JSON → filter_complex, progress, cancel, NVENC detect

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.
> زنجیرهٔ اجباری: probe → typed operation → capability check → safe execute → verify → provenance.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | سه کلیپ بدون همپوشانی خروجی‌ای می‌دهند که مدت آن با جمع مدت‌ها حداکثر یک فریم فرق دارد و رزولوشن و fps مطابق تنظیم است. | pytest واقعی | `tests/test_export.py` |
| AC-2 | کلیک صدا در `2.0s` با onset کتابخانهٔ `librosa` در `2.0s ±20ms` می‌نشیند. | pytest واقعی | همان فایل |
| AC-3 | لغو در `40%` فرآیند را در کمتر از `1s` می‌کشد و فایل نهایی نمی‌ماند. | pytest واقعی | همان فایل |
| AC-4 | codec یا filter غایب `missing` است و پاس نیست. لیست encoder نامشخص `unknown` است و پاس نیست. NVENC فقط با لیست mock شده واحد تست می‌شود و fallback به `libx264` در provenance ثبت می‌شود. | pytest واحد | `tests/unit/test_export_plan.py` |
| AC-5 | overwrite بدون consent رد می‌شود. مسیر خارج از workspace رد می‌شود. نتیجه JSON ساختاریافته و provenance دارد. parser متنی فقط fallback صریح probe است. | pytest | هر دو فایل |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | کانال WebSocket | کارت بعدی | S-029 |
| NG-2 | دیالوگ و پریست UI | بعد از کانال | S-030 |
| NG-3 | میکس داکینگ و LUFS | کارت صدا | S-032 |
| NG-4 | سوییت SSIM خروجی و faststart | شروع نمی‌شود | S-033 |
| NG-5 | عوض کردن `run_ffmpeg()` که همیشه `-y` دارد | ACهای S-004 معتبرند | مسیر export جدا است؛ ممیزی license همچنان S-086 |

## Forward-knowledge compliance

- Registry IDs: `K-001` برای زنجیرهٔ probe تا provenance در مسیر export همین مرحله. `K-002` و `BUG-18` باز می‌مانند؛ `run_ffmpeg()` همچنان همیشه `-y` دارد و این مرحله آن را برای همیشه نمی‌بندد. `K-003` یعنی ffprobe JSON اول است و ابعاد تهی fail-closed است. `K-004` برای منبع timeline. `K-009` فقط اصول allow-list است و vendor نمی‌شود. `K-007` اعمال نمی‌شود. `K-008` مجوز GREEN نیست. `K-010` و `K-011` رد یا فقط مرجع‌اند.
- Open gaps: فهرست encoder برابر GPU available نیست. `user-gpu` باز است. شکاف‌های UI نام‌دار `S-015` `S-023` `S-024` `S-026` با export بسته نمی‌شوند.
- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ کارت S-028؛ CONTRACT و REVIEW مرحله‌های `S-012` و `S-013` و `S-004`؛ `BUG-18` در `06_BUGS.md`؛ گیت و `STYLE_MATCH_ARCHITECTURE.md` و ایندکس.
- REVIEWها و architecture updateهای اعمال‌شده: S-012 و S-013 هر دو `REVIEW` هستند و GREEN نمی‌شوند. job از `submit()` موجود می‌گذرد، نه از یک thread خام در route. Style Match مدل بار نمی‌کند.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: probe با ffprobe JSON اول است. operation فقط allow-list است: `trim` `setpts` `concat` `scale` `pad` `fps` `amix` `afade` `encode`. capability فقط `available` / `missing` / `unknown`. اجرای امن به فایل موقت می‌نویسد و بدون consent روی مقصد `-y` نمی‌زند. verify مدت و stream و codec را می‌خواند. provenance ساخت plan و encoder واقعی را ثبت می‌کند.
- Deferred: WebSocket → S-029. UI پیشرفت → S-031. داکینگ و `-14 LUFS` → S-032. SSIM فایل و moov/faststart → S-033 که شروع نمی‌شود. ممیزی license FFmpeg → S-086. `BUG-18` در `run_ffmpeg()` باز می‌ماند چون آن تابع مسیر S-004 است.
- Negative boundary: فیلد `raw_command` و `filter_graph` از assistant رد می‌شود. graph دلخواه که با بازکامپایل ops یکی نباشد رد می‌شود. `missing` و `unknown` پاس نیستند. overwrite ناایمن رد می‌شود. مسیر با `..` یا خارج از workspace رد می‌شود. نتیجهٔ verify نشده provenance موفق ندارد.
- Evidence plan: واحد compiler بدون شبکه، بعد از static. pytest رسانه روی Windows CI چون Ubuntu فقط `tests/unit` را اجرا می‌کند. رفتار offline یعنی هیچ socket در compiler نیست. رفتار Windows یعنی مرز مسیر با جداکنندهٔ ویندوز هم رد می‌شود. failure به skip تبدیل نمی‌شود. آستانهٔ `±1 frame` و `±20ms` و `1s` شل نمی‌شود.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
