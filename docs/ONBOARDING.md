# راهنمای ورود مهندس جدید — Cutting Edge v2

> این سند برای کسی است که **هیچ چیزی** از این پروژه نمی‌داند و باید (الف) بفهمد چیست، (ب) بفهمد کجای تولید هستیم، (پ) آنچه ساخته شده را بازرسی کند، (ت) ادامه دهد.
> تاریخ: ۲۰۲۶-۰۹-۰۸ · شاخهٔ مرجع: `arena/01a0c936-cutting-edge-v2` · آخرین کامیت ناظر: `c9f90d0`
>
> همهٔ لینک‌ها به همین شاخه روی GitHub اشاره می‌کنند:
> `https://github.com/yousefghorbanian98-create/cutting-edge-v2/tree/arena/01a0c936-cutting-edge-v2`

---

## ۱. این برنامه چیست؟

**Cutting Edge v2** یک ویرایشگر ویدیوی دسکتاپ برای ویندوز است که برای تولیدکنندگان محتوای ورزشی/بدن‌سازی ساخته می‌شود. رابط کاربری **فارسی‌اول (راست‌به‌چپ)** با انگلیسی به‌عنوان زبان دوم. باید **آفلاین** کار کند (به‌جز چند قابلیت هوش مصنوعی ابری رایگان) و روی سخت‌افزار متوسط اجرا شود.

### سه ماژول محصول (۱۶ قابلیت مصوب)
| ماژول | قابلیت‌ها |
|---|---|
| **ویرایشگر هوشمند** (۵) | Beat Sync (برش روی ضرب موسیقی)، Living Timeline (نقشهٔ حرارتی انرژی/احساس)، Emotion Color (LUT خودکار)، One-Click Viral Cut (برش عمودی ۹:۱۶ با ردیابی سوژه)، Voice Command (فرمان صوتی فارسی/انگلیسی) |
| **Style Match** (۵) | Mood DNA، مقایسهٔ سبک دو ویدیو، Pose-to-Pose، Transition Intelligence، پیش‌نمایش زندهٔ سبک (WebGL) |
| **دستیار هوشمند** (۵) | Multi-Modal Brain (چت با زمینهٔ فریم/ترنسکریپت/تایم‌لاین)، Auto-Narrator (گویندهٔ خودکار)، Proactive Coach، Workout Form Analyzer (شمارش تکرار و زاویهٔ مفاصل)، Content Strategy |
| **Muscle Enhancer** (۱) | بهبود **۱۰۰٪ طبیعی** نمای عضلات (نور/کنتراست/وضوح محلی) — بدون تغییر شکل بدن. با محافظت صورت |

### استک فنی (قفل‌شده — تغییر ممنوع)
```
Desktop shell : Tauri 2 (Rust)
Frontend      : Next.js 15 (static export) · React 19 · TypeScript 5.5 strict · Tailwind 4 + DaisyUI 5 · Framer Motion 11 · Zustand 5
AI backend    : Python 3.11 · FastAPI · MediaPipe · OpenCV · MoviePy 2 · librosa · faster-whisper small · edge-tts
Cloud AI      : OpenRouter (فقط مدل‌های :free) + Nvidia NIM — بودجه صفر دلار
Packaging     : PyInstaller sidecar داخل Tauri · نصب‌کنندهٔ NSIS (.exe) · آپدیتر از GitHub Releases
Tooling       : Turborepo + pnpm · Vitest / Playwright / pytest · Biome / Ruff · GitHub Actions
```
سخت‌افزار هدف: ۱۶ گیگ RAM، GTX 1650 با ۴ گیگ VRAM، CUDA 11.8. بودجه: RAM اپ < ۱.۵ گیگ، VRAM مدل‌ها < ۸۰۰ مگ.

هدف نهایی: **انتشار نصب‌کنندهٔ ویندوز v1.0 روی GitHub Release** (فایل exe + SHA256 + فایل آپدیتر).

---

## ۲. مدل تولید: چگونه ساخته می‌شود؟

پروژه ۱۰۰٪ توسط ایجنت‌های هوش مصنوعی در Arena ساخته می‌شود؛ انسان فقط سه دخالت دارد (کلید API، تست روی ویندوز/GPU در پایان هر مایلستون، تصمیم‌های محصولی اختیاری).

