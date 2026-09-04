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

هر شماره در `03_STEPS.md` دقیقاً با این ۱۰ گام اجرا می‌شود. گام‌ها قابل حذف نیستند؛ فقط می‌توانند «N/A با دلیل مکتوب» باشند.
سه نقش وجود دارد: **Builder** (گام‌های ①–⑦ و ⑨–⑩)، **Reviewer** (گام ⑧) و **Supervisor** (خارج از گام‌ها؛ ممیزی دوره‌ای اجرای لوپ با `scripts/supervise.py` — `11_SUPERVISOR.md`) — **هرگز یک سشن/کانتکست هر دو نقش را بازی نمی‌کند** (الگوی Finn-loop: بازبین تازه، `08_FINN_LOOP_ADOPTION.md`).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  S-xxx                                                                      │
│                                                                             │
│  ① SYNC       ② CONTRACT     ③ BUILD      ④ STATIC       ⑤ TEST-REAL       │
│     │             │             │            │               │              │
│     ▼             ▼             ▼            ▼               ▼              │
│  clean tree    AC-N / NG-N   code +      biome/ruff/     pytest -m real    │
│  read ledger   test FIRST    docs        tsc/cargo       playwright        │
│  read step     (red)                     verify_ledger   artifact check    │
│                                                                             │
│  ⑥ REHEAL-CHECK  ⑦ DEBUG (≤5)   ⑧ REVIEW (fresh)   ⑨ EVIDENCE   ⑩ COMMIT   │
│     │                │               │                 │            │       │
│     ▼                ▼               ▼                 ▼            ▼       │
│  chaos probe     root-cause →    new context       ledger row    scope     │
│  touched layer   fix → back ④    verdict [AC]/     GREEN/AMBER   ledger in │
│                                  [DEFECT]/[SEC]    + artifacts   commit    │
│                                  ≤2 rounds                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ① SYNC (همگام‌سازی)
- `git fetch && git status --porcelain` — روی شاخه‌ی سشن (Arena) هستیم؛ هیچ شاخه‌ی دیگری ساخته نمی‌شود. **working tree باید تمیز باشد**؛ اگر نیست، گزارش بده و pass را تمام کن — هرگز stash/reset روی کار ناشناخته نکن.
- `python scripts/verify_ledger.py` باید سبز باشد. اگر قرمز است، **اول** آن را درست کن (بدهی از سشن قبل).
- **اول صف بازبینی:** اگر ردیفی با وضعیت `REVIEW` و verdict `changes-requested` هست، قبل از کار جدید فقط موارد Must-fix آن را درست کن (یک واحد کار در هر pass).
- مرحله‌ی بعدی = اولین ردیف `TODO`/`RED` در دفترچه که همه‌ی `deps` آن `GREEN` هستند. ترتیب شماره‌ها را نشکن مگر با دلیل مکتوب در notes.
- خواندن کارت مرحله در `03_STEPS.md` (هدف، فایل‌ها، تست واقعی، done-when).

### ② CONTRACT (قرارداد؛ تست اول)
- فایل `docs/loop/evidence/S-xxx/CONTRACT.md` را از قالب `templates/CONTRACT.md` بساز:
  - **AC-1…AC-n**: معیارهای پذیرش **مشاهده‌پذیر** (چه چیزی، با چه ابزاری، چه مقداری) — از `real_test` کارت مشتق می‌شود.
  - **NG-1…NG-n**: نا-هدف‌ها — چه چیزی عمداً در این مرحله ساخته **نمی‌شود** (الزام‌آور؛ جلوی scope creep و «refactor فرصت‌طلبانه» را می‌گیرد).
  - ریسک‌ها و لایه‌های Reheal درگیر.
