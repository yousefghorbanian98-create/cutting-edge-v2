# CONTRACT — S-007 — Frontend styling fix: Tailwind 4 + DaisyUI 5 + fonts + globals.css

> نوشته‌شده توسط Builder در گام ② قبل از هر خط کد. **اگر در این فایل نیست، وجود ندارد.**
> منبع: کارت S-007 در `03_STEPS.md` (goal/files/real_test/done-when).

## مسئله (از `01_STATE_OF_REPO.md` B-4)

`apps/desktop/src/app/page.tsx` هشتادوشش `className` با کلاس‌های Tailwind دارد ولی
`tailwindcss`/`postcss`/`daisyui`/`globals.css` هیچ‌کدام وجود ندارند → صفحه **بدون CSS** رندر
می‌شود. `layout.tsx` رنگ پس‌زمینه و فونت را با **inline style** می‌گذارد، پس «پس‌زمینه درست
است» هیچ چیز را درباره‌ی stylesheet اثبات نمی‌کند. فونت‌ها فقط رشته‌ی `font-family` هستند و
هیچ فایلی بارگذاری نمی‌شود.

## Acceptance Criteria (مشاهده‌پذیر، قابل اندازه‌گیری)

| id | معیار | ابزار سنجش | تست اثبات (اول قرمز) |
|----|-------|-----------|----------------------|
| AC-1 | زنجیره‌ی build واقعی: `apps/desktop/postcss.config.mjs` پلاگین `@tailwindcss/postcss` را وصل می‌کند، `src/app/globals.css` با `@import "tailwindcss"` + `@plugin "daisyui"` شروع می‌شود، و `next build` با `output: 'export'` در `out/` حداقل یک فایل CSS بزرگ‌تر از **۱۰KB** تولید می‌کند | `next build` + اندازه‌ی فایل‌های `out/**/*.css` | `apps/desktop/tests/styling.spec.ts` → `build emits CSS > 10KB` |
| AC-2 | پس‌زمینه‌ی `body` از **stylesheet** می‌آید نه inline style: `document.body.style.backgroundColor === ''` و `getComputedStyle(body).backgroundColor === 'rgb(9, 9, 11)'` | Playwright روی `out/index.html` | `styling.spec.ts` → `body background comes from the stylesheet` |
| AC-3 | گرادیان متن هدر واقعی است: `h1` هدر computed `background-image` شامل `linear-gradient`، `-webkit-background-clip: text` و `color: rgba(0, 0, 0, 0)` | Playwright computed style | `styling.spec.ts` → `header gradient text is real` |
| AC-4 | سه فونت **آفلاین و self-hosted** بارگذاری می‌شوند: `document.fonts.load('400 16px Vazirmatn' / 'Inter Variable' / 'JetBrains Mono')` حداقل یک FontFace برمی‌گرداند و `document.fonts.check(...)` برای هر سه `true` است؛ هیچ درخواست فونت به دامنه‌ی خارجی نمی‌رود | Playwright `document.fonts` + sniffing درخواست‌ها | `styling.spec.ts` → `fonts are self-hosted and resolved` |
| AC-5 | **صفر console error و صفر page error** هنگام بارگذاری صفحه (پولینگ `/health` با یک stub محلی روی `127.0.0.1:8001` پاسخ می‌گیرد تا خطای شبکه مصنوعی تولید نکند) | Playwright `page.on('console')` / `page.on('pageerror')` | `styling.spec.ts` → `zero console/page errors` |
| AC-6 | DaisyUI **۵** واقعاً کامپایل شده (نه ۴): یک کلاس DaisyUI مثل `.btn` computed style غیرپیش‌فرض دارد (border-radius و background غیر `initial`) — DaisyUI 4 با Tailwind 4 کار نمی‌کند، پس این هم‌زمان سازگاری نسخه را اثبات می‌کند | Playwright computed style | `styling.spec.ts` → `daisyui 5 is compiled` |
| AC-7 | RTL/فارسی حفظ می‌شود و baseline بصری ذخیره می‌شود: `out/index.html` شامل `<html lang="fa" dir="rtl">` است (اثبات static)، و `styling.spec.ts` علاوه بر `document.documentElement.dir==='rtl'` یک اسکرین‌شات ۱۴۴۰×۹۰۰ در `docs/loop/evidence/S-007/` می‌نویسد | HTML export + Playwright screenshot | `build-artifacts.spec.ts` → `exported HTML is Persian + RTL` (✅) / `styling.spec.ts` → `rtl + screenshot baseline` (unverified:ci) |

