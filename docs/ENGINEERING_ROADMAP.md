# Cutting Edge v2.0 — Complete Engineering Roadmap & Context Transfer

> **Canonical project context. Read this document before changing architecture, stack, or scope.**
>
> Version: `0.2-alpha` → Target: `1.0`
> Date maintained: 2026-09-04
> Current status: Interactive prototype / early MVP (approximately 30–35% overall)
> Repository: `yousefghorbanian98-create/cutting-edge-v2`
> Working branch: `arena/01a06891-cutting-edge-v2`
>
> The branch name above is the active Arena branch. Older planning notes mentioned `arena/01a06904-cutting-edge-v2`; do not switch to or create that branch.

## Contents

1. Origin and vision
2. Hardware constraints
3. Approved features
4. Locked technology stack
5. Architecture and data flow
6. Current file structure
7. Current status: done
8. Remaining work
9. Known bugs and required fixes
10. Reheal Loop (seven layers)
11. AI configuration
12. Design system
13. Open-source references
14. Phased roadmap
15. Decisions needed from the user
16. Handoff prompt for future AI sessions
17. Definition of done and release checklist

---

## 1. Origin and vision

### Previous project

- Project: Chat2DB v1.4.0
- Repository: `github.com/yousefghorbanian98-create/Chat2DB`
- Problems: weak frontend, heavy Electron architecture, and poor UX
- Decision: full rewrite from scratch

### New project: Cutting Edge v2.0

- Type: Windows desktop video editor
- Core modules: Editor, Style Match, AI Assistant
- Bonus module: Muscle Enhancer with natural muscle definition
- Quality target: Linear / Supabase / Cursor-level product polish
- Budget: `$0`, using free tools and free API tiers
- Primary use case: sports, fitness, and bodybuilding video editing
- Repository is separate from Chat2DB
- Default language direction: Persian/RTL with English support

### Product promise

The application should make fitness-video editing fast without falsifying a person’s body. Muscle enhancement may improve local definition and lighting only; it must never reshape the body, liquify the subject, or create fake muscles.

---

## 2. Hardware constraints

- OS: Windows
- RAM: 16 GB
- GPU: Nvidia GTX 1650, 4 GB VRAM
- CUDA target: 11.8
- VRAM budget: below 800 MB for simultaneously loaded models where possible
- Application RAM target: below 1.5 GB for normal preview work
- Local AI: Whisper Small, MediaPipe, OpenCV
- Heavy language/vision AI: cloud APIs on free tiers
- Do not rely on local LLMs above 3B parameters
- Ollama is removed and must not be reintroduced as a requirement
- PyTorch, if introduced for a specific pipeline, must target CUDA 11.8 and float16
- 1080p is the comfortable preview target; 4K should be downscaled for preview

Performance work must be measured on the target GTX 1650 machine. Never make GPU acceleration a hard requirement when a CPU fallback is available.

---

## 3. Approved feature set (all 16 approved)

### Editor — five features

1. **Living Timeline:** frame energy/emotion heat-map.
2. **Voice Command Editing:** Persian/English speech to edit actions using Whisper.
3. **Beat Sync:** automatic cuts on music beats using librosa and extracted audio.
4. **Emotion Color Engine:** color grade based on scene emotion.
5. **One-Click Viral Cut:** find the best 30 seconds for Reels, Shorts, or TikTok.

### Style Match — five features

6. **Mood DNA Extraction:** energy, color, rhythm, camera, motion, lighting, transitions, and emotion.
7. **Pose-to-Pose Mapping:** MediaPipe 33-point body tracking comparison.
8. **Transition Intelligence:** understand the context and purpose of a transition, not only its type.
9. **Real-Time Style Preview:** LUT-based preview without a full render.
10. **Style Library:** reusable presets, including generic fitness/cinematic looks and user-created presets.

> Named creator styles must be treated as inspiration/preset labels only and must not imply endorsement or copy protected branding without permission.

### AI Assistant — five features

