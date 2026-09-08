# Learnings (ECC "remember")

One file per builder session: `YYYY-MM-DD-<slug>.md`, ≤ 20 lines, three sections — `## What broke`, `## Root cause`, `## Rule`.
The supervisor turns every entry into a check, protocol rule, prompt change, or step card (`docs/loop/11_SUPERVISOR.md` §7).
Copy `TEMPLATE.md`. Hygiene is enforced by `tests/unit/test_repo_hygiene.py` from S-101 and by `scripts/supervise.py` C13.