### دو نقش، دو چت
| نقش | چت/شاخه | کار |
|---|---|---|
| **ناظر (Supervisor)** | چت ثابت، شاخهٔ `arena/01a0c936-cutting-edge-v2` | ممیزی با ۱۶ چک خودکار، بازبینی مستقل هر مرحله (تست‌ها را خودش دوباره اجرا می‌کند)، ادغام شاخهٔ سازنده، به‌روزرسانی لوپ |
| **سازنده (Builder)** | چت دسته‌ای، شاخهٔ خودش `arena/<id>-cutting-edge-v2` | ساخت مراحل شماره‌دار به ترتیب دفترچه، هر مرحله: قرارداد → تست واقعی قرمز → کد → گیت ایستا → تست → کامیت با Scope Ledger → push |

### لوپ ۱۰ گامی هر مرحله
```
① SYNC (تمیز بودن درخت، گیت پوش، خواندن درس‌ها)
② CONTRACT (AC-n معیارهای پذیرش / NG-n نا-هدف‌ها؛ تست واقعی اول نوشته و قرمز می‌شود)
③ BUILD
④ STATIC (Biome, tsc, Ruff, gitleaks, verify_ledger, چک توکن‌های طراحی، ممیزی UI)
⑤ TEST-REAL (سرور زندهٔ uvicorn + مدیای واقعی FFmpeg‌ساز؛ Playwright واقعی؛ نه mock)
⑥ REHEAL-CHECK (probe آشوب برای لایه‌های خودترمیمی)
⑦ DEBUG-LOOP (حداکثر ۵ تکرار؛ سپس BLOCKED)
⑧ REVIEW (بازبین تازه = ناظر؛ حداکثر ۲ دور)
⑨ EVIDENCE (ردیف دفترچه: GREEN فقط با شواهد)
⑩ COMMIT + PUSH + فایل درس (learnings)
```
قاعدهٔ طلایی: **اگر در CONTRACT نیست، وجود ندارد.** تست ضعیف‌کردن برای سبز شدن ممنوع. Skip ≠ Pass.

### وضعیت‌های دفترچه
`TODO → RED → REVIEW → GREEN` (یا `AMBER` منتظر کاربر، `BLOCKED` با دلیل). فقط ناظر می‌تواند با verdict «approved» اجازهٔ GREEN بدهد؛ اسکریپت `verify_ledger.py` این را مکانیکی چک می‌کند (GREEN بدون REVIEW.md تأییدشده = خطا).

---

## ۳. کجای تولید هستیم؟ (وضعیت واقعی، نه ادعا)

### نقشهٔ راه: ۸ فاز، ۱۰۱ مرحلهٔ شماره‌دار
```
P0 Foundation Repair   S-001…S-012 + S-099…S-101   v0.2.1   ← اینجا هستیم
P1 Timeline Real       S-013…S-027                 v0.3.0
P2 Export Pipeline     S-028…S-034                 v0.4.0
P3 AI Full Integration S-035…S-057                 v0.5.0   ← هر ۱۶ قابلیت
P4 Tauri Desktop       S-058…S-067                 v0.6.0   ← اولین نصب‌کنندهٔ قابل نصب
P5 Project & Stability S-068…S-078                 v0.7.0   ← ۷ لایهٔ Reheal + تست آشوب
P6 Testing & Polish    S-079…S-090                 v0.8.0   ← RC1
P7 Release             S-091…S-098                 v1.0.0
```

