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
| AC-6 | `/muscle/enhance` → دانلود خروجی → `assert_playable` سبز **و** اثبات اثربخشی در برابر **کنترل**: خروجیِ enhance نسبت به یک re-encodeِ بدون enhance از همان ورودی (همان writer `mp4v`) اختلاف mean-abs > 0.8 دارد (اندازه‌گیری‌شده ۱٫۲۷) و از نویز codec بیشتر است؛ کنترل منفی (`intensity=0` از همان endpoint) باید **دقیقاً ۰٫۰** باشد. | زنده uvicorn + `requests` + `mean_abs_pixel_diff` | `tests/test_api_live.py::test_muscle_enhance_live_http` |
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

- ریسک کم: در این sandbox `mediapipe` با `opencv-python`/`opencv-contrib-python` به‌خاطر نبود `libGL.so.1` import نمی‌شود. با نصب `opencv-python-headless`/`opencv-contrib-python-headless` (نکته‌ی S-009 برای CI ubuntu: یا `libgl1` نصب شود یا از واریانت headless استفاده شود) mediapipe import می‌شود؛ اندازه‌گیری r2 نشان می‌دهد سیگنال enhance نسبت به کنترل در هر دو حالت **یکسان (۱٫۲۶۶۲)** است، پس تست به این تفاوت حساس نیست. مسیر face-protection همچنان در S-035/CI windows تست می‌شود.
- `probe_duration_and_streams` به `ffmpeg -i` (stderr) و `ffprobe` نیست؛ مقایسه با تلورانس و با باز کردن OpenCV کامل می‌شود.
- `test_muscle_enhance_live_http` به OpenCV نیاز دارد (`opencv-python-headless`).

## Revision r2 — چرا AC-6 از «diff > 2.0 نسبت به ورودی» به «diff نسبت به کنترل» تغییر کرد

اندازه‌گیری واقعی روی فیکسچر `short_2s.mp4` (sandbox، mediapipe قابل import با `opencv-*-headless`):

| اندازه‌گیری | مقدار |
|---|---|
| re-encode ساده (بدون enhance، همان writer `mp4v`) نسبت به ورودی | **1.6349** |
| enhance با `natural_gym` نسبت به ورودی | 1.8883 … 1.8972 |
| enhance با `natural_gym` نسبت به **کنترل** (re-encode بدون enhance) | **1.2662** (هم با mediapipe و هم بدون آن — یکسان) |
| `intensity=0` نسبت به کنترل | **0.0000** |

آستانه‌ی مطلق `> 2.0` روی «خروجی در برابر ورودی» عمدتاً **نویز codec** را می‌سنجد (۱٫۶۳ از بودجه‌ی ۲٫۰ را خودِ re-encode پر می‌کند) و به همین دلیل ناپایدار است: با import شدن mediapipe به ۱٫۸۹ می‌افتد و در CI که `libgl1` نصب است قرمز می‌شد. معیار کنترل‌محور نویز را حذف می‌کند، به حضور/absence mediapipe حساس نیست، و با کنترل منفیِ دقیقاً صفر **سخت‌گیرانه‌تر** از آستانه‌ی قبلی است. این «ساده‌کردن تست برای سبز شدن» نیست؛ تست قبلی اشتباه می‌سنجید (پروتکل ⑦: «اگر تست اشتباه است، توضیح مکتوب در commit لازم است»).

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست.
