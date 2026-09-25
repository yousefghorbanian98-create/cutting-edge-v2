"""Minimal in-process job runner (S-012).

Heavy work runs on a thread pool so the FastAPI event loop, and therefore
``GET /health``, stays responsive. Priority, persistence, retry, and resume
belong to S-072 — this module is only submit / poll / cancel.

Inference jobs use a separate one-worker pool when a GPU answers. If it does
not, they fall back to the CPU pool and the view says ``unverified``, never
``pass``. No model is loaded here.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any


class Cancelled(Exception):
    """Raised inside a worker when the caller asked the job to stop."""


def probe_gpu() -> bool:
    """True only when an NVIDIA GPU answers. Absence is not a pass."""
    try:
        import GPUtil
    except ImportError:
        return False
    try:
        return bool(GPUtil.getGPUs())
    except Exception as exc:
        logging.getLogger(__name__).debug("gpu probe unverified: %s", exc)
        return False


@dataclass
class Job:
    """Mutable job record. Mutate only while holding ``JobManager._lock``."""

    id: str
    status: str = "queued"
    progress: float = 0.0
    error: str | None = None
    result: dict[str, Any] | None = None
    output_filename: str | None = None
    partial_removed: bool = False
    kind: str = "cpu"
    device: str = "cpu"
    gpu: str = "unverified"
    fps: float | None = None
    stage: str = "queued"
    created_at: float = field(default_factory=time.monotonic)
    started_at: float | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    future: Future[None] | None = None


class JobControl:
    """What a worker is allowed to touch: progress, cancel, and the partial file."""

    def __init__(self, job: Job, manager: JobManager) -> None:
        self._job = job
        self._manager = manager

    @property
    def cancelled(self) -> bool:
        return self._job.cancel_event.is_set()

    @property
    def job_id(self) -> str:
        return self._job.id

    @property
    def cancel_event(self) -> threading.Event:
        return self._job.cancel_event

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise Cancelled()

    def report(self, progress: float) -> None:
        """Record 0..1 progress and abort if cancel was requested."""
        self._manager.set_progress(self._job.id, progress)
        self.raise_if_cancelled()

    def attach_partial(self, download_name: str) -> None:
        """Name the file cancel must delete. The name is a storage basename."""
        self._manager.set_output_filename(self._job.id, download_name)


class JobManager:
    """A fixed thread pool plus an in-memory job table.

    ``on_cancel_cleanup`` receives the download basename and must delete that
    file if it exists. The manager does not know about storage paths.
    """

    def __init__(
        self,
        max_workers: int = 2,
        on_cancel_cleanup: Callable[[str], None] | None = None,
        gpu_probe: Callable[[], bool] | None = None,
    ) -> None:
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ce-job")
        # Structural cap: one GPU inference body at a time. CPU jobs stay on _pool.
        self._gpu_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ce-gpu")
        self._gpu_probe = gpu_probe or probe_gpu
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._on_cancel_cleanup = on_cancel_cleanup

    def submit(self, fn: Callable[[JobControl], dict[str, Any]], *, kind: str = "cpu") -> str:
        """Queue ``fn`` and return the new job id. ``fn`` runs off the event loop.

        ``kind="inference"`` uses the single GPU worker when the probe is true.
        A false probe runs the same function on the CPU pool and records
        ``gpu="unverified"``.
        """
        if kind not in {"cpu", "inference"}:
            raise ValueError(f"unknown job kind: {kind}")
        use_gpu = kind == "inference" and bool(self._gpu_probe())
        job = Job(
            id=uuid.uuid4().hex,
            kind=kind,
            device="gpu" if use_gpu else "cpu",
            gpu="slot" if use_gpu else "unverified",
        )
        control = JobControl(job, self)
        with self._lock:
            self._jobs[job.id] = job
        pool = self._gpu_pool if use_gpu else self._pool
        job.future = pool.submit(self._run, job, fn, control)
        return job.id

    def submit_inference(self, fn: Callable[[JobControl], dict[str, Any]]) -> str:
        """Queue an analysis job. Missing GPU falls back to CPU and is not a pass."""
        return self.submit(fn, kind="inference")

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return None if job is None else self._view(job)

    def cancel(self, job_id: str) -> dict[str, Any] | None:
        """Request stop. The worker observes it at the next ``report`` / frame check."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if job.status in {"done", "error", "cancelled"}:
                return self._view(job)
            job.cancel_event.set()
            return self._view(job)

    def set_meter(self, job_id: str, *, fps: float | None = None, stage: str | None = None) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if fps is not None:
                job.fps = fps
            if stage is not None:
                job.stage = stage

    def set_progress(self, job_id: str, progress: float) -> None:
        bounded = max(0.0, min(1.0, float(progress)))
        with self._lock:
            job = self._jobs[job_id]
            if job.status in {"done", "error", "cancelled"}:
                return
            job.progress = bounded

    def set_output_filename(self, job_id: str, name: str) -> None:
        with self._lock:
            self._jobs[job_id].output_filename = name

    def _run(self, job: Job, fn: Callable[[JobControl], dict[str, Any]], control: JobControl) -> None:
        with self._lock:
            if job.cancel_event.is_set():
                job.status = "cancelled"
                job.partial_removed = True
                return
            job.status = "running"
            job.started_at = time.monotonic()
        try:
            result = fn(control)
        except Cancelled:
            self._finish_cancel(job)
            return
        except Exception as exc:
            self._delete_partial(job)
            with self._lock:
                job.status = "error"
                job.error = str(exc) or exc.__class__.__name__
                job.partial_removed = job.output_filename is not None
            return
        with self._lock:
            if job.cancel_event.is_set():
                pass
            else:
                job.result = result
                job.progress = 1.0
                job.status = "done"
                return
        self._finish_cancel(job)

    def _finish_cancel(self, job: Job) -> None:
        self._delete_partial(job)
        with self._lock:
            job.status = "cancelled"
            job.result = None
            job.partial_removed = True

    def _delete_partial(self, job: Job) -> None:
        name = job.output_filename
        if name and self._on_cancel_cleanup is not None:
            self._on_cancel_cleanup(name)

    def _view(self, job: Job) -> dict[str, Any]:
        eta_s: float | None = None
        if job.started_at is not None and 0.0 < job.progress < 1.0:
            elapsed = time.monotonic() - job.started_at
            eta_s = round(elapsed * (1.0 - job.progress) / job.progress, 2)
        percent = int(round(job.progress * 100))
        return {
            "id": job.id,
            "status": job.status,
            "progress": round(job.progress, 4),
            "percent": percent,
            "eta_s": eta_s,
            "error": job.error,
            "result": job.result,
            "output_filename": job.output_filename,
            "partial_removed": job.partial_removed,
            "kind": job.kind,
            "device": job.device,
            "gpu": job.gpu,
            "fps": job.fps,
            "stage": job.stage or job.status,
        }
