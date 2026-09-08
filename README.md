# Cutting Edge v2.0
World-Class Desktop Video Editor + AI Style Match + Muscle Enhancer (Persian-first, offline-capable, Windows)

> **For AI agents:** read `AGENTS.md` first, then `docs/loop/00_INDEX.md`. `DESIGN.md` is the visual authority.

## Quick Start (Windows PowerShell)
```powershell
git clone https://github.com/yousefghorbanian98-create/cutting-edge-v2.git
cd cutting-edge-v2

# AI Backend
cd ai-engine
python -m venv .venv
.venv\Scripts\activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
pip install -e .
..\scripts\dev-backend.ps1

# Frontend (new terminal)
cd apps/desktop
pnpm install
pnpm dev
```

## Architecture
- **Desktop**: Tauri 2.0 (Rust) + Next.js 15 (React 19) + Tailwind 4 / DaisyUI 5
- **AI Core**: Python FastAPI + MediaPipe + faster-whisper + OpenRouter (free tier only)
- **Self-Healing**: Reheal Loop (7-layer auto-recovery)
- **Hardware**: Optimized for 16GB RAM | GTX 1650 4GB | $0 budget

## Docs
| Doc | Purpose |
|---|---|
| `AGENTS.md` | Agent operating manual (entry point for every AI session) |
| `DESIGN.md` | Design system authority — tokens mirrored in code and gated in CI |
| `docs/loop/00_INDEX.md` | Delivery loop: numbered steps, ledger, protocol, supervisor |
| `docs/loop/12_SIXTEEN_LAYER_MAP.md` | How the 16-layer production plan maps onto this desktop product |
| `docs/loop/13_INTEGRATIONS_ADOPTION.md` | What was adopted from ECC / Web Interface Guidelines / awesome-design-md |
| `docs/16-LAYER-PRODUCTION-PLAN.md` | Reference input (generic 16-layer plan) |
| `docs/ROADMAP-v2-WITH-INTEGRATIONS.md` | Reference input (integration proposal) |
| `docs/adr/` | Architecture decision records |
| `docs/learnings/` | Session learnings (ECC "remember") |
