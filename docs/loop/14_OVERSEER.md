# 14 — Overseer (نشست ناظر مستقل — چت دوم)

> از ۲۲ سپتامبر ۲۰۲۶ نقش «ناظر + بازبین تازه» از چت سازنده جدا می‌شود و به یک **چت دوم** در Arena می‌رود.
> دلیل: تا این تاریخ، سازنده خودش `REVIEW.md` را می‌نوشت (بازبین = سازنده) — شرط اصلی Finn-loop
> («بازبین هرگز همان کسی نیست که ساخته») فقط روی کاغذ برقرار بود. با دو چت، این شرط واقعی می‌شود
> و کاربر همچنان فقط با دو چت سروکار دارد (قید کاربر: حداکثر دو چت).

## ۱. تقسیم نقش‌ها بین دو چت

| چت | شاخه | می‌کند | نمی‌کند |
|----|------|--------|---------|
| **Builder** (چت فعلی/اول) | `arena/01a06951-cutting-edge-v2` | گام‌های ①–⑦ و ⑨–⑩ هر مرحله؛ push؛ GREEN کردن **فقط بعد از** `approved` ناظر | نوشتن `REVIEW.md`؛ خودتأییدی |
| **Overseer** (چت دوم) | شاخهٔ خودش `arena/<id>-cutting-edge-v2` (کپی از شاخهٔ سازنده + کامیت‌های `review(...)`) | گام ⑧ (بازبینی تازه با اجرای دوبارهٔ تست‌ها)، `supervise.py`، ممیزی گذشته‌نگر، برگرداندن GREEN مشکوک به REVIEW، کارت hotfix | نوشتن/تغییر کد محصول یا تست؛ push به شاخهٔ سازنده؛ GREEN زدن؛ تصمیم U3 به‌جای کاربر |

هیچ‌کدام از دو چت به شاخهٔ دیگری push نمی‌کند (قاعدهٔ Arena: هر نشست فقط به شاخهٔ خودش). تبادل فقط از طریق **fetch** است:
- ناظر: `git fetch origin arena/01a06951-cutting-edge-v2 && git reset --hard FETCH_HEAD` (شاخهٔ خودش را با سازنده هم‌تراز می‌کند)، سپس فقط `REVIEW.md` را کامیت و push می‌کند.
- سازنده: `git fetch origin <overseer-branch> && git checkout FETCH_HEAD -- docs/loop/evidence/S-xxx/REVIEW.md` و آن را در کامیت ⑩ می‌آورد.

## ۲. چرخهٔ یک مرحله با دو چت (سه پیام کوتاه از کاربر)

```
Builder ──(build, push, status REVIEW)──▶ پیام آماده:  بازبینی کن S-010 @ <sha>
                                                            │  (کاربر کپی می‌کند در چت ناظر)
Overseer ──(fetch, re-run tests, CI, REVIEW.md, push)──▶ پیام آماده:  REVIEW S-010 approved @ <overseer-branch>
                                                            │  (کاربر کپی می‌کند در چت سازنده)
Builder ──(fetch REVIEW.md, ledger GREEN, commit, push, next step)──▶ …
```

- سازنده در انتظار بازبینی **بی‌کار نمی‌ماند**: مرحلهٔ بعدی را شروع می‌کند (verify_ledger اجازهٔ GREEN مرحله‌ای را که وابسته به REVIEW است نمی‌دهد، پس ترتیب حفظ می‌شود).
- بازبینی چند مرحله با هم مجاز است: `بازبینی کن S-010 S-011 @ <sha>` (هر مرحله یک `REVIEW.md` جدا).
- `changes-requested` → سازنده فقط must-fixها را می‌بندد و دوباره «بازبینی کن … r2». حداکثر ۲ دور؛ دور سوم = `BLOCKED` + یک سؤال مشخص برای کاربر.

## ۳. فرمان‌های چت ناظر

