# CONTRACT — S-006 — Test harness: live-server API tests + artifact assertions helper

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-006 در `03_STEPS.md` (goal/files/real_test/done-when).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | `conftest.py` فیکسچر `live_api` دارد که uvicorn واقعی را روی پورت آزاد بالا می‌آورد و منتظر `/health` می‌ماند. | pytest fixture `live_api` | `tests/test_api_live.py` (session fixture) |
| AC-2 | مارکرهای pytest `unit/real/heavy/gpu` در `pytest.ini` ثبت شده‌اند و `--strict-markers` فعال است. | `pytest.ini` | `tests/test_api_live.py` (مارکرهای `real`, `heavy`) |
| AC-3 | `assert_playable(path, min_dur, has_audio, w, h)` فایل را واقعاً پخش‌پذیر می‌داند (ffffprobe-equivalent + OpenCV) و بر فایل خالی/ناقص AssertionError می‌دهد. | `assert_playable` | `tests/test_api_live.py::test_assert_playable_helper` |
| AC-4 | `frame_diff(a,b)` و `mean_abs_pixel_diff` و `ssim_region` رفتار صحیح دارند (خودسان 0/1.0؛ جابه‌جایی واضح تشخیص). | helper راست‌آزمایی | `tests/test_api_live.py` (helper) |
| AC-5 | آپلود فیکسچر (a) به `/editor/beat-sync` از طریق HTTP واقعی → JSON schema معتبر (status/bpm/total_beats/clips) و clips غیرخالی و bpm≈120. | زنده uvicorn + `requests` | `tests/test_api_live.py::test_beat_sync_live_http` |
| AC-6 | `/muscle/enhance` → دانلود خروجی → `assert_playable` سبز و mean abs pixel diff با ورودی > 2.0. | زنده uvicorn + `requests` | `tests/test_api_live.py::test_muscle_enhance_live_http` |
| AC-7 | قانون skipped ≠ passed: اجرا با `junit` skips را جدا گزارش می‌دهد (reports separate). | `pytest -m real --junitxml` | `pytest.ini` addopts `-ra` (junit report) |

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | بدون تغییر در منطق/کیفیت اندپوینت‌ها یا الگوریتم‌ها — فقط هارنس تست + helper | کارت S-006 فقط تست است | S-007, … |
| NG-2 | بدون ساخت `gate.py` (S-011) یا تنظیم CI (S-009)؛ فقط pytest markers + conftest | این‌ها مرحله‌ی خودشان | S-009, S-011 |
| NG-3 | بدون رفع باگ‌های Muscle (خروجی mp4v/بی‌صدا در S-037) یا WebSocket (S-029) یا temp cleanup (S-074) | هر باگ در مرحله‌ی خودش | S-029, S-037, S-074 |
| NG-4 | بدون ساخت کارخانه فیکسچر (S-005 تمام شد)؛ این مرحله صرفاً از فیکسچرها استفاده می‌کند | منبع فیکسچر در S-005 | S-005 |

## Reheal layers touched

- هیچ‌کدام — این مرحله صرفاً ابزار تست و helper است؛ هیچ لایه‌ی Reheal (L1–L7) یا مسیر runtime تغییر نمی‌کند. Probe آشوب: N/A با دلیل مکتوب (تصدیق رفتار/پیکسل خروجی؛ نه بازیابی از کرش).

## Risks / unknowns

- ریسک کم: `mediapipe` در این sandbox به‌خاطر نبود `libGL.so.1` import نمی‌شود؛ MuscleEnhancer به‌صورت graceful (face protection disabled) ادامه می‌دهد و تست `/muscle/enhance` همچنان output واقعی و pixel-diff > 2.0 را اثبات می‌کند. مسیر face-protection در S-035/CI windows تست می‌شود.
- `probe_duration_and_streams` به `ffmpeg -i` (stderr) و `ffprobe` نیست؛ مقایسه با تلورانس و با باز کردن OpenCV کامل می‌شود.
- `test_muscle_enhance_live_http` به OpenCV نیاز دارد (`opencv-python-headless`).

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست.
