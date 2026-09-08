# 🌍 نقشه جامع تولید محصول — cutting-edge-v2
## معماری ۱۶ لایه | AI-Native & Production-Ready From Day One

> **وضعیت مخزن فعلی:** `cutting-edge-v2` در گیت‌هاب فقط شامل `Initial commit` و `README.md` است. این نقشه بر اساس فرض «پروژه نسل دوم لبه فناوری با توسعه ۱۰۰٪ مبتنی بر AI» تدوین شده و به عنوان **Single Source of Truth** برای تیم مهندسی قابل استفاده مستقیم است.

---

### 📌 مفروضات پایه (چون فیلدها خالی بودند — قابل تغییر در جلسه Kick-off)

| پارامتر | مفروضه پیشنهادی | دلیل |
|---|---|---|
| **PROJECT NAME** | **cutting-edge-v2 — پلتفرم AI-Native نسل دوم** | نام مخزن |
| **PROJECT DESCRIPTION** | پلتفرم ماژولار SaaS با هسته LLM/RAG، اتوماسیون گردش‌کار، داشبورد تحلیلی و API-first برای ارائه قابلیت‌های AI به کسب‌وکارها (چت هوشمند، تولید محتوا، تحلیل داده، اتوماسیون) به صورت multi-tenant و مقیاس‌پذیر | پوشش بیشترین حالت‌های استفاده «تماماً AI» |
| **TARGET USERS** | 1) SMB/Startup 2) تیم‌های محصول و مارکتینگ 3) توسعه‌دهندگان (API consumers) 4) Enterprise (SSO, Compliance) | B2B2C |
| **SCALE EXPECTATION** | **Day 1: 10K MAU → 6 ماه: 100K → 12 ماه: 1M** (طراحی برای 10x = 10M) | الزام «مقیاس‌پذیری» |
| **TECH PREFERENCE** | **Next.js 15 (App Router) + Node.js (NestJS) + PostgreSQL + Prisma + Redis + pgvector/Qdrant + Tailwind/shadcn** | پشته پیشنهادی شما + AI-ready |
| **TEAM SIZE** | **۶ نفر**: 1 Tech Lead, 2 Full-stack, 1 AI/ML, 1 DevOps, 1 Product/QA | بهینه برای ۶ ماه |
| **TIMELINE** | **۶ ماه تا GA** (MVP در ۱۰ هفته) | Startup/Scale-up |
| **BUDGET** | **Scale-up** (متوسط به بالا، تمرکز بر سرعت + کیفیت) |  |
| **اصل طلایی** | **AI-First SDLC**: هر لایه توسط AI agents طراحی، تولید، تست و مانیتور می‌شود — انسان نقش Architect/Reviewer | درخواست شما |

---

## 🚀 خلاصه اجرایی سطح بالا (Executive Summary کل پروژه)

**cutting-edge-v2** به عنوان یک **Modular Monolith** با قابلیت استخراج به Microservices طراحی می‌شود تا تعادل بین سرعت توسعه استارتاپی و مقیاس‌پذیری سازمانی حفظ شود. تمام ۱۶ لایه به صورت **AI-Augmented** پیاده‌سازی می‌شوند: از تولید PRD با LLM تا کدنویسی با Cursor/Copilot، تولید تست با AI، استقرار خودکار و مانیتورینگ هوشمند.

**استراتژی کلیدی:**
1.  **Monolith ماژولار + DDD + Clean Architecture** → استقرار سریع، دیباگ آسان، جداسازی دامنه‌ها برای آینده
2.  **API-First + Event-Driven** (REST + Webhook + Queue) → آماده برای موبایل، شرکای ثالث و عامل‌های AI
3.  **داده:** PostgreSQL + pgvector (شروع) → Qdrant جداگانه در اسکیل >500K، Redis برای کش/صف، S3 برای فایل
4.  **هوش مصنوعی:** لایه RAG + Agent + Function Calling + Evaluation Harness از روز اول، نه به عنوان افزونه
5.  **Production از روز اول:** CI/CD، IaC، Observability، Security و تست 80%+ قبل از اولین فیچر

**نقشه راه ۴ فاز:**

```
فاز 0 (هفته 1-2): Foundation — L1,L2,L3,L10,L11
فاز 1 (هفته 3-10): MVP — L4,L5,L6,L8 + هسته AI (L15)
فاز 2 (هفته 11-18): Hardening — L7,L9,L12,L13,L14
فاز 3 (هفته 19-26): Scale & Polish — L16, بهینه‌سازی، Multi-region, GA
```

**KPI موفقیت ۶ ماهه:** 99.9% Uptime, p95 <300ms, 80% Coverage, <2% AI Hallucination, <1sec RAG latency, 100K MAU.

---

## نقشه ۱۶ لایه — هر لایه ۷ بخش استاندارد

> برای هر لایه: 1) خلاصه اجرایی 2) پلن گام‌به‌گام 3) استک پیشنهادی 4) ساختار پوشه 5) Pitfallها 6) تخمین تلاش 7) وابستگی‌ها

---

### ▶ LAYER 1 — PRODUCT REQUIREMENTS & SPECIFICATION

#### 1. ✅ Executive Summary
لایه 1 اسکلت پروژه است. بدون PRD شفاف، حتی بهترین معماری شکست می‌خورد. در مدل AI-Native، ما PRD را با LLM می‌نویسیم اما با Human-in-the-loop اعتبارسنجی می‌کنیم و آن را به User Storyهای قابل تست تبدیل می‌کنیم.

#### 2. 🏗️ Detailed Implementation Plan
**گام 1 — کشف (Week 1):**
- Workshop با ذینفعان + تحلیل رقبا (با AI research agent: Perplexity/ChatGPT Deep Research)
- تدوین Vision & North Star Metric: مثلاً `Weekly Active Teams with AI Task Completed`

**گام 2 — PRD (Week 1-2):**
- قالب PRD شامل: خلاصه، مسئله، Persona، User Journey، Requirements (MoSCoW), Non-functional, Risks, Open Questions
- تولید اولیه با LLM (prompt: "Act as Senior PM...") سپس بازبینی انسانی

**گام 3 — User Stories + Acceptance Criteria (Gherkin):**
```gherkin
عنوان: به عنوان کاربر می‌خواهم با فایل PDF چت کنم
Story: US-015 — RAG Chat over Document
AC:
  Given کاربر احراز هویت شده و فایل PDF <10MB آپلود کرده
  When سوال "خلاصه این قرارداد چیست؟" می‌پرسد
  Then در <2s پاسخ با citation (صفحه/پاراگراف) + پیشنهاد follow-up دریافت کند
  And لاگ prompt/completion برای audit ذخیره شود
```

**گام 4 — MVP vs Full Scope:**
| MVP (10 هفته) | Full Scope (6 ماه) |
|---|---|
| Auth (Email/OAuth), Upload, RAG Chat, Dashboard, Billing Stripe, Admin | SSO/SAML, Team RBAC پیشرفته, Workflow Builder, Mobile App, Marketplace, On-prem option |

**گام 5 — Success Metrics:**
- Activation: 60% کاربران در 24h اولین چت را انجام دهند
- Retention D7: 25%
- AI Quality: Hallucation <2%, Relevance >4.2/5

