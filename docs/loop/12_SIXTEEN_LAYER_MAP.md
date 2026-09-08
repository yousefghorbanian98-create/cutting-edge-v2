# 12 — نگاشت نقشه‌ی ۱۶ لایه روی این محصول

> ورودی: `docs/16-LAYER-PRODUCTION-PLAN.md` (نقشه‌ی عمومی تولید، ۱۶ لایه × ۷ بخش) و `docs/ROADMAP-v2-WITH-INTEGRATIONS.md`.
> آن سند برای یک SaaS چندمستأجره با NestJS/Postgres نوشته شده و **استک این پروژه قفل است**. بنابراین لایه‌ها را می‌گیریم، محتوای بیگانه را کنار می‌گذاریم، و هر لایه را به مراحل شماره‌دار همین لوپ وصل می‌کنیم.
> نتیجه‌ی این نگاشت: **۳ مرحله‌ی جدید** (S-099, S-100, S-101) و **۴ کارت تقویت‌شده** (S-009, S-053, S-084, S-087). هیچ لایه‌ای بی‌صاحب نمانده است.

## قاعده‌ی نگاشت
| علامت | معنی |
|---|---|
| ✅ پوشش دارد | لایه از قبل در steps.json مرحله دارد |
| ➕ افزوده شد | مرحله یا محتوای جدید در این به‌روزرسانی |
| ✂️ حذف عمدی | بخش‌های SaaS/ابری که با محصول دسکتاپ آفلاین، بودجه‌ی صفر و استک قفل‌شده تعارض دارند |

## جدول نگاشت

| لایه | در نقشه‌ی ۱۶لایه | در Cutting Edge v2 (مراحل) | وضعیت |
|---|---|---|---|
| L1 Product Requirements | PRD، User Story، Gherkin AC | ۱۶ قابلیت مصوب در سند مرجع؛ هر مرحله `CONTRACT.md` با AC/NG (معادل Gherkin)؛ تصمیم‌های محصولی در `docs/DECISIONS.md` (U3) | ✅ |
| L2 System Design & ADR | Modular Monolith، C4، ADR | معماری سه‌لایه Tauri ⇄ Next ⇄ FastAPI sidecar؛ **ADRها تا امروز فقط داخل steps.json و ۰۲ بودند** → `docs/adr/` | ➕ S-101 |
| L3 Database | Postgres، Prisma، pgvector | بدون DB سرور. داده‌ی محلی: فایل پروژه `.cev2` (S-068)، کش تحلیل به هش (S-045)، صف کار پایدار (S-072)، migrations اسکیمای پروژه (S-068) | ✅ / ✂️ Postgres |
| L4 API Contract | OpenAPI، versioning، idempotency | OpenAPI از FastAPI + تست قرارداد (S-080)؛ job model و WebSocket (S-012, S-029)؛ idempotency با content-hash cache (S-056) | ✅ / ✂️ gateway/rate-tier |
| L5 Backend | Clean Architecture، صف | `ai_engine.core.*` (storage, ffmpeg, jobs)، thread-pool + job queue (S-012, S-072)، Reheal L1–L7 (S-069…S-076) | ✅ |
| L6 Frontend | Next 15، state، a11y، perf | Tailwind 4 / DaisyUI 5 (S-007)، تایم‌لاین P1، Command Palette (S-025)، بودجه‌ی 60fps (S-015, S-082) | ✅ |
| L7 Design System & Motion | توکن، Storybook، Framer | `tokens.ts` ⇄ `@theme` (S-007) + **DESIGN.md به‌عنوان مرجع واحد و گیت‌شده** | ➕ S-099 ، ✅ S-087 |
| L8 Auth | OAuth/SSO/RBAC | تک‌کاربره‌ی دسکتاپ؛ فقط کلید OpenRouter در keyring ویندوز (S-086) | ✂️ auth / ✅ S-086 |
| L9 Security & Compliance | OWASP، secrets، SBOM | S-003 (traversal/size/type/CORS)، gitleaks در gate (S-008)، ممیزی امنیت + CSP + capabilities (S-086)، third-party notices (S-095) | ✅ |
| L10 DevOps & CI/CD | pipeline، pre-commit، hooks | S-008 (lefthook, gate.py)، S-009 (CI matrix ubuntu/windows، artifacts)، release.yml (S-097) + **چک‌های طراحی در CI** | ✅ / ➕ S-009 تقویت |
| L11 Infra & Cloud | K8s، Terraform، CDN | بدون زیرساخت ابری؛ «زیرساخت» = نصب‌کننده NSIS، sidecar PyInstaller، آپدیتر (S-060…S-065) | ✂️ / ✅ P4 |
| L12 Caching & Performance | Redis، CDN، budgets | کش تحلیل روی دیسک به هش (S-045, S-056)، بودجه‌های کارایی روی GTX 1650 (S-082)، leak audit (S-083) | ✅ / ✂️ Redis |
| L13 Observability | OTEL، Grafana، alerting | لاگ JSON ساخت‌یافته + viewer (S-073)، crash bundle اختیاری بدون telemetry (S-089)، Reheal drawer | ✅ / ✂️ SaaS metrics |
| L14 Testing | پیرامید، coverage 80%، E2E، chaos | قانون «تست واقعی» (۰۲ §1-⑤)، فیکسچر واقعی (S-005)، هارنس زنده (S-006)، coverage ≥ 80% (S-079)، chaos (S-077)، visual regression (S-081) | ✅ |
| L15 AI & Automation | RAG، eval harness، prompt versioning، agent SDLC | Multi-Modal Brain + fallback chain (S-053)، guardrails $0 (S-056)، **پرامپت‌های نسخه‌دار + eval آفلاین** ، «AI-first SDLC» = همین لوپ ناظر/سازنده | ✅ / ➕ S-053 تقویت |
| L16 Docs & DX | ADR، runbooks، onboarding < 1 روز | `docs/loop/*` ، مستندات کاربر (S-092)، README (S-093)، **AGENTS.md به‌عنوان نقطه‌ی ورود** ، learnings | ➕ S-099, S-101 / ✅ P7 |