11. **Proactive Coach:** suggest improvements without being asked.
12. **Workout Form Analyzer:** pose analysis such as squat depth and alignment.
13. **Multi-Modal Brain:** vision, audio, and text context.
14. **Auto-Narrator:** Persian/English narration through free `edge-tts` voices.
15. **Content Strategy AI:** virality-score guidance and platform recommendations.

### Muscle Enhancer — one feature with five techniques

16. Natural muscle-definition enhancement:
   - muscle-aware CLAHE/local contrast
   - AI dodge and burn for ridges/grooves
   - edge-aware sharpening
   - natural skin-texture enhancement
   - midtone sculpting
   - face protection using a feathered face mask
   - presets: Competition, Natural Gym, Cinematic, Instagram
   - hard constraint: no body reshaping, liquify, or fabricated muscles

---

## 4. Technology stack (locked unless explicitly re-approved)

### Desktop and frontend

- Desktop shell: Tauri 2.0 (Rust)
- Frontend: Next.js App Router with static-export-compatible architecture
- UI: React 19, TypeScript strict mode
- State: Zustand 5
- Styling: Tailwind CSS 4 + DaisyUI 4
- Animation: Framer Motion 11
- Icons: Lucide React
- Fonts: Inter Variable, JetBrains Mono, Vazirmatn
- Monorepo: Turborepo + pnpm

### Backend and media

- AI backend: Python FastAPI + Uvicorn
- Primary cloud AI: OpenRouter free tier
- Secondary provider: Nvidia NIM free tier (planned)
- Local speech: faster-whisper Small, CUDA 11.8/float16 where available
- Pose/face: MediaPipe 0.10 on CPU
- Scene detection: PySceneDetect 0.6
- Video editing: MoviePy 2.x where useful
- Image processing: OpenCV 4.x
- Audio analysis: librosa
- TTS: edge-tts, no API key, Persian support
- Codec/export: FFmpeg command line

### Engineering tools

- Build: Turborepo + pnpm; Next.js dev/build currently used by the root workspace
- Tests: Vitest, Playwright, pytest
- Linting/formatting: Biome (JS/TS), Ruff (Python)
- Logging: tracing (Rust), loguru or structured logging (Python)
- CI/CD: GitHub Actions free tier

> Repository audit note: the current checkout is a root Next.js app plus `ai-engine`; the full `apps/desktop` Tauri monorepo layout described below is the target architecture and is not yet fully present. Do not mark planned files as implemented without verifying them in the checkout.

---

## 5. Architecture and data flow

### Layers

1. **Presentation:** Tauri window → Next.js → React, Framer Motion, DaisyUI. Panels: Editor, Style Match, AI Assistant, Muscle Enhancer.
2. **IPC bridge:** Tauri commands between Rust and TypeScript. **Planned.**
3. **Core engine:** FFmpeg decoder, audio engine, render pipeline, and file manager in Rust. **Planned.**
4. **AI layer:** Python FastAPI on port `8001`: OpenRouter, Whisper, MediaPipe, OpenCV, scene detection, beat sync, Muscle Enhancer, Mood DNA, voice editor, color engine, viral cut, coach, form analyzer, narrator, and content strategy.
5. **Reheal:** health monitor → error catcher → auto-fixer → pipeline validator → crash recovery → memory guard → GPU guard.

### Intended data flow

```text
User drops video
  → frontend creates FormData
  → FastAPI validates and queues a job
  → Python/OpenCV/MediaPipe/librosa/FFmpeg processes it
  → API returns JSON, job status, and downloadable files
  → frontend stores state in Zustand
  → UI re-renders timeline, preview, and logs
```

Local development may use `http://127.0.0.1:8001`; browser-facing deployed code must use a configured relative/proxied URL and must never hard-code localhost for a remote user.

---

## 6. File structure

### Current checkout

