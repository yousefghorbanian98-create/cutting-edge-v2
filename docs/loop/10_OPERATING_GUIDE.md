# 10 — راهنمای اجرای لوپ با کمترین خطا (برای شما، نه ایجنت)

> لوپ خودش را چک می‌کند (`verify_ledger.py`، CI، بازبین تازه). بیشترین خطاها از **نحوه‌ی راه‌اندازی سشن‌ها و دستور دادن** می‌آید، نه از کد. این سند فقط همان را پوشش می‌دهد.

## A. یک‌بار برای همیشه (۱۵ دقیقه)

| # | کار | چرا |
|---|-----|-----|
| A1 | در GitHub → Settings → Actions مطمئن شوید Actions فعال است و `windows-latest` مجاز است (ریپو public است → رانرها رایگان و نامحدود) | بدون CI هیچ مرحله‌ای GREEN نمی‌شود |
| A2 | Settings → Branches → قانون برای `main`: Require PR + Require status checks `ci / ubuntu` و `ci / windows` (بعد از S-009 که این جاب‌ها ساخته می‌شوند) | جلوی merge کد قرمز به main |
| A3 | کلید OpenRouter را بسازید ولی **به ایجنت ندهید**؛ فقط در `ai-engine/.env` روی ماشین خودتان یا بعداً در Settings برنامه (S-086) | امنیت — U1 |
| A4 | روی ویندوز: PowerShell 7، Git، و درایور Nvidia با CUDA 11.8 آماده باشد | برای `smoke-gpu.ps1` در مایلستون‌ها — U2 |
| A5 | این پیام را جایی ذخیره کنید (پرامپت شروع سشن؛ بخش C) | هر سشن دقیقاً همین را می‌فرستید |

## B0. حالت ساده (پیش‌فرض): فقط دو چت

```
چت ۱ = ناظر + بازبین (ثابت، همیشه باز)
چت ۲ = سازنده‌ی دسته‌ای — برای هر فاز (یا تا جایی که کانتکست اجازه دهد) یک چت جدید از شاخه‌ی ناظر
```
کاربر فقط: چت ۲ را می‌سازد → پرامپت BUILDER را می‌فرستد → جواب آخر را به چت ۱ می‌آورد و می‌نویسد «چک کن».
ناظر ممیزی + بازبینی را انجام می‌دهد و پیام بعدی چت ۲ را می‌دهد.

## B. حالت کامل: یک سشن = یک نقش = یک مرحله

```
Builder session  →  S-xxx  →  push  →  status REVIEW
Reviewer session →  S-xxx  →  REVIEW.md (approved / changes-requested)
Builder session  →  (fix must-fix if any) → GREEN → S-(xxx+1)
```

- **Builder و Reviewer هرگز یک چت نباشند.** یک چت جدید (ترجیحاً مدل دیگر) برای Reviewer باز کنید. این تنها چیزی است که «خود-تأییدی» را می‌شکند.
- در یک چت بیش از ۲–۳ مرحله جلو نروید؛ کانتکست طولانی = خطای بیشتر. مرحله‌ی جدید، چت جدید.
- هیچ‌وقت وسط مرحله «راستی این را هم اضافه کن» نگویید. اگر ایده دارید بگویید: «این را به‌عنوان کارت جدید در `steps.json` اضافه کن، الان اجرا نکن.»

## C. پیام‌های آماده (کپی کنید)

**اول هر سشن (تأیید جای درست):**
```
Run and paste raw output: git fetch --unshallow origin 2>/dev/null || git fetch --deepen=200 origin;
git remote get-url origin; git rev-parse --abbrev-ref HEAD; git log --oneline -3;
git merge-base --is-ancestor <SUPERVISOR_HEAD_SHA> HEAD && echo BASE_OK || echo BASE_WRONG; git status --porcelain | wc -l
Do not start any step until I confirm.
```
(SHA را ناظر می‌دهد. `BASE_WRONG` = سشن از main ساخته شده → ببندید و از شاخه‌ی ناظر بسازید.)

**شروع سشن Builder (پیش‌فرض):**
```
Role: BUILDER. Read docs/loop/07_SESSION_HANDOFF.md and follow it exactly.
Run python scripts/verify_ledger.py first. Work only the next eligible step in docs/loop/04_LEDGER.md
(or the oldest step in REVIEW with changes-requested). Stop after that one step is pushed with status REVIEW.
Do not ask me anything except U1/U2/U3 as defined; apply defaults on U3.
```

**شروع سشن Reviewer (چت جدید):**
```
Role: FRESH REVIEWER for step S-xxx. Use the reviewer prompt in docs/loop/07_SESSION_HANDOFF.md.
Re-run the tests and open the artifacts yourself; do not trust the builder's claims.
Write docs/loop/evidence/S-xxx/REVIEW.md and commit only that file. Never push code, never mark GREEN.
```

