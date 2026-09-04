"""Safe upload/download storage (S-003: path traversal, size & type limits).

This is the only module allowed to touch the media storage directory. It:
  * sanitizes every client-supplied filename so it can never escape the base dir,
  * enforces an extension allow-list (→ 415),
  * enforces a maximum upload size, streaming to disk and counting bytes (→ 413),
  * resolves download names strictly inside the base dir (→ 404 on traversal).
"""
from __future__ import annotations

import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Iterable

from fastapi import UploadFile

# Media types the app intentionally accepts. Keep in sync with the frontend.
VIDEO_EXTENSIONS = frozenset({".mp4", ".m4v", ".mov", ".mkv", ".avi", ".webm", ".wmv"})
AUDIO_EXTENSIONS = frozenset({".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac"})
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"})
SUBTITLE_EXTENSIONS = frozenset({".srt"})
ALLOWED_EXTENSIONS = (
    VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | IMAGE_EXTENSIONS | SUBTITLE_EXTENSIONS
)

DEFAULT_MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB (card S-003 default)


class MediaTypeError(Exception):
    """Raised when a file's extension is not in the allow-list (→ 415)."""


class PayloadTooLargeError(Exception):
    """Raised when an upload exceeds the configured limit (→ 413)."""


class PathTraversalError(Exception):
    """Raised when a download/name would resolve outside the base dir (→ 404)."""


# Nasty separator / dot-dot sequences that must never appear in a stored name.
UNSAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._\u0600-\u06FF\u0020-]")
SEPARATOR_CHARS = {"/", "\\", "\x00"}
DOT_DOT = {".."}


def sanitize_filename(name: str) -> str:
    """Return a safe basename for `name`, or '' if nothing usable remains.

    Strips any path components and dot-dot, removes control/separator chars, and
    collapses runs of dots. The returned value is a *bare* name — safe to join
    under a trusted base directory.
    """
    if not name:
        return ""
    raw = name.replace("\\", "/")
    base = raw.split("/")[-1]
    # Drop any leading/trailing dot-dot and dots-only tokens.
    tokens = [t for t in base.split(".") if t not in ("", "..")]
    base = ".".join(tokens)
    base = UNSAFE_NAME_RE.sub("_", base).strip(" .")
    return base


def _is_safe_basename(name: str) -> bool:
    if not name or name in {"", ".", ".."}:
        return True  # empty names resolved to '' mean "not found" downstream
    if any(c in name for c in SEPARATOR_CHARS):
        return False
    parts = name.split("/")
    if any(p in DOT_DOT or p == "" for p in parts):
        return False
    return True


class Storage:
    """Stores uploads/artifacts under a single trusted base directory."""

    def __init__(
        self,
        base_dir: str | os.PathLike[str],
        max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
        allowed_extensions: Iterable[str] = ALLOWED_EXTENSIONS,
    ) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_upload_bytes = int(max_upload_bytes)
        self.allowed = {ext.lower() for ext in allowed_extensions}

    # ── internals ──
    def _validate_extension(self, name: str) -> str:
        ext = Path(name).suffix.lower()
        if ext not in self.allowed:
            raise MediaTypeError(f"نوع فایل غیرمجاز است: {ext or '(بدون پسوند)'}")
        return ext

    def _safe_path(self, name: str) -> Path:
        """Resolve `name` under base_dir and forbid escaping it."""
        candidate = (self.base_dir / name).resolve()
        if _is_safe_basename(name) is False:
            raise PathTraversalError(name)
        try:
            candidate.relative_to(self.base_dir)
        except ValueError as exc:
            raise PathTraversalError(name) from exc
        return candidate

    # ── public API ──
    def save_upload(self, file: UploadFile) -> str:
        """Stream an uploaded file to disk under a UUID name; returns abs path."""
        safe = sanitize_filename(file.filename or "")
        ext = self._validate_extension(safe or "file.bin")
        stored_name = f"{uuid.uuid4().hex}{ext}"
        path = self.base_dir / stored_name

        written = 0
        with open(path, "wb") as out:
            while True:
                chunk = file.file.read(1024 * 1024)  # 1 MiB
                if not chunk:
                    break
                written += len(chunk)
                if written > self.max_upload_bytes:
                    out.close()
                    path.unlink(missing_ok=True)
                    raise PayloadTooLargeError(
                        f"حجم فایل از حد مجاز بیشتر است ({self.max_upload_bytes} bytes)"
                    )
                out.write(chunk)
        return str(path)

    def save_output(self, original_name: str = "output.mp4") -> tuple[str, str]:
        """Reserve a safe output path. Returns (absolute_path, safe_download_name)."""
        safe = sanitize_filename(original_name) or "output.mp4"
        ext = self._validate_extension(safe)
        stored_name = f"{uuid.uuid4().hex}{ext}"
        return str(self.base_dir / stored_name), stored_name

    def resolve_download(self, name: str) -> Path:
        """Return a safe path for `name` or raise PathTraversalError."""
        return self._safe_path(name)

    def exists(self, name: str) -> bool:
        try:
            return self._safe_path(name).is_file()
        except PathTraversalError:
            return False

    def delete(self, name: str) -> None:
        try:
            self._safe_path(name).unlink(missing_ok=True)
        except PathTraversalError:
            pass

    def clear(self) -> None:
        """Remove all stored files (used by tests / temp cleanup)."""
        shutil.rmtree(self.base_dir, ignore_errors=True)
        self.base_dir.mkdir(parents=True, exist_ok=True)