**ابزار تست:** `@playwright/test` (`apps/desktop/tests/styling.spec.ts` + `playwright.config.ts`)
روی خروجی **static export** که با وب‌سرور خودِ Playwright (`webServer`) سرو می‌شود — نه `next dev`.
دلیل: (۱) کارت «`next build` emits out/» را می‌خواهد و مسیر Tauri (S-010/S-060) هم همان `out/`
را بارگذاری می‌کند، پس تست باید همان artifact را بسنجد؛ (۲) `playwright-report/` خروجیِ
`@playwright/test` است که S-009 به‌عنوان artifact آپلود می‌کند؛ (۳) marker `e2e` در `pytest.ini`
برای نگاشت `gate.py --stage e2e` (S-011) به `pnpm --filter cutting-edge-desktop test:e2e` می‌ماند.

### دو فایل تست و تقسیم پوشش (مهم)

`npx playwright install chromium` در این sandbox ممکن نیست: تنها registry.npmjs.org و PyPI
پروکسی‌شده‌اند و `cdn.playwright.dev` / `playwright.azureedge.net` / `storage.googleapis.com` /
`deb.debian.org` همگی `000` برمی‌گرداند (curl). هیچ Chromium سیستمی هم نصب نیست. پس تست به دو
فایل تقسیم شد تا **هیچ AC‌ای بدون شواهد نماند**:

| فایل | نیاز به مرورگر | چه چیزی را اثبات می‌کند | وضعیت در این sandbox |
|------|----------------|--------------------------|----------------------|
| `apps/desktop/tests/build-artifacts.spec.ts` | **نه** | خروجی واقعی `next build`: اندازه‌ی CSS، قواعد کامپایل‌شده‌ی `body`/گرادیان/`bg-clip-text`/`text-transparent`، `@font-face`ها و woff2های bundle‌شده، نبود `fonts.googleapis.com`، قواعد `.btn` و توکن DaisyUI، `lang=fa dir=rtl` در HTML، همگامی `tokens.ts ↔ @theme` | ✅ اجرا شد (۸/۸) |
| `apps/desktop/tests/styling.spec.ts` | **بله** (Chromium) | لایه‌ی DOM: computed style واقعی، `document.fonts.check/load`، صفر console/page error، اسکرین‌شات baseline | ⛔ `unverified:ci` — gate در S-009 (ubuntu job) |

هر دو فایل در CI اجرا می‌شوند؛ `build-artifacts` حتی اگر مرورگر دانلود نشود CI را سبز/قرمز
می‌کند و `styling` لایه‌ی computed-style را می‌بندد.

**اثبات قرمز-اول (اجراشده):** با برگرداندن `globals.css`/`postcss.config.mjs`/`layout.tsx` به
`HEAD` و build مجدد: `out/` **هیچ فایل CSS‌ای تولید نکرد** (دقیقاً B-4) و همان spec با
**۶ failed / 2 passed** قرمز شد؛ بعد از برگرداندن تغییرات ۸/۸ سبز. دو تستی که در هر دو حالت
سبز می‌مانند (`lang=fa dir=rtl` و git-ignore بودن `out/`) عمدتاً مستقل از این اصلاح‌اند.

## Non-Goals (الزام‌آور — عمداً در این مرحله ساخته نمی‌شود)

