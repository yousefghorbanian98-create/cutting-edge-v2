# REVIEW — S-100 — round 1 — commit (this commit; see ledger)

> Supervisor as independent reviewer (fresh pass: inputs = CONTRACT.md, EVIDENCE.md, `git diff`, checker output on fixtures + real tree). Reviewer pushes nothing.

CI: `ci / ubuntu` gate step (`--strict-missing`) and `tests/unit` on both runners will execute the checker; the run for the pushed commit is cited in the ledger row.
Evidence re-produced by reviewer: **yes** — `python scripts/design_audit.py tests/fixtures/ui/violations.tsx --json` → 8 findings at lines 9/12/13/16/17/18/19/20 (opened the fixture: each line holds the construct claimed); `clean.tsx --strict` → 0; `apps/desktop/src --strict` → 0 in 4 files; `git diff apps/desktop/src` read line by line — every change is an a11y/motion/transition fix, no behaviour change except the backdrop click now checks `e.target === e.currentTarget` (equivalent to the removed `stopPropagation`); `pytest tests/unit` 52 passed.

## Summary
Adds the deterministic half of the Web Interface Guidelines as a Python checker in the static gate, proves it on planted fixtures with exact line numbers, and then uses it for real: 17 findings in the shipped UI were fixed (not suppressed) except one documented backdrop case owned by S-084.

## 1. Must fix before GREEN
- None. AC-1…AC-6 reproduced. Test-weakening check: the fixture's only edit during the build was adding `aria-label` to the `outline-none` input so line 12 tests exactly one rule — the input-label rule is still exercised by line 20. `unused-ignore` guarantees the single real-tree ignore cannot rot silently.

## 2. Should fix soon (non-blocking)
- `[UX]` Transport buttons now have Persian `aria-label`s hard-coded; S-085 (i18n) must move them to the message catalogue with the rest of `page.tsx` strings.
- `[REHEAL-L1]` `reduced-motion` accepts `useReducedMotion` being imported anywhere in the file; it does not prove each `motion.*` uses it. S-084's Playwright run with `reducedMotion: 'reduce'` should assert zero transform deltas.
- The checker's JSX tokenizer is intentionally small; if S-013+ introduce components with JSX inside attribute expressions (render props), add a fixture case before relying on it there.

## 3. Verdict
approved — exact on fixtures, clean on the real tree by fixing code, wired into gate and CI with MISSING semantics.
