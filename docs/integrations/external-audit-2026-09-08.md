# External stack audit — 2026-09-08 (verbatim summary, for traceability)

Source: senior-engineer review pasted by the owner into the supervisor chat. The reviewer could not open the repository and audited the generic 16-layer plan. Triage decision: `docs/adr/0002-external-tool-audit-triage.md`.

## Claimed critical incompatibilities (all refer to the reference plan, none to this codebase)
Prisma→SQLAlchemy/Alembic · Flyway→Alembic · CleanArchitecture(C#)→fastapi-best-practices · tRPC→Hey API · Lucia(deprecated)→better-auth · Terraform(BUSL)→OpenTofu · Redis→Valkey · Kong→Traefik/Caddy · Argo CD→defer · Mintlify→Docusaurus/Starlight · Vault→Infisical/SOPS+age · shadcn+DaisyUI→pick one.

## Claimed gaps per layer
L3 pgvector, restic/kopia · L4 Bruno, Schemathesis · L6 i18n/RTL (Vazirmatn, next-intl, logical properties) · L9 Bandit, pip-audit, Gitleaks, Trivy, Semgrep, ZAP, CodeQL · L13 Uptime Kuma, GlitchTip · L14 pytest+coverage, axe-core, testcontainers · L15 Langfuse, Ollama, LangGraph, pydantic-ai · cross-cutting: Unleash, PostHog/Umami, R2/MinIO, transactional email.

## Loop upgrades proposed
1 Context7 MCP · 2 Playwright MCP for supervisor · 3 check #15 Stack-Fit · 4 check #16 License-Fit · 5 verify_ledger/supervise in GitHub Actions · 6 github/spec-kit · 7 walking-skeleton first.

## Free-forever hosting plan proposed
Public repo (Actions/CodeQL/Dependabot) · Cloudflare Pages · Oracle Always Free + Dokploy + Postgres + Valkey · Neon/Supabase · Ollama + qwen3 · Resend · domain ≈ $10/yr · Docker Compose everywhere.

## Open question from the reviewer
"What is `apps/desktop`? If real desktop → Tauri." — It is Tauri 2 (locked stack).