**وقتی ایجنت گیر کرد یا سؤال بی‌مورد پرسید:**
```
Apply the card's default and continue. If you truly cannot, mark BLOCKED with one concrete question
with options in docs/loop/blockers/S-xxx.md and move to the next independent step.
```

**پایان مایلستون (وقتی ایجنت لینک exe داد):**
نصب → `pwsh scripts/smoke-gpu.ps1` → JSON خروجی را عیناً paste کنید و بنویسید:
```
U2 result for S-xxx attached. Record it under docs/loop/evidence/S-xxx/ and update the ledger.
```

## D. چک ۶۰ ثانیه‌ای بعد از هر سشن (تنها نظارت لازم شما)

1. `git log --oneline -3` — پیام commit شماره‌ی مرحله دارد؟ بدنه Scope Ledger دارد؟
2. `04_LEDGER.md` — فقط **یک** ردیف تغییر کرده؟ اگر چند ردیف یک‌باره GREEN شد، مشکوک است.
3. CI روی شاخه سبز است؟ (تب Actions) — اگر قرمز و ایجنت گفته «لوکال سبز بود»: در سشن بعدی اول همان را بدهید.
4. `docs/loop/evidence/S-xxx/` سه چیز دارد؟ `CONTRACT.md`، `REVIEW.md`، حداقل یک artifact (junit/اسکرین‌شات/لینک).
5. `verify_ledger.py` خط `WATCHDOG:` چاپ کرده؟ یعنی مرحله‌ای ۳+ تکرار خورده — سشن بعد را با Reviewer شروع کنید نه Builder.

اگر هر ۵ مورد درست بود، هیچ کار دیگری ندارید.

## E. نشانه‌های انحراف (فوراً متوقف کنید)

| نشانه | معنی | واکنش |
|-------|------|-------|
| ایجنت تستی را «ساده‌تر» کرد تا سبز شود | نقض قانون ⑦ | revert + «restore the original assertion; fix the code, not the test» |
| GREEN بدون `REVIEW.md` | verify_ledger باید رد می‌کرد → کسی آن را دور زده | `python scripts/verify_ledger.py` را خودتان اجرا کنید؛ اگر پاس شد، اسکریپت دستکاری شده — `git diff scripts/` |
| کتابخانه‌ی جدید خارج از استک (مثلاً Redux، MUI، Electron) | نقض §5 پروتکل | revert؛ «locked stack — see 02_LOOP_PROTOCOL §5» |
| فایل بزرگ (mp4، مدل، exe) در git | نقض ignore | «remove from git, add to .gitignore, use CI artifacts/Release assets» |
| ایجنت چند مرحله را در یک commit زد | کانتکست پرشده | چت را ببندید؛ سشن جدید با Reviewer برای همان commit |
| «به‌جای CI روی لوکال تست کردم» برای ویندوز/Tauri | CI حقیقت است | «CI windows job must be green; local is not evidence» |
| کلید API در chat یا فایل | امنیت | کلید را revoke کنید؛ `gitleaks` در S-008 این را می‌گیرد |

## F. کجاها واقعاً به شما نیاز است (و بس)

| زمان | مرحله | کار شما |
|------|-------|---------|
| قبل از S-053 | U1 | کلید OpenRouter در `.env` محلی |
| S-027, S-034, S-057, S-067, S-078, S-090, S-097 | U2 | نصب exe + `smoke-gpu.ps1` + paste JSON (~۱۰ دقیقه × ۷) |
| S-090 | U2 طولانی | ۷ روز استفاده‌ی واقعی و ثبت اشکالات به‌صورت لیست ساده |
| هر وقت پرسیده شد | U3 | یک کلمه جواب یا سکوت (= پیش‌فرض) |
| A2 | یک‌بار | Branch protection بعد از S-009 |

## G. ترتیب پیشنهادی هفته‌ی اول

1. سشن ۱ (Builder): S-001 → S-002 (کوچک‌اند؛ دو مرحله در یک سشن قابل قبول است).
2. سشن ۲ (Reviewer): بازبینی S-001 و S-002.
3. سشن ۳ (Builder): GREEN کردن آن دو + S-003.
4. از اینجا به بعد یک‌مرحله‌ای. تا پایان **S-011** لوپ ابزارهای خودش (`gate.py`, `smoke-gpu.ps1`) را دارد و خطای انسانی به حداقل می‌رسد.
5. **S-010** اولین exe را می‌دهد — همان‌جا یک‌بار نصب امتحانی کنید تا مسیر U2 را قبل از مایلستون واقعی تمرین کرده باشید.
