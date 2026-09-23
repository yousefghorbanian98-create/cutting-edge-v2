# EVIDENCE — S-012 — Non-blocking jobs

Builder. Status: REVIEW (not GREEN). Proof: `local-linux`. `ci / windows` has not run this commit yet. BUG-11 stays OPEN until that job is green.

## What landed

| file | role |
|------|------|
| `ai-engine/src/core/jobs.py` | `JobManager`, two workers, progress, cancel, partial cleanup after the writer is released |
| `ai-engine/src/main.py` | five heavy routes return `202` + `job_id`; `GET /jobs/{id}` and `POST /jobs/{id}/cancel` |
| `ai-engine/src/muscle/muscle_enhancer.py` | cancel checked before open and each frame; writer released in `finally` |
| `apps/desktop/openapi.json` | FastAPI schema, committed |
| `apps/desktop/src/lib/openapi/` | `@hey-api/openapi-ts@0.99.0` output (`@hey-api/client-fetch@0.13.1`) |
| `apps/desktop/src/lib/api.ts` | barrel only: `export * from './openapi'` |
| `apps/desktop/src/app/page.tsx` | polls through that client; no `fetch(` |
| `scripts/check_openapi_client.py` | gate check `openapi-client` |

## Local proof (`local-linux`)

```
CE_TEST_VENV=ai-engine/.venv ai-engine/.venv/bin/python -m pytest tests/test_jobs.py -m real -q
2 passed, 1 warning in 60.12s
```

The warning is the offline fixture note (`CE_FIXTURE_HUMAN_CLIP_URL` unset). The 10s 720p clip is synthetic.

| AC | result |
|----|--------|
| AC-1 | `202` + `job_id`; 50 `/health` samples, p95 `< 200ms` while enhance ran |
| AC-2 | `percent == 100`, `status == done`, `assert_playable` (1280×720, duration ≥ 9s, no audio) |
| AC-3 | cancel once `percent >= 30` → `cancelled` within 2s, `partial_removed`, download `404` |
| AC-4 | `JobView` has `progress`, `percent`, `eta_s`, `error` |
| AC-5 | beat-sync, viral-cut, mood-dna, enhance, style-compare are jobs; `/health` is still direct |
| AC-6 | `python scripts/check_openapi_client.py` printed `openapi client matches FastAPI` |

`ruff check` on the touched Python passed. `tsc --noEmit` passed. `design_audit.py --strict` reported 0 findings.

## Carried

| item | owner |
|------|-------|
| BUG-11 close | `ci / windows` pytest, not this local run |
| Windows file-lock on cancel | same job; writer is released before `storage.delete` |
| priority / persistence / retry | S-072 |
| audio + H.264 on the enhancer | S-037 |
