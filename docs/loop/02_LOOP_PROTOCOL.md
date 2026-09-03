# 02 — The Loop Protocol (پروتکل لوپ)

> این سند «قانون اساسی» اجرای پروژه است. هر ایجنت/سشن قبل از نوشتن حتی یک خط کد باید آن را بخواند.
> هدف: کاربر **کمترین دخالت ممکن** را داشته باشد؛ کیفیت **کلاس جهانی** باشد؛ هیچ مرحله‌ای بدون **تست واقعی** سبز نشود.

---

## 0. سه اصل غیرقابل مذاکره

1. **هیچ چیز بدون شواهد سبز نمی‌شود.** «تست پاس شد» یعنی یک artifact واقعی (فایل ویدیوی قابل پخش، اسکرین‌شات، JSON خروجی، لینک CI) وجود دارد و در `04_LEDGER.md` ثبت شده. عدد پوشش تست یا «۱۲ تست پاس» به‌تنهایی شواهد نیست.
2. **Skip ≠ Pass.** تستی که به‌خاطر نبود GPU/شبکه/کلید skip شده، در دفترچه با برچسب `unverified:<reason>` ثبت می‌شود، نه GREEN. اگر بدون آن نمی‌شود GREEN شد، وضعیت `AMBER` می‌ماند تا کاربر `smoke-gpu.ps1` را اجرا کند.
3. **هر مرحله یک .exe قابل نصب تحویل می‌دهد** (از S-010 به بعد). اگر build نصب‌کننده قرمز شود، هیچ مرحله‌ی دیگری شروع نمی‌شود تا سبز شود.

---

## 1. ساختار لوپ برای هر مرحله `S-xxx`

هر شماره در `03_STEPS.md` دقیقاً با این ۹ گام اجرا می‌شود. گام‌ها قابل حذف نیستند؛ فقط می‌توانند «N/A با دلیل مکتوب» باشند.

```
┌───────────────────────────────────────────────────────────────────────┐
│  S-xxx                                                                │
│                                                                       │
│  ① SYNC      ② PLAN      ③ BUILD      ④ STATIC      ⑤ TEST-REAL      │
│     │            │           │            │              │            │
│     ▼            ▼           ▼            ▼              ▼            │
│  git pull     write        code +      biome/ruff/    pytest -m real │
│  read ledger  test FIRST   docs        tsc/cargo      playwright     │
│  read step    (red)                    verify_ledger  artifact check │
│                                                                       │
│  ⑥ REHEAL-CHECK   ⑦ DEBUG-LOOP (≤5)   ⑧ EVIDENCE      ⑨ COMMIT+PUSH  │
│     │                  │                  │                 │         │
│     ▼                  ▼                  ▼                 ▼         │
│  chaos probe        root-cause →      ledger row        conventional │
│  for touched        fix → back to     GREEN/AMBER       commit, push │
│  Reheal layer       ④ (never ⑤)       + artifacts       CI must pass │
└───────────────────────────────────────────────────────────────────────┘
```

### ① SYNC (همگام‌سازی)
- `git fetch && git status` — روی شاخه‌ی سشن (Arena) هستیم؛ هیچ شاخه‌ی دیگری ساخته نمی‌شود.
- `python scripts/verify_ledger.py` باید سبز باشد. اگر قرمز است، **اول** آن را درست کن (بدهی از سشن قبل).
- مرحله‌ی بعدی = اولین ردیف `TODO`/`RED` در دفترچه که همه‌ی `deps` آن `GREEN` هستند. ترتیب شماره‌ها را نشکن مگر با دلیل مکتوب در notes.
- خواندن کارت مرحله در `03_STEPS.md` (هدف، فایل‌ها، تست واقعی، done-when).

### ② PLAN (طرح؛ تست اول)
- در ≤ ۱۰ خط بنویس: چه می‌سازی، چه تستی ثابت می‌کند کار می‌کند، چه چیزی ممکن است بشکند.
- **تست واقعی را اول بنویس** و اجرا کن تا قرمز شود (اثبات این‌که تست واقعاً چیزی را می‌سنجد).
- اگر تصمیم محصولی لازم است (`U3`) و پاسخی نیست: پیش‌فرض کارت را اعمال کن، در `docs/DECISIONS.md` ثبت کن، ادامه بده. **منتظر نمان.**