**گام 6 — ابزار مدیریت:** Linear / Jira + PRD در Notion/Confluence با versioning

#### 3. 🛠️ Recommended Tech Stack & Tools
- **Spec:** Notion, Confluence, Miro, FigJam
- **AI Assist:** ChatGPT/Gemini برای PRD draft, Elicit برای تحقیق
- **Tracking:** Linear (پیشنهاد اول، سبک) | Jira (اگر enterprise)
- **Analytics post-launch:** PostHog + Mixpanel

#### 4. 📁 Folder/File Structure
```
/docs
  /prd
    01-vision.md
    02-personas.md
    03-user-journeys.md
    04-prd-v1.0.md
  /adr
  /metrics
    kpi-dashboard.md
```

#### 5. ⚠️ Common Pitfalls to Avoid
- نوشتن PRD ۵۰ صفحه‌ای بدون نمونه اولیه → **راه حل:** PRD 5 صفحه + Prototype کلیک‌شدنی در Figma
- عدم تعریف Non-functional (مثلاً latency RAG) → از روز اول SLA بنویس
- Scope creep در MVP → از MoSCoW و RICE برای اولویت‌بندی استفاده کن

#### 6. 📊 Effort Estimation
- **8-10 روز کاری** (1 PM + Tech Lead + AI assist). Story Points: 21

#### 7. 🔗 Dependencies
- وابسته به هیچ لایه فنی نیست؛ پیش‌نیاز **همه لایه‌ها** است. خروجی آن ورودی L2, L3, L4 است.

---

### ▶ LAYER 2 — SYSTEM DESIGN & ARCHITECTURE

#### 1. ✅ Executive Summary
معماری پیشنهادی **Modular Monolith** با مرزهای DDD است — سریع‌ترین مسیر تا MVP با کمترین overhead عملیاتی، اما با قابلیت جداسازی به Microservices بدون بازنویسی. تمام تصمیمات در ADR ثبت می‌شود.

#### 2. 🏗️ Detailed Implementation Plan
**الگوی معماری:** Modular Monolith (NestJS modules) + Event Bus داخلی (و بعداً Redis/RabbitMQ). چرا نه Microservices از ابتدا؟ ۶ نفر + ۶ ماه → Microservices هزینه DevOps و Latency را 3x می‌کند. چرا نه Monolith یکپارچه؟ مرزهای دامنه از هم می‌پاشد.

**High-Level Architecture Diagram (Text/ASCII):**

```
                         ┌─────────────────────────────────┐
                         │           CDN (Cloudflare)        │
                         │  WAF, Cache, DDoS, Image Opt     │
                         └──────────────┬──────────────────┘
                                        │
                         ┌──────────────▼──────────────────┐
                         │      Load Balancer (ALB)        │
                         └──────────────┬──────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           │                            │                            │
  ┌────────▼────────┐         ┌────────▼────────┐        ┌────────▼────────┐
  │  Frontend (Next.js 15)     │  Backend (NestJS API)    │  AI Worker(s)   │
  │  SSR/SSG/ISR, Edge         │  Modular Monolith        │  Queue Consumers│
  │  Vercel / K8s              │  REST + Webhooks         │  RAG, Embedding │
  └────────┬────────┘         └────────┬────────┘        └────────┬────────┘
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            ┌───────▼───────┐   ┌──────▼──────┐    ┌──────▼──────┐
            │  PostgreSQL   │   │   Redis     │    │  S3 / R2    │
            │  + pgvector   │   │ Cache+Queue │    │  Storage    │
            └───────────────┘   └─────────────┘    └─────────────┘
                    │                   │
            ┌───────▼───────┐   ┌──────▼──────┐
            │  Qdrant (opt) │   │  Observ.    │
            │  Vector DB    │   │  Grafana/OTEL│
            └───────────────┘   └─────────────┘
```

**C4 Model:**
- **L1 Context:** Users (Web, Mobile, API Partners) → cutting-edge-v2 → Stripe, OAuth providers, LLM providers (OpenAI/Anthropic), Email
- **L2 Container:** Web App (Next.js), API (NestJS), Worker, DB, Cache, Storage, Vector DB, Monitoring
- **L3 Component (Backend):** Modules: Auth, User, Organization, Document, Ingestion, RAG, Chat, Billing, Notification, Admin — هر کدام Controller-Service-Repository-Entity
- **L4 Code:** Clean Architecture layers: Controller → Service (UseCase) → Domain → Repository (Prisma)

**ADRs نمونه:**
- ADR-001: Modular Monolith over Microservices (2026-09-08)
- ADR-002: PostgreSQL + pgvector برای شروع (هزینه کمتر، JOIN آسان)
- ADR-003: NestJS over Express (DI, modularity, CQRS ready)
- ADR-004: LLM Provider abstraction (OpenAI primary, Anthropic fallback)

#### 3. 🛠️ Recommended Tech Stack & Tools
- **Diagram:** Mermaid, PlantUML, Excalidraw
- **ADR:** `adr-tools` + `/docs/adr/*.md`
- **Decision log:** Log4brains

#### 4. 📁 Folder/File Structure
```
/docs
  /architecture
    c4-context.puml
    c4-container.puml
    sequence-rag.puml
  /adr
    001-modular-monolith.md
    002-pgvector.md
```

#### 5. ⚠️ Pitfalls
- Over-engineering با Event Sourcing از روز اول → فقط برای Audit/Billing استفاده کن
- عدم تعریف anti-corruption layer برای LLM provider → حتماً Interface بساز

#### 6. 📊 Effort
- **10-12 روز** (Tech Lead + Staff Eng). SP: 34

#### 7. 🔗 Dependencies
- وابسته به L1. پیش‌نیاز L3, L4, L5, L11

---

### ▶ LAYER 3 — DATABASE DESIGN & DATA MODELING

#### 1. ✅ Executive Summary
داده قلب سیستم است. طراحی با **PostgreSQL 16 + Prisma + pgvector** شروع می‌شود، با ایندکس‌گذاری هوشمند، پارتیشن‌بندی آینده‌نگر و استراتژی بکاپ PITR. GDPR از اسکیما لحاظ می‌شود نه بعداً.

#### 2. 🏗️ Detailed Implementation Plan
**ERD اصلی (Text):**

```
[users] 1—N [organizations] via [organization_members] (role)
[users] 1—N [documents] 1—N [chunks] (embedding vector(1536))
[users] 1—N [conversations] 1—N [messages] (prompt/completion, tokens)
[organizations] 1—N [api_keys]
[organizations] 1—N [subscriptions] → [invoices]
[audit_logs] (append-only, partitioned by month)
```

**Schema نمونه Prisma:**

```prisma
model User {
  id            String   @id @default(cuid())
  email         String   @unique
  name          String?
  passwordHash  String?
  createdAt     DateTime @default(now())
  memberships   OrganizationMember[]
  documents     Document[]
}

model Document {
  id             String   @id @default(cuid())
  ownerId        String
  orgId          String
  filename       String
  s3Key          String
  status         DocumentStatus // PENDING, PROCESSING, READY, FAILED
  chunks         Chunk[]
  createdAt      DateTime @default(now())
  @@index([orgId, createdAt])
  @@index([ownerId])
}

model Chunk {
  id          String @id @default(cuid())
  documentId  String
  content     String @db.Text
  embedding   Unsupported("vector(1536)")?
  metadata    Json?
  @@index([documentId])
}

// pgvector extension + HNSW index via migration SQL
// CREATE INDEX ON "Chunk" USING hnsw (embedding vector_cosine_ops);
```

