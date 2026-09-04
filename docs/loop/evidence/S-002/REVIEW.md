# REVIEW — S-002 — round 1 — commit 976aa9d

> Written by the SUPERVISOR acting as the independent reviewer (`11_SUPERVISOR.md` §6). Inputs: `CONTRACT.md`, full diff of `976aa9d`, card S-002, `02_LOOP_PROTOCOL.md` §1-⑧ and §4.

CI: not configured — `ci.yml` triggers only on `main` (S-009). Evidence is `local-linux`.
Evidence re-produced by reviewer: **yes** — ran `CE_PORT=8765 bash scripts/dev-backend.sh` on a clean venv: package installed editable, uvicorn booted as `ai_engine.main:app`, `GET /health` → `200 {"status":"healthy","ram":7.7,"cpu":0.0,"gpu_mem":0,"ai":false,"reheal":true}`; no ImportError. `python3 scripts/verify_ledger.py` → OK. Scope ledger present in commit body (AC-1…6, NG-1…5, Other behavior changes: None, Risk: Medium). Additionally attempted a non-editable wheel build (`python -m build --wheel`) to exercise packaging.

## Summary
Fixes B-1/BUG-7/BUG-13: backend now runs as the `ai_engine` package via `pyproject.toml` package-dir mapping, loads `.env` with python-dotenv, gets `CE_HOST`/`CE_PORT` overrides, pinned `requirements.txt`, `.env.example`, `dev-backend.sh` + `.ps1`, and a live-server real test (`tests/real/test_backend_boot.py`, 6 tests, includes a genuine 60 s idle window). `.gitignore` gains `.venv/` and `*.egg-info/`.

## 1. Must fix before GREEN
- `[DEFECT]` `ai-engine/pyproject.toml` declares `readme = "README.md"` but `ai-engine/README.md` does not exist. Editable install (`pip install -e .`) tolerates it, but a standard build/install emits `UserWarning: File 'README.md' cannot be found` and PyPA tooling treats a missing declared readme as invalid metadata — this will bite S-060 (PyInstaller/sidecar packaging). Fix: either drop the `readme` line or add a 5-line `ai-engine/README.md`. Add an assertion to `test_pinned_requirements_and_pyproject` that every file referenced by `[project]` exists.

## 2. Should fix soon (non-blocking → notes)
- `[UX]` `dev-backend.sh` step 2 installs only boot deps and skips `requirements.txt`; first call to any media endpoint will fail with ImportError until the user installs the full stack. Acceptable per NG-5 for this step, but the script should print a one-line hint (fa/en) after boot: "media/AI deps not installed — run `pip install -r requirements.txt`". Track under S-003 notes or S-011.
- AC-6 (`dev-backend.ps1`) is static-only (`unverified:windows`) — correctly labelled in ledger; will be exercised by CI windows job in S-009.

## 3. Verdict
changes-requested — one small must-fix (`[DEFECT]` missing README referenced by pyproject) that takes minutes; everything else verified and good. Round 2 may be a re-check of the single fix only.
