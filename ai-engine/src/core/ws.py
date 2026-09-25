"""WebSocket progress messages (S-029). Percent comes from the job, not a fake clock."""

from __future__ import annotations

from typing import Any


def progress_message(view: dict[str, Any]) -> dict[str, Any]:
    return {
        "percent": int(view.get("percent") or 0),
        "fps": view.get("fps"),
        "eta": view.get("eta_s"),
        "stage": view.get("stage") or view.get("status") or "unknown",
        "log": view.get("error") or "",
    }