```text
cutting-edge-v2/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                 # current interactive editor prototype
│   └── globals.css
├── ai-engine/
│   ├── requirements.txt
│   └── src/
│       ├── main.py              # FastAPI health/chat/enhance endpoints
│       ├── muscle/muscle_enhancer.py
│       ├── style_match/mood_dna.py
│       └── reheal/
│           ├── health_monitor.py
│           ├── auto_fixer.py
│           └── crash_recovery.py
├── packages/design-system/tokens.ts
├── scripts/setup-ai.ps1
├── docs/ENGINEERING_ROADMAP.md
├── package.json
├── pnpm-workspace.yaml
├── next.config.mjs
├── tsconfig.json
└── README.md
```

### Target structure

```text
apps/desktop/
├── src-tauri/                   # complete Tauri shell, commands, config
└── src/
    ├── app/
    ├── components/
    │   ├── editor/
    │   ├── style-match/
    │   ├── ai-assistant/
    │   ├── muscle-enhancer/
    │   └── shared/
    ├── stores/
    ├── hooks/
    └── lib/
packages/
├── ui/
├── design-system/
└── ai-core/
ai-engine/src/
├── analyzer/
├── captioner/
├── style_match/
├── muscle/
├── editor_ai/
├── assistant/
└── reheal/
tests/
.github/workflows/ci.yml
```

Planned modules include `video_analyzer.py`, `whisper_caption.py`, `pose_mapper.py`, `transition_ai.py`, `beat_sync.py`, `voice_editor.py`, `emotion_color.py`, `viral_cut.py`, `proactive_coach.py`, `form_analyzer.py`, `auto_narrator.py`, `content_strategy.py`, `pipeline_validator.py`, and `memory_guard.py`.

---

## 7. Current status — done

### Frontend

- Dark modern UI with indigo/purple accents and lime product accent
- Sidebar, workspace header, project list, and status bar
- Video preview with local file import
- Drag-and-drop video import
- Play/pause, duration display, and progress indication
- Living Timeline visual prototype
- Media Bin visual prototype
- AI Copilot chat UI connected to FastAPI
- Persian response mode requested by the frontend
- Muscle Enhancer panel, presets, toggle, and intensity slider
- Style Match panel and Mood DNA placeholder
- Responsive layout
- Next.js production build passes

### Backend

- FastAPI server foundation on port `8001`
- `GET /health` with CPU, RAM, AI-key, and Reheal status
- `POST /ai/chat` using OpenRouter Llama free model configuration
- `POST /muscle/enhance` using OpenCV processing
- Muscle Enhancer CLI with MP4 output
- Basic Mood DNA extractor
- Reheal health monitor, memory auto-fix, and JSON checkpoint recovery
- CORS enabled for local frontend development
- Secure setup script: `scripts/setup-ai.ps1`
- `.env` excluded from Git

### Infrastructure

- Git repository and active Arena branch
- npm build path verified; pnpm workspace file exists
- Design tokens package
- Windows setup documentation
- Live preview can run with `npm run dev -- --hostname 0.0.0.0`

> Do not claim Tauri, Zustand, Tailwind/DaisyUI, WebSocket progress, 7-layer Reheal, or the full AI module list as implemented until the files and tests exist.

---

## 8. Remaining work

### Frontend: real timeline (critical)

- Import multiple files into Media Bin
- Real draggable clips
- Trim handles and split at playhead
- Clip selection and multi-select
- Video, audio, and text tracks
- Playhead synchronized to playback
- Zoom and snap to beats
- `Ctrl+B` split shortcut
- Undo/redo history

### Project management

- New-project dialog
- Save/load project JSON
- Resolution, FPS, and aspect-ratio settings
- Rename/delete clips
- Auto-save and recovery

### Export pipeline (critical)

- Export dialog
- 720p/1080p/4K selector
- 24/30/60 FPS selector
- H.264/H.265 selector
- Bitrate control
- FFmpeg export
- Real progress and cancellation
- Output-folder action
- YouTube, Reels, and TikTok presets
- Audio mixdown

### AI integration

- Muscle before/after preview and progress
- Face-protected pose-aware enhancement
- Mood DNA charts
- Style Match side-by-side comparison
- Beat markers on timeline
- Microphone recording and Whisper transcription
- Captions overlay
- Proactive Coach notices
- Form Analyzer overlay
- Content Strategy dashboard
- Auto-narration controls

