# CONTRACT — S-024 — Sequence preview player: multi-clip compositing playback

> نوشته‌شده پیش از implementation. ledger تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | سکانس clipA در `0–3s` و clipB با منبع `5–8s` در زمان `3.2s` فریم منبع `5.2s` کلیپ B را نشان می‌دهد. SSIM بیشتر از `0.9` است. | Playwright | `apps/desktop/tests/sequence.spec.ts` |
| AC-2 | فاصلهٔ سوئیچ سر برش، با preload، کمتر از `100ms` است. | Playwright | همان فایل |
| AC-3 | ترک متن روی canvas رسم می‌شود و صدای چند منبع از WebAudio می‌آید. زیر فشار، کیفیت پایین می‌شود و پخش قطع نمی‌شود. | Playwright | همان فایل |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | خروجی فایل و mux | export نیست | S-028 |
| NG-2 | رجیستری کامل شورتکات | کارت بعدی | S-025 |
| NG-3 | ادعای CPU زیر `60%` بدون اندازه‌گیری | skip یا عدد ساختگی پاس نیست | اگر اندازه گرفته نشود `unverified:cpu` می‌ماند |
| NG-4 | `submit_inference()` | مدل Style Match نیست | بعد از job system و کارت مدل |

## Forward-knowledge compliance

- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ CONTRACT مرحلهٔ `S-023`؛ کارت S-024؛ REVIEWهای `S-016` و `S-022`؛ گیت و `STYLE_MATCH_ARCHITECTURE.md` و `06_BUGS.md`.
- REVIEWها و architecture updateهای اعمال‌شده: S-023 در همین batch و هنوز GREEN نیست. وابستگی زنجیره‌ای رعایت می‌شود: integration پلیر بعد از دامنهٔ زوم و عبور static/unit/typecheck. S-022 سبز نمی‌شود.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: نگاشت زمان سکانس به منبع یک domain operation است. رسم از همان تابع فریم است، نه یک data-attribute جعلی. capability صدا فقط `available` / `missing` / `unknown` است و `missing` پاس نیست. کیفیت پایین Reheal L2 یک حالت صریح است.
- Deferred: شورتکات و مودال → S-025. سفر E2E → S-026. export و provenance فایل → S-028. اعتبار SSIM خروجی فایل → S-033 که شروع نمی‌شود. CPU فرآیند اگر در مرورگر قابل خواندن نباشد `unverified:cpu` می‌ماند و پاس شمرده نمی‌شود.
- Evidence note: CI `36120355492` فاصلهٔ پلی‌هد را `0.0259s` در برابر `< 1/60` گرفت. آستانه شل نمی‌شود. transform ثابت قفل فریم نیست؛ پخش انیمیشن هم‌نرخ می‌کشد و در هر فریم state ریکت را عوض نمی‌کند.
- Negative boundary: mutation مستقیم sequence ممنوع است. فریم مرجع تست از زمان منبع ساخته می‌شود، نه کپی بوم پلیر. raw FFmpeg command و filter graph دلخواه اینجا اجرا نمی‌شود.
- Evidence plan: vitest برای نگاشت زمان. Playwright برای SSIM و گپ و متن و صدا بعد از integration. آستانهٔ SSIM `0.9` و گپ `100ms` شل نمی‌شود. CI کامل پیش از تحویل.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