### پیشرفت: ۶ از ۱۰۱ مرحله GREEN (≈ ۶٪ از مسیر شماره‌دار)
| مرحله | عنوان | وضعیت | چه چیزی واقعاً ساخته شد |
|---|---|---|---|
| S-001 | هایجین ریپو | GREEN | LICENSE (MIT)، .editorconfig، حذف اسکریپت‌های ژنراتور |
| S-002 | بوت بک‌اند | GREEN | پکیج `ai_engine`، dotenv، اسکریپت‌های dev، تست بوت زنده |
| S-003 | امنیت آپلود/دانلود | GREEN | `core/storage.py`: نام UUID، allow-list پسوند (۴۱۵)، سقف حجم (۴۱۳)، ضد traversal (۴۰۴)، CORS محدود |
| S-004 | MoviePy 2 + FFmpeg-first | GREEN | `core/ffmpeg.py`؛ Beat Sync روی MP4 واقعی BPM ≈ 120 می‌دهد؛ باگ‌های ۱ و ۴ بسته |
| S-005 | کارخانهٔ فیکسچر واقعی | GREEN | ۸ ویدیوی تستی با FFmpeg در زمان تست ساخته می‌شوند (هیچ مدیایی کامیت نمی‌شود) |
| S-006 | هارنس تست زنده | GREEN | `live_api` (uvicorn واقعی روی پورت آزاد)، `assert_playable`، `frame_diff`، `ssim_region` |
| S-007 | استایل فرانت (Tailwind 4 + DaisyUI 5 + فونت آفلاین) | GREEN (local-linux + ci-ubuntu) | CSS ۶۴ کیلوبایتی؛ تست مرورگری `styling.spec.ts` ۷/۷ در CI سبز (run 35673944671) |
| S-008 | ابزارها (Biome/Ruff/tsc/Turbo 2/lefthook/gate.py) | GREEN | ساخته‌شده در جلسهٔ ناظر (۲۲ سپتامبر ۲۰۲۶)؛ `scripts/gate.py --stage static` با ۱۳ چک؛ شواهد در `docs/loop/evidence/S-008/` |
| S-009 | CI سه‌جابه (ubuntu / windows / loop-audit) با اکشن‌های SHA-pin، آرتیفکت شواهد، CodeQL/Dependabot/gitleaks | GREEN (ci-ubuntu; ci-windows) | ۴ اجرا تا سبز شدن؛ درس‌ها در `docs/learnings/2026-09-22-ci-*.md`؛ شکست‌ها بدون توکن از annotation خوانده می‌شوند |
| S-101 | ADR 0001…0009 + validator مشترک ADR/learnings | GREEN | `scripts/loop/hygiene.py`؛ ناظر C13 حالا FAIL می‌دهد اگر سشنی درس ننویسد |
| S-099 | DESIGN.md مرجع واحد + چک سه‌طرفهٔ توکن + AGENTS.md و فایل‌های هارنس نازک | GREEN | `check-design-tokens.js` در gate و C14؛ ADR-0010؛ `tests/unit/test_agent_docs.py` |
| S-100 | چک‌کنندهٔ آفلاین Web Interface Guidelines (`design_audit.py`, ۸ قاعده) در gate | GREEN | ۱۷ یافتهٔ واقعی UI همان‌جا رفع شد؛ `pnpm design:audit`؛ فقط یک ignore دلیل‌دار (S-084) |
| S-010 | Tauri skeleton + اولین `.exe` | REVIEW (CI سبز، منتظر Overseer) | run 35711041909؛ نصاب در artifact `cutting-edge-windows-x64-setup` |
| S-011 … S-012 | ابزار لوپ، job model | TODO | ترتیب: S-011 → S-012 |

مجموعهٔ تست فعلی (CI run 35711041909): **ubuntu ۶۵ unit + ۱۵ Playwright، windows ۹۲ pytest با مدیای واقعی + cargo fmt/clippy/test + `tauri build` + smoke نصاب ۱۷/۱۷** — همه سبز؛ تنها skip: `cargo-clippy` خارج از ویندوز (مالک: جاب windows).

### آنچه از قبل در کد هست ولی هنوز «ادعا» است (بازرسی لازم)
پوشه‌های `ai-engine/src/{analyzer,assistant,captioner,editor_ai,muscle,reheal,style_match}` ماژول‌های اولیهٔ ۱۶ قابلیت را دارند اما فقط Beat Sync و Muscle Enhancer با تست واقعی سنجیده شده‌اند. ممیزی صادقانهٔ وضعیت اولیه (پیشرفت واقعی ۱۲–۱۵٪ در برابر ادعای ۳۰–۳۵٪) در `docs/loop/01_STATE_OF_REPO.md` است. فرانت‌اند فعلاً یک صفحهٔ نمایشی است (`page.tsx`)؛ تایم‌لاین واقعی در P1 ساخته می‌شود. پوشهٔ `src-tauri` از S-010 روی `ci / windows` کامپایل و به نصاب NSIS تبدیل می‌شود (`Cargo.lock` هنوز commit نشده — BUG-17).

