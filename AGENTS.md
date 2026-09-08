# AGENTS.md — Cutting Edge v2

> **Agent Operating Manual.** Every AI session (Arena builder, Arena supervisor, Claude Code, Cursor, Copilot, Codex) reads this file first.
> It is short on purpose: the authority for *how we work* is `docs/loop/`, the authority for *how it looks* is `DESIGN.md`.

## 1. What this project is
- **Product:** Persian-first (RTL) Windows desktop video editor for sports/fitness creators, with AI Style Match, AI Assistant and a 100 %-natural Muscle Enhancer. Ships as an NSIS `.exe` via GitHub Releases.
- **Locked stack (do not change):** Tauri 2 (Rust) · Next.js 15 / React 19 / TypeScript 5.5 strict · Tailwind 4 + DaisyUI 5 · Framer Motion 11 · Zustand 5 · FastAPI (Python 3.11) · MediaPipe · OpenCV · MoviePy 2 · librosa · faster-whisper small · edge-tts · OpenRouter `:free` models + Nvidia NIM · Turborepo + pnpm · Vitest / Playwright / pytest · Biome / Ruff.
- **Not this project:** no NestJS, Prisma, PostgreSQL, Redis, shadcn/ui, Geist fonts, SaaS multi-tenant, RAG chat. Those words appear in `docs/16-LAYER-PRODUCTION-PLAN.md` and `docs/ROADMAP-v2-WITH-INTEGRATIONS.md`, which are **generic reference inputs**, mapped onto this product in `docs/loop/12_SIXTEEN_LAYER_MAP.md`.
- **Hardware budget:** 16 GB RAM, GTX 1650 4 GB, CUDA 11.8, float16. App RAM < 1.5 GB, model VRAM < 800 MB. Budget $0.

## 2. Where to look (in this order)
| # | File | Why |
|---|------|-----|
| 1 | `docs/loop/00_INDEX.md` | Entry point of the delivery loop |
| 2 | `docs/loop/02_LOOP_PROTOCOL.md` | The 10-stage loop every step runs (contract → real test → build → static → review → evidence) |
| 3 | `docs/loop/04_LEDGER.md` | Status of every numbered step; machine-checked |
| 4 | `docs/loop/03_STEPS.md` | The step cards (generated from `steps.json`) |
| 5 | `DESIGN.md` | Visual authority: tokens, typography, motion, component rules |
| 6 | `docs/loop/13_INTEGRATIONS_ADOPTION.md` | What we took from ECC / Web Interface Guidelines / awesome-design-md and how it is enforced |
| 7 | `docs/adr/` | Architecture decisions (why things are the way they are) |
| 8 | `docs/learnings/` | What went wrong before and the rule we derived — read before repeating a mistake |

## 3. How to build and test
```bash
# backend
cd ai-engine && python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
../scripts/dev-backend.sh                                        # Windows: ..\scripts\dev-backend.ps1
# frontend
cd apps/desktop && pnpm install && pnpm dev
# gates (from repo root)
python scripts/gate.py --stage static      # Biome, tsc, Ruff, gitleaks, verify_ledger, design checks
python scripts/gate.py --stage real        # pytest -m real against a live uvicorn with FFmpeg-generated media
python scripts/verify_ledger.py
```
Fixtures are generated at test time with the bundled `imageio-ffmpeg` binary — media is never committed.

## 4. Workflow (mandatory, from `02_LOOP_PROTOCOL.md`)
```
plan (CONTRACT: AC-n / NG-n) → red real test → implement → static → real test → reheal probe
→ fresh review (supervisor) → evidence → commit with Scope Ledger → push → learnings entry
```
- **If it is not in `docs/loop/evidence/S-xxx/CONTRACT.md`, it does not exist.**
- One step per commit; commit subject carries the step id; body carries the Scope Ledger.
- Builder never marks GREEN; the supervisor's `REVIEW.md` verdict does. Max 2 review rounds.
- Never weaken a test to make it pass. Skipped ≠ passed. `unverified:<reason>` is recorded in the ledger.
- Sandbox limits (no browser download, no cargo, no network beyond npm/PyPI) are **not** a reason to stop: write the test, mark `unverified:ci`/`unverified:windows`, CI is the gate.
- Before starting a new step, confirm the previous one is on GitHub: `git ls-remote origin <branch>` must show your HEAD. If push fails with an auth error, say so and stop — never ask for tokens.

## 5. UI rules (enforced, not advisory)
- Read `DESIGN.md` before any UI work. Colors, radius, typography and motion only from tokens (`packages/design-system/tokens.ts` ⇄ `apps/desktop/src/app/globals.css` `@theme`). `node scripts/check-design-tokens.js` fails the static gate on drift.
- After UI work run `python scripts/design_audit.py apps/desktop/src --strict` (offline Web Interface Guidelines checker). Suppress only with `// wig-ignore <rule>: <why> (S-xxx)`.
- Always: `aria-label` on icon-only buttons, `focus-visible:` ring (never bare `outline-none`), animate `transform`/`opacity` only, honor `prefers-reduced-motion`, `<button>` for actions, `Intl.*` for dates/numbers, Persian `«»` quotes, `tabular-nums` for numeric columns, RTL-correct logical properties.
- Every action has a keyboard shortcut and appears in the Command Palette; every async > 500 ms has progress + cancel.

## 6. Security & privacy
- Never commit `.env`, keys, or media. `gitleaks` and `scripts/gate.py --stage static` run in CI; OpenRouter key lives in `ai-engine/.env` locally and in the OS keyring after S-086.
- Uploads go through `ai_engine.core.storage.Storage` (UUID names, extension allow-list, size cap, traversal-safe). Do not bypass it.
- No telemetry by default.

## 7. Prompts & AI
- Prompts live in `ai-engine/prompts/*.md` (versioned, S-053+) with an offline eval fixture set; changing a prompt without updating its eval fails the test.
- Only OpenRouter `:free` models with the fallback chain in S-053/S-056; offline mode must degrade gracefully with a Persian message.

## 8. Roles in Arena
- **Supervisor chat** (fixed): audits with `python scripts/supervise.py --write`, reviews, merges builder branches fast-forward into `arena/01a06951-cutting-edge-v2`.
- **Builder chat** (batch mode): builds numbered steps from `04_LEDGER.md`, pushes to its own branch, reports SHAs. Prompt: `docs/loop/07_SESSION_HANDOFF.md` → "BATCH BUILDER".
- Humans do: OpenRouter key (U1), Windows/GPU smoke at milestones (U2), product decisions (U3, defaults apply on silence).
