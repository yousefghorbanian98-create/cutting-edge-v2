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

## Retro-audit — 2026-09-24 — FFmpeg execution-contract review

Evidence re-produced: yes (fresh source audit plus the existing live-media evidence; the helper implementation was inspected against AC-3).

- [AC-3] `assert_playable()` silently skips a requested width/height assertion when the probe returns `None` (`if width is not None and info["width"] is not None`). A malformed or insufficiently-probed video can therefore pass a dimension assertion without proving its dimensions. The original review already noted this as a follow-up, but S-011 has not yet landed on the public Builder branch.
- [DEFECT] The helper's probe path is human-readable stderr parsing rather than structured `ffprobe` JSON. This is acceptable as the documented sandbox fallback, but a production path needs capability detection and a structured probe when available.

Retro verdict: send S-006 back to REVIEW for the AC-3 assertion fix (or an explicitly evidenced equivalent in S-011) before treating the harness as the final production evidence layer. S-004/S-006 remain otherwise reproducible; no product code was changed by this audit.

## Independent review — round 3 — target `ab409cd0d2ead26dc21b0ee10efab66397f80cda`

Reproduced by Overseer: source audit yes; fresh Python tests no (the detached review worktree had no pytest/ai-engine environment). The fix correctly fails when an expected width/height is absent, and structured ffprobe JSON is primary with text fallback.

- AC-3 fix is directionally correct and the new unit test is present.
- Fresh live AC-5/AC-6 evidence was not reproduced in this review.
- Verdict: **REVIEW — not approved**. Keep S-006 out of GREEN until the fresh unit and live evidence is reproducible, including the required CI evidence. The previous retro finding is resolved in source, not yet independently evidenced.

## Independent review — round 4 — target `4b3204abe1ae6ee5ba98f7720be94de228177e3f`

CI evidence reproduced from run `36068746332`: loop-audit passed; Ubuntu unit/real suite and Windows pytest passed; the probe fix is exercised on Windows. The artifact helper now fails closed for missing expected dimensions and uses structured ffprobe JSON first.

Verdict: **approved for Builder's next ledger decision**. Overseer does not change the ledger or GREEN this step. Existing overwrite policy finding remains assigned to S-028/S-033/S-086.
