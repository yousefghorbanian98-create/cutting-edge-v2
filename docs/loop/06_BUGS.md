# 06 — Known Bugs (باگ‌های شناخته‌شده)

> هر باگ یک شناسه، وضعیت واقعی (بر اساس کد، نه ادعا)، مرحله‌ی بستن و **تست اثبات** دارد. باگ فقط وقتی `CLOSED` می‌شود که تست اثباتش در CI سبز باشد.

| id | عنوان | وضعیت واقعی | فایل | مرحله | تست اثبات |
|----|-------|-------------|------|-------|-----------|
| BUG-1 | librosa نمی‌تواند MP4 بخواند | **OPEN (regressed)** — «رفع» با `moviepy.editor` انجام شده که در MoviePy 2 وجود ندارد؛ عملاً هنوز شکسته | `editor_ai/beat_sync.py` | S-004 | `test_beat_sync.py::test_mp4_click_track_bpm` |
| BUG-2 | ViralCut روی ویدیوی کوتاه کرش می‌کند | FIXED در کد؛ **بدون تست** | `editor_ai/viral_cut.py` | S-006 (تست), S-042 | `test_api_live.py::test_viral_cut_short_video` |
| BUG-3 | محافظت صورت دقیق نیست (۳۴ نقطه) | OPEN | `muscle/muscle_enhancer.py` | S-035 | `test_face_guard.py::test_face_ssim_preserved` |
| BUG-4 | بدون fallback استخراج صدا | OPEN | `editor_ai/beat_sync.py` | S-004 | `test_beat_sync.py::test_ffmpeg_extract_aac` |
| BUG-5 | فایل‌های موقت پاک نمی‌شوند | OPEN | `main.py` | S-074 | `test_cleanup.py::test_old_files_removed` |
| BUG-6 | بدون WebSocket پیشرفت | OPEN | `main.py` + فرانت | S-029 | `test_ws.py::test_progress_monotonic` |
| BUG-7 | **(جدید)** import نسبی + `python main.py` → ImportError | OPEN | `main.py` | S-002 | `scripts/dev-backend.sh` در CI + `/health` |
| BUG-8 | **(جدید)** path traversal در upload/download | OPEN — امنیتی | `main.py` | S-003 | `test_security.py::test_traversal_*` |
| BUG-9 | **(جدید)** Tailwind/DaisyUI نصب نیست؛ UI بدون استایل | OPEN | `apps/desktop` | S-007 | Playwright computed-style |
| BUG-10 | **(جدید)** Tauri کامپایل نمی‌شود (`shell-open`, بدون build.rs/آیکون) | OPEN | `src-tauri` | S-010 | CI windows `tauri build` artifact |
| BUG-11 | **(جدید)** اندپوینت‌های async سرور را بلاک می‌کنند | OPEN | `main.py` | S-012 | `test_jobs.py::test_health_latency_during_job` |
| BUG-12 | **(جدید)** خروجی Muscle Enhancer بدون صدا و با `mp4v` | OPEN | `muscle_enhancer.py` | S-037 | `assert_playable(has_audio=True, vcodec='h264')` |
| BUG-13 | **(جدید)** `.env` خوانده نمی‌شود (بدون dotenv) | OPEN | `main.py` | S-002 | `test_config.py` |
| BUG-14 | **(جدید)** CORS `*` روی سرویس محلی | OPEN | `main.py` | S-003 | `test_security.py::test_cors_origin` |
| BUG-15 | **(جدید)** `turbo.json` فرمت Turbo 1 با `turbo@latest` (=2) | OPEN | `turbo.json` | S-008 | `pnpm turbo run build` در CI |

## پروتکل باگ جدید
1. شناسه‌ی بعدی بگیر (`BUG-16` …).
2. **اول** تست بازتولید بنویس (قرمز).
3. اگر در حوزه‌ی مرحله‌ی جاری است همان‌جا ببند؛ وگرنه کارت hotfix `S-xxx-hN` بساز و به دفترچه اضافه کن (از طریق `steps.json`).
4. بستن = تست اثبات سبز در CI + ردیف این جدول `CLOSED (S-xxx, <commit>)`.
