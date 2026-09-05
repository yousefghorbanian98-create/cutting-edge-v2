# 04 — Ledger (دفترچه‌ی وضعیت)

> **ماشین‌خوان است.** هر ردیف یک مرحله از `steps.json`. فقط ستون‌های `status`, `iter`, `verified_on`, `evidence`, `notes` را ویرایش کنید.
> `python scripts/verify_ledger.py` این فایل را در CI بررسی می‌کند.
>
> **status ∈ {TODO, RED, REVIEW, AMBER, GREEN, BLOCKED}**
> - `TODO` شروع نشده
> - `RED` در حال کار، تست واقعی قرمز
> - `REVIEW` کد و تست Builder سبز؛ منتظر verdict بازبین تازه (`evidence/S-xxx/REVIEW.md`)
> - `AMBER` کد کامل، منتظر تأیید کاربر (U1/U2/U3) یا تست خارجی
> - `GREEN` تست واقعی سبز + REVIEW approved + شواهد ثبت‌شده (`verified_on` الزامی)
> - `BLOCKED` وابستگی خارجی؛ دلیل در notes
>
> **verified_on** لیستی با کاما از: `ci-ubuntu`, `ci-windows`, `local-linux`, `user-gpu` (ماشین کاربر با GTX 1650).
> **evidence** لینک/مسیر: CI run URL، فایل junit، اسکرین‌شات، JSON خروجی smoke-gpu.ps1.