### باگ‌های شناخته‌شده
۱۵ باگ در `docs/loop/06_BUGS.md`؛ ۲ تا بسته (BUG-1، BUG-4)، بقیه به مراحل مشخص ارجاع دارند و هرکدام «تست اثبات» تعریف‌شده دارد.

---

## ۴. نقشهٔ فایل‌ها (چه چیزی کجاست و چرا)

پیشوند همهٔ لینک‌ها:
`https://github.com/yousefghorbanian98-create/cutting-edge-v2/blob/arena/01a0c936-cutting-edge-v2/`

### نقطه‌های ورود (به ترتیب خواندن)
| فایل | چیست |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | دفترچهٔ عملیاتی هر ایجنت/مهندس: محصول چیست و چه چیزی **نیست**، استک قفل، قواعد UI، امنیت، نقش‌ها |
| [`docs/loop/00_INDEX.md`](loop/00_INDEX.md) | فهرست لوپ تحویل و دستورات روزمره |
| [`docs/loop/01_STATE_OF_REPO.md`](loop/01_STATE_OF_REPO.md) | ممیزی واقعی کد اولیه — به اسناد خوش‌بینانهٔ قدیمی اعتماد نکنید |
| [`docs/loop/02_LOOP_PROTOCOL.md`](loop/02_LOOP_PROTOCOL.md) | لوپ ۱۰ گامی، تعریف «تست واقعی»، چک‌لیست کلاس جهانی، قواعد استک |
| [`docs/loop/03_STEPS.md`](loop/03_STEPS.md) | ۱۰۱ کارت مرحله (تولیدشده از `steps.json` — دستی ویرایش نکنید) |
| [`docs/loop/04_LEDGER.md`](loop/04_LEDGER.md) | **دفترچهٔ وضعیت** — منبع حقیقتِ «کجا هستیم»؛ ماشین‌خوان |
| [`docs/loop/steps.json`](loop/steps.json) | منبع حقیقت مراحل؛ بعد از ویرایش: `python scripts/loop/render_steps.py` |

### اسناد تکمیلی لوپ
| فایل | چیست |
|---|---|
| [`05_REHEAL_MATRIX.md`](loop/05_REHEAL_MATRIX.md) | ۷ لایهٔ خودترمیمی × مرحلهٔ ساخت × probe آشوب |
| [`06_BUGS.md`](loop/06_BUGS.md) | باگ‌های شناخته‌شده با تست اثبات |
| [`07_SESSION_HANDOFF.md`](loop/07_SESSION_HANDOFF.md) | پرامپت‌های آمادهٔ سازنده (BATCH BUILDER) و بازبین |
| [`08_FINN_LOOP_ADOPTION.md`](loop/08_FINN_LOOP_ADOPTION.md) | چه چیزی از الگوی Finn-loop گرفتیم (بازبین تازه، AC/NG، Scope Ledger) |
| [`09_UI_COMPONENT_PROMPT.md`](loop/09_UI_COMPONENT_PROMPT.md) | پرامپت تولید کامپوننت UI کلاس جهانی |
| [`10_OPERATING_GUIDE.md`](loop/10_OPERATING_GUIDE.md) | راهنمای اپراتور انسانی: دو چت، پیام «Sync and continue»، انقضای توکن |
| [`11_SUPERVISOR.md`](loop/11_SUPERVISOR.md) | نقش ناظر، ۱۶ چک، حلقهٔ improve |
| [`12_SIXTEEN_LAYER_MAP.md`](loop/12_SIXTEEN_LAYER_MAP.md) | نگاشت نقشهٔ ۱۶ لایهٔ تولید روی این محصول |
| [`13_INTEGRATIONS_ADOPTION.md`](loop/13_INTEGRATIONS_ADOPTION.md) | سه ادغام (ECC، Web Interface Guidelines، awesome-design-md): پذیرفته/رد/گیت |
| [`evidence/`](loop/evidence/) | هر مرحله: `CONTRACT.md` + `REVIEW.md` (+ artifacts)؛ `SESSIONS.md` لاگ سشن‌ها؛ `SUPERVISOR/` گزارش‌های ممیزی |
| [`templates/`](loop/templates/) | قالب CONTRACT و REVIEW |

