# EVIDENCE — S-012 — Non-blocking jobs

Builder. Status: REVIEW (not GREEN). Proof: `local-linux`. `ci / windows` has not run this commit yet. BUG-11 stays OPEN until that job is green.

## What landed

| file | role |
|------|------|
| `ai-engine/src/core/jobs.py` | `JobManager`, two CPU workers, one GPU inference slot, progress, cancel, partial cleanup after the writer is released |
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

## Card alignment (`614f4b4`)

The overseer card now requires a one-slot GPU scheduler, CPU fallback, and `unverified` rather than `pass` when no GPU answers. Style Match models were not installed.

```
/tmp/ce-unit/bin/python -m pytest tests/unit/test_job_scheduler.py -m unit -q
4 passed in 0.10s
probe_gpu False
```

| AC | result |
|----|--------|
| AC-7 | one GPU inference body at a time; a CPU job finished while the slot was held |
| AC-8 | false probe → `device=cpu`, `gpu=unverified`, never `pass`; this host probe is `False` |
| AC-9 | Ollama, PySide6, Gradio, Ultralytics absent from manifests and runtime imports |

HTTP `JobView` fields are unchanged, so the committed OpenAPI client was not regenerated. AC-1..AC-3 still rest on the 60.12s run: the five media routes still call `submit()` without `kind="inference"`.

## Carried

| item | owner |
|------|-------|
| BUG-11 close | `ci / windows` pytest, not this local run |
| Windows file-lock on cancel | same job; writer is released before `storage.delete` |
| real GPU slot on GTX 1650 | `unverified:gpu` until `user-gpu`; this host probe is false |
| priority / persistence / retry | S-072 |
| audio + H.264 on the enhancer | S-037 |
