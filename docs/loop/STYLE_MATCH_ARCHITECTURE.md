# Style Match — implementation direction

> برنامه‌ریزی معماری؛ این فایل کد محصول یا تست اجرایی نیست. منبع تصمیم برای کارت‌های S-012، S-040، S-045، S-046، S-048، S-055 و S-056 است.

## هدف

Style Match باید یک دستیار قابل توضیح باشد، نه یک فیلتر یا یک `similarity score` مبهم:

```text
observe → explain → plan → execute → validate → revise
```

از ویدیوی مرجع و ویدیوی کاربر برای هرکدام یک `Style Signature` نسخه‌دار می‌سازیم و این محورها را جداگانه مقایسه می‌کنیم:

- semantic content
- composition و subject placement
- palette، lighting و contrast
- shot duration و cut density
- motion و temporal consistency
- pose و crop safety
- speech، silence و music energy

خروجی هر محور باید `score`، `confidence`، توضیح، و timestampهای evidence داشته باشد؛ خروجی نهایی فقط یک عدد نیست.

## معماری مرحله‌ای

1. **CPU-first baseline:** FFmpeg، OpenCV، PySceneDetect، color/histogram، shot duration، optical-flow محدود و audio energy.
2. **Feature adapters:** semantic encoder اختیاری مانند OpenCLIP و pose adapter؛ هر مدل با cache، version، license metadata، CPU fallback و memory estimate.
3. **Style Signature:** نتیجهٔ per-shot به یک signature قابل cache با hash فایل و نسخهٔ الگوریتم aggregate می‌شود.
4. **Planner:** مدل زبانی فقط JSON مطابق schema تولید می‌کند؛ هر action باید محدود، reversible و دارای دلیل و confidence باشد.
5. **Executor:** فقط actionهای allow-list شده را با FFmpeg/OpenCV اجرا می‌کند، checkpoint می‌سازد، progress/cancel دارد و خروجی را validate یا rollback می‌کند.
6. **Memory:** فقط signature، plan تأییدشده و preference کاربر ذخیره می‌شود؛ media خام بدون اجازه نگه‌داری نمی‌شود.

## محدودیت سخت‌افزار

هدف اولیه `GTX 1650 4GB / RAM 16GB` است. فقط یک GPU inference job هم‌زمان مجاز است؛ کارهای CPU می‌توانند هم‌زمان اجرا شوند. مدل‌ها پیش‌فرض داخل installer bundle نمی‌شوند. model swapping اختیاری است و باید با benchmark واقعی و حاشیهٔ امن VRAM اثبات شود، نه با تخمین weight size.

## تصمیم‌های منفی

- افزودن Kdenlive، Shotcut، Olive، Blender یا PySide6/Gradio به runtime ممنوع؛ frontend فعلی Next/Tauri مرجع است.
- Ollama وارد stack نمی‌شود؛ LLM باید از adapter/provider موجود استفاده کند.
- Ultralytics YOLO بدون تصمیم license مستقل وارد نمی‌شود؛ AGPL/Enterprise باید پیش از هر استفاده بررسی شود.
- BLIP/LAVIS، Demucs، madmom و مدل‌های بزرگ فقط بعد از benchmark و license audit قابل بررسی‌اند.
- raw command یا parameter از LLM اجرا نمی‌شود؛ plan باید schema-validated باشد.

## معیار کیفیت

هر پیشنهاد Style Match باید با before/after measurement، playable output، audio/video sync، resolution، frame rate، subject visibility و temporal stability بررسی شود. نبود مدل، audio یا GPU `MISSING`/`unverified` است و هرگز `PASS` محسوب نمی‌شود.

## وابستگی به مراحل

