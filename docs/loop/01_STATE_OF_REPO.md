# 01 — State of the Repo (ممیزی واقعی، ۲۰۲۶-۰۹-۰۳)

> این سند نتیجه‌ی خواندن **کد واقعی** شاخه‌ی `arena/01a06904-cutting-edge-v2` (commit `a76272e`) است، نه بازنویسی سند خوش‌بینانه‌ی قبلی. تخمین واقعی پیشرفت به سمت v1.0: **~12–15٪** (سند قبلی: ۳۰–۳۵٪). دلیل تفاوت در بخش «شکاف‌های بحرانی» آمده.

## وضعیت شاخه‌ها
- `main` = فقط `README.md` (یک خط).
- `arena/01a06904-cutting-edge-v2` = ۵۱ فایل، ۳٬۷۳۴ خط، ۶ کامیت. این شاخه به‌صورت fast-forward روی شاخه‌ی سشن فعلی (`arena/01a06951-cutting-edge-v2`) آورده شد تا کار از روی آخرین کد ادامه یابد.
- هیچ تگ/Release/CI run موفقی وجود ندارد.

## آنچه واقعاً وجود دارد و کار می‌کند
| بخش | فایل | ارزیابی |
|-----|------|---------|
| FastAPI | `ai-engine/src/main.py` (۲۲۰ خط) | ۹ اندپوینت؛ منطق واقعی OpenCV/librosa؛ **ولی** با import نسبی نوشته شده و `python main.py` کرش می‌کند (بخش شکاف‌ها) |
| ماژول‌های AI | ۱۶ فایل پایتون (~۱٬۵۰۰ خط) | الگوریتم‌های واقعی اما ساده؛ اکثراً بدون تست؛ بدون progress/cancel |
| Muscle Enhancer | `muscle_enhancer.py` | ۵ تکنیک پیاده شده؛ face mask با ۳۴ نقطه؛ خروجی `mp4v` **بدون صدا** |
| Reheal | ۵ فایل کوچک (~۱۵۰ خط) | HealthMonitor/AutoFixer/CrashRecovery/MemoryGuard/Validator موجود اما **به FastAPI وصل نیستند** (فقط `/health` مستقیماً psutil می‌خواند) |
| Frontend | `page.tsx` (۳۸۳ خط) + ۲ store + ۲ کامپوننت | یک صفحه‌ی monolith با UI کامل و fetch واقعی به `127.0.0.1:8001` |
| Tauri | `main.rs` (۳۱ خط) + Cargo.toml + conf ۷ خطی | ۲ command ساده؛ **کامپایل نمی‌شود** (بخش شکاف‌ها) |
| CI | `ci.yml` | فقط `main`، فقط pytest سنگین روی windows-latest بدون کش؛ تا حالا اجرا نشده چون روی main کدی نیست |
| تست | `tests/test_pipeline.py` (۴ تست) | با فریم‌های تصادفی numpy؛ هیچ تست API/E2E/فرانت |

## شکاف‌های بحرانی (چرا «۳۰–۳۵٪» واقع‌بینانه نبود)

### B-1 بک‌اند اجرا نمی‌شود آن‌طور که مستند شده
`main.py` از `from .editor_ai.beat_sync import …` استفاده می‌کند ولی `if __name__ == "__main__": uvicorn.run(app, …)` دارد → `ImportError: attempted relative import`. باید به‌صورت پکیج اجرا شود (`uvicorn src.main:app` از داخل `ai-engine`) که مستند نشده. `python-dotenv` هم نیست، پس `.env` خوانده نمی‌شود. → **S-002**

### B-2 Beat Sync هنوز شکسته است
`from moviepy.editor import VideoFileClip` و آرگومان `verbose=False` هر دو در MoviePy ≥ 2.0 (که در requirements پین شده: `moviepy>=2.0.0`) وجود ندارند → استخراج صدا همیشه به `except` می‌افتد و `""` برمی‌گرداند. «BUG 1 FIXED» در سند قبلی صحیح نیست. → **S-004**

### B-3 حفره‌ی امنیتی path traversal
`save_upload` مسیر را از `file.filename` خام می‌سازد و `/muscle/download/{filename}` بدون پاک‌سازی `os.path.join(TEMP_DIR, filename)` می‌کند. `allow_origins=["*"]`. → **S-003**

