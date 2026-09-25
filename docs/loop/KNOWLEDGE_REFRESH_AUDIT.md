# Knowledge Refresh & Retrospective Audit — mandatory before future implementation

> This is a process and evidence requirement. It does not change product scope, ledger status, or prior verdicts by itself.

## Purpose

When a new architectural reference, tool, audit finding, or failure pattern is accepted, Builder must re-read the path already taken instead of applying the new knowledge only to future code. The goal is to find gaps that were previously invisible, while preserving the historical truth of existing evidence.

## Trigger

Run this audit before starting the next implementation batch after any accepted update to:

- architecture or execution contracts;
- media, browser, UI, security, or evidence workflow;
- external reference such as `ffmpeg-skill`, `iris`, or `anti-slop`;
- a newly discovered CI, Windows, Playwright, installer, or provenance failure.

For the current roadmap, this audit is required before continuing S-023 and must cover S-001 through the current stage.

## Required review surface

Read and cross-check:

1. every affected stage `CONTRACT.md`, `EVIDENCE.md`, and `REVIEW.md`;
2. the ledger and dependency graph;
3. product code and tests for the affected paths;
4. CI job logs, annotations, artifacts, and known evidence-policy exceptions;
5. `FORWARD_KNOWLEDGE_GATE.md` and `STYLE_MATCH_ARCHITECTURE.md`;
6. the accepted external references and their licenses/boundaries.

## Required lenses

At minimum, inspect the historical path for:

- **Media:** probe, typed operation, capability detection, safe execution, verification, provenance, overwrite, rollback, workspace boundary, Windows/offline behavior;
- **UI/browser:** stable render waiting, viewport/scroll geometry, selector collisions, keyboard/mouse interaction, responsive states, accessibility, screenshot evidence, and visual-versus-behavioral proof;
- **State:** domain operation → store action → Immer → temporal history → real UI evidence;
- **Quality:** purpose before decoration, real interaction over mock signals, no fake metrics, no silent fallback, and no threshold relaxation;
- **Evidence:** local versus CI proof, skipped/missing/unverified states, artifact readability, public annotation policy, and reproducibility;
- **Security/supply chain:** path safety, command injection, dependency/license risk, secrets, mutable `latest` images, and unsupported platform assumptions.

## Output

Builder must create or update a retrospective audit record under:

```text
docs/loop/evidence/RETRO-AUDIT-<date-or-batch>.md
```

The record must contain a table with:

```text
historical stage/path
new knowledge or reference
observed gap or no-gap result
evidence inspected
severity: blocker / must-fix / deferred / informational
owner stage or bug
required action
```

Every `no gap` conclusion must name the evidence checked. Every deferred item must have an owner. A finding must not be silently fixed in unrelated scope.

## Status rules

- This audit does not GREEN any stage.
- It does not rewrite a prior verdict; it records whether the new lens changes the next action.
- A blocker or must-fix finding sends the affected stage back to REVIEW or to its named owner stage.
- A local screenshot, unit test, or static pass cannot close a browser, media, Windows, installer, or provenance gap.
- After the audit, Builder sends the SHA and audit path to the independent Overseer before starting the next implementation batch.

## Current reference lenses

### Iris

Use only as an optional visual camera/reference for stable screenshots, selector-specific capture, viewport variants, and render-settling observation. It does not replace Playwright assertions, CDP budgets, CI, or installer evidence. Do not vendor it or make it a product dependency without a separate CONTRACT and audit.

### anti-slop

Use only as a design/process reference: purpose before decoration, real interaction evidence, responsive/accessibility review, no fake metrics, and explicit delivery gates. Do not install its plugin system or copy its rules wholesale into runtime. Adapt selected principles into project contracts and `DESIGN.md` only through review.
