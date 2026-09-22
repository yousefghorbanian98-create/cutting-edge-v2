# Copilot instructions — Cutting Edge v2 (thin pointer)

This repository's rules are not duplicated here. Read:

- `AGENTS.md` — product, locked stack, build/test commands, the mandatory contract → real-test → review loop.
- `DESIGN.md` — the single visual authority; tokens are machine-checked (`node scripts/check-design-tokens.js`).
- `docs/loop/00_INDEX.md` — the numbered steps; each change belongs to an `S-xxx` card with a CONTRACT.

UI review: apply the offline Web Interface Guidelines snapshot at
`docs/integrations/web-guidelines/web-interface-guidelines.md` and run
`python scripts/design_audit.py apps/desktop/src --strict` (S-100). Report findings as `file:line rule message`.