- `S-012`: job model، GPU lock، progress، cancel و عدم block شدن `/health`.
- `S-040`: ویژگی‌های زمانی و energy؛ پایهٔ مشترک Style Match و Content Strategy.
- `S-045`: Style DNA و signature قابل cache.
- `S-046`: مقایسه، diff، plan و Apply Style با تأیید کاربر.
- `S-048`: transition intelligence فقط بعد از validated plan.
- `S-055`: استفاده از featureهای ثبت‌شده برای hook و virality، بدون ادعای causal score.
- `S-056`: cache بر اساس content hash، offline UX و allow-list مدل/provider.

هر مرحله قرارداد، تست واقعی، شواهد و review مستقل خودش را دارد؛ این سند به‌تنهایی scope مرحلهٔ جاری را تغییر نمی‌دهد.

## Hypit-inspired workflow direction (reference only)

Hypit demonstrates a useful product idea: a reference video can become a reusable, source-controlled production workflow rather than a one-off render. We adopt the idea, not Hypit code, skill, runtime, packages or license-dependent components.

Our future internal workflow should support:

- semantic anchors tied to spoken words or script phrases, not only absolute seconds;
- reusable shot, caption, B-roll, audio and effect components;
- a validated, versioned `EditPlan` that can produce multiple variants;
- reflow when script, language, voice or duration changes;
- deterministic components rendered locally with FFmpeg/Tauri/Python;
- provider adapters for optional generation services, never hidden credentials or mandatory paid APIs;
- source-controlled manifests so a result can be inspected, rerun and diffed.

This is not a license to copy Hypit. Hypit's modified Apache license restricts commercial redistribution and bundled derivative products without permission. Cutting Edge must implement its own schema and runtime after a separate license review.

Suggested internal model:

```text
Reference analysis
→ Style Signature
→ semantic EditPlan
→ schema validator
→ timeline/job executor
→ output validation
→ reusable variant manifest
```

The workflow layer complements Style Match; it does not replace shot analysis, visual scoring or human confirmation.

## Forward knowledge is binding for future stages

The `docs/loop/FORWARD_KNOWLEDGE_GATE.md` is a mandatory pre-implementation gate for every future Builder stage. A new stage must explicitly state which accepted architecture and review findings it applies, which are deferred, which unsafe inputs it rejects, and how compliance will be evidenced. This is a process constraint; it does not silently expand the current stage's scope or authorize a ledger change.

A knowledge refresh is also required before the next batch: `docs/loop/KNOWLEDGE_REFRESH_AUDIT.md` requires a retrospective audit of the historical path, not only a forward-looking contract. Durable accepted findings are indexed in `docs/loop/KNOWLEDGE_REGISTRY.md`; chat-only knowledge is not an implementation input.

## External reference lenses — adopted principles, not dependencies

### Iris (`brijr/iris`)

Iris is a reference for an optional visual camera: stable render waiting, selector-specific screenshots, viewport/device variants, and structured capture results. It must remain separate from behavioral acceptance: Playwright assertions, CDP performance budgets, CI, Windows, and installer evidence remain authoritative. Iris is not a product dependency, runtime integration, or vendor source.

### anti-slop (`miqdadbadjuber/anti-slop`)

anti-slop is a reference for process/design quality: purpose before decoration, real interaction evidence, responsive and accessibility review, no fake metrics, and an explicit delivery gate. Only selected principles may be adapted into project contracts or `DESIGN.md` after audit. Its plugin system, rules, dependencies, and repository are not copied or installed into Cutting Edge.

### HotClip (`xixihhhh/hotclip`)

HotClip is an external reference for a local-first clipping workflow: ffprobe-backed media discovery, reference-clip pacing, measurable caption/clip quality fixtures, processing receipts, and a platform-agnostic API seam. Additional useful patterns are review-first highlight candidates, word-aligned speech-safe cuts, private atomic export staging, cancel cleanup, resumable checkpoints, bounded local cache, source relinking, stream-consistent analysis, and evidence-gated HDR/SDR handling. These principles fit future Style Match/export planning, but HotClip is AGPL-3.0 and must not be vendored, copied, or added as a runtime dependency without a separate legal and architecture decision. Its local-first and receipt ideas do not replace our typed executor, capability states, verification, provenance, or CI evidence.