**Indexing Strategy:**
- B-Tree برای `orgId, createdAt` , `email`, `status`
- GIN برای `metadata JSONB`, `FTS`
- HNSW برای `embedding` (cosine)
- Partial index برای `status = 'READY'`

**Partitioning/Sharding:**
- **Phase 1:** Single Primary + Read Replica
- **Phase 2 (>1M rows/month):** Partition `audit_logs`, `messages` by RANGE (month) + pg_partman
- **Phase 3 (>10M):** Citus یا جداسازی Vector DB به Qdrant (sharded)

**Migration:** Prisma Migrate + `shadow DB` + `expand-contract` pattern (add column nullable → backfill → make not null)

**Backup & Recovery:**
- PITR با WAL-G → S3, Retention 30 روز, Point-in-time recovery تست ماهانه
- `pg_basebackup` روزانه + `barman`, RTO 15min, RPO 5min
- اسکریپت `make db-restore PITR=2026-09-08T10:00:00Z`

**GDPR:**
- `deletedAt` soft delete + `anonymize()` job (30 روز پس از درخواست)
- ستون `data_retention_expires_at`, Encryption at rest (AES-256), Column-level encryption برای PII با `pgcrypto`

#### 3. 🛠️ Tech Stack
- PostgreSQL 16 + pgvector 0.7, Prisma 5, PGBouncer, WAL-G, pg_partman

#### 4. 📁 Structure
```
/prisma
  schema.prisma
  migrations/
  seed.ts
/packages/db
  client.ts
  extensions/vector.ts
```

#### 5. ⚠️ Pitfalls
- ذخیره embedding به صورت JSON → حتماً `vector` type
- N+1 query → Prisma `include` + DataLoader
- عدم vacuum برای HNSW → autovacuum tuning

#### 6. 📊 Effort
- **12-15 روز** (Backend + DBA). SP: 40

#### 7. 🔗 Dependencies
- L2 → L4, L5, L12 (caching)

---

### ▶ LAYER 4 — API DESIGN & CONTRACT

#### 1. ✅ Executive Summary
API قرارداد محصول است. طراحی **RESTful + OpenAPI 3.1** با versioning در URL (`/api/v1`), idempotency, pagination استاندارد و Webhook برای events. Gateway وظیفه rate limiting و auth را دارد.

#### 2. 🏗️ Detailed Implementation Plan
**Style:** REST (JSON:API-ish) + تعداد محدودی RPC برای AI (`/v1/chat/completions` سازگار با OpenAI). GraphQL در فاز 2 اگر نیاز Frontend پیچیده شد (فعلاً نه).

**OpenAPI ساختار:**

```yaml
openapi: 3.1.0
info: { title: cutting-edge-v2 API, version: 1.0.0 }
servers: [{ url: https://api.cutting-edge.app/api/v1 }]
paths:
  /documents:
    post:
      summary: Upload document
      security: [{ bearerAuth: [] }]
      requestBody:
        content: { multipart/form-data: { schema: { type: object, properties: { file: {type: string, format: binary} } } } }
      responses: { '201': { description: Created, content: { application/json: { schema: { $ref: '#/components/schemas/Document' } } } } }
  /chat:
    post:
      parameters: [{ name: Idempotency-Key, in: header, required: true }]
```

**Versioning:** URL versioning (`/api/v1` → `/api/v2` breaking), Header `Accept: application/vnd.api.v1+json` برای minor. Deprecation header: `Sunset: Sat, 31 Dec 2026 23:59:59 GMT`

**Rate Limiting:**
- Tiered: Free 60 req/min, Pro 600, Enterprise 6000 (Redis sliding window)
- Headers: `X-RateLimit-Remaining`, `Retry-After`
- Gateway: Kong / AWS API Gateway / Cloudflare Workers (پیشنهاد: **Kong** برای self-host یا **Cloudflare** برای سرعت)

**Idempotency & Pagination:**
- `Idempotency-Key: uuid` برای POST (ذخیره 24h در Redis)
- Cursor pagination: `?cursor=ey...&limit=20` نه offset

**Webhook:**
```json
{
  "event": "document.ready",
  "data": { "documentId": "doc_123", "orgId": "org_1" },
  "signature": "sha256=..."
}
```
Retry with exponential backoff (1m,5m,30m), HMAC verification.

**Docs:** Swagger UI + Redoc + SDK auto-gen (openapi-generator → `packages/sdk-js`)

#### 3. 🛠️ Stack
- OpenAPI 3.1, Swagger, Redoc, Kong/Cloudflare, openapi-generator, Zod برای validation

#### 4. 📁 Structure
```
/apps/api/src/modules/document
  document.controller.ts
  dto/create-document.dto.ts
/openapi
  openapi.yaml
/packages/sdk-js
```

#### 5. ⚠️ Pitfalls
- Breaking change بدون version → حتماً contract test (Pact)
- عدم idempotency برای billing → double charge

#### 6. 📊 Effort
- **8-10 روز**. SP: 26

#### 7. 🔗 Dependencies
- L2, L3 → L5, L6, L8

---

### ▶ LAYER 5 — BACKEND ARCHITECTURE

#### 1. ✅ Executive Summary
بک‌اند با **NestJS + Clean Architecture + DDD** پیاده‌سازی می‌شود: کنترلر نازک، سرویس غنی، ریپازیتوری انتزاعی، دامنه خالص. CQRS سبک برای Chat/Ingestion و صف برای کارهای سنگین.

#### 2. 🏗️ Detailed Implementation Plan
**Layers:**

```
Controller (HTTP, Zod validation) 
  → UseCase/Service (business logic, transaction)
    → Domain (Entity, ValueObject, DomainEvent)
      → Repository (Prisma)  +  Infrastructure (S3, LLM, Queue)
```

**CQRS:** فقط برای `Ingestion` (Command: Upload → Event: DocumentUploaded → Handler: Chunk & Embed) و `Chat` (Query: RAG). Event Sourcing کامل نه — فقط Event Bus + Outbox pattern.

**Repository Pattern:**

```typescript
// domain/repositories/document.repository.ts
export interface DocumentRepository {
  create(data: CreateDocument): Promise<Document>;
  findById(id: string): Promise<Document | null>;
}

// infrastructure/prisma-document.repository.ts
@Injectable()
export class PrismaDocumentRepository implements DocumentRepository {
  constructor(private prisma: PrismaService) {}
  create(data) { return this.prisma.document.create({ data }); }
}
```

**Queue & Jobs:** BullMQ + Redis برای `embed-document`, `send-email`, `generate-report`. Retry 3x, DLQ, cron با `@nestjs/schedule`.

**Error Handling:**

```typescript
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(e, host) {
    const traceId = randomUUID();
    this.logger.error({ traceId, err: e });
    // Sentry.captureException(e, { extra: { traceId } })
  }
}
```

**DI:** NestJS built-in, `@Module` per bounded context.

