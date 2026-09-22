# Architecture Decision Records

Format: `NNNN-<slug>.md` with `## Status`, `## Context`, `## Decision`, `## Consequences`. Hygiene enforced from S-101.
Template: `TEMPLATE.md` (MADR short). Validator: `python scripts/loop/hygiene.py` (also run by `tests/unit/test_repo_hygiene.py` and supervise C13). Decisions taken before this log existed were back-filled in S-101 from `docs/loop/steps.json`, `02_LOOP_PROTOCOL.md` §5 and `docs/DECISIONS.md`.

| # | Title | Status |
|---|-------|--------|
| 0001 | Locked stack (Tauri 2 · Next 15 · FastAPI · Tailwind 4 + DaisyUI 5) and what the 16-layer plan is *not* | Accepted |
| 0002 | Triage of the external tool audit (adopt Stack-Fit/License-Fit/Bandit/CodeQL/Hey API/Schemathesis; reject SaaS tooling) | Accepted |
| 0003 | DaisyUI 5 (not 4) on Tailwind 4 via `@tailwindcss/postcss`; tokens in `@theme static` ⇄ `tokens.ts` | Accepted |
| 0004 | FFmpeg subprocess is the media path; MoviePy 2 fallback only | Accepted |
| 0005 | FastAPI backend shipped as a PyInstaller sidecar spawned by Tauri; models downloaded on first run | Accepted |
| 0006 | Only free-tier cloud LLMs (OpenRouter `:free`, NIM); no Ollama; key in OS keyring, never in git | Accepted |
| 0007 | Product defaults: MIT, "Cutting Edge", Persian-first RTL, no telemetry, MP4 H.264 default | Accepted |
| 0008 | Numbered steps run by a Supervisor/Builder loop with contracts, fresh review, evidence ledger, Skip ≠ Pass | Accepted |
| 0009 | CI as public evidence: SHA-pinned actions, least privilege, strict-missing gate, junit annotations | Accepted |