## چه چیزهایی از Roadmap v2 عمداً وارد نشد و چرا
| مورد | دلیل |
|---|---|
| نصب ECC (۲۶۱ skill، هوک‌های Claude Code، GitHub App) | این محیط (Arena) هوک و اسکیل‌لودر ندارد؛ آن‌چه ECC می‌دهد (plan→test→implement→review→verify→remember→improve) از قبل به‌شکل ۱۰ گام لوپ + ناظر پیاده شده. فقط دو حلقه‌ی گم‌شده‌ی آن — **remember/improve** — با `docs/learnings/` و چک ناظر اضافه شد (S-101). جزئیات در `13_INTEGRATIONS_ADOPTION.md` |
| Skill زنده‌ی Vercel (fetch از GitHub در هر بار) | سندباکس شبکه ندارد و نتیجه غیرقطعی می‌شد → چک‌کننده‌ی **آفلاین و قطعی** روی snapshot قوانین (S-100) |
| Storybook + Chromatic | هزینه/سرویس خارجی؛ visual regression با Playwright در S-081 پوشش داده می‌شود |
| Jest coverage 80% | ما Vitest/pytest داریم؛ همان هدف در S-079 |
| DESIGN.md با Geist/blurple/چت RAG | با توکن‌های واقعی S-007 تعارض داشت → به‌عنوان پیش‌نویس علامت خورد و در S-099 با توکن‌های واقعی یکی می‌شود |
| برنامه‌ی ۲۶ هفته‌ای/۶ نفره/RACI | تیم = یک کاربر + دو چت؛ زمان‌بندی از ledger و مایلستون‌های v0.3…v1.0 می‌آید |

## ترتیب اجرای مراحل جدید در P0 (پس از S-012)
```
S-099 (DESIGN.md + AGENTS.md + check-design-tokens)  ← deps S-007, S-008
S-100 (design_audit در gate static)                  ← deps S-099
S-101 (ADR + learnings + چک هایجین)                  ← deps S-001  (می‌تواند زودتر و مستقل ساخته شود)
```
سپس P1 (S-013…) طبق قبل. کارت‌های S-084/S-087 در P6 اکنون به S-099/S-100 ارجاع دارند.