### ③ BUILD (ساخت)
- کد کامل و production-grade. بدون `TODO`، بدون placeholder، بدون `any` در TS، بدون `except: pass` در Python.
- هر تابع عمومی docstring/JSDoc دارد. پیام‌های کاربر فارسی و انگلیسی (از i18n بعد از S-085).
- به‌روزرسانی مستندات همان مرحله (README بخش مربوط، docs/user اگر قابلیت کاربری است).
- محدودیت سخت‌افزار همیشه در ذهن: RAM اپ < 1.5GB، VRAM مدل‌ها < 800MB، CUDA 11.8، float16.

### ④ STATIC (تحلیل ایستا)
```
python scripts/gate.py --stage static
```
شامل: Biome (lint+format)، `tsc --noEmit` strict، Ruff (lint+format، قوانین S=security، B=bugbear)، `cargo fmt --check && cargo clippy -D warnings`، gitleaks، `verify_ledger.py`، `sync-version.py --check` (بعد از S-063). هر خطا = توقف.

### ⑤ TEST-REAL (تست واقعی)
```
python scripts/gate.py --stage unit     # vitest + pytest -m unit + cargo test
python scripts/gate.py --stage real     # pytest -m real  (live uvicorn, real FFmpeg media)
python scripts/gate.py --stage e2e      # playwright (web) / tauri-driver (windows CI)
```
معنای «واقعی» در این پروژه:
| نوع | قابل قبول | غیرقابل قبول |
|-----|-----------|--------------|
| بک‌اند | آپلود مدیای واقعی FFmpeg‌ساز به سرور زنده‌ی uvicorn، بررسی خروجی با `ffprobe`/پیکسل | فراخوانی مستقیم تابع با آرایه‌ی تصادفی numpy (مثل `test_pipeline.py` فعلی) |
| خروجی ویدیو | `assert_playable` (استریم‌ها، مدت، رزولوشن) + SSIM/اختلاف پیکسلی + پخش در Chromium | «فایل وجود دارد و > 0 بایت» |
| UI | Playwright با ماوس/کیبورد واقعی، اسکرین‌شات رگرسیون، `document.fonts.check`، بررسی computed style | snapshot تست کامپوننت با mock store |
| AI ابری | با کلید واقعی اگر موجود؛ بدون کلید = `unverified:no-key` در دفترچه | mock که همیشه موفق است و مرحله GREEN می‌شود |
| GPU | `smoke-gpu.ps1` روی ماشین کاربر با خروجی JSON | «روی CPU کار کرد پس روی GPU هم کار می‌کند» |
| دسکتاپ | نصب silent روی windows-latest، `Get-Process`، بررسی orphan، حذف تمیز | «cargo build موفق شد» |

### ⑥ REHEAL-CHECK (بررسی خودترمیمی)
برای هر لایه‌ی Reheal که این مرحله به آن دست زده (`docs/loop/05_REHEAL_MATRIX.md`)، حداقل یک **probe آشوب** اجرا شود: کشتن پروسه، پرکردن temp، قطع شبکه، کلید غلط، فایل خراب. باید: (a) کرش نکند، (b) لاگ ساختاریافته بنویسد، (c) UI حالت قابل فهم نشان دهد، (d) بعد از رفع مشکل خودش برگردد.

### ⑦ DEBUG-LOOP (حلقه‌ی اشکال‌زدایی، حداکثر ۵ تکرار)
- هر شکست: **ریشه‌یابی** (لاگ JSON، تریس، بازتولید حداقلی) → اصلاح → **برگرد به ④** (نه ⑤؛ استاتیک دوباره باید پاس شود).
- شمارنده‌ی `iter` در دفترچه +1.
- در تکرار ۵ اگر هنوز قرمز: وضعیت `BLOCKED`، نوشتن `docs/loop/blockers/S-xxx.md` (چه امتحان شد، فرضیه‌ها، پیشنهاد)، رفتن به مرحله‌ی بعدیِ **مستقل** (بدون وابستگی به این). فقط اگر مرحله‌ای مستقل نمانده، از کاربر بپرس.
- ممنوع: کم‌کردن سخت‌گیری تست برای سبز شدن. اگر تست اشتباه است، توضیح مکتوب در commit لازم است.

