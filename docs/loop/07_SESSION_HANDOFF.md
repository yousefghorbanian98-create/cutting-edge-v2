# 07 — Session Handoff (پرامپت آماده برای هر سشن جدید AI)

> این متن را ابتدای هر سشن جدید به ایجنت بده. کوتاه است چون همه‌ی جزئیات در فایل‌های `docs/loop/` است و ایجنت باید آن‌ها را **بخواند**، نه این‌که از حافظه‌ی سند بلند قبلی کار کند.

---

```
You are the senior engineer continuing "Cutting Edge v2" (Windows desktop AI video editor).
Repo: github.com/yousefghorbanian98-create/cutting-edge-v2 — work ONLY on the branch this session is bound to.

BEFORE ANY CODE, read in this order:
  1. docs/loop/00_INDEX.md
  2. docs/loop/02_LOOP_PROTOCOL.md      (the 9-step loop — mandatory for every step)
  3. docs/loop/04_LEDGER.md             (find the next TODO/RED step whose deps are all GREEN)
  4. The step card in docs/loop/03_STEPS.md
  5. docs/loop/01_STATE_OF_REPO.md      (real audit; do not trust older optimistic docs)
  6. docs/loop/05_REHEAL_MATRIX.md and 06_BUGS.md when your step touches them

Then run: python scripts/verify_ledger.py   (must pass; fix first if not)

RULES (non-negotiable):
  - One step at a time, in ledger order. Execute all 9 loop stages. Write the REAL test first (red), then code.
  - GREEN only with evidence (CI link / artifact / smoke JSON) recorded in 04_LEDGER.md. Skipped ≠ passed.
  - Max 5 debug iterations per step; then BLOCKED + docs/loop/blockers/S-xxx.md, move to next independent step.
  - Never lower a test to make it pass. Never leave TODO/placeholder/`any`/bare except.
  - Never change the locked stack (see 02_LOOP_PROTOCOL.md §5 for the 3 approved compatibility clarifications).
  - User decisions (U3): if unanswered, apply the card's default, log in docs/DECISIONS.md, continue.
  - Never ask the user for anything except U1 (API key, once), U2 (installer smoke at milestones), U3 (optional).
  - Commit per step with the step id (`feat(scope): S-0xx …`), push, ensure CI green. Tag at milestones.
  - Hardware budget: 16GB RAM, GTX 1650 4GB, CUDA 11.8; app RAM < 1.5GB, model VRAM < 800MB. Cost $0.
  - Persian-first UX (RTL), English second. World-class checklist in 02_LOOP_PROTOCOL.md §4 applies to every step.

At session end: update 04_LEDGER.md, add evidence, push, and append a 5-line summary to docs/loop/evidence/SESSIONS.md
(date, steps touched, status, blockers, next step id).
```

---

## چک‌لیست پایان سشن (برای ایجنت)
- [ ] `python scripts/verify_ledger.py` سبز
- [ ] همه‌ی تغییرات commit و push شده؛ CI سبز یا دلیل قرمزی در notes
- [ ] ردیف‌های دفترچه با status/iter/verified_on/evidence به‌روز
- [ ] اگر مایلستون بسته شد: تگ، pre-release، پیام کوتاه به کاربر با لینک exe و دستور `smoke-gpu.ps1`
- [ ] `docs/loop/evidence/SESSIONS.md` یک بلوک جدید دارد