**Background:** Worker process جدا (`apps/worker`) که صف را مصرف می‌کند — scale مستقل از API.

#### 3. 🛠️ Stack
- NestJS 10, Prisma, BullMQ, Zod, Pino, OpenTelemetry, Jest

#### 4. 📁 Structure
```
/apps
  /api/src/modules/{auth,document,chat,billing}
    {module}.module.ts
    {module}.controller.ts
    {module}.service.ts
    dto/
    domain/
  /worker/src/processors
    embed.processor.ts
/packages
  /shared (constants, errors, logger)
```

#### 5. ⚠️ Pitfalls
- Fat controller / Anemic domain → حتماً logic در Service/Domain
- Sync embedding در request → حتماً async via queue

#### 6. 📊 Effort
- **25-30 روز** (2 backend). SP: 80

#### 7. 🔗 Dependencies
- L2, L3, L4 → L6, L12, L13

---

### ▶ LAYER 6 — FRONTEND ARCHITECTURE

#### 1. ✅ Executive Summary
فرانت با **Next.js 15 App Router + React 19 + TypeScript + Tailwind + shadcn/ui** به صورت SSR/ISR ترکیبی، با مدیریت حالت سبک (Zustand + TanStack Query) و بهینه‌سازی Core Web Vitals.

#### 2. 🏗️ Detailed Implementation Plan
**Component Hierarchy:**

```
app/
  (marketing)/page.tsx (SSG)
  (app)/dashboard/page.tsx (SSR, protected)
  api/ (Route Handlers proxy)
components/
  ui/ (shadcn: Button, Dialog)
  features/chat/ (ChatWindow, Message, Citation)
  layouts/
lib/
  api-client.ts (fetch + retry + auth)
  hooks/
stores/
  useChatStore.ts (Zustand)
```

**State:**
- Server State: TanStack Query (cache, refetch, optimistic update)
- Client State: Zustand (chat input, UI)
- Form: React Hook Form + Zod resolver

**Routing:** App Router, Parallel Routes برای modal (`@modal`), Intercepting Routes, Middleware برای auth (`middleware.ts` → redirect if !session).

**Rendering:**
- Marketing: **SSG** + ISR (revalidate 60s)
- Dashboard: **SSR** (auth) + CSR برای chat realtime
- Document viewer: **ISR** + Edge caching

**Bundle Opt:**
- `next/bundle-analyzer`, dynamic import برای `pdf-viewer`, `recharts`
- `sharp` برای image, `next/font` برای فونت, `serverComponents` external packages

**SEO:**
- `next-seo`, `sitemap.ts`, `robots.ts`, JSON-LD, OG image dynamic (`opengraph-image.tsx`)

**A11y:** `eslint-plugin-jsx-a11y`, `axe-core` در CI, keyboard nav, focus ring

**Perf Targets:** LCP <2.5s, INP <200ms, CLS <0.1, Bundle <200KB gz

#### 3. 🛠️ Stack
- Next.js 15, React 19, TypeScript 5, Tailwind 3, shadcn/ui, Zustand, TanStack Query, Playwright

#### 4. 📁 Structure
```
/apps/web
  app/
  components/
  lib/
  stores/
  public/
```

#### 5. ⚠️ Pitfalls
- Client component همه‌جا → حتماً Server Component default
- Waterfall fetch → از `Promise.all` + `Suspense`

#### 6. 📊 Effort
- **20-25 روز** (2 frontend). SP: 65

#### 7. 🔗 Dependencies
- L4, L5, L7

---

### ▶ LAYER 7 — UI/UX DESIGN SYSTEM & MOTION

#### 1. ✅ Executive Summary
سیستم طراحی **Token-based** با Tailwind + CSS Variables، تم روشن/تاریک، و انیمیشن‌های معنادار (Framer Motion) که حس «AI زنده» می‌دهد بدون آزار کاربر.

#### 2. 🏗️ Detailed Implementation Plan
**Design Tokens:**

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --primary: 221 83% 53%; /* #3B82F6 */
  --radius: 0.75rem;
  --font-sans: 'Inter', system-ui;
  --shadow-soft: 0 4px 20px rgba(0,0,0,0.06);
}
.dark { --background: 222 47% 4%; --foreground: 210 40% 98%; }
```

**Typography Scale:** `text-xs(12) → text-4xl(36)`, line-height 1.5-1.7, clamp برای fluid
**Spacing:** 4pt grid (4,8,12,16,24,32)
**Component lib:** shadcn/ui (Radix headless + Tailwind) — سفارشی‌سازی با `cva`

**Motion Principles:**
- Duration: 150-300ms, Easing: `ease-out` (enter), `ease-in` (exit)
- Chat stream: typewriter + fade-in per token (Framer Motion `AnimatePresence`)
- Skeleton + optimistic UI برای هر async

```tsx
<motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{duration:0.2}}>
  <Message />
</motion.div>
```

**Dark/Light:** `next-themes`, `prefers-color-scheme`, toggle با `localStorage`, جلوگیری از FOUC با `suppressHydrationWarning`

**Breakpoints:** `sm:640, md:768, lg:1024, xl:1280, 2xl:1536` + Container Queries برای کارت‌ها

**Design-to-Code:** Figma Tokens → `style-dictionary` → Tailwind config, Storybook برای مستندسازی

#### 3. 🛠️ Stack
- Figma, Tokens Studio, Style Dictionary, Tailwind, shadcn/ui, Framer Motion, Storybook 8

#### 4. 📁 Structure
```
/apps/web/components/ui
/packages/design-tokens
  tokens.json
  tailwind.preset.ts
```

#### 5. ⚠️ Pitfalls
- انیمیشن زیاد → باتری/حرکت‌زدگی → `prefers-reduced-motion`
- رنگ بدون کنتراست → چک WCAG AA (4.5:1)

#### 6. 📊 Effort
- **10-12 روز** (1 designer + 1 FE). SP: 30

#### 7. 🔗 Dependencies
- L6

---

### ▶ LAYER 8 — AUTHENTICATION & AUTHORIZATION

#### 1. ✅ Executive Summary
احراز هویت **Auth.js (NextAuth v5) + JWT (short-lived) + Refresh Rotation + RBAC** . MVP با Email/OAuth، Enterprise با SAML SSO.

#### 2. 🏗️ Detailed Implementation Plan
**Strategy:** 
- Web: `httpOnly, Secure, SameSite=Lax` cookie با JWT (15min) + Refresh (7 days, rotation)
- Mobile/API: `Bearer` + `API Keys` (prefix `sk_live_...`, hashed in DB)
- OAuth2: Google, GitHub (NextAuth providers)

**RBAC Model:**

```prisma
model OrganizationMember {
  userId String
  orgId  String
  role   Role // OWNER, ADMIN, MEMBER, VIEWER
  @@id([userId, orgId])
}
enum Role { OWNER ADMIN MEMBER VIEWER }
// ABAC later: policies JSON { "action": "document:delete", "condition": "ownerId==userId" }
```

Middleware:

```typescript
// middleware.ts
export function middleware(req: NextRequest) {
  const token = req.cookies.get('access_token');
  if (!token && req.nextUrl.pathname.startsWith('/dashboard')) 
    return NextResponse.redirect(new URL('/login', req.url));
}
```

**MFA:** TOTP (speakeasy) + backup codes, enforce برای ADMIN

**Token Refresh:**

```
Client 401 → /api/auth/refresh (with refresh_token cookie) → new access_token → retry original
Refresh rotation: old token invalidated, theft detection (reuse → revoke all)
```

**Session:** Redis store `sess:{jti}` با TTL, revoke on logout/password change

**SSO Enterprise:** SAML via WorkOS/Auth0, SCIM provisioning

#### 3. 🛠️ Stack
- Auth.js, Lucia (alternative), jose (JWT), bcrypt/argon2, Speakeasy, WorkOS

#### 4. 📁 Structure
```
/apps/api/src/modules/auth
  strategies/jwt.strategy.ts
  guards/roles.guard.ts