| id | title | status | iter | verified_on | evidence | notes |
|----|-------|--------|------|-------------|----------|-------|
| S-001 | Repo hygiene: remove generator scripts, add LICENSE/.editorconfig/docs tree | GREEN | 2 | local-linux | docs/loop/evidence/S-001/CONTRACT.md; docs/loop/evidence/S-001/REVIEW.md; tests/unit/test_repo_hygiene.py (5/5 pass local-linux) | CI absent until S-009 |
| S-002 | Backend boot fix: package imports, dotenv, dev scripts | GREEN | 2 | local-linux | docs/loop/evidence/S-002/CONTRACT.md; docs/loop/evidence/S-002/REVIEW.md (approved r2); tests/real/test_backend_boot.py (6/6 pass local-linux) | Round-1 [DEFECT] fixed (ai-engine/README.md + tomllib assertion every [project] file exists); no metadata warning on non-editable install. Non-blocking carried: dev-backend.sh fa/en hint for missing media deps (S-011); AC-6 (.ps1) unverified:windows until S-009. CI absent until S-009. |
| S-003 | Security fix: upload/download path traversal, size & type limits, CORS | GREEN | 2 | local-linux | docs/loop/evidence/S-003/CONTRACT.md (revised r2 + AC-7); docs/loop/evidence/S-003/REVIEW.md (approved r2); tests/test_security.py (6/6 pass real, local-linux) | Round 2: fixed round-1 [SECURITY] (null byte → 500). _safe_path now validates _is_safe_basename BEFORE resolve(), wraps resolve() in try/except (ValueError,OSError) → PathTraversalError, and rejects ''/'.'/'..' explicitly. Added x%00.mp4, %00, a%00b.mp4 cases to test_download_traversal_returns_404 (all → 404, no 500). Ruff/Bandit deferred to S-008; applicable static checks (verify_ledger.py, py_compile) green. Closed (⑨⑩) after REVIEW r2 `approved`. Carried non-blocking: `%` handling comment/strip in sanitize_filename → S-008. CI absent until S-009. |
| S-004 | MoviePy 2.0 compatibility + FFmpeg-first audio extraction (BUG 4) | GREEN | 1 | local-linux | docs/loop/evidence/S-004/CONTRACT.md; docs/loop/evidence/S-004/REVIEW.md (approved r1); tests/test_beat_sync.py (3/3 pass local-linux) | BUG-1 and BUG-4 CLOSED (see 06_BUGS.md). core/ffmpeg.py (discover CE_FFMPEG_BIN→PATH→imageio-ffmpeg; ffmpeg subprocess primary, MoviePy 2 import only fallback); beat_sync returns [] on silence (no dummy beats). BPM 117.45 (±3 of 120) on click-track MP4; silent MP4 → []; AAC 48k → WAV 22050 mono. Non-blocking: probe_duration_and_streams uses ffmpeg -i parser; prefer ffprobe json when S-005 lands. CI absent until S-009. |
| S-005 | Real-media fixture factory (FFmpeg-generated + licensed human clip) | REVIEW | 1 |  | docs/loop/evidence/S-005/CONTRACT.md; tests/test_fixtures.py (5/5 pass real, local-linux) | Ready for fresh review. make_fixtures.py builds all 8 synthetic fixtures (120BPM 720p, silent, 2s short, 0-byte, broken header, 9:16, 4K 3s, Persian name) via imageio-ffmpeg; probe_duration_and_streams verifies; offline degrades with explicit OFFLINE warning (human_clip.mp4 + pose.jpg = unverified:network). conftest exposes by name; fixtures cached in gitignored dir (never committed). Pexels/pose network download = unverified:network. |
| S-006 | Test harness: live-server API tests + artifact assertions helper | REVIEW | 1 |  | docs/loop/evidence/S-006/CONTRACT.md; tests/test_api_live.py + tests/helpers/media.py (live uvicorn; 3/3 pass real, local-linux) | Ready for fresh review. conftest `live_api` (real uvicorn on free port), helpers assert_playable/frame_diff/ssim_region, `--strict-markers` with unit/real/heavy/gpu. Live HTTP: /editor/beat-sync → 120 BPM JSON, clips non-empty; /muscle/enhance → playable output + mean abs pixel diff > 2.0. mediapipe absent (no libGL) → enhancer degrades gracefully; face-protection path deferred to S-035. Full `-m real` suite 17 passed (incl. S-002/003/004/005) no regressions. |
| S-007 | Frontend styling fix: Tailwind 4 + DaisyUI 5 + fonts + globals.css | TODO | 0 |  |  |  |
| S-008 | Toolchain: Biome, Ruff, tsc strict, Turbo 2 tasks, pinned versions, pre-commit | TODO | 0 |  |  |  |
| S-009 | CI overhaul: matrix (ubuntu lint/unit/e2e + windows heavy/tauri), caching, artifacts, all branches | TODO | 0 |  |  |  |
| S-010 | Tauri walking skeleton that compiles and ships a first .exe | TODO | 0 |  |  |  |
| S-011 | Loop tooling: gate.py stages, ledger verifier, smoke-gpu.ps1, session handoff template | TODO | 0 |  |  |  |
| S-012 | Non-blocking processing: job model + thread pool so /health stays alive | TODO | 0 |  |  |  |
| S-013 | Timeline domain model + Zustand store with undo history (zundo) + vitest | TODO | 0 |  |  |  |
| S-014 | Media Bin: multi-file import, metadata probe, thumbnails, rename/delete | TODO | 0 |  |  |  |
| S-015 | Timeline canvas: ruler, tracks, virtualized clips, 60fps rendering | TODO | 0 |  |  |  |
| S-016 | Playhead sync, scrubbing, JKL, frame-step, time display | TODO | 0 |  |  |  |
| S-017 | Clip drag/move/reorder across tracks with snapping | TODO | 0 |  |  |  |
| S-018 | Trim handles (in/out), ripple & roll trim | TODO | 0 |  |  |  |
| S-019 | Split at playhead (Ctrl+B), delete, ripple delete | TODO | 0 |  |  |  |
| S-020 | Selection (click/shift/marquee), copy/paste/duplicate | TODO | 0 |  |  |  |
| S-021 | Undo/Redo UI (Ctrl+Z / Ctrl+Shift+Z) + history panel | TODO | 0 |  |  |  |
| S-022 | Multi-track: add/remove tracks, mute/solo/lock, text track | TODO | 0 |  |  |  |
| S-023 | Timeline zoom (Ctrl+wheel, slider, fit) + horizontal scroll + minimap | TODO | 0 |  |  |  |
| S-024 | Sequence preview player: multi-clip compositing playback | TODO | 0 |  |  |  |
| S-025 | Keyboard shortcuts registry + in-app cheat sheet (?) | TODO | 0 |  |  |  |
| S-026 | E2E journey v0.3: import → arrange → trim → split → undo → preview | TODO | 0 |  |  |  |
| S-027 | MILESTONE v0.3.0: regression, tag, CI installer, pre-release, user smoke test | TODO | 0 |  |  |  |
| S-028 | FFmpeg export engine: timeline JSON → filter_complex, progress, cancel, NVENC detect | TODO | 0 |  |  |  |
| S-029 | WebSocket progress channel /ws/jobs/{id} (BUG 6) + frontend hook | TODO | 0 |  |  |  |
| S-030 | Export dialog: resolution/fps/codec/bitrate/presets/destination | TODO | 0 |  |  |  |
| S-031 | Export progress UI, cancel, open output folder, export history | TODO | 0 |  |  |  |
| S-032 | Audio mixdown: track gains, fades, ducking, music bed | TODO | 0 |  |  |  |
| S-033 | Export quality validation suite (ffprobe + SSIM + browser playback) | TODO | 0 |  |  |  |
| S-034 | MILESTONE v0.4.0 | TODO | 0 |  |  |  |
| S-035 | Muscle Enhancer: 478-pt Face Mesh protection with feathering + temporal smoothing (BUG 3) | TODO | 0 |  |  |  |
| S-036 | Muscle Enhancer: real pose-based body/muscle-group masks + GPU path + CPU fallback + frame checkpoints | TODO | 0 |  |  |  |
| S-037 | Muscle Enhancer: FFmpeg mux (keep audio, H.264 not mp4v), job progress, cancel | TODO | 0 |  |  |  |
| S-038 | Muscle Enhancer UI: before/after split slider on live frame, presets, progress | TODO | 0 |  |  |  |
| S-039 | Beat Sync integration: markers on timeline, snap-to-beat, auto-cut to clips, music import | TODO | 0 |  |  |  |
| S-040 | Living Timeline: real energy/emotion heat-map per segment | TODO | 0 |  |  |  |
| S-041 | Emotion Color Engine: analysis → LUT (.cube) → preview + export (lut3d) | TODO | 0 |  |  |  |
| S-042 | One-Click Viral Cut → new sequence with 9:16 subject-tracked crop | TODO | 0 |  |  |  |
| S-043 | Voice Command: mic UI → Whisper → Persian/English intent → editor actions | TODO | 0 |  |  |  |
| S-044 | Whisper captions: transcript panel, SRT export, caption text track, burn-in on export | TODO | 0 |  |  |  |
| S-045 | Mood DNA visualization: radar + timeline charts, cache by hash | TODO | 0 |  |  |  |
| S-046 | Style Match: side-by-side compare, DNA diff, 'Apply Style' suggestions | TODO | 0 |  |  |  |
| S-047 | Pose-to-Pose mapping: skeleton overlay + matched segments | TODO | 0 |  |  |  |
| S-048 | Transition Intelligence: per-cut suggestions with reasoning + apply via xfade | TODO | 0 |  |  |  |
| S-049 | Real-Time Style Preview: WebGL LUT shader on preview canvas | TODO | 0 |  |  |  |
| S-050 | Style Library: preset JSON, thumbnails, import/export, naming policy | TODO | 0 |  |  |  |
| S-051 | Proactive Coach: analysis-triggered suggestions panel (apply/dismiss, throttled) | TODO | 0 |  |  |  |
| S-052 | Workout Form Analyzer: pose overlay, rep counting, joint angles, report | TODO | 0 |  |  |  |
| S-053 | Multi-Modal Brain: chat with frame/transcript/timeline context + fallback chain (Reheal L4) | TODO | 0 |  |  |  |
| S-054 | Auto-Narrator: script generation → edge-tts → audio clip on timeline | TODO | 0 |  |  |  |
| S-055 | Content Strategy dashboard: virality score breakdown, hook timing, length, hashtags | TODO | 0 |  |  |  |
| S-056 | AI guardrails: rate limits, content-hash cache, offline mode UX, cost = $0 enforcement | TODO | 0 |  |  |  |
| S-057 | MILESTONE v0.5.0 | TODO | 0 |  |  |  |
| S-058 | Tauri shell: custom titlebar, window state, min size, dark theme, drag region | TODO | 0 |  |  |  |
| S-059 | Rust IPC: dialogs, fs metadata, native drag-drop paths, opener, minimal capabilities | TODO | 0 |  |  |  |
| S-060 | Python backend as sidecar: PyInstaller bundle, spawn/health-wait/restart, model download on first run | TODO | 0 |  |  |  |
| S-061 | Windows path handling: asset protocol for preview, unicode/Persian names, long paths, drive letters | TODO | 0 |  |  |  |
| S-062 | NSIS installer: icon, license, per-user install, shortcuts, clean uninstall, fa/en languages | TODO | 0 |  |  |  |
| S-063 | Branding: final icon set, metadata, single-source version sync | TODO | 0 |  |  |  |
| S-064 | System tray, single-instance, graceful shutdown with running jobs | TODO | 0 |  |  |  |
| S-065 | Auto-updater: tauri-plugin-updater + GitHub Releases + minisign keys in CI secrets | TODO | 0 |  |  |  |
| S-066 | Desktop E2E on CI Windows: tauri-driver journeys + installer smoke + orphan/leak checks | TODO | 0 |  |  |  |
| S-067 | MILESTONE v0.6.0 — first installable pre-release | TODO | 0 |  |  |  |
| S-068 | Project file (.cev2) versioned JSON schema, save/save-as/open/recent, migrations | TODO | 0 |  |  |  |
| S-069 | Auto-save + crash restore (Reheal L6) | TODO | 0 |  |  |  |
| S-070 | Project & sequence settings: resolution, fps, aspect, color space; new-project dialog | TODO | 0 |  |  |  |
| S-071 | Media relink + integrity (checksum, backup before overwrite) (Reheal L5) | TODO | 0 |  |  |  |
| S-072 | Full job queue: priority, concurrency=2, retry×3 backoff, persistence, resume from checkpoint (Reheal L7) | TODO | 0 |  |  |  |
| S-073 | Structured logging (JSON) + rotation + log viewer API + Reheal drawer real data | TODO | 0 |  |  |  |
| S-074 | Temp cleanup (BUG 5) + disk space guard | TODO | 0 |  |  |  |
| S-075 | Memory & GPU guards live (Reheal L1/L2): thresholds, float16 switch, preview downscale | TODO | 0 |  |  |  |
| S-076 | Rust watchdog for sidecar + frontend reconnect UX | TODO | 0 |  |  |  |
| S-077 | Chaos test suite: kill backend mid-export, pull file mid-import, fill temp, no GPU, bad key | TODO | 0 |  |  |  |
| S-078 | MILESTONE v0.7.0 | TODO | 0 |  |  |  |
| S-079 | Coverage targets: Python core ≥ 80%, TS domain ≥ 80%, Rust commands ≥ 70%; mutation spot-checks | TODO | 0 |  |  |  |
| S-080 | Integration tests for every endpoint with real fixtures + OpenAPI contract check | TODO | 0 |  |  |  |
| S-081 | Full E2E journeys + visual regression across all panels (fa & en, RTL & LTR) | TODO | 0 |  |  |  |
| S-082 | Performance benchmark suite + budgets (CI CPU baseline + user GTX 1650 profile) | TODO | 0 |  |  |  |
| S-083 | Memory leak audit: frontend heap snapshots, Python tracemalloc soak, Rust valgrind-lite | TODO | 0 |  |  |  |
| S-084 | Accessibility WCAG 2.1 AA: axe, keyboard-only, focus, contrast, reduced motion | TODO | 0 |  |  |  |
| S-085 | i18n: fa + en with runtime switch, all strings externalized, RTL/LTR, number/date locale | TODO | 0 |  |  |  |
| S-086 | Security audit: secrets in OS keyring, CSP, capabilities, dependency audits, path/ssrf review | TODO | 0 |  |  |  |
| S-087 | UX polish: empty states, skeletons, error states, onboarding, motion tokens, micro-interactions | TODO | 0 |  |  |  |
| S-088 | Shortcuts documentation + settings for remapping | TODO | 0 |  |  |  |
| S-089 | Privacy & diagnostics: no telemetry by default, opt-in local crash bundle export | TODO | 0 |  |  |  |
| S-090 | MILESTONE v0.8.0 (Release Candidate 1) | TODO | 0 |  |  |  |
| S-091 | Decision freeze: product name, default language, formats, icon, license (defaults apply on silence) | TODO | 0 |  |  |  |
| S-092 | User documentation (fa + en): install, first run, each module, troubleshooting, GPU notes, FAQ | TODO | 0 |  |  |  |
| S-093 | README overhaul: screenshots/GIF, badges, architecture diagram, quick start | TODO | 0 |  |  |  |
| S-094 | Demo video: auto-recorded Playwright journey + Auto-Narrator voiceover (fa/en) | TODO | 0 |  |  |  |
| S-095 | Licensing & third-party notices: FFmpeg (LGPL build), models, fonts, dependencies | TODO | 0 |  |  |  |
| S-096 | Release rehearsal: clean-VM install, upgrade 0.8→1.0 via updater, uninstall, rollback plan | TODO | 0 |  |  |  |
| S-097 | SHIP v1.0.0: tag, GitHub Release (exe + SHA256 + latest.json), release notes fa/en, CHANGELOG | TODO | 0 |  |  |  |
| S-098 | Post-release loop: issue templates, triage labels, 1.0.x hotfix protocol, next-cycle backlog | TODO | 0 |  |  |  |