### اسناد مرجع و تصمیم‌ها
| فایل | چیست |
|---|---|
| [`DESIGN.md`](../DESIGN.md) | **مرجع بصری واحد** (S-099, ADR-0010): بلوک‌های `# tokens:` با `node scripts/check-design-tokens.js` سه‌طرفه با `globals.css` و `tokens.ts` مقایسه می‌شوند (۲۷ + ۱۹ توکن، drift = خطای gate) |
| [`docs/adr/`](adr/) | تصمیم‌های معماری (ADR-0001…0009، قالب MADR کوتاه، انگلیسی)؛ ADR جدید = کپی `TEMPLATE.md` + یک ردیف در `README.md`؛ اعتبارسنجی با `python scripts/loop/hygiene.py` |
| [`docs/learnings/`](learnings/) | درس‌های هر سشن (≤ ۲۰ خط: چه شکست / ریشه / قاعده) — قبل از تکرار اشتباه بخوانید؛ همان validator بررسی‌شان می‌کند و ناظر (C13) نبودشان را FAIL می‌کند |
| [`docs/DECISIONS.md`](DECISIONS.md) | تصمیم‌های محصولی (U3) و پیش‌فرض‌ها |
| [`docs/16-LAYER-PRODUCTION-PLAN.md`](16-LAYER-PRODUCTION-PLAN.md) | ورودی مرجع (نقشهٔ عمومی؛ استکش با این پروژه فرق دارد) |
| [`docs/ROADMAP-v2-WITH-INTEGRATIONS.md`](ROADMAP-v2-WITH-INTEGRATIONS.md) | ورودی مرجع (پیشنهاد سه ادغام) |
| [`docs/integrations/`](integrations/) | snapshot قوانین Vercel Web Interface Guidelines و توضیح ECC |

