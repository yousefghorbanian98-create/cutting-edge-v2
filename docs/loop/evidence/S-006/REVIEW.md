# REVIEW — S-006 — round 1 — commit c33e095

> Supervisor as independent reviewer. Inputs: CONTRACT.md, full diff, card S-006, protocol §1-⑧/§4.

CI: not configured (S-009). Evidence `local-linux`.
Evidence re-produced by reviewer: **yes** — fresh venv; `pytest tests/test_api_live.py` → 3 passed against a real uvicorn on a free port (beat-sync over HTTP ≈120 BPM with non-empty, well-formed clips; muscle-enhance → HTTP download → `assert_playable` 640×360 ≥1.5 s → mean-abs pixel diff > 2.0); whole repo `pytest` → **32 passed, 0 skipped** in 172 s. `--strict-markers` verified (`unit/real/heavy/gpu/e2e/perf/chaos` registered). Helpers sanity-checked: identical frames → diff 0 / SSIM 1.0; shifted → large diff / low SSIM.

## Summary
Session-scoped `live_api` fixture (subprocess uvicorn, health-wait, process-group teardown), `tests/helpers/media.py` (`assert_playable`, `frame_diff`, `mean_abs_pixel_diff`, `ssim_region`), first real HTTP tests for two endpoints, markers wired. This is the harness every later step's ⑤ stage will use.

## 1. Must fix before GREEN
- None.

## 2. Should fix soon (non-blocking)
- `assert_playable` skips the width/height assert when the probe returns `None` (`if width is not None and info["width"] is not None`). For a *video* file, a `None` width should fail, not pass silently. Tighten in S-011 (gate.py stage work) or when the ffprobe-json path lands.
- `test_muscle_enhance_live_http` has a dead line `out_path = Path(__file__).parent / f"_dl_{out_name}"` before the tempdir version — remove.
- Junit: AC-7 relies on `-ra`; S-009 must add `--junitxml=reports/junit.xml` in CI so skips are machine-readable (card done-when).
- mediapipe unavailable here (no libGL) → face-protection branch of the enhancer is untested; keep `unverified:windows` on that path until S-035 / CI windows job.

## 3. Verdict
approved — all seven ACs evidenced; NGs preserved; no regressions across 32 tests.