### brag (`latent-spaces/brag`) — K-015, dated 2026-09-27

brag is an MIT-licensed workflow reference for turning a real project into a short, source-backed launch video. Cutting Edge may adopt the workflow ideas below. It must not install the skill, vendor its scripts, depend on Hyperframes, run unpinned `npx`, or import its music, SFX, or provider adapters.

Adopted as future-stage principles only:

- inspect the real source before writing claims;
- reuse the product's real UI and assets instead of inventing a look;
- plan the user flow as entry, action, then result;
- keep the storyboard and edit plan typed and reviewable;
- every claim must point at a source surface;
- text must fit a readability budget;
- visual QA includes a settled frame and a mid-transition frame;
- the poster and frame zero are validated, not assumed;
- each run writes to a timestamped, bounded output directory;
- a processing receipt, manifest, and checksum travel with the output;
- secrets, PII, credentials, and internal hostnames are excluded;
- voice is opt-in and never implied by a default provider;
- audio and SFX need source, license, and checksum before use;
- an optional adapter exposes capability state and may be absent.

Rejected from this reference: Hyperframes as runtime or exporter, `/brag-slim` as an unbounded model executor, remote unpinned `npx`, `ffmpeg -y`, direct overwrite, implicit Kokoro or other voice providers, and any claim that a dry-run or software render is a GPU pass.

These principles do not start `S-033` and do not close `BUG-18`.

### Concat (`jub0t/Concat`) — K-016, dated 2026-09-27

Concat is AGPL-3.0-or-later. It is a reference for editor architecture only. No crate, shader, MCP server, runtime, asset, or source file from Concat or HotClip may be vendored or copied.

Adopted as independently redesigned principles only:

- dependencies point one way: core does not know the window, and core does not link the media backend;
- one document model and one command path serve UI, CLI, API, and agent;
- a pure frame plan exists before decode or composite;
- preview and export share timeline semantics;
- time is exact and quantised to the frame grid; hidden float equality is not a clock;
- a reference compositor can check GPU output, but a software path is not a GPU pass;
- cache size, worker count, and prefetch are bounded;
- scheduler priority is explicit;
- hardware capability is detected, and software fallback is named;
- a stale async result is discarded when the project or session closes;
- effects and plugins enter only through a validated manifest, with limits and a deterministic failure;
- models carry version, digest, license, and offline state;
- per-run logs have a retention bound and do not store secrets or private media without consent;
- performance claims come from a measured table, not a generic success check;
- the default capability state is local and offline;
- HDR/SDR claims stay evidence-gated.

These principles do not replace the existing probe, typed operation, capability, safe execute, verify, and provenance chain. They do not authorize a schema migration in this batch.

## FFmpeg execution direction (reference from `ffmpeg-skill`)

The project may adopt the following execution principles, but must keep its own Python/Tauri implementation rather than vendor the external repository:

```text
probe → typed operation → capability check → safe execute → verify → provenance
```

Required internal contracts for future media stages:

- probe media before planning from measured duration, fps, resolution, streams and color metadata;
- represent trim, cut, concat, fit, fill, resize, speed, overlay, transition, color, audio and export as allow-listed typed operations;
- reject raw shell strings, arbitrary filter graphs and unknown operations from the assistant;
- expose FFmpeg/ffprobe capability states as `available`, `missing` or `unknown`;
- refuse accidental overwrite and use temporary output plus atomic replacement/rollback;
- keep all input/output/temp paths within the workspace boundary;
- verify playable output, duration, streams, sync, codec and requested delivery constraints;
- emit structured JSON provenance containing input, operation, parameters, output, warnings, capabilities and validation;
- create low-resolution proxies for AI analysis and execute approved plans on the original media;
- make platform delivery checks and loudness checks explicit rather than implicit in a prompt.

This is an architectural reference from the MIT-licensed `kajisho5/ffmpeg-skill`; it is not a product dependency decision. Any reuse of source code requires a separate dependency, security and license audit.
