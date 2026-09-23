# CONTRACT — S-012 — Non-blocking processing: job model + thread pool so /health stays alive

> Builder. Deps: S-006 GREEN. Does not mark this step GREEN.

## Acceptance Criteria

| # | Criterion | Proof |
|---|-----------|-------|
| AC-1 | `POST /muscle/enhance` on the 10s 720p fixture returns `202` and a `job_id` without waiting for the render. While that job runs, 50 `GET /health` calls have p95 latency `< 200ms` | `tests/test_jobs.py::test_health_p95_under_200ms_while_enhance_runs_and_output_is_playable` |
| AC-2 | That job reaches `percent == 100` and `status == done`. The downloaded file passes `assert_playable` (duration ≥ 9s, 1280×720, video stream present) | same test |
| AC-3 | `POST /jobs/{id}/cancel` once `percent >= 30` makes `status == cancelled` within 2s, `partial_removed` is true, and `GET /muscle/download/{output_filename}` is 404 | `tests/test_jobs.py::test_cancel_at_30_percent_stops_within_2s_and_removes_partial` |
| AC-4 | `GET /jobs/{id}` reports `progress` (0..1), `percent` (0..100), `eta_s`, and `error` | both tests; OpenAPI `JobView` |
| AC-5 | Every `async def` endpoint that used to run local media work on the event loop now returns a job: `/editor/beat-sync`, `/editor/viral-cut`, `/mood-dna`, `/muscle/enhance`, `/style-match/compare`. `/health` stays a direct read | route table; S-006 live tests poll the job and still assert the same result schema |
| AC-6 | `apps/desktop/src/lib/api.ts` is the committed client entry. `@hey-api/openapi-ts@0.99.0` (client `@hey-api/client-fetch@0.13.1`) emits a module at `apps/desktop/src/lib/openapi/`; `api.ts` only re-exports it. The desktop page polls jobs through that client. `gate.py` check `openapi-client` fails if the schema, the generated module, or the barrel drifts | `scripts/gate.py` check `openapi-client`; `apps/desktop/src/app/page.tsx` |

## Non-Goals

| # | Not in this step | Owner |
|---|------------------|-------|
| NG-1 | Priority queue, persistence, retry, resume | S-072 |
| NG-2 | WebSocket progress | S-029 |
| NG-3 | Keep audio / H.264 mux on the enhancer output | S-037 |
| NG-4 | RAM/VRAM guard actions | S-075 |
| NG-5 | Hand-typed endpoint interfaces in the desktop client | this step forbids them |
| NG-6 | Marking S-012 GREEN | Overseer `approved` |

## Reheal layers touched

- L1 base only: jobs run off the event loop so `/health` can still answer. The RAM-pressure probe stays S-075.
- L7 not built. Cancel deletes the partial file; it does not resume. Resume is S-072.

## U-decisions

None. Chat and voice-command stay request/response: they are already `def` (threadpool) and are not local media jobs.