### ⑧ EVIDENCE (شواهد)
به‌روزرسانی ردیف `04_LEDGER.md`:
- `status`: `GREEN` فقط اگر ⑤ و ⑥ سبز و شواهد موجود؛ `AMBER` اگر منتظر `U1/U2`.
- `verified_on`: `ci-ubuntu`, `ci-windows`, `local-linux`, `user-gpu`.
- `evidence`: لینک CI run + مسیر artifact (junit، playwright-report، exe، smoke JSON در `docs/loop/evidence/S-xxx/`).
- `notes`: `unverified:<reason>` برای هر تست skip شده.
- اگر باگ شناخته‌شده‌ای بسته شد، `docs/loop/06_BUGS.md` به‌روز شود.

### ⑨ COMMIT + PUSH
- Conventional Commits: `feat(timeline): S-018 trim handles with ripple/roll` — شماره‌ی مرحله همیشه در پیام.
- `git push origin <session-branch>`؛ CI باید سبز شود. اگر CI قرمز شد و لوکال سبز بود: **اول CI را درست کن** (محیط تمیز حقیقت است).
- بعد از هر مایلستون (S-027, S-034, …): تگ `vX.Y.0`، pre-release با exe از CI، به‌روزرسانی `CHANGELOG.md`، درخواست `U2` از کاربر با لینک مستقیم دانلود + یک خط دستور `smoke-gpu.ps1`.

---

## 2. لوپ خارجی (مایلستون‌ها)

```
for phase in P0..P7:
    for step in phase.steps:          # لوپ داخلی بالا
        run_9_steps(step)
    regression: gate.py --stage all   # همه‌ی مراحل قبلی دوباره
    tag + pre-release (.exe)
    request U2 (user smoke on GTX 1650)   ← تنها نقطه‌ی دخالت الزامی کاربر
    while user smoke reports issue:
        open hotfix card S-xxx-hN → run_9_steps
    ledger: milestone GREEN with verified_on=user-gpu
```

**قاعده‌ی ادامه بدون کاربر:** اگر کاربر تا ۷۲ ساعت smoke نداد، ایجنت فاز بعدی را شروع می‌کند ولی مایلستون `AMBER` می‌ماند و در ابتدای هر سشن یادآوری می‌شود. هیچ نسخه‌ی `1.0.0` بدون `user-gpu` سبز روی S-090 و S-097 منتشر نمی‌شود.

---

## 3. حداقل دخالت کاربر — دقیقاً چه چیزی از کاربر خواسته می‌شود

| کد | چه وقت | چه کاری | زمان تقریبی |
|----|--------|---------|-------------|
| U1 | یک‌بار، قبل از S-053 | کلید OpenRouter را در Settings برنامه (یا `ai-engine/.env`) بگذارد | ۲ دقیقه |
| U2 | پایان هر مایلستون (۸ بار کل پروژه) | نصب exe از لینک + اجرای `scripts/smoke-gpu.ps1` + چسباندن JSON خروجی | ۱۰ دقیقه |
| U3 | هر وقت پرسیده شد؛ پاسخ ندادن = پیش‌فرض | تصمیم‌های محصولی (نام، لایسنس، زبان پیش‌فرض، آیکون) | اختیاری |

همه‌چیز غیر از این سه، مسئولیت ایجنت است — شامل نوشتن تست، رفع باگ، CI، مستندات، آیکون موقت، انتشار.

---

## 4. تعریف «کلاس جهانی» — چک‌لیستی که در هر مرحله اعمال می‌شود

قبل از GREEN کردن هر مرحله، هر مورد مرتبط باید پاسخ «بله» داشته باشد:

**کد**
- [ ] TypeScript strict بدون `any`/`@ts-ignore`; Python type-hinted و Ruff-clean; Rust clippy-clean
- [ ] هر خطا به کاربر با پیام فارسی قابل اقدام می‌رسد (نه stack trace)
- [ ] هر عملیات > ۵۰۰ms: نشانگر پیشرفت + قابل لغو
- [ ] هر عملیات مخرب: undo یا تأیید

**تجربه‌ی کاربری (معیار Linear/Cursor/Raycast)**
- [ ] حالت‌های خالی/بارگذاری/خطا/موفقیت طراحی شده‌اند
- [ ] انیمیشن‌ها با توکن‌های spring یکسان؛ `prefers-reduced-motion` رعایت شده
- [ ] ۶۰fps در تعامل‌های تایم‌لاین (اندازه‌گیری شده، نه حدس)
- [ ] کیبورد-محور: هر اکشن شورتکات دارد و در Command Palette هست
- [ ] RTL بی‌نقص؛ فونت فارسی بارگذاری‌شده‌ی آفلاین

