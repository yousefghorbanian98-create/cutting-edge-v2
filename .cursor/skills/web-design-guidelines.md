---
name: web-design-guidelines
description: Review UI code in this repository for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX".
metadata:
  author: vercel-labs (snapshot adapted for cutting-edge-v2, S-099)
  version: "1.1.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines — Cutting Edge v2 (offline)

This is a thin pointer. The project's rules live in:

- `AGENTS.md` — operating manual (stack, loop, enforcement)
- `DESIGN.md` — the single visual authority (tokens are machine-checked)
- `docs/loop/00_INDEX.md` — the numbered delivery loop

## How it works (no network)

1. Read the rule snapshot: `docs/integrations/web-guidelines/web-interface-guidelines.md` (do **not** fetch a live URL — the desktop app and its tooling are offline by design).
2. Read the requested files (default: `apps/desktop/src/**/*.tsx`).
3. Run the deterministic checker first and start from its output:
   `python scripts/design_audit.py apps/desktop/src --strict` (S-100)
4. Add anything the checker cannot see (copy, hierarchy, RTL mirroring, motion feel) in the same terse format.

## Output

`file:line rule message` — one finding per line, no prose. Suppressions in code only as `// wig-ignore <rule>: <why> (S-xxx)`.
