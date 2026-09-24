# S-006 reopen — retro-audit

Builder. Status: REVIEW. Not GREEN.

The existing REVIEW.md verdict stays `approved` for round 1. This file does not replace it and does not self-approve the reopen.

## Defect

`assert_playable` skipped the width/height check when the probe returned `None`. An expected width or height must fail in that case.

## Fix under review

- Expected width or height now raises `AssertionError` when the probe value is `None`.
- `probe_duration_and_streams` uses structured `ffprobe -print_format json` when ffprobe is available.
- The textual `ffmpeg -i` parser runs only as fallback.
- Proof: `tests/unit/test_probe.py`.

## Not in this reopen

S-004 ACs stay valid. `run_ffmpeg()` still always passes `-y`. That overwrite gap is BUG-18 and belongs to S-028, S-033, and S-086. No new CONTRACT for the current timeline step.
