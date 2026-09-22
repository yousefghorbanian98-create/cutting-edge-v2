# ADR-0010 — `DESIGN.md` is the single UI authority, machine-checked against the code

## Status
Accepted — 2026-09-22

## Context
The imported `DESIGN.md` (Roadmap v2 / awesome-design-md hybrid) described a generic SaaS look — Geist fonts, Linear blurple `#5E6AD2`, light mode, RAG chat bubbles — while the shipping code (S-007, CI-verified) uses zinc surfaces, indigo primary, violet AI accent, Inter Variable + Vazirmatn + JetBrains Mono, dark only. Agent harness files (`.cursorrules`, Copilot, Claude/Cursor/Windsurf skills) repeated the foreign stack (NestJS, Prisma, shadcn) and told agents to fetch rules from the network. Two written authorities that disagree means agents pick one at random.

## Decision
- `DESIGN.md` documents **only** the tokens that exist in code, in fenced `# tokens: <group>` YAML blocks; `scripts/check-design-tokens.js` compares `DESIGN.md ⇄ globals.css @theme static ⇄ tokens.ts` three ways and fails the static gate (`design-tokens`), supervisor C14 and CI on any drift, orphan, or missing group.
- A token change is one commit touching all three files; the doc is never edited alone.
- The product is dark-only, RTL-first, DaisyUI 5 components recoloured with tokens; no light theme, no second button system.
- `AGENTS.md` is the entry point for every agent; harness files are thin pointers to `AGENTS.md`, `DESIGN.md`, `docs/loop/00_INDEX.md`, reference the **offline** WIG snapshot, and are tested for foreign-stack words (`tests/unit/test_agent_docs.py`).

## Consequences
- Positive: one visual truth for humans, agents and CI; UI cards (S-013+) can cite `DESIGN.md` sections in contracts; drift is caught before review.
- Negative: adding a token costs three edits; DESIGN.md prose still needs human review for taste (the check covers values, not judgement).
- Follow-ups: S-100 offline WIG checker; S-013 promotes the `primary` scale to `--color-primary-*` when utilities are needed; S-084 axe + contrast tests; S-085 typography per locale.