### Backend processing

- Validated upload/FormData workflow
- Async job queue with at most two concurrent heavy jobs
- WebSocket or SSE progress
- FFmpeg fallback for difficult codecs
- Corrupt-frame skipping and output validation
- Temp-file cleanup after one hour
- GPU/CPU capability detection and safe fallback
- Structured error responses and logs

### Reheal completion

- Seven layers active in production paths
- Three-attempt exponential retry
- Checkpoint resume during render
- Memory and VRAM thresholds
- Pipeline validation at every stage
- Reheal log API and UI drawer
- Crash recovery integration tests

### Tauri release

- Complete shell and custom title bar
- Rust IPC commands
- Native file dialogs and Windows path handling
- Auto-start/stop Python backend
- NSIS or WiX installer
- Icons and metadata
- Firewall guidance
- Optional signing
- System tray and auto-updater

### Testing and release

- pytest unit tests for Python modules
- Vitest component/store tests
- API integration tests
- Playwright E2E flows
- GTX 1650 performance benchmark
- Memory-leak and failure tests
- Security audit for keys and file paths
- Accessibility WCAG 2.1 AA
- Persian/English i18n checks
- Release notes, demo video, screenshots, and license
- GitHub Release with Windows installer

---

## 9. Known bugs and required fixes

1. **Face protection is not precise:** use full Face Mesh with a feathered mask and verify that facial pixels remain unchanged.
2. **Audio extraction fallback is missing:** use FFmpeg subprocess fallback when MoviePy cannot decode a container.
3. **Temporary files can accumulate:** add a background cleanup task for files older than one hour.
4. **No real-time job progress:** add WebSocket/SSE and connect it to the frontend progress UI.
5. **API key errors need safe UX:** never return the secret or raw provider response; expose a clear configuration error.
6. **File path security:** validate paths, restrict processing to approved workspace/temp folders, and prevent path traversal.
7. **Current prototype is not yet Tauri:** do not describe the browser preview as a packaged desktop release.
8. **Hardware claims need measurement:** verify CUDA, VRAM, RAM, and processing time on a real GTX 1650 before release.

Historical fixes to preserve when the modules are implemented:

- Beat sync must extract MP4 audio before calling librosa.
- Viral cut must handle videos shorter than its analysis window.

---

## 10. Reheal Loop — seven layers

### L1 — Memory Guard

LRU cache (target 300 MB for frames and 1 GB for models), pre-operation RAM estimate, `gc.collect()`, and CUDA cache clear.

### L2 — GPU Guard

Monitor VRAM, threshold around 3.5 GB of 4 GB, downscale previews and fall back to CPU when pressure is high.

### L3 — Pipeline Guard

Validate file existence, size, codec, frames, non-black/corrupt content, output playability, and output dimensions.

### L4 — AI Guard

Fallback chain: OpenRouter → Nvidia NIM → local model → cache. Every remote call needs a 15-second timeout, bounded retries, and exponential backoff.

### L5 — File Guard

Checksum on read, backup before overwrite, safe temp directory, atomic output writes, and cleanup.

### L6 — State Guard

React error boundaries, Zustand persist middleware, autosave, and project recovery.

### L7 — Render Guard

Checkpoint every 100 frames, validate each segment, CPU fallback if GPU fails, and resume from last successful frame.

### Reheal UI

- StatusBar with RAM/CPU/GPU state
- RehealIndicator with green/red state and fix count
- RehealDrawer with fix history
- Toasts for recovery and errors
- Health polling initially; WebSocket/SSE once processing jobs exist

---

## 11. AI backend configuration

### OpenRouter

- URL: `https://openrouter.ai/api/v1/chat/completions`
- Primary chat model: `meta-llama/llama-3.1-8b-instruct:free`
- Auth: `OPENROUTER_API_KEY` environment variable
- Local file: `ai-engine/.env`
- Never commit `.env` or paste the key into chat
- The repository provides `scripts/setup-ai.ps1` to create the file securely on Windows

### Nvidia NIM

