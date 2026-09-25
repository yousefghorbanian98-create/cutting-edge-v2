# CONTRACT — S-023 — Timeline zoom (Ctrl+wheel, slider, fit) + horizontal scroll + minimap

> نوشته‌شده پیش از implementation. اگر در این فایل نیست، در این مرحله وجود ندارد.
> منبع: کارت S-023 در `docs/loop/03_STEPS.md` و `docs/loop/steps.json`.
> ledger این مرحله تا verdict مستقل `REVIEW` می‌ماند، نه `GREEN`.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | Ctrl+wheel روی x=400 زمان زیر نشانگر را عوض نمی‌کند. خطای پیکسلی حداکثر `1` است. | Playwright | `apps/desktop/tests/zoom.spec.ts` |
| AC-2 | fit کل سکانس را در عرض نما نشان می‌دهد. | Playwright | همان فایل |
| AC-3 | اسکرول افقی و مینی‌مپ viewport را نشان می‌دهند. زوم از slider هم همان دامنه را عوض می‌کند. | Playwright + vitest | `zoom.spec.ts` و `src/domain/__tests__/zoom.test.ts` |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا |
|----|--------|--------------|-----|
| NG-1 | پخش چندکلیپی و ping-pong | کارت بعدی | S-024 |
| NG-2 | رجیستری شورتکات و مودال `?` | بعد از پلیر | S-025 |
| NG-3 | export و FFmpeg | زنجیرهٔ جدا | S-028 |
| NG-4 | GREEN کردن S-022 یا S-006 تا S-021 | دستور صریح همین batch | نگه داشته می‌شود |

## Forward-knowledge compliance

- Contract و dependencyهای خوانده‌شده: این CONTRACT؛ کارت S-023؛ CONTRACT و REVIEW مرحلهٔ `S-022`؛ CONTRACTهای `S-015` و `S-017` و `S-021`؛ `docs/loop/FORWARD_KNOWLEDGE_GATE.md`؛ `docs/loop/STYLE_MATCH_ARCHITECTURE.md`؛ `docs/loop/00_INDEX.md`؛ `docs/loop/06_BUGS.md`.
- REVIEWها و architecture updateهای اعمال‌شده: S-022 approved برای تصمیم ledger است و GREEN نیست. وابستگی S-022 برابر `REVIEW` است. شروع این batch با دستور صریح کاربر است و آن ردیف را GREEN نمی‌کند. Style Match فقط roadmap است و `submit_inference()` اینجا صدا زده نمی‌شود.
- اصول جدیدی که در همین مرحله اجرا می‌شوند: زوم view state است، نه mutation سکانس. فرمول زوم حول نشانگر در دامنه است و UI فقط از action فروشگاهٔ زوم می‌خواند. `PX_PER_SECOND` پیش‌فرض `100` می‌ماند تا تست‌های قبلی شل نشوند.
- Deferred: پخش سکانس → S-024. شورتکات `?` → S-025. export و overwrite → S-028. اعتبار خروجی → S-033 که شروع نمی‌شود. GPU کاربر → S-027 و `unverified` است، نه پاس.
- Negative boundary: `useTimelineStore.setState` برای sequence ممنوع است. زوم history سکانس را دور نمی‌زند چون اصلاً sequence را عوض نمی‌کند. raw command، filter graph، و overwrite فایل در این مرحله وجود ندارد و رد می‌شود.
- Evidence plan: vitest دامنه پیش از integration. بعد از static و unit و typecheck، Playwright. پیش از تحویل batch، CI کامل Ubuntu و Windows. local pass جایگزین CI نیست. آستانهٔ `±1px` شل نمی‌شود. عرض قفل نشانگر باید در state بماند تا رندر React آن را قبل از assertion جمع نکند.
- Status: `REVIEW` تا verdict مستقل. GREEN نمی‌شود.