### B-4 فرانت بدون استایل رندر می‌شود
`page.tsx` ۸۶ بار `className` با کلاس‌های Tailwind دارد اما `tailwindcss`, `postcss`, `daisyui`, `globals.css` هیچ‌کدام وجود ندارند. `next build` احتمالاً موفق می‌شود ولی خروجی، صفحه‌ای بدون CSS است. فونت‌ها فقط `font-family` رشته‌ای هستند بدون بارگذاری. → **S-007**

### B-5 Tauri کامپایل نمی‌شود
- `tauri = { features = ["shell-open"] }` — این feature در Tauri 2 وجود ندارد.
- `build.rs` و `tauri-build` نیست؛ `tauri.conf.json` بدون `build.devUrl/beforeBuildCommand`, بدون `bundle`, بدون آیکون (Tauri بدون آیکون build نمی‌کند).
- پکیج `@tauri-apps/cli` و `@tauri-apps/api` در `package.json` نیستند.
→ **S-010**

### B-6 پردازش سنگین، سرور را قفل می‌کند
اندپوینت‌های `async def` کار CPU-bound را مستقیم اجرا می‌کنند → در طول Muscle Enhance، `/health` پاسخ نمی‌دهد و Reheal فرانت «قرمز» می‌شود. → **S-012**

### B-7 ابزارهای کیفیت نصب نیستند
Biome، Ruff، Vitest، Playwright، pytest markers، pre-commit — هیچ‌کدام. `turbo.json` از `pipeline` (Turbo 1) استفاده می‌کند؛ `turbo: latest` = Turbo 2 که `tasks` می‌خواهد. نسخه‌های `latest` در چند جا. → **S-008**

### B-8 دو اسکریپت تولیدکننده در ریشه
`build_cutting_edge.py` (۱٬۲۳۸ خط) و `extend_cutting_edge_part2.py` (۴۸۲ خط) کد منبع را از داخل رشته‌های پایتون تولید می‌کنند. با ادامه‌ی کار روی فایل‌های واقعی، این‌ها منبع تناقض می‌شوند. → **S-001**

### B-9 Reheal فقط اسکلت است
لایه‌های L1–L5 هر کدام ۲۰–۴۰ خط هستند و هیچ‌کدام در مسیر درخواست‌های FastAPI استفاده نمی‌شوند؛ L6 فقط یک ErrorBoundary؛ L7 وجود ندارد. «۷ لایه فعال» در UI یک رشته‌ی ثابت در Rust است. → **P5 (S-072…S-077)**

## چه چیزی از سند قبلی معتبر است و حفظ می‌شود
- ۱۶ قابلیت تأییدشده — همگی در `03_STEPS.md` نگاشت شده‌اند (S-035…S-056).
- استک قفل‌شده — با سه شفاف‌سازی ناسازگاری (DaisyUI 5، MoviePy import، Tauri plugins) که در `02_LOOP_PROTOCOL.md §5` توضیح داده شده.
- محدودیت‌های سخت‌افزاری و بودجه‌ی $0 — به‌عنوان بودجه‌های قابل اندازه‌گیری در چک‌لیست کلاس جهانی و S-082.
- توکن‌های طراحی، مدل‌های OpenRouter، صداهای edge-tts.
- سؤالات باز کاربر — به کارت‌های `U3` با پیش‌فرض تبدیل شدند تا هیچ‌کدام مسدودکننده نباشند.

## نگاشت سریع: سند قبلی → مرحله‌ی لوپ
| آیتم سند قبلی | مرحله |
|---------------|--------|
| BUG 3 face protection | S-035 |
| BUG 4 audio fallback | S-004 |
| BUG 5 temp cleanup | S-074 |
| BUG 6 WebSocket | S-029 |
| Timeline Real (0.3) | S-013 → S-027 |
| Export (0.4) | S-028 → S-034 |
| AI Integration (0.5) | S-035 → S-057 |
| Tauri (0.6) | S-058 → S-067 |
| Project & Stability (0.7) | S-068 → S-078 |
| Testing & Polish (0.8) | S-079 → S-090 |
| Release (1.0) | S-091 → S-098 |
| ۷ لایه‌ی Reheal | `05_REHEAL_MATRIX.md` |
| ۷ سؤال باز | S-001, S-050, S-063, S-085, S-089, S-091 (همه با پیش‌فرض) |
