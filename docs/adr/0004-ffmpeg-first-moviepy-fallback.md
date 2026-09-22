# ADR-0004 — FFmpeg subprocess is the media path; MoviePy 2 is a fallback only

## Status
Accepted — 2026-09-06

## Context
`from moviepy.editor import …` no longer exists in MoviePy 2 and crashed beat-sync (BUG-1); librosa cannot read MP4 directly. Users run on 16 GB RAM / GTX 1650; MoviePy's frame-by-frame Python loops are slow and memory-hungry for 1080p exports. Card S-004, S-006.

## Decision
`ai_engine/core/ffmpeg.py` owns audio extraction, probing and (later) muxing via an FFmpeg subprocess with a fixed argv list, resolved by `find_ffmpeg()` (system binary → bundled `imageio-ffmpeg`). MoviePy 2 stays installed **only** as a fallback for effects not yet ported, imported with the MoviePy-2 module paths. No `shell=True`, ever.

## Consequences
- Positive: predictable performance, real audio/video probing in tests (`tests/helpers/media.py::assert_playable`), no giant Python frame loops on the user's machine.
- Negative: two code paths until the fallback is removed; the MoviePy pin drags `pillow<11` (18 documented pip-audit exceptions in `ai-engine/pip-audit-ignore.txt`).
- Follow-ups: S-037 replaces the muscle-enhancer `mp4v`/no-audio writer with an FFmpeg mux and drops the MoviePy fallback, closing the pillow exceptions; S-074 temp-dir cleanup.