- **تست واقعی را اول بنویس** و اجرا کن تا قرمز شود (اثبات این‌که تست واقعاً چیزی را می‌سنجد). هر AC حداقل یک تست دارد.
- اگر تصمیم محصولی لازم است (`U3`) و پاسخی نیست: پیش‌فرض کارت را اعمال کن، در `docs/DECISIONS.md` ثبت کن، ادامه بده. **منتظر نمان.** اگر واقعاً نمی‌توان با پیش‌فرض ادامه داد: **یک سؤال مشخص با گزینه‌ها** بنویس (هرگز «مبهم است»)، وضعیت `BLOCKED`، برو مرحله‌ی مستقل بعدی.
- قاعده‌ی Finn-loop: **اگر در CONTRACT نیست، وجود ندارد.** هیچ دستور جانبی از چت، scope را گسترش نمی‌دهد؛ فقط ویرایش CONTRACT (و در صورت نیاز `steps.json`).

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
- فقط داخل قرارداد: اصلاحی که یک `NG-N` را نقض کند ممنوع است → `[SCOPE-CONFLICT]` و `BLOCKED`.
- شمارنده‌ی `iter` در دفترچه +1.
- در تکرار ۵ اگر هنوز قرمز: وضعیت `BLOCKED`، نوشتن `docs/loop/blockers/S-xxx.md` (چه امتحان شد، فرضیه‌ها، پیشنهاد)، رفتن به مرحله‌ی بعدیِ **مستقل** (بدون وابستگی به این). فقط اگر مرحله‌ای مستقل نمانده، از کاربر بپرس.
- ممنوع: کم‌کردن سخت‌گیری تست برای سبز شدن. اگر تست اشتباه است، توضیح مکتوب در commit لازم است.

### ⑧ REVIEW (بازبین تازه — الگوی Finn-loop)
- Builder وضعیت دفترچه را `REVIEW` می‌کند، commit می‌زند و push می‌کند (بدون GREEN).
- یک **سشن/ایجنت جدید با کانتکست خالی** (یا همان ایجنت با subagent مستقل که فقط CONTRACT + diff + لاگ CI را می‌بیند) فایل `docs/loop/evidence/S-xxx/REVIEW.md` را از قالب می‌نویسد:
  - فقط در برابر CONTRACT بازبینی می‌کند: شکاف AC، نقص، جریان داده‌ی شکسته، گسترش scope، امنیت، حالت‌های loading/error، کدی که ایجنت بعدی نمی‌تواند نگه دارد.
  - هر یافته‌ی Must-fix با یکی از تگ‌ها شروع می‌شود: `[AC-N]` `[DEFECT]` `[SECURITY]` `[CI]` `[SCOPE-CONFLICT AC-N ↔ NG-N]` `[REHEAL-Lx]` `[UX]` (نقض چک‌لیست §4).
  - شواهد را **خودش دوباره تولید می‌کند** (تست‌ها را اجرا می‌کند / artifact را باز می‌کند)، نه این‌که به ادعای Builder اعتماد کند. CI قرمز یا غایب = `[CI]`.
  - Verdict: `approved` | `changes-requested` | `needs-human` (فقط برای SCOPE-CONFLICT یا تصمیم محصولی).
- `changes-requested` → Builder فقط Must-fixها را درست می‌کند → بازبین تازه‌ی دیگر. **حداکثر ۲ دور**؛ بعد `BLOCKED` + `blockers/S-xxx.md`.
- Reviewer هرگز کد push نمی‌کند و هرگز GREEN نمی‌زند؛ فقط verdict می‌نویسد.

### ⑨ EVIDENCE (شواهد)
به‌روزرسانی ردیف `04_LEDGER.md` (توسط Builder پس از `approved`):
- `status`: `GREEN` فقط اگر ⑤، ⑥ سبز، `REVIEW.md` با verdict `approved` موجود و شواهد ثبت‌شده؛ `AMBER` اگر منتظر `U1/U2`.
- `verified_on`: `ci-ubuntu`, `ci-windows`, `local-linux`, `user-gpu`.
- `evidence`: لینک CI run + مسیر artifact (junit، playwright-report، exe، smoke JSON در `docs/loop/evidence/S-xxx/`).
- `notes`: `unverified:<reason>` برای هر تست skip شده.
- اگر باگ شناخته‌شده‌ای بسته شد، `docs/loop/06_BUGS.md` به‌روز شود.