- URL: `https://integrate.api.nvidia.com/v1`
- Secondary provider; not integrated yet

### Local models

- faster-whisper Small, CUDA float16 when available
- MediaPipe Pose, complexity 1, CPU
- MediaPipe Face Mesh, full landmarks, CPU
- OpenCV processing with CPU fallback

### TTS

- Persian male: `fa-IR-FaridNeural`
- Persian female: `fa-IR-DilaraNeural`
- English male: `en-US-GuyNeural`
- edge-tts requires no API key

---

## 12. Design principles and tokens

### Principles

- Dark by default, calm and focused
- Linear/Vercel/Supabase/Raycast/Cursor-inspired density and polish
- Persian RTL first, with deliberate LTR support
- Progressive disclosure: advanced controls stay out of the way
- Every long operation has status, progress, cancellation, and recovery feedback
- Accessibility and keyboard workflows are first-class
- Never hide destructive actions behind ambiguous controls

### Colors

- Primary indigo: `#6366f1`
- AI purple: `#8b5cf6`
- Muscle orange: `#f97316`
- Surface base: `#09090b`
- Surface raised: `#18181b`
- Surface overlay: `#27272a`
- Border: `rgba(255,255,255,0.06)`
- Success: `#10b981`
- Warning: `#f59e0b`
- Error: `#ef4444`
- Product accent currently used in prototype: `#c6f36a`

### Typography and motion

- Sans: Inter Variable + Vazirmatn
- Mono: JetBrains Mono
- Spring: stiffness 300, damping 30
- Smooth: 0.3 seconds, ease `[0.25, 0.1, 0.25, 1]`
- Target: 60 fps for UI interactions
- AI glow and timeline heat-map must remain subtle and performant

Source of truth for reusable tokens: `packages/design-system/tokens.ts`.

---

## 13. Open-source references

Research and inspiration only; preserve licenses and attribution when code is reused.

- Auto-Editor — `github.com/WyattBlue/auto-editor`
- Editly — `github.com/mifi/editly`
- MoneyPrinterTurbo — `github.com/harry0703/MoneyPrinterTurbo`
- VideoLingo — `github.com/Huanshere/VideoLingo`
- TokenFlow — `github.com/omerbt/TokenFlow`
- CoDeF — `github.com/qiuyu96/CoDeF`
- Dify — `github.com/langgenius/dify`
- PySceneDetect — `github.com/Breakthrough/PySceneDetect`
- Whisper — `github.com/openai/whisper`
- MediaPipe — `github.com/google/mediapipe`
- 21ST.dev, Skiper UI, Vengeance UI, Originkit, DaisyUI, and Framer Motion for UI research

---

## 14. Phased roadmap

### 0.3 — Real Timeline (next priority)

- Multi-file import and Media Bin state
- Draggable clips, trim handles, cut/split
- Playhead/playback synchronization
- Video + audio tracks
- Snap to grid and beat markers
- Zoom
- Undo/redo
- Tests for all timeline mutations

**Exit criteria:** a user can import at least two clips, arrange them, trim/split them, undo changes, and preview the result without corrupting state.

### 0.4 — Export Pipeline

- FFmpeg command builder
- Export settings and presets
- Progress, cancel, error, and retry states
- Audio mixdown and output validation

**Exit criteria:** a valid MP4 is exported from a multi-clip project on the target Windows machine.

### 0.5 — Full AI integration

- Muscle split preview and progress
- Mood DNA visualization and Style Match comparison
- Beat markers
- Voice recording, Whisper, captions
- Coach, Form Analyzer, narrator, and content strategy

**Exit criteria:** every approved AI feature has a user-visible happy path, an error path, and a test or documented hardware limitation.

### 0.6 — Tauri Desktop

- Complete Tauri shell and Rust IPC
- Native dialogs and backend lifecycle
- NSIS installer, icons, metadata, system tray

**Exit criteria:** a clean Windows machine can install, launch, use, and close the app without manually starting Python.

### 0.7 — Project and stability

