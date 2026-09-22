# ADR-0005 — Ship the FastAPI backend as a PyInstaller sidecar spawned by Tauri

## Status
Accepted — 2026-09-05

## Context
The product is a single Windows `.exe` for non-technical users; the AI core is Python (FastAPI, MediaPipe, faster-whisper, librosa). Users cannot be asked to install Python or a venv. Budget is $0, so no hosted backend. Cards S-010, S-060, S-062, S-076.

## Decision
Bundle the backend with **PyInstaller** into `ai-engine.exe`, register it as a Tauri 2 `externalBin` sidecar, spawn it from Rust on app start, wait on `/health`, restart it on crash (Rust watchdog), and stop it on exit. Heavy models (Whisper small, FFmpeg) are downloaded on first run into the user data dir with checksums, keeping the installer small. The desktop app talks to `127.0.0.1:<port>` only; CORS allow-list is `tauri://localhost` + dev origins.

## Consequences
- Positive: one installer, no user-visible Python; the backend can be tested in isolation with the same binary CI builds.
- Negative: PyInstaller + MediaPipe/torch bundles are large and fragile (hidden imports, DLLs); first-run download needs a clear Persian UI and offline degradation.
- Follow-ups: S-010 walking skeleton (tauri build once, BUG-16), S-060 sidecar + first-run downloads, S-066 installer smoke + orphan-process checks, S-076 watchdog.
