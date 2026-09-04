# REVIEW — S-003 — round 1 — commit 219f69c

> Supervisor as independent reviewer (`11_SUPERVISOR.md` §6). Inputs: CONTRACT.md, full diff, card S-003, protocol §1-⑧/§4.

CI: not configured (S-009). Evidence `local-linux`.
Evidence re-produced by reviewer: **yes** — `pytest tests/test_security.py` → 6 passed against a live uvicorn. Additionally ran my own probe set against `Storage.resolve_download` and the live `/muscle/download/{name}` endpoint: `../../etc/passwd`, `/etc/passwd`, `C:\Windows\win.ini`, `a/../../b.mp4`, `....//....//x`, `..`, `%2e%2e/%2e%2e/etc/passwd`, `..%2F..%2Fetc%2Fpasswd` → all 404 or resolved strictly inside base. Persian filename accepted. CORS allow-list verified (evil origin not reflected).

## Summary
Introduces `ai_engine/core/storage.py` (UUID names, extension allow-list → 415, streaming size cap → 413, traversal-safe resolve → 404), wires all upload endpoints through it *before* heavy imports (fail-fast), restricts CORS to the four local/tauri origins, and adds typed exception handlers. Design is sound and the module is the single choke point for disk access — good.

## 1. Must fix before GREEN
- `[SECURITY]` **Null byte in download name crashes the handler → 500.** `GET /muscle/download/x%00.mp4` returns `500 Internal Server Error` because `Path.resolve()` raises `ValueError: embedded null byte` *before* `_is_safe_basename` is consulted (in `_safe_path` the resolve happens first, the check second). A 500 leaks that the input reached the filesystem layer and is a classic probe signal. Fix: in `_safe_path`, run `_is_safe_basename(name)` **before** building/resolving the path, and wrap `resolve()` in `try/except (ValueError, OSError) → PathTraversalError`. Add `x\x00.mp4` and `%00` to `tests/test_security.py::test_download_traversal_returns_404`.

## 2. Should fix soon (non-blocking)
- `[DEFECT-minor]` `_is_safe_basename` returns `True` for `""`/`"."` relying on downstream `is_file()`; `resolve_download(".")` returns the base dir itself (a directory). Harmless today because the endpoint checks `is_file()`, but tighten to reject empty/`.` explicitly so the invariant lives in one place.
- `sanitize_filename` keeps `%` so `..%2F..%2F` becomes `_2F._2F…` — safe, but if any future code URL-decodes stored names this becomes a traversal. Add a comment or strip `%`.
- CORS test accepts Starlette's 400 for disallowed origins — correct behavior; fine.

## 3. Verdict
changes-requested — one small `[SECURITY]` ordering bug (null byte → 500). Everything else verified; round 2 = re-check of that fix only.