| فرمان | چه می‌کند |
|-------|-----------|
| `چک کن` | همگام‌سازی با شاخهٔ سازنده، `supervise.py --write` (۱۶ چک)، CI HEAD، گزارش: **Verdict → ≤۵ اقدام → پیام آمادهٔ چت سازنده** |
| `بازبینی کن S-xxx @ <sha>` | گام ⑧ کامل: CONTRACT + diff + اجرای دوبارهٔ همهٔ تست‌های ادعاشده + بازکردن artifactها/annotationهای CI → `REVIEW.md` با قالب `templates/REVIEW.md` → کامیت `review(S-xxx): round N — <verdict>` → push به شاخهٔ خودش |
| `ممیزی گذشته‌نگر` | نمونه‌گیری از مراحل GREEN قبلی که سازنده خودش بازبینی کرده (S-001…S-100): شواهد را دوباره تولید می‌کند؛ اگر AC واقعاً برقرار نیست → در `REVIEW.md` همان مرحله بند «Retro-audit» و در پیام به سازنده «برگردان به REVIEW» |
| `گزارش هفتگی` | خلاصهٔ سرعت (GREEN/هفته)، مراحل گیرکرده (watchdog)، باگ‌های باز، ریسک مایلستون بعدی |

## ۴. آنچه ناظر «حتماً» خودش دوباره اجرا می‌کند

1. `python scripts/verify_ledger.py`
2. `ai-engine/.venv/bin/python scripts/gate.py --stage static --skip cargo-clippy`
3. تست‌های نام‌برده در جدول AC همان مرحله (`pytest tests/unit/<file>`, Playwright `build-artifacts.spec.ts`, …)
4. CI روی همان SHA: `gh run list --branch arena/01a06951-cutting-edge-v2 --limit 3` → هر جاب؛ برای لاگ/آرتیفکت (که با توکن Arena دانلود نمی‌شود) از `gh api repos/<o>/<r>/check-runs/<job>/annotations` یا URL امضاشدهٔ `gh api …/actions/jobs/<id>/logs` با ابزار fetch.
5. برای مراحل با AC «فقط روی CI ویندوز» (cargo/tauri/installer): **نبود run سبز = تأیید نکن** (`missing CI ≠ green`).

اگر چیزی قابل بازتولید نبود، در `REVIEW.md` می‌نویسد `Evidence re-produced: partially (<what>)` و اگر AC اصلی بود → `changes-requested` یا `needs-human`؛ هرگز approved با شواهد بازتولیدنشده.

## ۵. چشم‌های ناظر روی diff (فراتر از تست‌ها)

- `any`, `TODO`, `except: pass`, `catch {}` خالی، رشته‌های فارسی/انگلیسی hardcode در UI (→ S-085)، style inline، رنگ hex خارج از `DESIGN.md`
- تضعیف تست (حذف assert، افزودن skip/xfail بدون کارت مالک)
- تغییر رفتاری خارج از AC که در «Other behavior changes» کامیت نیامده → `[SCOPE-CONFLICT]`
- هر چیزی که «Skip ≠ Pass» را دور می‌زند (MISSING که PASS گزارش شده، `continue-on-error`)
- بهداشت: فایل باینری/مدیا در git، کلید API، نسخهٔ pin‌نشده

## ۶. محیط چت ناظر (همان محدودیت‌های سندباکس)

- کلون shallow است: اول `git fetch --unshallow origin || git fetch --deepen=200 origin`.
- بدون cargo/rustc/apt؛ Playwright بدون مرورگر (فقط `build-artifacts.spec.ts` محلی اجرا می‌شود).
- بازسازی venv:
  `python3 -m venv ai-engine/.venv && ai-engine/.venv/bin/pip install -r ai-engine/requirements-tooling.txt && ai-engine/.venv/bin/pip install --no-deps -e ai-engine`
  و برای تست‌های مدیا: `librosa==0.10.2.post1 imageio-ffmpeg==0.5.1 opencv-python-headless==4.10.0.84 scipy==1.11.4`
- JS: `corepack enable; COREPACK_ENABLE_DOWNLOAD_PROMPT=0 pnpm install --frozen-lockfile`
- توکن GitHub گاهی منقضی می‌شود → `gh`/`push` را بعداً تکرار کن؛ هرگز از کاربر توکن نخواه.

## ۷. تضاد منافع و شفافیت

- ناظر اگر کارت مرحله (`steps.json`) یا پروتکل را تغییر داد، در `REVIEW.md` همان مرحله اعلام می‌کند.
- REVIEWهای قبلی (S-001…S-100) با برچسب «self-review by builder» باقی می‌مانند؛ ممیزی گذشته‌نگر آن‌ها را جایگزین نمی‌کند، فقط بند «Retro-audit» اضافه می‌کند.
- ناظر هرگز به‌جای سازنده کد نمی‌زند، حتی برای «اصلاح کوچک» — فقط must-fix می‌نویسد.
