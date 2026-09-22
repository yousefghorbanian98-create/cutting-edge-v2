# EVIDENCE — S-099 — Agent operating manual + DESIGN.md reconciled to the real design tokens (single source, gated)

Builder: Supervisor session (autonomous chain). Verified on: `local-linux` (Node 22.22.3, Python 3.11). The check is pure Node + file reads → runs identically in `ci / ubuntu` (gate `--strict-missing`).

## Red → Green proof (real, not numeric)

| AC | Red state (before) | Green state (after) | How reproduced |
|----|--------------------|---------------------|----------------|
| AC-1 | `node scripts/check-design-tokens.js --json` on the imported DESIGN.md → `ok:false`, **51 problems**: 27 `missing from DESIGN.md`, 19 `ts:… missing`, 5 `missing # tokens: <group> block` (draft documented `#010102`, `#5E6AD2`, Geist, light mode) | `✓ design tokens — three-way 27 / tokens.ts-only 19 / drift 0 (css vars 27, DESIGN.md keys 46)`; banner "AUTHORITY (S-099)"; no draft value survives | `test_token_check_green_on_clean_tree`, `test_design_md_has_no_draft_values` |
| AC-2 | script = 2-line `console.log('placeholder')` | 240-line dependency-free parser (DESIGN fenced blocks / `@theme static` / `designTokens` + `cssTheme` walker), `--design/--css/--tokens/--json`, exit 0/1/2 | mutation runs below |
| AC-3 | gate `design-tokens ⏭️ SKIP placeholder until S-099` | gate `design-tokens ✅ PASS`; `summary: 11 pass, 0 fail, 0 missing, 2 skip` (cargo → windows job, design-audit → S-100); supervise C14 switches to enforced on this ledger flip | `gate.py --stage static --skip cargo-clippy`; `test_gate.py` |
| AC-4 | `.cursorrules`: "expert in Next.js 15, **NestJS, Prisma**, Tailwind, **shadcn/ui** … `zod`, `Prisma`, citation for every **RAG** answer"; 4 skill files told agents to `WebFetch` rules from `raw.githubusercontent.com` | 5 thin pointers (≤ 40 lines) linking `AGENTS.md`, `DESIGN.md`, `docs/loop/00_INDEX.md`; skills point at the offline snapshot + `design_audit.py` | `test_harness_files_are_thin_pointers[5]` (11 foreign words × 5 files, word-boundary regex) |
| AC-5 | AGENTS.md §5 pointed at a placeholder; no ADR for DESIGN.md authority | AGENTS.md §2/§5 updated; ADR-0010 written + indexed; hygiene validator `10 ADRs, 0 problems` | `test_agents_md_entry_point` |
| AC-6 | — | mutations (each on a temp copy, originals untouched): `--radius-md: 12px` in CSS → `✗ --radius-md: DESIGN.md=10px globals.css=12px tokens.ts=10px` exit 1; `success: '#22c55e'` in tokens.ts → `✗ --color-success: … tokens.ts=#22c55e`; motion block deleted from DESIGN.md → 6 problems incl. `missing \`# tokens: motion\` block`; `--color-ai-glow: "#7c3aed"` edited in DESIGN.md alone → `✗ --color-ai-glow: DESIGN.md=#7c3aed globals.css=#8b5cf6 tokens.ts=#8b5cf6` | `test_token_check_detects_drift_in_each_source` (4 mutations) |

Suite: `pytest tests/unit` → **46 passed / 1 skipped** (cargo); `biome check` 11 files clean (checker itself is Biome-linted: no `use strict`, no assignment-in-expression); `ruff` clean.

## Design content decisions recorded (documentation of existing code, NG-1 respected)
- Two accents rule (indigo = user action, violet = AI), text opacity ladder 100/80/40/20 with contrast figures, shared red/orange/yellow across status/heat/energy by value.
- `primary` scale stays tokens.ts-only (documented as `ts:colors.primary.*`); promotion to `--color-primary-*` utilities is owned by S-013 (first UI card that needs them).
- Dark only, no theme library (ADR-0003/0007); DaisyUI 5 components recoloured with tokens instead of a hand-rolled button system.

## Reheal / carry
- The checker's `tokens.ts` walker is a minimal tokenizer for this file's shape (nested object literals, strings, numbers, arrays). If S-013 adds functions or template literals to `designTokens`, the walker must be extended — `test_token_check_green_on_clean_tree` would fail loudly (exit 2), not silently pass.
- Biome ignore on `<video>` (useMediaCaption) still owned by S-047; noted in DESIGN.md §6.
