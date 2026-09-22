# 2026-09-22 — S-011: a unit marker still collects real modules

Steps: S-011 · Branch: arena/01a0c936-cutting-edge-v2 · Commits: S-011

## What broke
- `pytest -m unit` died at collection with `ModuleNotFoundError: cv2` in `tests/test_api_live.py`, so the gate unit stage was MISSING while `tests/unit` itself was green.

## Root cause
- pytest imports every file under `testpaths` before the marker deselects. A missing real-media dependency fails the unit stage.

## Rule
- `gate.py` unit runs `pytest tests/unit -m unit`; real runs `pytest tests -m real`. A collection import error with no FAILED line is MISSING, never a silent pass. Nested gate sets `CE_INSIDE_GATE=1` so the unit suite does not re-enter `--stage all`.
