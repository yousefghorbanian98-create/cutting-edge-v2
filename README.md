# cutting-edge-v2 — AI-Native Platform

<p align="center">
  <strong>Modular Monolith • AI-First • Production-Ready from Day One</strong><br/>
  <sub>16-Layer Architecture + ECC + Web Guidelines + Awesome Design</sub>
</p>

<p align="center">
  <a href="docs/16-LAYER-PRODUCTION-PLAN.md">📐 16-Layer Plan</a> •
  <a href="docs/ROADMAP-v2-WITH-INTEGRATIONS.md">🗺️ Roadmap v2</a> •
  <a href="DESIGN.md">🎨 DESIGN.md</a> •
  <a href="AGENTS.md">🤖 AGENTS.md</a>
</p>

---

## 🚀 Quick Start (Agent-Aware)

```bash
git clone https://github.com/yousefghorbanian98-create/cutting-edge-v2.git
cd cutting-edge-v2
pnpm install
cp .env.example .env
docker compose up -d
pnpm dev
# web: http://localhost:3000  api: http://localhost:4000
```

**For AI Agents:** Read `AGENTS.md` and `DESIGN.md` first — they are the operating manual.

## 📚 Docs

| Doc | Purpose |
|---|---|
| `docs/16-LAYER-PRODUCTION-PLAN.md` | Complete 16-layer production plan (520 SP, 26 weeks) |
| `docs/ROADMAP-v2-WITH-INTEGRATIONS.md` | **NEW** Roadmap with 3 integrations (ECC + Guidelines + Design) |
| `DESIGN.md` | Hybrid design system (Linear + Vercel + Stripe) — Agent reads this |
| `AGENTS.md` | How agents should work in this repo |
| `docs/integrations/ecc/` | ECC harness docs |
| `docs/integrations/web-guidelines/` | Vercel Web Guidelines Skill |
| `docs/integrations/awesome-design/` | Awesome Design MD refs |
| `design-md/` | 3 reference DESIGN.md files (Linear, Vercel, Stripe) |

## 🎨 Design System

- **Root:** `DESIGN.md` — dark-first (#010102 + #5E6AD2 blurple), Geist Sans
- **References:** `design-md/DESIGN.*.md` (VoltAgent/awesome-design-md, MIT)
- **Quality:** `.claude/skills/web-design-guidelines/SKILL.md` audits every UI

```bash
# Ask agent:
"Use DESIGN.md to build a login page"
# Then audit:
pnpm design:audit
```

## 🤖 Agent Harness (ECC)

Selective install from `affaan-m/ECC` (213K stars, MIT):

- `tdd-workflow`, `code-review`, `security-scan`, `plan`
- Hooks: SessionStart, PreCommit
- GitHub App (optional): `/ecc-tools analyze` on any issue/PR

See `AGENTS.md` §3 and `docs/integrations/ecc/README.md`.

## ✅ Quality Gates

```bash
pnpm lint && pnpm typecheck
pnpm test --coverage   # ≥80%
pnpm design:audit      # 0 a11y violations
npx ecc-agentshield scan --path .
```

## 🗺️ Roadmap

See `docs/ROADMAP-v2-WITH-INTEGRATIONS.md`:

- **Phase 0 (W1-2):** Foundation + Integrations Setup ✅ (this commit)
- **Phase 1 (W3-10):** MVP (Auth, Upload, RAG Chat, Dashboard)
- **Phase 2 (W11-18):** Hardening (Security, Perf, Obs, Tests)
- **Phase 3 (W19-26):** Scale & Polish (Agent, Multi-region, GA)

## 📄 License

MIT — Integrations: ECC (MIT), Web Guidelines (MIT), Awesome Design (MIT)

---

> Built with AI — `AGENTS.md` is the source of truth for agents.
