# CONTRACT — S-004 — MoviePy 2.0 compatibility + FFmpeg-first audio extraction (BUG 4)

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-004 در `03_STEPS.md` (goal/files/real_test/done-when).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | `ai-engine/src/core/ffmpeg.py` وجود دارد و با کشف باینری (env `CE_FFMPEG_BIN` → PATH → `imageio-ffmpeg`) دستور برون‌ریز `ffmpeg -y -i <video> -vn -ac 1 -ar 22050 <out.wav>` را اجرا می‌کند و در صورت نبود باینری خطای واضح می‌دهد. | `find_ffmpeg()` + اجرای واقعی | `tests/test_beat_sync.py::test_ffmpeg_extract_aac` |
| AC-2 | MP4 با صدای AAC 48k → خروجی WAV با نمونه‌برداری **22050** و تک‌کاناله (mono) استخراج می‌شود (BUG-4؛ قبلاً همیشه `""` برمی‌گشت). | `wave` module + `extract_audio` | `tests/test_beat_sync.py::test_ffmpeg_extract_aac` |
| AC-3 | فیکسچر MP4 کلیک‌ترک ۱۲۰ BPM → BPM شناسایی‌شده در بازه‌ی ±3 باشد و بیات‌ها خالی نباشند. | `BeatSyncEngine.analyze_audio` + `librosa.beat.beat_track` | `tests/test_beat_sync.py::test_click_track_bpm_within_3` |
| AC-4 | MP4 بی‌صدا → بدون استثنا `[]` برمی‌گردد (نه بیات‌های ساختگی) و `tempo` غیرمثبت/خالی است. | `BeatSyncEngine.analyze_audio` | `tests/test_beat_sync.py::test_silent_mp4_returns_empty_without_exception` |
| AC-5 | هیچ import از `moviepy.editor` (ماژول حذف‌شده در MoviePy 2) سه‌واژه‌ای در مسیر اصلی نیست؛ `moviepy.editor` فقط در fallback داخلی `core/ffmpeg` و با import صحیح MoviePy 2 است. | `grep -rn "moviepy.editor" ai-engine/` | `tests/test_beat_sync.py` (بازبینی مسیر) |

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | هیچ تغییر در API اندپوینت‌ها یا فرمت خروجی دیگری؛ فقط استخراج صدا و BPM داخل `BeatSyncEngine` | کارت S-004 فقط BUG-4 است | S-029, S-039… |
| NG-2 | بدون تغییر `.github/workflows/ci.yml` و بدون ابزار کیفیت یا `gate.py` | CI = S-009؛ ابزار = S-008/S-011 | S-008, S-009, S-011 |
| NG-3 | بدون رفع سایر باگ‌ها (مثلاً BUG-3 face protection، BUG-6 WebSocket، BUG-5 temp cleanup) | بسته شدن هر باگ در مرحله‌ی خودش | S-029, S-035, S-074 |
| NG-4 | بدون ساخت «کارخانه فیکسچر» (S-005) یا `assert_playable` (S-006)؛ این‌ها در مراحل بعدی ساخته می‌شوند | این مرحله فقط BPM/استخراج صدا را اثبات می‌کند | S-005, S-006 |

## Reheal layers touched

- هیچ‌کدام — این مرحله فقط مسیر استخراج صدا و سازماندهی کد را اصلاح می‌کند؛ هیچ لایه‌ی Reheal (L1–L7) را تغییر نمی‌دهد. Probe آشوب: N/A با دلیل مکتوب (محاسبه‌ی هم‌زمان بیات؛ هیچ پروسه‌ی ماندگار/حالت جدیدی برای آشوب وجود ندارد).

## Risks / unknowns

- ریسک متوسط: استخراج صدا اکنون به FFmpeg وابسته است؛ اگر FFmpeg در محیط اجرا نباشد، fallback به MoviePy 2 می‌شود (و در بدترین حالت `[]` برمی‌گردد نه کرش). در این sandbox سیستم ffmpeg موجود نیست؛ از `imageio-ffmpeg` (باندل) استفاده شد و `ffprobe` جدا در دسترس نیست → تأیید WAV با ماژول `wave` (معادل ffprobe) انجام می‌شود و در ماژول `ffmpeg.side` یک `probe_duration_and_streams` با `ffmpeg -i` (استیرد) افزوده شد.
- `librosa` به عنوان وابستگی واقعی BPM باقی است؛ این مرحله به آن نیاز دارد.

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست.