### ⑩ COMMIT + PUSH
- Conventional Commits: `feat(timeline): S-018 trim handles with ripple/roll` — شماره‌ی مرحله همیشه در پیام.
- بدنه‌ی commit (یا PR) شامل **Scope Ledger** است:
  ```
  AC-1: <evidence path / test name>       ✅
  AC-2: ...                               ✅
  NG-1: preserved — <how verified>
  Other behavior changes: None
  Reheal layers touched: L3, L7 — probes: tests/chaos/test_xxx.py
  Risk: Low | Medium | High
  ```
  اگر `Other behavior changes: None` صادق نیست، **توقف** و اول CONTRACT اصلاح شود.
- `git push origin <session-branch>`؛ CI باید سبز شود. اگر CI قرمز شد و لوکال سبز بود: **اول CI را درست کن** (محیط تمیز حقیقت است).
- بعد از هر مایلستون (S-027, S-034, …): تگ `vX.Y.0`، pre-release با exe از CI، به‌روزرسانی `CHANGELOG.md`، درخواست `U2` از کاربر با لینک مستقیم دانلود + یک خط دستور `smoke-gpu.ps1`.

---

### حالت دسته‌ای (Batch) — سرعت بدون حذف گیت
یک سشن سازنده می‌تواند چند مرحله‌ی متوالی را بسازد به شرط: (۱) هر مرحله کامیت، CONTRACT، تست واقعی و ردیف دفترچه‌ی خودش را داشته باشد؛ (۲) بعد از هر مرحله push شود؛ (۳) هیچ مرحله‌ای GREEN نشود — همه REVIEW می‌مانند تا ناظر/بازبین دسته را یک‌جا بازبینی کند؛ (۴) وابستگی به مرحله‌ای که هنوز REVIEW است مجاز است فقط اگر در همان دسته ساخته شده باشد. اگر بازبینی مرحله‌ای در دسته `changes-requested` شد، فقط همان مرحله و وابسته‌های مستقیمش برمی‌گردند، نه کل دسته. `verify_ledger` وابستگی GREEN→GREEN را همچنان در لحظه‌ی GREEN شدن اعمال می‌کند.

## 2. لوپ خارجی (مایلستون‌ها)

```
for phase in P0..P7:
    for step in phase.steps:          # لوپ داخلی بالا
        builder.run(step, stages=①..⑦)      # contract → build → real test → chaos probe
        for round in 1..2:
            verdict = fresh_reviewer.review(step)   # ⑧ — کانتکست جدید
            if verdict == approved: break
            builder.fix_must_fix_only(step)
        else: mark BLOCKED
        builder.evidence_and_commit(step)   # ⑨ ⑩
    regression: gate.py --stage all   # همه‌ی مراحل قبلی دوباره
    tag + pre-release (.exe)
    request U2 (user smoke on GTX 1650)   ← تنها نقطه‌ی دخالت الزامی کاربر
    while user smoke reports issue:
        open hotfix card S-xxx-hN → same inner loop
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
├── 07_SESSION_HANDOFF.md    ← پرامپت آماده برای سشن بعدی AI (Builder / Reviewer)
├── 08_FINN_LOOP_ADOPTION.md ← چه چیزی از Finn-loop گرفته شد و چرا
├── 09_UI_COMPONENT_PROMPT.md← پرامپت تولید کامپوننت‌های UI کلاس جهانی برای یک AI دیگر
├── templates/CONTRACT.md, REVIEW.md
├── steps.json               ← منبع حقیقت مراحل
├── evidence/S-xxx/          ← CONTRACT.md + REVIEW.md + شواهد (JSON smoke، اسکرین‌شات، لینک CI)
└── blockers/S-xxx.md        ← گزارش انسداد بعد از ۵ تکرار
scripts/
├── loop/render_steps.py     ← steps.json → 03_STEPS.md + ردیف‌های جدید ledger
├── verify_ledger.py         ← قواعد دفترچه (در CI)
├── gate.py                  ← اجرای مراحل static/unit/real/e2e/perf/chaos   [S-011]
└── smoke-gpu.ps1            ← تست دودی روی ماشین کاربر با خروجی JSON       [S-011]
```
