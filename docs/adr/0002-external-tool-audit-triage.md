# ADR-0002 — Triage of the external "100+ free tools" stack audit

## Status
Accepted — 2026-09-08

## Context
An external senior-engineer audit (reproduced in `docs/integrations/external-audit-2026-09-08.md`) reviewed the 16-layer plan and proposed ~100 tools, 10 swaps (Prisma→SQLAlchemy, Redis→Valkey, Terraform→OpenTofu, …), two new supervisor checks (Stack-Fit, License-Fit) and a "free-forever" hosting plan (Cloudflare Pages, Oracle Always Free, Ollama). The auditor could not open the repository and audited the *generic* 16-layer plan, not this product.

Facts the auditor did not have:
- This is a **single-user offline Windows desktop app** (Tauri sidecar). There is no server, database, cache, auth, hosting, uptime, email, analytics or IaC layer to choose tools for. `apps/desktop` is Tauri already (the auditor's own recommendation).
- The stack is locked (`AGENTS.md` §1, ADR-0001). Prisma/Flyway/tRPC/Lucia/Kong/Argo/Terraform/Redis/Vault/Mintlify were never in it — they only appear in the imported reference document. The "swap" rows are therefore moot: nothing to swap.
- Ollama was **explicitly removed** by the product owner (16 GB RAM / 4 GB VRAM machine; no local LLM > 3B). The $0 rule is met with OpenRouter `:free` + Nvidia NIM, guarded in S-056.
- DaisyUI 5 is the single design system; shadcn is not used. Vazirmatn is already bundled offline (S-007). RTL is a first-class requirement (02 §4).

## Decision
Adopt what is real for a desktop product, reject what belongs to a SaaS, and make the two process ideas mechanical:

| Auditor item | Decision | Where |
|---|---|---|
| Supervisor check #15 Stack-Fit | **Adopted** as `supervise.py` C15: any new dependency line in the five manifests matching a foreign-stack pattern fails the audit until an ADR + `steps.json` change exists | `scripts/supervise.py` |
| Supervisor check #16 License-Fit | **Adopted** as C16, enforced by `scripts/license_check.py` (pip-licenses + license-checker + cargo-license, OSI allow-list, LGPL only for FFmpeg) | S-086 |
| Bandit, pip-audit, pnpm audit | **Adopted** into `gate.py --stage static` | S-008 |
| CodeQL + Dependabot (free on public repos), `verify_ledger`/`supervise` in CI | **Adopted** | S-009 |
| Hey API OpenAPI → TS client (instead of hand-typed fetch) | **Adopted**; committed output + drift check | S-012 |
| Schemathesis fuzzing of the live OpenAPI | **Adopted** | S-080 |
| axe-core via `@axe-core/playwright` | Already in S-084 (kept) | S-084 |
| next-intl + Tailwind logical properties | **Adopted as candidate** chosen in S-085's CONTRACT (must work with `output: export`) | S-085 |
| MADR-style ADR template | **Adopted** | S-101 |
| Context7 MCP / Playwright MCP / spec-kit | **Not adoptable in Arena** (no MCP servers, no skill loader). Equivalent already exists: pinned versions + `docs/learnings/`; supervisor re-runs Playwright itself; CONTRACT AC/NG = spec-kit's specify/plan/tasks. Revisit if the agent runtime gains MCP | — |
| Walking-skeleton warning | Already the plan: S-010 ships the first `.exe` in P0, before any deep layer | S-010 |
| SQLAlchemy/Alembic/pgvector/Valkey/Celery/arq/structlog/TanStack Query/react-hook-form/better-auth/Keycloak/Traefik/Caddy/OpenTofu/k3s/Dokploy/Prometheus/Grafana/Loki/Sentry/GlitchTip/Uptime Kuma/SigNoz/Unleash/PostHog/MinIO/Resend/Cloudflare Pages/Oracle Cloud/Docusaurus/mkdocs/Storybook/Penpot/langchain/langgraph/pydantic-ai/litellm/langfuse/Ollama | **Rejected** — no server side, no hosting, no telemetry by default, locked stack, owner removed Ollama. Structured logging is done with stdlib `logging` + JSON formatter in S-073 to keep the PyInstaller bundle small | — |
| Ruff, pytest, Biome, Playwright, Vitest, Turbo, pnpm, lefthook, gitleaks, git-cliff (changelog) | Already in the stack; git-cliff considered for S-097 release notes | — |

## Consequences
- Two new supervisor checks (16 total). C15 turns the "Prisma/tRPC mistake" the auditor feared into a mechanical failure instead of a review opinion.
- Six step cards strengthened (S-008, S-009, S-012, S-080, S-085, S-086, S-101). No new steps: everything fits existing cards.
- The external audit is stored verbatim so future reviewers see what was considered and why most of it does not apply to a desktop product.
