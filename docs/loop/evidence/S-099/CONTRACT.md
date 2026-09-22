# CONTRACT — S-099 — Agent operating manual + DESIGN.md reconciled to the real design tokens (single source, gated)

> Builder: Supervisor session (autonomous chain). Deps: S-007 GREEN, S-008 GREEN.

## Acceptance Criteria

| # | Criterion | Proof |
|---|-----------|-------|
| AC-1 | `DESIGN.md` sections Colors / Typography / Radius / Motion / Shadows carry machine-readable fenced blocks (` ```yaml ` whose first line is `# tokens: <group>`) whose values equal the shipping tokens: every `--color-*`, `--font-*`, `--radius-*` in `apps/desktop/src/app/globals.css` `@theme static` (27 vars) **and** `designTokens` in `packages/design-system/tokens.ts` (incl. `primary` scale, `radius.full`, `motion`, `shadows`). Draft-only values (`#010102`, `#5E6AD2`, Geist, Linear Display, `next-themes`, light mode, RAG bubbles) are gone; the "IMPORTED DRAFT" banner is replaced by an authority banner | `node scripts/check-design-tokens.js` exit 0, report `three-way 27 / tokens.ts-only ≥ 16 / drift 0`; `tests/unit/test_agent_docs.py::test_design_md_has_no_draft_values` |
| AC-2 | `scripts/check-design-tokens.js` is a real dependency-free Node check (no `placeholder`): parses the three sources, reports each mismatch as `<var> DESIGN.md=<v1> globals.css=<v2> tokens.ts=<v3>`, exit 1 on any drift, missing var, or orphan (declared in one source only); flags `--design/--css/--tokens PATH` and `--json` so tests can run it on mutated copies | `test_token_check_green_on_clean_tree`, `test_token_check_detects_drift_in_each_source` (mutate one colour in each of the three files → exit 1 naming the var and both values) |
| AC-3 | Gate: `scripts/gate.py --stage static` runs the check as `design-tokens` (PASS, not SKIP); supervise C14 enforces when this row is GREEN | `gate.py --stage static --skip cargo-clippy` → `11 pass / 0 fail / 0 missing / 2 skip`; `test_gate.py` |
| AC-4 | Agent harness files `.cursorrules`, `.github/copilot-instructions.md`, `.claude/skills/web-design-guidelines/SKILL.md`, `.cursor/skills/web-design-guidelines.md`, `.windsurf/rules/web-design-guidelines.md` are thin pointers: each links `AGENTS.md`, `DESIGN.md`, `docs/loop/00_INDEX.md`; none contains a foreign-stack word (`NestJS`, `Prisma`, `shadcn`, `PostgreSQL`, `Redis`, `zod`, `RAG`, `Geist`, `next-themes`, `apps/web`); the skill files point at the offline snapshot `docs/integrations/web-guidelines/web-interface-guidelines.md` + `scripts/design_audit.py` instead of a live fetch | `test_agent_docs.py::test_harness_files_are_thin_pointers` |
| AC-5 | `AGENTS.md` stays the entry point: lists the token check + DESIGN.md sections, links ADR-0010; `ADR-0010 — DESIGN.md is the single UI authority` added (README row) | `test_agent_docs.py::test_agents_md_entry_point`; hygiene validator |
| AC-6 | Negative proof: removing a `# tokens:` block from a copy of DESIGN.md, or changing `--radius-md` in a copy of globals.css, or `success` in a copy of tokens.ts each fails the check with the offending var | `test_token_check_detects_drift_in_each_source` (3 mutations) |

## Non-Goals
| # | Not in this step | Owner |
|---|------------------|-------|
| NG-1 | No token **values** change in `globals.css` / `tokens.ts` (S-007 GREEN, CI-verified) — DESIGN.md is rewritten to the code, not the reverse | — |
| NG-2 | No `page.tsx` restyle; ad-hoc `text-indigo-400`/`bg-white/5` utilities stay until S-013+ UI cards | S-013…S-025 |
| NG-3 | No offline WIG rule checker (`design_audit.py`) | S-100 |
| NG-4 | No light theme, no theme toggle (product is dark-only per ADR-0003) | — |

## U-decisions
None (DESIGN.md content = documentation of existing decisions).