/apps/web/app/(auth)/login/page.tsx
```

#### 5. ⚠️ Pitfalls
- JWT در localStorage → XSS → حتماً httpOnly cookie
- عدم revoke refresh → theft risk

#### 6. 📊 Effort
- **10-12 روز**. SP: 34

#### 7. 🔗 Dependencies
- L3, L5, L9

---

### ▶ LAYER 9 — SECURITY & COMPLIANCE

#### 1. ✅ Executive Summary
امنیت به عنوان **Shift-Left**: از OWASP Top 10 تا CSP، secrets در Vault، audit log تغییرناپذیر و انطباق GDPR/SOC2 از معماری.

#### 2. 🏗️ Detailed Implementation Plan
**OWASP Checklist:**
- A01 Broken Access: RBAC guard + tests
- A02 Crypto: TLS 1.3, AES-256 at rest, Argon2id
- A03 Injection: Zod + Prisma parameterized + DOMPurify
- A04 Insecure Design: Threat modeling (STRIDE)
- A07 Auth: MFA + rate limit login (5/min IP)
- A08 Data Integrity: SLSA, signed commits

**Input Validation:** Zod در Controller + `class-validator` + sanitization (`xss` lib)

**Security Headers (Next.js):**

```typescript
// next.config.js
headers: async () => [{ source: '/(.*)', headers: [
  { key: 'Content-Security-Policy', value: "default-src 'self'; script-src 'self' 'unsafe-inline'; connect-src 'self' https://api.openai.com" },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  { key: 'X-Frame-Options', value: 'DENY' },
]}]
```

**Secrets:** Doppler / HashiCorp Vault / AWS Secrets Manager, never `.env` in git, `git-secrets` hook

**Pentest:** OWASP ZAP در CI + annual external pentest

**Audit Log:** Append-only table `audit_logs` (who, what, when, where, before/after) + immutability via trigger

**Compliance:**
- GDPR: DPA, Right to erasure, Data minimization, EU data residency option
- SOC2: Logging, Access control, Backup evidence
- Dependency scan: `npm audit`, Snyk, Dependabot, `trivy` for images

#### 3. 🛠️ Stack
- Helmet, Zod, DOMPurify, Snyk, Trivy, OWASP ZAP, Vault/Doppler, Cloudflare WAF

#### 4. 📁 Structure
```
/apps/api/src/common/filters
/security
  csp.config.ts
  audit.interceptor.ts
