# EVIDENCE — S-012 — Non-blocking jobs

Builder. Status: GREEN. Closed after Overseer `approved` r2 @ `071a4fd`. CI run 35999861447. BUG-11 is CLOSED. Host GPU probe remains unverified, not a pass.

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
| round-1 windows job | [35986178547](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35986178547) job `107589257940` failed: `test_muscle_enhance_live_http` expected `200`, got `202`. |
| round-2 windows job | [35996988592](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35996988592) @ `273003f`, job `107624150630`: pytest 0 failed / 108, installer smoke 17/17, exe sha256 `8E4FEA0DE11D73B4D933744BDF872408FD7FE38A2DC92AB55DA7D8B138B6F4B1`. BUG-11 CLOSED. Not GREEN. |
| Windows file-lock on cancel | same job; writer is released before `storage.delete` |
| real GPU slot on GTX 1650 | `unverified:gpu` until `user-gpu`; this host probe is false |
| priority / persistence / retry | S-072 |
| audio + H.264 on the enhancer | S-037 |
