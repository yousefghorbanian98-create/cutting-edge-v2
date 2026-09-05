# REVIEW — S-005 — round 1 — commit 77cfb0d

> Supervisor as independent reviewer. Inputs: CONTRACT.md, full diff, card S-005, protocol §1-⑧/§4.

CI: not configured (S-009). Evidence `local-linux`.
Evidence re-produced by reviewer: **yes** — fresh venv (numpy, librosa, imageio-ffmpeg, opencv-headless); `pytest tests/test_fixtures.py` → 5 passed; all 8 synthetic fixtures generated into a gitignored cache (`git status` clean afterwards); offline run emits the explicit `OFFLINE:` warning (visible in `-ra` summary), no silent skip. Checked from this sandbox too: Pexels / mediapipe-assets hosts unreachable (curl → 000), so the downloaded pair is correctly `unverified:network`.

## Summary
`make_fixtures.py` + committed `manifest.json` + `conftest` name lookup. Generation uses the bundled imageio-ffmpeg binary, which is exactly the sandbox rule; the runtime manifest records SHA256 of generated files. Clean, deterministic, no committed media.

## 1. Must fix before GREEN
- None.

## 2. Should fix soon (non-blocking — do in Job 0 as a small follow-up commit, then close)
- `[AC-1h]` Fixture (h) is named `كلیپ-تمرین. mp4`: the extension is `. mp4` (space before `mp4`) and the first letter is Arabic kāf `ك`, not Persian `ک`. `Storage._validate_extension` would reject that name with 415, so the fixture cannot be used in any upload test — which defeats its purpose. Rename to `کلیپ تمرین ۱.mp4` (Persian letters, internal space + Persian digit, proper `.mp4`), update manifest + docstring, and drop the `-f mp4` special-case if no longer needed.
- `_fetch_human_clip` depends on `CE_FIXTURE_HUMAN_CLIP_URL`; when network is available (supervisor CI on GitHub-hosted runner, S-009), pin a concrete Pexels permalink + SHA256 in `manifest.json.downloaded`. Track under S-009.
- `conftest._default_cache` uses `tempfile.mkdtemp` at import → a fresh dir per pytest process unless `CE_FIXTURES_DIR` is set. Default to `tests/fixtures/.cache/` (already gitignored) so local reruns and CI cache actually hit.

## 3. Verdict
approved — all six ACs reproduced; NG-1..NG-4 preserved. Close after the (h) rename lands (same step, no new review round required: test-data change only, must keep 5/5 green).
