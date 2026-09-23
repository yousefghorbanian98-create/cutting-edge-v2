# 2026-09-23 — openapi-ts emits a directory

Steps: S-012 · Branch: arena/01a0c936-cutting-edge-v2

## What broke
- `@hey-api/openapi-ts@0.99.0` wrote `src/lib/openapi/` (18 files), not `src/lib/api.ts`.
- With no `baseUrl`, the client used `apps` from the spec path `apps/desktop/openapi.json`.

## Root cause
- The card names one file. This generator version emits a module, and `baseUrl: true` falls back to the first path segment when the spec has no `servers`.

## Rule
- Pin the generator, set `baseUrl` in `openapi-ts.config.ts`, commit the folder, and keep `api.ts` as a one-line re-export that `scripts/check_openapi_client.py` owns.
