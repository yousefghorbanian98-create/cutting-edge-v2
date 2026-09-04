# CONTRACT — S-005 — Real-media fixture factory (FFmpeg-generated + licensed human clip)

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-005 در `03_STEPS.md` (goal/files/real_test/done-when).

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | `tests/fixtures/make_fixtures.py` همه‌ی فیکسچرهای **synthetic** را با FFmpeg واقعی می‌سازد: (a) 10s 720p testsrc متحرک + کلیک ۱۲۰BPM، (b) بی‌صدا، (c) 2s کوتاه، (d) ۰ بایت، (e) هدر خراب، (f) 9:16 عمودی، (g) 4K 3s، (h) نام فارسی+فاصله | `make_fixtures(workdir, allow_network=False)` | `tests/test_fixtures.py::test_factory_produces_all_fixtures` |
| AC-2 | `probe_duration_and_streams` (معادل ffprobe؛ imageio-ffmpeg فقط ffmpeg دارد) برای هر فیکسچر پخش‌شدنی، رزولوشن/طول/صدا را تأیید می‌کند و با `manifest.json` مطابقت دارد | `probe_duration_and_streams(paths[name])` | `tests/test_fixtures.py::test_probe_streams_duration_resolution` |
| AC-3 | فیکسچر `tone_120bpm_720p.mp4` → BPM شناسایی‌شده با `BeatSyncEngine` در بازه‌ی ±3 از 120 باشد (پس این فیکسچر واقعاً ۱۲۰ BPM است) | `BeatSyncEngine.analyze_audio` | `tests/test_fixtures.py::test_bpm_fixture_detects_120` |
| AC-4 | اجرای **آفلاین** (بدون دانلود Pexels/pose) هشدار **صریح** می‌دهد و به synthetic-only تنزل می‌کند — نه skip بی‌صدا؛ مجموعه‌ی دانلودی با `unverified:network` ثبت می‌شود | `make_fixtures(allow_network=False)` → `warnings` | `tests/test_fixtures.py::test_offline_degrades_explicitly_not_silent` |
| AC-5 | `manifest.json` (commit‌شده) همه‌ی فیکسچرهای synthetic را توصیف می‌کند و SHA256 پسوندی برای assetهای دانلودی قابل pin کردن دارد | پارس `manifest.json` | `tests/test_fixtures.py::test_manifest_describes_every_synthetic_fixture` |
| AC-6 | `tests/conftest.py` فیکسچرها را با نام expose می‌کند (`fixture("name")`/`fixtures_dir`) و دایرکتوری فیکسچرها git-ignored است (مدیا هرگز commit نمی‌شود) | pytest fixture + `git check-ignore` | `tests/test_fixtures.py` (با `fixture`/`fixtures_dir`) |

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | هیچ تغییری در بک‌اند/اندپوینت‌ها یا الگوریتم‌های AI — فقط کارخانه‌ی فیکسچر + conftest | کارت S-005 فقط فیکسچر است | S-006, … |
| NG-2 | بدون `assert_playable`/`frame_diff`/`ssim_region` (این‌ها S-006) و بدون تست‌های API live (S-006) | این مرحله صرفاً فیکسچر تولید می‌کند | S-006 |
| NG-3 | بدون رفع باگ/کد upstream | جلوگیری از scope creep | — |
| NG-4 | دانلود کلیپ انسانیِ واقعی (Pexels) و تصویر pose فقط در صورت وجود شبکه؛ اینجا با pin SHA256 و fallback آفلاین | sandbox/CI بدون شبکه است | CI + رونوشت آفلاین |

## Reheal layers touched

- هیچ‌کدام — مرحله فقط ابزار تست/فیکسچر است؛ هیچ لایه‌ی Reheal (L1–L7) یا مسیر داده‌ی runtime تغییر نمی‌کند. Probe آشوب: N/A با دلیل مکتوب (بدون رفتار runtime؛ رفتار آفلاین/کرش با AC-4 اثبات می‌شود).

## Risks / unknowns

- ریسک کم: تولید فیکسچر با `testsrc2` ممکن است بر اساس نسخه‌ی ffmpeg کمی متفاوت باشد؛ مقایسه‌های duration/resolution با تلورانس (±2 پیکسل، ±0.5s) انجام می‌شود.
- `probe_duration_and_streams` از `ffmpeg -i` (stderr) استفاده می‌کند که نسخه‌محور است؛ وقتی S-005/CI با ffprobe موجود شد، اولویت به `ffprobe -print_format json` داده می‌شود (يادداشت از S-004 REVIEW).
- `tone_120bpm_720p.mp4` ممکن است فایل بزرگ‌تری بسازد؛ در cache git-ignored تولید می‌شود، هرگز commit نمی‌شود.

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست.
