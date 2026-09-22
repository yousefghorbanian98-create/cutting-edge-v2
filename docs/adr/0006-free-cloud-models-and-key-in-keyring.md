# ADR-0006 — Only free-tier cloud LLMs (OpenRouter `:free`, Nvidia NIM); API key in the OS keyring, never in git

## Status
Accepted — 2026-09-05

## Context
Budget is $0. The GPU (GTX 1650, 4 GB) cannot host a useful local LLM (> 3B) beside MediaPipe/Whisper, and Ollama was removed for that reason. The AI Assistant features (coach, captions translation, content strategy) still need an LLM. The OpenRouter key is user-supplied and must not leak through the repository.

## Decision
- Use OpenRouter models that carry the `:free` suffix, with a fallback chain and Nvidia NIM as second provider; no paid model is ever selected automatically.
- Local inference is limited to MediaPipe, OpenCV, faster-whisper *small* (CUDA 11.8, float16) and librosa; **no Ollama, no local LLM**.
- The key lives in `ai-engine/.env` during development (git-ignored) and in the Windows Credential Manager via `keyring` after S-086; `gitleaks` + `scripts/gate.py` secret scan + supervise C10 block any `sk-or-v1-`/`nvapi-` literal in tracked files.
- Every LLM call degrades gracefully offline with a Persian message; features must work without the key, minus the AI text.

## Consequences
- Positive: zero recurring cost; VRAM budget (< 800 MB) stays for vision/audio models; no secret in history.
- Negative: free tiers rate-limit and change; the fallback chain needs monitoring cards (S-053/S-056) and the user must paste a key once (U1).
- Follow-ups: S-086 keyring, S-053/S-056 provider chain, C15 rejects `ollama`/`langchain`/`litellm` in manifests.