### کد
| مسیر | چیست | وضعیت |
|---|---|---|
| [`ai-engine/src/main.py`](../ai-engine/src/main.py) | FastAPI: `/health`, `/ai/chat`, `/editor/beat-sync`, `/editor/viral-cut`, `/mood-dna`, `/muscle/enhance`, `/muscle/download/{f}`, `/editor/voice-command`, `/style-match/compare` | امن‌شده (S-003)؛ هنوز بلاک‌کننده (S-012) |
| [`ai-engine/src/core/storage.py`](../ai-engine/src/core/storage.py) | تنها نقطهٔ دسترسی به دیسک برای آپلود/دانلود | GREEN، بازرسی‌شده با probe‌های traversal |
| [`ai-engine/src/core/ffmpeg.py`](../ai-engine/src/core/ffmpeg.py) | کشف باینری FFmpeg (env → PATH → imageio-ffmpeg)، استخراج صدا، probe | GREEN |
| [`ai-engine/src/editor_ai/beat_sync.py`](../ai-engine/src/editor_ai/beat_sync.py) | تشخیص ضرب با librosa روی WAV استخراج‌شده | GREEN |
| [`ai-engine/src/muscle/muscle_enhancer.py`](../ai-engine/src/muscle/muscle_enhancer.py) | Muscle Enhancer با OpenCV؛ محافظت صورت ۳۶ نقطه‌ای | کار می‌کند؛ باگ ۳ و ۱۲ باز (S-035, S-037) |
| `ai-engine/src/{analyzer,assistant,captioner,style_match,reheal}` | ماژول‌های اولیهٔ قابلیت‌ها و لایه‌های Reheal | **تست‌نشده؛ بازرسی لازم** (P3, P5) |
| [`ai-engine/pyproject.toml`](../ai-engine/pyproject.toml) / `requirements.txt` | پکیج `ai_engine`، نسخه‌های پین‌شده | GREEN |
| [`apps/desktop/src/app/`](../apps/desktop/src/app/) | `layout.tsx` (fa/rtl)، `globals.css` (Tailwind 4 `@theme` + DaisyUI 5 + فونت آفلاین)، `page.tsx` (صفحهٔ نمایشی) | S-007 |
| [`apps/desktop/src/stores/`](../apps/desktop/src/stores/) | Zustand: `editorStore.ts`, `rehealStore.ts` | اولیه |
| [`apps/desktop/tests/`](../apps/desktop/tests/) | Playwright: `build-artifacts.spec.ts` (۸ تست، سبز)، `styling.spec.ts` (نیاز به مرورگر → CI) | S-007 |
| [`apps/desktop/src-tauri/`](../apps/desktop/src-tauri/) | پوستهٔ Tauri 2 (`lib.rs` + `main.rs`، آیکون‌های تولیدی، `nsis/Farsi.nsh`) | کامپایل و بسته‌بندی فقط روی `ci / windows` (S-010) |
| [`packages/design-system/tokens.ts`](../packages/design-system/tokens.ts) | توکن‌های طراحی (آینهٔ `@theme`) | GREEN |
| [`tests/`](../tests/) | `conftest.py` (فیکسچرها + `live_api`)، `fixtures/make_fixtures.py`، `helpers/media.py`، `test_security.py`، `test_beat_sync.py`، `test_fixtures.py`، `test_api_live.py`، `real/test_backend_boot.py`، `unit/test_repo_hygiene.py` | ۳۲ تست سبز |
| [`scripts/`](../scripts/) | `verify_ledger.py` (سلامت دفترچه)، `supervise.py` (۱۶ چک ناظر)، `loop/render_steps.py`، `dev-backend.{sh,ps1}`، `check-design-tokens.js` (چک سه‌طرفهٔ توکن‌ها، S-099)، `loop/hygiene.py` (ADR/learnings)، `ci/junit_annotate.py` | — |
| [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | CI سه‌جابه (S-009): `ubuntu` (gate + unit + build + Playwright)، `windows` (pytest مدیای واقعی + cargo advisory)، `loop-audit` (ledger + supervisor)؛ `codeql.yml`، `dependabot.yml` | GREEN |

---

## ۵. چگونه در ۳۰ دقیقه آنچه هست را بازرسی کنید

```bash
# 1) کلون و شاخهٔ درست
git clone https://github.com/yousefghorbanian98-create/cutting-edge-v2.git
cd cutting-edge-v2
git checkout arena/01a0c936-cutting-edge-v2
git log --oneline -1          # باید c9f90d0 یا جدیدتر باشد

# 2) سلامت دفترچه و ممیزی ناظر (بدون وابستگی)
python3 scripts/verify_ledger.py          # انتظار: ledger OK — 6/101 GREEN
python3 scripts/supervise.py              # ۱۶ چک؛ verdict OK/ATTENTION/STOP

# 3) بک‌اند + کل تست‌های واقعی (≈ ۳ دقیقه؛ فیکسچرها با imageio-ffmpeg ساخته می‌شوند)
cd ai-engine && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && pip install -e . && cd ..
python -m pytest -q                       # انتظار: 32 passed, 0 skipped

# 4) فرانت‌اند
cd apps/desktop && npm install && npx next build     # انتظار: out/_next/static/css/*.css ≈ 64 KB
npx playwright test tests/build-artifacts.spec.ts    # انتظار: 8 passed
```

### چه چیزهایی را باید با شک بررسی کنید
1. **هر مرحلهٔ GREEN** باید سه چیز داشته باشد: `evidence/S-xxx/CONTRACT.md`، `evidence/S-xxx/REVIEW.md` با verdict `approved`، و تستی که در کامیت مرحله اول قرمز بوده. `verify_ledger.py` این را مکانیکی چک می‌کند؛ شما محتوایش را بخوانید.
2. **ادعاهای ماژول‌های تست‌نشده** در `ai-engine/src` (style_match، assistant، captioner، reheal): تا وقتی مرحلهٔ مربوطه در P3/P5 با تست واقعی سبز نشده، «ساخته‌شده» محسوب نمی‌شوند.
3. **DESIGN.md مرجع است** (S-099). تغییر هر توکن = یک کامیت که هر سه فایل (`DESIGN.md`، `globals.css`، `tokens.ts`) را با هم عوض می‌کند؛ در غیر این صورت gate نام متغیر و دو مقدار را چاپ می‌کند و CI قرمز می‌شود.
4. **S-008 روی GitHub است** (بازسازی‌شده در شاخهٔ ناظر). قبل از هر کامیت `pnpm install` و سپس `pnpm lefthook install` را اجرا کنید تا هوک‌های pre-commit/commit-msg فعال شوند؛ `pnpm gate:static` همان چیزی است که CI اجرا می‌کند.
5. **CI فعال است** (S-009). هر push به `arena/**` سه جاب را اجرا می‌کند؛ GREEN شدن مرحله‌ای که AC وابسته به محیط دارد باید لینک run سبز را در EVIDENCE بیاورد. اگر لاگ/آرتیفکت با توکن قابل دانلود نبود: annotation‌های عمومی check-run را بخوانید (`gh api repos/…/check-runs/<job>/annotations`) یا URL امضاشدهٔ `gh api …/actions/jobs/<id>/logs` را با ابزار fetch باز کنید. شواهد جاب windows بدون توکن هم خواندنی‌اند: annotationهای `installer smoke`، `installer` (sha256) و `Cargo.lock` (S-010).

---

## ۶. چگونه ادامه دهید

### اگر با ایجنت در Arena ادامه می‌دهید
1. چت جدید روی مخزن، شاخهٔ مبدأ `arena/01a0c936-cutting-edge-v2`.
2. پرامپت «BATCH BUILDER» را از `docs/loop/07_SESSION_HANDOFF.md` بفرستید؛ جای `<SUPERVISOR_HEAD>` سر فعلی شاخهٔ ناظر و جای `<FROM>–<TO>` مثلاً `S-008` تا `S-012`.
3. گزارش پایانی سازنده را به چت ناظر ببرید و بنویسید «چک کن». ناظر ادغام، بازبینی و پیام بعدی را می‌دهد. جزئیات در `10_OPERATING_GUIDE.md`.

### اگر خودتان (انسان) ادامه می‌دهید
همان لوپ را اجرا کنید؛ چیزی در آن مخصوص ایجنت نیست:
1. `04_LEDGER.md` → اولین `TODO` که وابستگی‌هایش GREEN است (ترتیب توصیه‌شدهٔ P0: S-011 → S-012؛ S-010 منتظر Overseer).
2. کارت مرحله در `03_STEPS.md` را بخوانید؛ `evidence/S-xxx/CONTRACT.md` را از قالب بنویسید (AC/NG).
3. تست واقعی اول (قرمز)، بعد کد، بعد گیت‌ها، کامیت با Scope Ledger در بدنه، push، وضعیت `REVIEW`.
4. یک نفر دیگر (یا چت ناظر) `REVIEW.md` می‌نویسد؛ فقط بعد از `approved` وضعیت `GREEN` با `verified_on` و `evidence`.
5. پایان هر سشن: یک فایل در `docs/learnings/`.

### دخالت‌های انسانی برنامه‌ریزی‌شده
- **U1** یک‌بار: کلید OpenRouter در `ai-engine/.env` (هرگز در git) — قبل از S-053.
- **U2** ۸ بار: پایان هر مایلستون، نصب exe روی ویندوز واقعی + اجرای `scripts/smoke-gpu.ps1` (از S-011) و چسباندن JSON.
- **U3** اختیاری: نام محصول، آیکون، زبان پیش‌فرض، فرمت‌ها — سکوت = پیش‌فرض ثبت‌شده در `docs/DECISIONS.md`.

---

## ۷. خلاصهٔ یک‌پاراگرافی برای مدیر
ویرایشگر ویدیوی دسکتاپ فارسی با ۱۶ قابلیت هوش مصنوعی برای محتوای ورزشی؛ استک Tauri + Next.js + FastAPI؛ بودجه صفر؛ ساخت کاملاً توسط ایجنت با یک لوپ ۱۰ گامی مستند و ۱۰۱ مرحلهٔ شماره‌دار تا انتشار نصب‌کنندهٔ ویندوز v1.0. امروز: پایه‌های ریپو تعمیر شده (۶ مرحله سبز، ۳۲ تست واقعی سبز، امنیت آپلود بسته، استایل فرانت برقرار)، CI و پوستهٔ Tauri هنوز ساخته نشده، و ماژول‌های AI به‌جز Beat Sync و Muscle Enhancer هنوز تست واقعی ندارند. مسیر باقی‌مانده کاملاً در دفترچه است؛ هیچ‌چیز به حافظهٔ افراد وابسته نیست.
