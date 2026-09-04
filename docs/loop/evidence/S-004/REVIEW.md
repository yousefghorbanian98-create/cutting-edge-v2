# REVIEW — S-004 — round 1 — commit 8dab714

> Supervisor as independent reviewer (`11_SUPERVISOR.md` §6). Inputs: CONTRACT.md, full diff, card S-004, BUG-1/BUG-4, protocol §1-⑧/§4.

CI: not configured (S-009). Evidence `local-linux`.
Evidence re-produced by reviewer: **yes** — installed `numpy`, `librosa`, `imageio-ffmpeg` into a fresh venv; `pytest tests/test_beat_sync.py` → 3 passed in ~30 s: 120-BPM click-track MP4 → 117.45 BPM (within ±3); silent MP4 → `[]` without exception; AAC 48 kHz → WAV 22050 mono. Grep confirms no `moviepy.editor` import and no `verbose=` kwarg anywhere in `ai-engine/src`.

## Summary
New `core/ffmpeg.py` with binary discovery (`CE_FFMPEG_BIN` → PATH → imageio-ffmpeg), `extract_audio`, a probe helper that parses `ffmpeg -i` output (since `ffprobe` isn't bundled by imageio-ffmpeg), and MoviePy 2 as a *fallback only* with the correct import location. `BeatSyncEngine` now returns `[]` for silent/no-audio input. Closes BUG-1 (regressed) and BUG-4.

## 1. Must fix before GREEN
- None.

## 2. Should fix soon (non-blocking)
- `probe_duration_and_streams` parses human-readable `ffmpeg -i` stderr, which is locale/version-fragile. When S-005 lands (fixture factory needs ffprobe anyway), prefer `ffprobe -print_format json` when available and keep the stderr parser as fallback. Note in S-005 CONTRACT.
- Update `06_BUGS.md`: BUG-1 and BUG-4 → CLOSED (S-004, 8dab714) once GREEN. Builder should do this in stage ⑨.
- Detected tempo 117.45 for a true 120 click is within contract tolerance but suggests `librosa.beat.beat_track` default hop; fine for now, revisit in S-039 (beat markers on timeline need ≤ 30 ms accuracy).

## 3. Verdict
approved — all three ACs reproduced; NGs preserved; BUG-1/BUG-4 genuinely fixed this time.