| id | نا-هدف | چرا اینجا نه | کجا ساخته می‌شود |
|----|--------|--------------|------------------|
| NG-1 | هیچ تغییری در `page.tsx` (منطق، JSX، کلاس‌ها) یا کامپوننت‌ها/storeها | کارت S-007 فقط زیرساخت استایل است؛ بازطراحی UI جای دیگری است | S-013+, S-087 |
| NG-2 | بدون Biome/Ruff/tsc-strict/turbo-`tasks`/lefthook و بدون حذف `latest` از بقیه‌ی package.jsonها | ابزار زنجیره مرحله‌ی خودش را دارد | S-008 |
| NG-3 | بدون `.github/workflows/*` و بدون اجرای Playwright در CI | CI مرحله‌ی خودش را دارد | S-009 |
| NG-4 | بدون Tauri/build.rs/آیکون/bundle | اسکلت دسکتاپ | S-010 |
| NG-5 | بدون تغییر بک‌اند، `gate.py` یا endpointها | — | S-011, S-012 |
| NG-6 | بدون `i18n`/سوییچ زبان و بدون توکن‌سازی کامل همه‌ی کلاس‌های hardcoded در `page.tsx` | نیاز به ویرایش page.tsx دارد (NG-1) | S-085 |

## Reheal layers touched

- هیچ‌کدام. این مرحله فقط زیرساخت استایل فرانت است؛ هیچ لایه‌ی L1–L7 یا مسیر داده‌ی runtime
  تغییر نمی‌کند. **Probe آشوب: N/A با دلیل مکتوب** — هیچ رفتار بازیابی وجود ندارد که probe
  شود؛ تنها رفتار قابل خرابی (فونت/CSS بارگذاری‌نشده) با AC-1/AC-4 به‌صورت مستقیم assert
  می‌شود. ErrorBoundary (L6) دست‌نخورده است.

## Risks / unknowns

- **نسخه‌ها:** Tailwind `4.3.3`، `@tailwindcss/postcss 4.3.3`، `daisyui 5.7.28`،
  `@fontsource/vazirmatn 5.3.0`، `@fontsource-variable/inter 5.3.0`،
  `@fontsource/jetbrains-mono 5.3.0` (همه از npm registry در همین sandbox تأیید شدند).
- `bg-gradient-to-l` در Tailwind 4 به `bg-linear-to-l` تغییر نام داده ولی به‌عنوان alias
  backward-compatible باقی است؛ چون NG-1 ویرایش `page.tsx` را ممنوع می‌کند، alias باید کار
  کند. AC-3 همین را **اندازه‌گیری** می‌کند (اگر alias کار نکند، تست قرمز می‌شود و آن‌وقت
  یا CONTRACT اصلاح می‌شود یا NG-1 با دلیل مکتوب شکسته می‌شود).
- **Playwright browser download:** اگر `npx playwright install chromium` در sandbox ممکن نباشد،
  تست نوشته و commit می‌شود ولی `unverified:ci` در دفترچه ثبت می‌شود و gate در S-009 است.
- پولینگ `/health` در `page.tsx` به `http://127.0.0.1:8001` hardcoded است؛ برای AC-5 یک stub
  محلی همان مسیر را پاسخ می‌دهد. این **mock موفق همیشه‌سبز نیست** (NG پروتکل §5): هدف AC-5
  فقط «بدون خطای console از سمت CSS/فونت/JS» است و رفتار API در S-006/S-012 تست واقعی دارد.
- `output: 'export'` با `next 15`؛ اگر export به‌خاطر ویژگی نامناسبی شکست خورد، دلیل مکتوب
  لازم است (تغییر `output` بدون ویرایش CONTRACT ممنوع).

## U-decisions

- `user: none` — هیچ تصمیم محصولی لازم نیست. فونت‌ها از `packages/design-system/tokens.ts`
  موجود می‌آیند (Inter Variable / Vazirmatn / JetBrains Mono) و پیش‌فرض کارت اعمال می‌شود.