- Save/load/autosave
- Job queue, progress transport, cleanup
- Seven-layer Reheal behavior
- Structured logs and crash resume

**Exit criteria:** interrupted processing can recover safely and failed jobs do not leave unbounded temp files.

### 0.8 — Testing and polish

- Unit, integration, E2E, performance, accessibility, and security checks
- Persian/English i18n
- Keyboard shortcut documentation
- UX polish based on real video testing

**Exit criteria:** CI is green and no release-blocking P0/P1 issues remain.

### 1.0 — Release

- Signed or clearly documented Windows installer
- GitHub Release
- Release notes and user docs
- Demo video and screenshots
- License (MIT or Apache 2.0, pending user decision)

**Exit criteria:** reproducible build, clean-install test, real-videos test, AI-offline test, and user approval.

---

## 15. Decisions needed from the user

1. Product name: keep “Cutting Edge” or rename?
2. Platforms: Windows only for 1.0, or macOS/Linux too?
3. Output formats: MP4/H.264 confirmed; need WebM, MOV, or GIF?
4. Default language: Persian RTL or English LTR with Persian option?
5. Maximum resolution: 1080p preview only, or allow 4K with downscaling?
6. App icon: custom icon required before installer?
7. License: MIT or Apache 2.0?
8. OpenRouter key: user creates it locally; never send it to the AI agent or commit it.
9. Export defaults: platform presets, bitrate, and audio format.
10. Privacy policy: confirm that cloud AI receives only the text/metadata explicitly sent, and video stays local unless a future feature says otherwise.

---

## 16. Handoff prompt for a future AI session

You are a senior full-stack engineer continuing Cutting Edge v2.0. Read `docs/ENGINEERING_ROADMAP.md` completely before editing code.

Current state: interactive prototype / early MVP, approximately 30–35% overall. The current checkout is a root Next.js app plus a Python FastAPI engine. Verify the repository before claiming any target `apps/desktop` files exist.

Immediate milestone: **0.3 Real Timeline**.

Implement production-quality code, not placeholders:

1. multi-file import into Media Bin;
2. real draggable clips;
3. trim handles and split at playhead;
4. playback/playhead synchronization;
5. `Ctrl+B` split;
6. undo/redo;
7. video and audio tracks;
8. timeline zoom and beat snapping;
9. tests for state transitions and edge cases;
10. keep the UI responsive on 16 GB RAM / GTX 1650 hardware.

Locked constraints: Windows target, `$0` tools/free APIs, no Ollama, cloud for heavy LLM work, CPU fallbacks, safe `.env` handling, and natural/no-reshaping Muscle Enhancer behavior.

Workflow:

- The user handles the OpenRouter key, real-video testing, hardware validation, and final approval.
- The agent handles code, UI, API, tests, docs, and repository structure.
- Run build, type checks, Python compile/tests, and `git diff --check` before each milestone.
- Push only to `arena/01a06891-cutting-edge-v2`.
- Do not expose or request credentials.
- Update this roadmap whenever architecture, scope, or milestone status changes.

---

## 17. Definition of done and release checklist

### Every feature

- [ ] Happy path works
- [ ] Empty/loading/error/cancel states exist
- [ ] No secret is logged or committed
- [ ] Input paths and file sizes are validated
- [ ] Memory use is bounded
- [ ] CPU fallback exists where practical
- [ ] Unit/integration coverage exists
- [ ] User documentation is updated

### Every milestone

- [ ] Version status updated in this file
- [ ] Changelog entry added
- [ ] Build passes
- [ ] Tests pass
- [ ] Manual smoke test recorded
- [ ] Git commit created
- [ ] Active Arena branch pushed

### Release 1.0

- [ ] All 16 approved features have a working path or an explicitly approved limitation
- [ ] Timeline and export are real, not mock UI
- [ ] Tauri installer works on clean Windows
- [ ] AI works with key and degrades safely without key/network
- [ ] Reheal seven-layer behavior is tested
- [ ] No critical security, data-loss, or crash issues remain
- [ ] README, screenshots, demo, license, and release notes are published
- [ ] User completes final acceptance test
