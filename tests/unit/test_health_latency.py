"""S-012: /health must not sleep inside the request.

The 200ms p95 budget is unchanged. A blocking cpu_percent(interval=0.1)
or an inline GPUtil probe makes that budget fail under concurrency.
"""

from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.unit


def test_health_does_not_wait_for_cpu_or_gpu(monkeypatch: pytest.MonkeyPatch) -> None:
    import ai_engine.main as main

    def slow_cpu(interval: float | None = None) -> float:
        assert interval is None
        time.sleep(0.01)
        return 3.0

    def slow_gpu() -> None:
        time.sleep(1.0)
        with main._gpu_lock:
            main._gpu_mem = 12.0

    monkeypatch.setattr(main.psutil, "cpu_percent", slow_cpu)
    monkeypatch.setattr(main, "_refresh_gpu_mem", slow_gpu)
    monkeypatch.setattr(main, "_gpu_probe_started", False)
    started = time.perf_counter()
    body = main.health()
    elapsed = time.perf_counter() - started
    assert elapsed < 0.2, elapsed
    assert body["status"] in {"healthy", "warning"}
    assert "cpu" in body and "gpu_mem" in body