```

#### 5. ⚠️ Pitfalls
- Log کردن PII/secrets → Pino redaction
- CORS `*` → whitelist

#### 6. 📊 Effort
- **8-10 روز** + continuous. SP: 28

#### 7. 🔗 Dependencies
- L5, L8, L10

---

### ▶ LAYER 10 — DEVOPS & CI/CD PIPELINE

#### 1. ✅ Executive Summary
پایپ‌لاین **Trunk-based + GitHub Actions + ArgoCD** با کیفیت‌گیت (lint, test, SAST, build, scan) و استقرار Blue/Green یا Canary + Feature Flags.

#### 2. 🏗️ Detailed Implementation Plan
**Branching:** Trunk-based (main is always deployable) + short-lived `feat/*` ≤2 روز, PR squash, Conventional Commits (`feat:`, `fix:`)

**CI Pipeline (.github/workflows/ci.yml):**

```yaml
name: CI
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint && pnpm typecheck
      - run: pnpm test --coverage --maxWorkers=2
      - run: pnpm audit
      - uses: trufflesecurity/trufflehog@main # secrets
      - run: docker build -t app:${{ github.sha }} .
      - run: trivy image app:${{ github.sha }}
```

**CD:** `main` → Staging auto (ArgoCD sync), `tag v*` → Production با approval

**Environments:** `dev (local Docker Compose) → staging (K8s namespace) → prod (K8s + managed DB)`

**Deployment:**
- **Blue/Green** برای API (2 deployment, switch service)
- **Canary** 10% → 50% → 100% با Flagger + Prometheus metrics (error rate <1%)

**Rollback:** `kubectl rollout undo` + DB expand-contract (rollback safe), ArgoCD auto-rollback on health fail

**Feature Flags:** LaunchDarkly / OpenFeature + Unleash (self-host) → `if (await flags.isEnabled('rag-v2', user))`

**Testing in Pipeline:** Unit (Jest) → Integration (Supertest + Testcontainers) → E2E (Playwright) → Load (k6) on staging

#### 3. 🛠️ Stack
- GitHub Actions, Docker, ArgoCD, Flagger, Unleash, Trivy, k6

#### 4. 📁 Structure
```
/.github/workflows/ci.yml
/.github/workflows/cd.yml
/deploy
  /helm/cutting-edge
  /k8s/staging
  /k8s/prod
```

#### 5. ⚠️ Pitfalls
- Long-lived branches → merge hell → trunk-based
- No staging parity → از Testcontainers + ephemeral env

#### 6. 📊 Effort
- **12-15 روز** (DevOps). SP: 42

#### 7. 🔗 Dependencies
- L11, L14

---

### ▶ LAYER 11 — INFRASTRUCTURE & CLOUD

#### 1. ✅ Executive Summary
زیرساخت **Cloud-agnostic اما AWS-first** (یا Hetzner برای cost-optimize) با IaC (Terraform), Kubernetes (EKS/ K3s) و Multi-AZ + DR.

#### 2. 🏗️ Detailed Implementation Plan
**Provider:** **AWS** (EKS, RDS PostgreSQL, ElastiCache Redis, S3, CloudFront) — جایگزین: **Contabo/Hetzner + Cloudflare R2** اگر بودجه startup (<$500/mo). Justify: اکوسیستم کامل، SOC2 ready.

**IaC:**

```
/infra/terraform
  modules/{vpc,eks,rds,redis,s3}
  envs/{staging,prod}/main.tf
  backend.tf (S3 + DynamoDB lock)
```

```hcl
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"
  cluster_version = "1.30"
  node_groups = { main = { desired_capacity = 3, instance_types = ["t3.medium"] } }
}
```

**Orchestration:** **Kubernetes (EKS)** + Helm, HPA (CPU 60% → scale 3-10), VPA برای worker. Alternative برای شروع سبک: **Docker Compose on VM + Coolify** (هزینه 1/5) سپس مهاجرت به K8s.

**CDN:** Cloudflare (free tier عالی) یا CloudFront, cache static + image optimization

**LB:** ALB (L7) + NLB برای gRPC اگر لازم شد

**Auto-scaling:** HPA + Cluster Autoscaler + KEDA برای queue (BullMQ length >100 → scale worker)

**Multi-region/DR:**
- Pilot-light: S3 cross-region replication + RDS snapshot cross-region, RTO 2h, RPO 1h
- بعداً Active-Active با Route53 latency routing

**Cost Opt:** Karpenter for spot, S3 Intelligent-Tiering, RDS Graviton, `infracost` در PR

#### 3. 🛠️ Stack
- Terraform, Terragrunt, Helm, EKS/K3s, ArgoCD, Karpenter, Infracost

#### 4. 📁 Structure
```
/infra
  /terraform
  /helm
  /scripts
```

#### 5. ⚠️ Pitfalls
- Over-provision → از ابتدا request/limits + HPA
- State در local → حتماً remote backend

#### 6. 📊 Effort
- **15-18 روز**. SP: 50

#### 7. 🔗 Dependencies
- L10, L13

---

### ▶ LAYER 12 — CACHING & PERFORMANCE

#### 1. ✅ Executive Summary
استراتژی **4 لایه کش** + بهینه‌سازی دیتابیس و Asset برای رسیدن به p95 <300ms و هزینه LLM بهینه.

#### 2. 🏗️ Detailed Implementation Plan
**Layers:**
1. **Browser:** `Cache-Control: public, max-age=31536000, immutable` برای static, `stale-while-revalidate` برای ISR
2. **CDN:** Cloudflare cache `/api/v1/documents` با `ETag`, purge on mutation
3. **Application (Redis):**
   - `cache:org:{id}:docs` TTL 60s
   - `ratelimit:{user}` sliding window
   - `rag:{queryHash}` TTL 5min (برای سوال تکراری)
   - `session:{jti}` 
4. **Database:** `pg_stat_statements` + `EXPLAIN ANALYZE`, materialized view برای dashboard

**Redis Strategy:**

```typescript
await redis.set(`rag:${hash}`, JSON.stringify(result), 'EX', 300); // 5m
// Cache-aside with stampede protection (lock)
```

**DB Tuning:** `work_mem`, `shared_buffers`, `pgbouncer` pool 20, index on `createdAt DESC`

**Asset Opt:**
- Images: `next/image` + AVIF, `sharp`, lazy + `blurDataURL`
- Fonts: `next/font` self-host, `display: swap`
- JS: `dynamic(() => import('./Heavy'))`, `React.lazy`, `bundle < 200KB`

**Perf Budgets (Lighthouse CI):**

```json
{ "budgets": [{ "resourceType": "script", "budget": 200 }, { "resourceType": "image", "budget": 500 }] }
```

**Lazy:** `IntersectionObserver` برای chat history, virtualized list (`react-virtuoso`) برای 10K messages

#### 3. 🛠️ Stack
- Redis 7, Cloudflare, PGBouncer, Lighthouse CI, Bundle Analyzer

#### 4. 📁 Structure
```
/apps/api/src/common/cache
  redis.module.ts
  cache.interceptor.ts
```

#### 5. ⚠️ Pitfalls
- Cache invalidation سخت → از key versioning (`v1:`) + event-based purge
- Caching PII → حتماً `private` + user-scoped key

#### 6. 📊 Effort
- **8-10 روز**. SP: 26

#### 7. 🔗 Dependencies
- L3, L5, L11

---

### ▶ LAYER 13 — MONITORING & OBSERVABILITY

#### 1. ✅ Executive Summary
Observability سه‌ستونه **Logs + Metrics + Traces** با OpenTelemetry, Prometheus, Grafana, Sentry و Uptime + On-call.

#### 2. 🏗️ Detailed Implementation Plan
**Logging:** Pino structured JSON (`level, time, traceId, orgId, userId, msg`) → Loki / CloudWatch, sampling برای high volume, redaction برای secrets

**Tracing:** OpenTelemetry SDK + OTLP → Tempo/Jaeger, trace هر `/api/chat` از FE تا LLM provider, `traceId` در header `X-Trace-Id`

```typescript
// instrumentation.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
new NodeSDK({ instrumentations: [getNodeAutoInstrumentations()] }).start();
```

**Metrics:** Prometheus + Grafana dashboards:
- RED: Rate, Error, Duration (p50,p95,p99)
- AI: tokens/sec, hallucination rate, embedding latency
- Infra: CPU, memory, queue depth

**Error Tracking:** Sentry (FE+BE) با release + sourcemap, alert on new issue

**Uptime:** Better Stack / UptimeRobot → check `/health` هر 30s از 3 region

**Alerting:**

```yaml
# prometheus rule
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
  for: 2m
  labels: { severity: page }
  annotations: { runbook: "https://wiki/runbooks/high-error" }
```

Escalation: PagerDuty/Opsgenie → Slack `#incidents` → On-call rotation (weekly)

**SLI/SLO/SLA:**
- SLI: Availability (200/5xx), Latency p95, AI Success Rate
- SLO: 99.9% avail (43m downtime/month), p95 <400ms, AI relevance >4/5
- SLA: 99.5% برای Enterprise (credit 10% if breach)

**Runbook:** `/docs/runbooks/{incident-template.md, db-failover.md, llm-outage.md}`

#### 3. 🛠️ Stack
- OpenTelemetry, Prometheus, Grafana, Loki, Tempo, Sentry, PagerDuty, Better Stack

#### 4. 📁 Structure
```
/apps/api/src/observability
  tracing.ts
  metrics.ts
/deploy/grafana/dashboards
/docs/runbooks
```

#### 5. ⚠️ Pitfalls
- Log بی‌ساختار → غیرقابل جستجو → حتماً JSON + traceId
- Alert fatigue → فقط page برای SLO breach

#### 6. 📊 Effort
- **10-12 روز**. SP: 34

#### 7. 🔗 Dependencies
- L5, L10, L11

---

### ▶ LAYER 14 — TESTING STRATEGY

#### 1. ✅ Executive Summary
هرم تست **70% Unit + 20% Integration + 10% E2E** با پوشش ≥80% , تست قرارداد، لود و امنیت و AI evaluation.

#### 2. 🏗️ Detailed Implementation Plan
**Pyramid:**

```
          E2E (Playwright, 10%)
     Integration (Supertest + Testcontainers, 20%)
    Unit (Jest/Vitest, 70%)
   ──────────────────────────────────
   Static: ESLint, TypeScript, SAST
```

**Unit:**

```typescript
describe('RagService', () => {
  it('should retrieve top 5 chunks', async () => {
    const result = await rag.retrieve('قرارداد چیست؟', { topK: 5 });
    expect(result).toHaveLength(5);
  });
});
```

**Integration:** Testcontainers (Postgres + Redis + S3 mock via LocalStack), `pnpm test:integration`

**E2E:** Playwright ( Chromium, Firefox, Mobile), `npx playwright test --project=chromium`, visual regression با `toHaveScreenshot`

**Coverage:** `jest --coverage --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80}}'`, fail CI if <80%

**Load:** k6

```javascript
import http from 'k6/http';
export default function() { http.post('https://api.cutting-edge.app/api/v1/chat', JSON.stringify({q:'test'}), {headers:{Authorization:'Bearer ...'}}); }
export const options = { stages: [{duration:'2m', target:100}, {duration:'5m', target:100}, {duration:'2m', target:0}] };
```

**Contract:** Pact برای `web → api`

**Security:** SAST (Semgrep, CodeQL), DAST (OWASP ZAP), Dependency (Snyk)

**A11y:** `axe-playwright`, `pa11y`

**Visual:** Chromatic / Percy برای Storybook

**AI Eval:** Dataset 100 Q/A طلایی + RAGAS metrics (faithfulness, relevance) + LLM-as-judge, run nightly

#### 3. 🛠️ Stack
- Vitest/Jest, Supertest, Testcontainers, Playwright, k6, Pact, Semgrep, RAGAS

#### 4. 📁 Structure
```
/apps/api/test
  unit/
  integration/
  e2e/
/apps/web/e2e
  chat.spec.ts
/k6
  load.js
```

#### 5. ⚠️ Pitfalls
- Flaky E2E → از `waitFor` درست + isolation با test org
- Mock بیش از حد → integration بدون mock

#### 6. 📊 Effort
- **15-18 روز** (continuous). SP: 48

#### 7. 🔗 Dependencies
- همه لایه‌ها (به‌ویژه L5, L6, L15)

---

### ▶ LAYER 15 — AI & AUTOMATION LAYER ⭐ (قلب درخواست شما — تماماً AI)

#### 1. ✅ Executive Summary
این لایه تفاوت cutting-edge-v2 با SaaS معمولی است: **RAG پیشرفته + Agent خودمختار + Evaluation + Automation** که هم محصول را هوشمند می‌کند و هم فرآیند توسعه را 100% با AI می‌سازد.

#### 2. 🏗️ Detailed Implementation Plan

**A. معماری AI Product:**

```
[User Query] → [Guardrails] → [Query Rewriter (LLM)] → [Retriever (Hybrid: BM25 + Vector HNSW)] 
  → [Reranker (Cohere)] → [Context Compressor] → [LLM Generator (GPT-4o / Claude 3.5 + Function Calling)] 
  → [Citation] → [Evaluator] → [Response Stream]
```

**Stack:**
- **LLM Gateway:** OpenAI primary, Anthropic fallback, abstraction `LLMProvider` interface + retry + fallback
- **Embeddings:** `text-embedding-3-large` (3072d → 1536 با Matryoshka) یا `bge-m3` خودمیزبان برای حریم خصوصی
- **Vector:** pgvector شروع → Qdrant (HNSW, payload filtering) در اسکیل
- **Orchestration:** LangChain / LlamaIndex سبک یا **کد خام** (پیشنهاد: کد خام + Vercel AI SDK برای کنترل بیشتر)
- **Reranker:** Cohere Rerank v3
- **Eval:** RAGAS + Phoenix (Arize) + LangSmith

**B. RAG Pipeline گام‌به‌گام:**

1. **Ingestion:** Upload → S3 → Queue `ingest` → `unstructured` / `pymupdf` → Chunk (Recursive 800 tokens, overlap 100) → Embed → Upsert
2. **Retrieval:** Hybrid search (`vector_cosine 0.7 + BM25 0.3`), filter by `orgId`, topK 20 → Rerank → top 5
3. **Generation:**

```typescript
// apps/api/src/modules/chat/rag.service.ts
import { openai } from '@/lib/llm';
export async function generateAnswer(query: string, chunks: Chunk[]) {
  const context = chunks.map(c => `[${c.metadata.page}] ${c.content}`).join('\n---\n');
  const stream = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    temperature: 0.2,
    messages: [
      { role: 'system', content: 'You are cutting-edge assistant. Answer ONLY from context. Cite sources like [1][2]. If not in context, say "در منابع شما نیافتم".' },
      { role: 'user', content: `Context:\n${context}\n\nQuestion: ${query}` }
    ],
    stream: true,
  });
  return stream;
}
```

4. **Guardrails:** PII redaction, Prompt injection detection (LLM classifier), Hallucination check (self-consistency)

**C. AI Agent Design (Autonomous):**

- **Agent Type:** ReAct + Function Calling
- **Tools:** `searchDocs`, `createTask`, `sendEmail`, `queryDB`
- **Framework:** Vercel AI SDK `tool` + `maxSteps: 5` یا LangGraph برای stateful
- **Memory:** Short-term (conversation) + Long-term (vector store of user preferences)
- **Example:** Agent «تحلیل قرارداد» → upload PDF → extract clauses → risk score → draft email

```typescript
import { tool } from 'ai';
const searchDocs = tool({
  description: 'Search org documents',
  parameters: z.object({ query: z.string() }),
  execute: async ({ query }) => rag.retrieve(query),
});
```

**D. Workflow Automation:**
- **n8n / Trigger.dev** برای automation بدون کدنویسی: `New Document → Auto-Summarize → Slack notify`
- **Background AI Jobs:** BullMQ `ai:summarize`, `ai:embed`, `ai:evaluate`

**E. Data Pipeline for AI:**
- **ETL:** Airbyte / custom → S3 → dbt (clean) → Vector DB
- **Feedback Loop:** کاربر 👍/👎 → ذخیره در `ai_feedback` → nightly fine-tune dataset → eval
- **Versioning:** DVC برای embeddings + Prompt versioning در `prompts/` با git

**F. Model Evaluation & Monitoring:**
- **Offline:** Dataset طلایی 200 Q/A → RAGAS (faithfulness >0.85, answer_relevancy >0.9)
- **Online:** LLM-as-judge (GPT-4) امتیاز هر پاسخ + Human review queue اگر score <3.5
- **Drift:** Phoenix → embedding drift alert, cost per 1K tokens dashboard

**G. Prompt Engineering Guidelines (در `/prompts`):**

```markdown
# prompts/system-rag.md (version 2.1)
Role: You are ...
Constraints: 1) Only use context 2) Cite 3) Language = fa (user lang)
Output: JSON { answer, citations: [{chunkId, page}], followUps: string[] }
```

- Few-shot, Chain-of-Thought (hidden), JSON mode
- Prompt lint + test در CI (`promptfoo eval`)

**H. AI-Augmented SDLC (توسعه 100% با AI — پاسخ به "تماماً Ai"):**

| مرحله SDLC | عامل AI | ابزار | خروجی |
|---|---|---|---|
| **PRD & Design** | PM Agent | ChatGPT, Claude, Figma AI | PRD draft, Figma wireframe |
| **Coding** | Dev Agent | Cursor, Copilot, Codeium, Aider | 70% کد اولیه |
| **Review** | Reviewer Agent | CodeRabbit, Greptile, Sonar AI | PR review + suggestions |
| **Testing** | QA Agent | Codium, Mutahunter, Playwright AI | تست‌های unit/integration auto |
| **Docs** | Docs Agent | Mintlify, Codeium | README, OpenAPI descriptions |
| **DevOps** | Ops Agent | Harness AI, K8s GPT | Terraform + Helm + runbook |
| **Monitoring** | SRE Agent | Sentry AI, Grafana LLM | خلاصه incident + پیشنهاد fix |

**Workflow نمونه:**

```bash
# Developer prompt to Cursor:
"Generate NestJS module for Document with CRUD, Prisma, Zod, tests — follow clean architecture"
# AI generates 80% → human reviews 20% → merge
```

**قوانین طلایی AI-First:**
1. هر PR باید توسط AI review شود قبل از human
2. هر prompt در git version شود
3. هر خروجی AI دارای eval و human approval برای prod
4. Cost guard: بودجه ماهانه LLM = $500 → alert در 80%

#### 3. 🛠️ Stack
- **LLM:** OpenAI, Anthropic, OpenRouter (fallback), Vercel AI SDK
- **Vector:** pgvector, Qdrant, Cohere Rerank
- **Eval:** RAGAS, Phoenix, LangSmith, Promptfoo, Braintrust
- **Automation:** Trigger.dev, n8n, BullMQ
- **SDLC AI:** Cursor, Copilot, CodeRabbit, Codium

#### 4. 📁 Structure
```
/apps/api/src/modules/ai
  llm/
    provider.interface.ts
    openai.provider.ts
    anthropic.provider.ts
  rag/
    ingestion.service.ts
    retrieval.service.ts
    reranker.ts
  agent/
    tools/
    graph.ts
/prompts
  system-rag.md
  agent-react.md
/evals
  dataset.jsonl
  ragas.config.ts
/packages/ai-shared
```

#### 5. ⚠️ Pitfalls
- Hallucination بدون citation → حتماً RAG + guardrail
- Vendor lock-in → abstraction layer
- Prompt injection → input sanitization + classifier
- Cost explosion → cache + smaller model برای rerank/rewrite
- عدم eval → «AI خوبه!» ذهنی → حتماً RAGAS nightly

#### 6. 📊 Effort
- **25-30 روز** (AI Engineer + Backend). SP: 85 (بزرگ‌ترین لایه)

#### 7. 🔗 Dependencies
- L3 (vector), L5 (backend), L12 (cache), L13 (monitoring), L14 (eval)

---

### ▶ LAYER 16 — DOCUMENTATION & DEVELOPER EXPERIENCE

#### 1. ✅ Executive Summary
مستندسازی **living** و DX عالی = سرعت onboarding <1 روز. Docs as Code با auto-generation از OpenAPI و کد.

#### 2. 🏗️ Detailed Implementation Plan
**Architecture Docs:** `docs/architecture` + C4 + ADR (Log4brains site)

**API Docs:** Redoc + Swagger UI auto از OpenAPI, SDK docs, Postman collection auto

**Onboarding Guide:** `CONTRIBUTING.md` + `make dev` یک‌دستوری

```bash
# One-command dev
git clone ... && pnpm install && cp .env.example .env && docker compose up -d && pnpm dev
# → web http://localhost:3000, api http://localhost:4000
```

**Runbooks:** `/docs/runbooks` (template: Symptom, Diagnosis, Mitigation, Prevention)

**Changelog:** `CHANGELOG.md` via `semantic-release` + Conventional Commits → auto version + GitHub Release

**Wiki Structure:**

```
/docs
  /getting-started (5min quickstart)
  /architecture
  /api
  /runbooks
  /adr
  /evals
```

**Developer Portal:** **Backstage** (اگر تیم >10) یا **Mintlify** / **Docusaurus** برای خارجی + **Storybook** برای UI

**DX Extras:**
- `pnpm dlx` generators: `pnpm gen:module chat`
- Dev container (`.devcontainer/devcontainer.json`) برای Codespaces
- AI assistant در repo: `cursor` rules در `.cursorrules`

```yaml
# .cursorrules
You are expert NestJS+Next.js. Always use Prisma, Zod, clean architecture. No any.
```

#### 3. 🛠️ Stack
- Docusaurus/Mintlify, Redoc, Storybook, Backstage, semantic-release, Dev Containers

#### 4. 📁 Structure
```
/docs
  README.md
  CONTRIBUTING.md
  CHANGELOG.md
  /api
  /architecture
  /runbooks
/.devcontainer
/.cursorrules
```

#### 5. ⚠️ Pitfalls
- Docs جدا از کد → قدیمی → حتماً docs-as-code + CI check
- عدم onboarding → هر hire جدید docs را بهبود دهد

#### 6. 📊 Effort
- **6-8 روز**. SP: 20

#### 7. 🔗 Dependencies
- همه لایه‌ها (تجمیعی)

---

## 📐 نقشه راه تجمیعی + تخمین کل

| فاز | هفته | لایه‌ها | خروجی |
|---|---|---|---|
| **0 — Foundation** | 1-2 | L1, L2, L3, L10, L11 (infra as code) | PRD + Arch + DB + CI/CD + Env |
| **1 — MVP Build** | 3-10 | L4, L5, L6, L8 + L15 هسته | Auth + Upload + RAG Chat + Dashboard |
| **2 — Hardening** | 11-18 | L7, L9, L12, L13, L14 | Security, Perf, Obs, Tests 80% |
| **3 — Polish & Scale** | 19-26 | L15 کامل + L16 + Multi-region | Agent, Automation, Docs, GA |

**تخمین کل تلاش:** **~170-200 روز-نفر** → با تیم 6 نفر ≈ **28-33 روز تقویمی** کار موازی فشرده → با بافر و QA → **6 ماه** واقع‌گرایانه.

**Story Points کل:** ~520 SP (Velocity فرضی 40 SP/اسپرینت 2 هفته‌ای → 13 اسپرینت = 26 هفته)

---

## ⚠️ ریسک‌های کلیدی و Mitigation

| ریسک | احتمال | اثر | Mitigation |
|---|---|---|---|
| هزینه LLM بالا | متوسط | بالا | کش RAG, مدل کوچک برای rewrite, fallback, بودجه alert |
| Hallucination | بالا | بالا | RAG + citation + eval + human review |
| مقیاس ناگهانی | کم | بالا | HPA + KEDA + Read replica + CDN |
| Vendor lock (OpenAI outage) | متوسط | متوسط | Multi-provider abstraction + self-hosted embed |
| Security breach | کم | بحرانی | Pen-test, WAF, audit log, secrets rotation |

---

## ✅ چک‌لیست Definition of Done (Production-Ready از روز اول)

- [ ] CI سبز + Coverage ≥80% + SAST pass
- [ ] OpenAPI sync + SDK generated
- [ ] Helm + Terraform apply در staging
- [ ] Sentry + Grafana + Alerting فعال
- [ ] Runbook برای هر سرویس
- [ ] RAGAS eval pass + Prompt versioned
- [ ] Load test 2x expected traffic

---

## 🚀 گام بعدی پیشنهادی (بدون اجرای خودکار — فقط با تایید شما)

1. تایید مفروضات (نام، مقیاس، استک) — اگر تغییر می‌خواهید بگویید
2. من `docs/adr` و `prisma/schema.prisma` اولیه را می‌سازم
3. سپس `apps/api` و `apps/web` با ساختار Modular Monolith
4. راه‌اندازی CI/CD + IaC

> بگویید: «تایید» یا تغییرات را اعلام کنید تا فاز 0 را شروع کنم. این نقشه به صورت فایل `docs/16-LAYER-PRODUCTION-PLAN.md` ذخیره شد و قابل ارائه مستقیم به تیم مهندسی است.

