# ECC Integration — cutting-edge-v2

> **Source:** `affaan-m/ECC` — The agent harness performance optimization system — MIT, 213K stars
> Website: https://ecc.tools — GitHub App: https://github.com/apps/ecc-tools

## چیست؟
ECC یک پکیج 261 Skill + 64 Agent + Hook است که فرآیند `plan -> test -> implement -> review -> verify -> remember` را به جای پرامپت تکراری، به صورت Skill قابل نصب در می‌آورد. برای هر Harness (Claude Code, Cursor, Codex, OpenCode) adapter دارد.

## چرا برای این پروژه؟
پروژه شما **AI-First SDLC** می‌خواهد — دقیقاً ماموریت ECC (لایه 15 نقشه 16-لایه). به جای اینکه هر بار بگوییم "لطفاً TDD کن"، ECC آن را به یک workflow گیت‌دار تبدیل می‌کند.

## نصب گزینشی (انجام شده — نه کامل)
ما **کل ECC را نصب نکردیم** تا Context Window پر نشود.

```bash
# نصب universal (selective)
npm i -g ecc-universal

# فقط core skills کپی شده به:
# .claude/skills/ (برای Claude Code)
# .cursor/ (برای Cursor)
# AGENTS.md (برای Codex)
```

**Skills فعال:**
| Skill | کاربرد در نقشه |
|---|---|
| `tdd-workflow` | L14 Testing — RED→GREEN→REFACTOR |
| `code-review` | هر PR با context تازه |
| `security-scan` | L9 Security — OWASP + secrets |
| `plan` (`/ecc:plan`) | L1/L2 — پلن قبل از کد |
| `build-fix` | L10 DevOps — فیکس بیلد خودکار |
| `e2e-testing` | Playwright |
| `doc-updater` | L16 Docs |

**Hooks فعال:**
- `SessionStart` — چک لود DESIGN.md/AGENTS.md
- `Stop` — خلاصه سشن
- `PreCommit` — lint+typecheck+secrets

## GitHub App (اختیاری — مرحله بعد)
1. نصب از https://github.com/apps/ecc-tools روی همین ریپو
2. کامنت `/ecc-tools analyze` روی Issue/PR
3. یک PR با Skillهای پیشنهادی اختصاصی همین ریپو می‌سازد — ما فقط موارد تایید شده را مرج می‌کنیم

## محدودیت‌ها
- Cursor/Copilot هوک ندارند — فقط instruction
- نصب کامل 261 Skill → توکن زیاد — به همین دلیل گزینشی

## فایل‌ها
- `docs/integrations/ecc/README.source.md` — خلاصه README اصلی ECC
- `AGENTS.md` بخش 3 — دستورالعمل Agent برای استفاده از ECC
