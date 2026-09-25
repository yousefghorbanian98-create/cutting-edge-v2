# Accepted Knowledge Registry

> Canonical index for durable knowledge. Chat messages are not the source of truth. Every accepted finding must be routed to its proper loop document, stage, bug, ADR, or evidence policy.

## Routing rule

When a new source, audit finding, or failure is accepted:

1. record it in this registry;
2. link the canonical document where it belongs;
3. list affected stages and owner/bug;
4. state whether it is adopted, deferred, rejected, or reference-only;
5. add it to the next stage CONTRACT through `Forward-knowledge compliance`.

Do not duplicate a rule with conflicting wording. This registry points to the canonical home; the canonical home contains the operative rule.

## Current entries

| ID | Knowledge / finding | Canonical home | Affected stages | Disposition |
|---|---|---|---|---|
| K-001 | FFmpeg skill principles: probe-first, typed operations, capability states, safe execute, verify, provenance | `STYLE_MATCH_ARCHITECTURE.md`; `FORWARD_KNOWLEDGE_GATE.md` | S-028, S-033, S-037, S-046, S-048, S-056, S-086 | Adopt principles; do not vendor/depend |
| K-002 | `run_ffmpeg()` unconditional `-y` overwrite risk | `docs/loop/evidence/S-004/REVIEW.md`; BUG-18; `06_BUGS.md` | S-028, S-033, S-086 | Deferred must-fix |
| K-003 | S-006 probe must fail closed for missing dimensions; ffprobe JSON first | `docs/loop/evidence/S-006/REVIEW.md` | S-006, S-028, S-033 | Adopted and reviewed |
| K-004 | Timeline edits must use store action → Immer → temporal history | `FORWARD_KNOWLEDGE_GATE.md`; S-013–S-022 REVIEWs | S-013–S-032 | Adopted; UI path must be evidenced |
| K-005 | Iris visual camera: settled selector/viewport screenshots are observation only | `STYLE_MATCH_ARCHITECTURE.md`; `KNOWLEDGE_REFRESH_AUDIT.md` | UI/browser stages | Reference only; no runtime dependency |
| K-006 | anti-slop: purpose, real interaction, responsive/accessibility review, no fake metrics, delivery gate | `STYLE_MATCH_ARCHITECTURE.md`; `KNOWLEDGE_REFRESH_AUDIT.md` | UI/design stages | Adopt selected principles; do not install/vendor |
| K-007 | Public CI annotations may be accepted for S-022 only when evidence archives fail with EOF | `docs/loop/evidence/S-022/EVIDENCE.md` and `REVIEW.md` | S-022 only | Explicitly resolved exception; not general policy |
| K-008 | Retrospective audit is required before the next batch after accepted new knowledge | `KNOWLEDGE_REFRESH_AUDIT.md`; `FORWARD_KNOWLEDGE_GATE.md` | S-023 onward | Mandatory process gate |
| K-009 | `video-editing-skill` patterns: typed edit request, operation graph, source-to-timeline mapping, allow-list, workspace boundary, executor, provenance | `STYLE_MATCH_ARCHITECTURE.md`; `FORWARD_KNOWLEDGE_GATE.md` | S-046, S-048, S-056, S-086 | Adopt principles; do not copy/vendor |
| K-010 | Hypit-inspired reusable, source-controlled production workflow; license constraints require independent implementation and review | `STYLE_MATCH_ARCHITECTURE.md`; `13_INTEGRATIONS_ADOPTION.md` | S-045, S-046, S-048, S-055 | Reference only; no code/dependency |
| K-011 | Generic AI Supervisor stack: observability ideas are useful, but the large dependency/Docker/plugin stack is rejected for current runtime | `KNOWLEDGE_REGISTRY.md`; `KNOWLEDGE_REFRESH_AUDIT.md` | S-023 onward; future observability stage only | Adopt selected principles; do not vendor/install |
| K-012 | HotClip principles: local-first media workflow, ffprobe pipeline, reference-driven pacing, measurable caption/clip quality, processing receipts, and platform-agnostic API seam | `STYLE_MATCH_ARCHITECTURE.md`; `FORWARD_KNOWLEDGE_GATE.md` | S-033, S-040, S-045, S-046, S-048, S-086 | Adopt principles only; do not vendor or depend on AGPL-3.0 code |
| K-013 | HotClip reliability patterns: review-first highlights, word-aligned timestamps, speech-safe cuts, atomic/private export staging, cancel cleanup, resumable checkpoints, bounded cache, source relinking, stream consistency, and evidence-gated HDR/SDR handling | `STYLE_MATCH_ARCHITECTURE.md`; `KNOWLEDGE_REFRESH_AUDIT.md` | S-033, S-037, S-040, S-045, S-046, S-048, S-068, S-074, S-086 | Adopt patterns; reimplement independently; no code copy/vendor |
| K-014 | .NET/C# Coherence Gate proposal: architecture rules, analyzers, SAST, dependency/license graph, fitness functions, public API and CI gates | `FORWARD_KNOWLEDGE_GATE.md`; `KNOWLEDGE_REFRESH_AUDIT.md` | Existing TS/Next/Tauri/Python/Rust gates; future architecture/quality stages | Adopt language-agnostic principles selectively; reject .NET-only tools and duplicate gates |

## Status vocabulary

```text
adopted       operative project principle
reference     informs design; not a dependency
reference-only external observation; no runtime use
rejected      explicitly not allowed
deferred      accepted but owned by a later stage/bug
exception     narrow evidence/process exception with explicit scope
```

## Required update

A new accepted item without a registry ID and canonical home is not durable project knowledge and must not silently influence implementation.