**قابلیت اطمینان (Reheal)**
- [ ] لایه‌های Reheal مرتبط probe شده‌اند (§1-⑥)
- [ ] هیچ پروسه‌ی یتیم (python/ffmpeg) بعد از خروج
- [ ] لاگ ساختاریافته برای هر خطای گرفته‌شده

**کارایی روی سخت‌افزار هدف**
- [ ] بودجه: RAM < 1.5GB، VRAM < 800MB مدل‌ها، راه‌اندازی < 3s، اولین فریم پیش‌نمایش < 1s
- [ ] مسیر CPU fallback برای هر مسیر GPU

**امنیت و حریم خصوصی**
- [ ] هیچ کلید/رمزی در git، لاگ یا بسته‌ی عیب‌یابی
- [ ] مسیر فایل‌ها پاک‌سازی‌شده؛ آپلودها با محدودیت نوع/اندازه
- [ ] بدون telemetry پیش‌فرض

**قابلیت نگه‌داری**
- [ ] تست واقعی برای رفتار جدید وجود دارد و اول قرمز بوده
- [ ] مستندات کاربر/توسعه‌دهنده به‌روز
- [ ] CHANGELOG (Unreleased) به‌روز

---

## 5. قواعد استک (قفل‌شده) و شفاف‌سازی‌های لازم

استک در سند مرجع «قفل» است. موارد زیر تغییر استک نیستند بلکه **اصلاح ناسازگاری‌های واقعی** هستند که با بررسی کد کشف شد:

| مورد | سند | واقعیت کد / اکوسیستم | تصمیم |
|------|-----|----------------------|--------|
| DaisyUI 4 + Tailwind 4 | DaisyUI 4 | DaisyUI 4 پلاگین Tailwind 3 است و با Tailwind 4 کار نمی‌کند | DaisyUI **5** (نسخه‌ی رسمی برای Tailwind 4) |
| MoviePy 2.0 | `from moviepy.editor import` | این ماژول در MoviePy 2 حذف شده | FFmpeg subprocess مسیر اصلی؛ MoviePy 2 با import صحیح فقط fallback |
| Tauri `shell-open` feature | `tauri = {features=["shell-open"]}` | در Tauri 2 وجود ندارد | `tauri-plugin-shell` / `tauri-plugin-opener` |
| Turbo `pipeline` | turbo.json فعلی | Turbo 2 کلید `tasks` می‌خواهد | مهاجرت در S-008 |
| Vite 6 | در استک Build | Next.js از Vite استفاده نمی‌کند | Vite فقط برای vitest؛ بدون تغییر ابزار build |
| Ollama | حذف‌شده | — | همچنان حذف؛ فقط API ابری رایگان + Whisper/MediaPipe محلی |

هر انحراف دیگری از استک ممنوع است مگر با کارت `U3` و ثبت در `DECISIONS.md`.

---

## 6. چیدمان فایل‌های لوپ

```
docs/loop/
├── 00_INDEX.md              ← نقطه‌ی شروع هر سشن (این پوشه را معرفی می‌کند)
├── 01_STATE_OF_REPO.md      ← وضعیت واقعی ریپو در تاریخ ممیزی (نه سند خوش‌بینانه)
├── 02_LOOP_PROTOCOL.md      ← این فایل
├── 03_STEPS.md              ← ۹۸ مرحله‌ی شماره‌دار (تولیدی از steps.json)
├── 04_LEDGER.md             ← وضعیت هر مرحله (ماشین‌خوان، در CI بررسی می‌شود)
├── 05_REHEAL_MATRIX.md      ← ۷ لایه × مراحل × probeهای آشوب
├── 06_BUGS.md               ← باگ‌های شناخته‌شده + مرحله‌ی بستن هرکدام
├── 07_SESSION_HANDOFF.md    ← پرامپت آماده برای سشن بعدی AI
├── steps.json               ← منبع حقیقت مراحل
├── evidence/S-xxx/          ← شواهد (JSON smoke، اسکرین‌شات، لینک CI)
└── blockers/S-xxx.md        ← گزارش انسداد بعد از ۵ تکرار
scripts/
├── loop/render_steps.py     ← steps.json → 03_STEPS.md + ردیف‌های جدید ledger
├── verify_ledger.py         ← قواعد دفترچه (در CI)
├── gate.py                  ← اجرای مراحل static/unit/real/e2e/perf/chaos   [S-011]
└── smoke-gpu.ps1            ← تست دودی روی ماشین کاربر با خروجی JSON       [S-011]
```
