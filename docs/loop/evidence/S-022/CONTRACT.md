# CONTRACT — S-022 — Multi-track: add/remove tracks, mute/solo/lock, text track

> نوشته‌شده پیش از implementation. اگر در این فایل نیست، در این مرحله وجود ندارد.
> منبع: کارت S-022 در `docs/loop/03_STEPS.md` و `docs/loop/steps.json`.
> ledger تغییر نکرده است. ردیف S-022 همچنان `TODO` است. این مرحله GREEN نیست.

## وضعیت فعلی

- ledger: `TODO`، iter 0. این ردیف در این کار تغییر نمی‌کند.
- وابستگی S-021 هنوز `REVIEW` است، نه `GREEN`. شروع implementation با دستور صریح همین سشن است و مجوز GREEN نیست.
- implementation در درخت است: هدر ترک، `tracks.ts`، و باس AudioContext. GREEN نیست.
- vitest و typecheck محلی پاس شده‌اند. Playwright محلی اجرا نشد چون دانلود Chromium با `ECONNRESET` قطع شد. این local pass جایگزین CI نیست.

## Acceptance Criteria

| id | معیار | ابزار سنجش | تست اثبات |
|----|-------|-----------|-----------|
| AC-1 | افزودن ترک `video` / `audio` / `text` و حذف ترک خالی از مسیر store انجام می‌شود. ترک دارای کلیپ و شناسهٔ تکراری رد می‌شود و همان آبجکت برمی‌گردد. | vitest | `apps/desktop/src/domain/__tests__/tracks.test.ts` |
| AC-2 | mute / solo / lock و جابه‌جایی ترتیب، store action هستند و undo همان ترتیب و پرچم را برمی‌گرداند. کلیک دوباره روی همان پرچم history جدید نمی‌سازد. | vitest | همان فایل + `history-path.test.ts` |
| AC-3 | قفل ترک، کشیدن کلیپ آن را no-op می‌کند. `data-start` و `data-track` بعد از drag عوض نمی‌شوند. | Playwright | `apps/desktop/tests/tracks.spec.ts` |
| AC-4 | در حین پخش، mute ترک صدا خروجی AudioContext را ساکت می‌کند. AnalyserNode خود گراف خوانده می‌شود، نه یک data-attribute جعلی. پیش از mute، RMS باید بالای `0.02` باشد و بعد از mute زیر `0.001`. این آستانه‌ها شل نمی‌شوند. | Playwright | `apps/desktop/tests/tracks.spec.ts` |
| AC-5 | solo همان نوع ترک را محدود می‌کند و mute حتی با solo هم ترک را خاموش می‌کند. ترک ویدیوی غیرفعال، پیش‌نمایش تک‌فایل را پنهان می‌کند. این compositing چندکلیپی نیست. | vitest + data attribute در Playwright | `tracks.test.ts` |

## Non-Goals

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | پخش چندکلیپی، ping-pong، و رسم ترک متن روی canvas | کارت S-024 است و scope اینجا را بزرگ نمی‌کند | S-024 |
| NG-2 | وصل کردن فایل مدیا به باس صدا | S-022 اثر mute را روی باس ترک اثبات می‌کند؛ منبع چندکلیپی مال S-024 است | S-024 |
| NG-3 | export فایل و سیاست overwrite | هیچ فرمان FFmpeg در این مرحله اجرا نمی‌شود | S-028, S-033, S-086 |
| NG-4 | زوم، فیت، و مینی‌مپ | کارت بعدی | S-023 |
| NG-5 | `submit_inference()` و مدل Style Match | سیستم job هنوز آمادهٔ مدل نیست | مرحلهٔ مدل، بعد از job system |
| NG-6 | GREEN کردن S-006 تا S-021 یا S-022 | verdict مستقل ناظر لازم است | بعد از REVIEW مستقل |

## Reheal layers touched

- L2 — probe: capability صدای مرورگر فقط `available` / `missing` / `unknown` است. `missing` پاس نیست.

## Risks / unknowns

- AudioContext در Chromium هدلس ممکن است تا gesture کاربر `suspended` بماند. resume باید داخل کلیک پخش باشد. اگر `running` نشود، تست رد می‌شود و skip نمی‌شود.
- باس S-022 یک نوسان‌ساز به‌ازای هر ترک صدا است تا mute بدون فایل مدیا هم قابل اندازه‌گیری باشد. این منبع نهایی کلیپ نیست.

## U-decisions

- U3: معنی lock = ممنوعیت ویرایش کلیپ، نه ممنوعیت جابه‌جایی خود ترک. پیش‌فرض همین است.
- U3: solo بر mute غلبه نمی‌کند. ترک mute همیشه غیرفعال است.

## Forward-knowledge compliance

- Read: `docs/loop/FORWARD_KNOWLEDGE_GATE.md`; `docs/loop/STYLE_MATCH_ARCHITECTURE.md`; `docs/loop/00_INDEX.md`; کارت S-022؛ CONTRACTهای S-013 و S-016 و S-017 و S-021؛ REVIEWهای S-006 و S-012 و S-013 تا S-021؛ `docs/loop/06_BUGS.md` به‌ویژه `BUG-18`.
- dependencyها: S-021 `REVIEW` و GREEN نیست. S-013 مدل ترک را داده است. S-016 پخش تک‌فایل را داده است. S-017 مسیر drag از `moveClip` را داده است. S-006 و S-012 `REVIEW` می‌مانند و این مرحله آن‌ها را GREEN نمی‌کند.
- Applied here: مسیر `domain operation → store action → Immer → temporal history → UI evidence`. پرچم و ترتیب ترک فقط از action فروشگاه می‌گذرند. capability صدا سه‌حالته است و `missing` پاس نیست. اثبات مرورگر با AnalyserNode است، نه local pass به‌جای CI.
- Deferred: رسم متن و صدای چندمنبعی → S-024. export، overwrite اتمیک، و provenance فایل → S-028 / S-033 / S-086 (`BUG-18`). probe ساختاری ffprobe در این UI دوباره پیاده نمی‌شود؛ مالک آن S-006 / S-028 است. GPU و `submit_inference()` → مرحلهٔ مدل Style Match.
- Rejected inputs: raw FFmpeg command، arbitrary filter graph، `useTimelineStore.setState` برای sequence، overwrite فایل، و نتیجهٔ `unverified` به‌عنوان پاس. kind خارج از `video | audio | text` رد می‌شود.
- Evidence plan: vitest برای دامنه و undo؛ typecheck و static پس از اسکلت؛ Playwright برای قفل و سکوت analyser پس از integration؛ پیش از review، CI کامل Ubuntu و Windows شامل cargo و Tauri و installer smoke. failure به skip تبدیل نمی‌شود و آستانهٔ RMS شل نمی‌شود.
- Parallel: دامنهٔ `tracks.ts`، هدر ترک، اسکلت Playwright، و گراف صدا از هم مستقل‌اند و بعد از این بخش با هم نوشته می‌شوند. integration زمانی است که static و unit و typecheck پاس شده باشند.
- Status: ledger `TODO` می‌ماند. این مرحله تا verdict مستقل `REVIEW` گزارش می‌شود و GREEN نمی‌شود.
