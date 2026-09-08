# ADR-0001 — Locked stack; the 16-layer plan and Roadmap v2 are reference inputs, not the architecture

## Status
Accepted — 2026-09-08

## Context
`docs/16-LAYER-PRODUCTION-PLAN.md` and `docs/ROADMAP-v2-WITH-INTEGRATIONS.md` were generated against an empty repository and describe a multi-tenant SaaS (NestJS, Prisma, PostgreSQL + pgvector, Redis, shadcn/ui, Geist, RAG chat). Cutting Edge v2 is a single-user, offline-capable Windows desktop video editor with a locked stack, a $0 budget and a GTX 1650 target. The two documents are valuable for their *layer checklist* and their *quality practices* (ADR log, prompt versioning, a11y gates, agent manual), not for their component choices.

## Decision
- The stack stays as locked in `AGENTS.md` §1 / `02_LOOP_PROTOCOL.md` §5. No server database, no auth service, no cloud infra.
- The 16 layers are mapped onto existing and new numbered steps in `docs/loop/12_SIXTEEN_LAYER_MAP.md`; the three integrations are adopted only as in-repo, scriptable gates (`13_INTEGRATIONS_ADOPTION.md`): S-099 (DESIGN.md + AGENTS.md + token gate), S-100 (offline Web Interface Guidelines audit), S-101 (ADR + learnings).
- `DESIGN.md` is the visual authority **after** S-099 reconciles it with the shipping tokens; until then the `@theme` block and `tokens.ts` win.

## Consequences
- Agents get one entry point (`AGENTS.md`) and cannot import foreign-stack assumptions from the reference docs (tested in S-099).
- Three extra P0 steps (~1 builder batch) before P1 timeline work; in exchange every later UI step is gated on tokens and a11y instead of relying on review taste.
- The reference documents remain in `docs/` unmodified for traceability.
