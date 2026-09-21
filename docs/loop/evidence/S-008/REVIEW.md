# REVIEW — S-008 — round 1 — commit (this commit; see ledger)

> Supervisor as independent reviewer (fresh pass after the build: inputs = CONTRACT.md, EVIDENCE.md, full `git diff`, `gate-static.json`).

CI: not configured (S-009). Evidence `local-linux`; `unverified:ci`, `unverified:windows` (cargo).
Evidence re-produced by reviewer: **yes** — `python scripts/gate.py --stage static --json` → `10 pass / 0 fail / 1 missing / 2 skip`; `pytest tests/unit/test_gate.py` → 18 passed; planted `sk-or-v1-…` file → real `git commit` blocked by the installed pre-commit hook (nothing landed, `git log -1` unchanged); `pnpm --filter cutting-edge-desktop build` → static export OK after the a11y/type edits.

## Summary
Static gate with 13 named checks (MISSING ≠ PASS, JSON report, `--staged` fast path, commit-message rule), Ruff/Biome/tsc/Turbo-2 configs, exact pins everywhere, lefthook hooks, and the three security scanners (bandit, pip-audit with a documented exception file, pnpm audit). Along the way it fixed 34 Python CVEs and 2 high JS CVEs by pinning to fixed versions inside the locked stack.

## 1. Must fix before GREEN
- None. AC-1…AC-7 reproduced. NG-1 verified by reading the full backend diff (formatting, typed excepts with logging, `contextlib.suppress`, builtin generics — no logic change). NG-2/NG-3/NG-4 respected (no workflow, other stages skeleton only, cargo MISSING). NG-5: JS pins equal the lockfile; Python bumps are security fixes and were re-tested (`test_security.py` + `tests/real` 12/12) — accepted as the documented exception, recorded in EVIDENCE.md.

## 2. Should fix soon (non-blocking)
- `[REHEAL-L1]` `page.tsx` uses `// biome-ignore lint/a11y/useMediaCaption` on the preview `<video>`; S-047 (Auto Captions) must attach a `<track>` and delete the ignore.
- `ai-engine/pip-audit-ignore.txt` holds 18 pillow/protobuf IDs with owner steps S-037/S-035; the U2 milestone checklist must re-run `pip-audit` without the file to confirm they still exist and are still transitive-only.
- Biome 1.9.4 vs 2.5.14: add a P6 hardening card (schema migration `biome migrate`), not urgent.
- `lefthook` runs `python` — on Windows the launcher may be `py`; S-009 windows job should exercise `gate.py` via `python` from the venv and S-011 should document `pnpm lefthook install` in ONBOARDING.

## 3. Verdict
approved — all ACs reproduced locally; CI-agnostic evidence sufficient for GREEN (`local-linux`) with `unverified:ci` carried to S-009.
