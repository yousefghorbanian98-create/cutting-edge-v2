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

## Status vocabulary

```text
adopted       operative project principle
reference     informs design; not a dependency
reference-only external observation; no runtime use
rejected      explicitly not allowed
 deferred     accepted but owned by a later stage/bug
exception     narrow evidence/process exception with explicit scope
```

## Required update

A new accepted item without a registry ID and canonical home is not durable project knowledge and must not silently influence implementation.
