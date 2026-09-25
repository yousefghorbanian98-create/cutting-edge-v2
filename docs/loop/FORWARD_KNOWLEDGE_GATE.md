# Forward Knowledge Gate — mandatory for every future Builder stage

> This is a roadmap/process rule, not a product implementation. It prevents a Builder from starting a future stage using an obsolete contract after a new architectural gap, audit finding, or external reference has been accepted.

## Rule

Before writing code for any new stage, Builder MUST read:

1. the current stage `CONTRACT.md` and its dependency contracts;
2. the latest `docs/loop/evidence/*/REVIEW.md` files for the dependency chain;
3. `docs/loop/STYLE_MATCH_ARCHITECTURE.md`;
4. this file;
5. accepted architecture updates and open bugs in `docs/loop/06_BUGS.md`.

The Builder MUST then add a short `Forward-knowledge compliance` section to the new stage `CONTRACT.md`. If the section is missing, the stage has not entered implementation.

## Required contract contents

The section MUST list, for the current stage:

- applicable new principles and their source review/ADR;
- which principle is implemented in this stage;
- which principle is intentionally deferred, with the owning stage and ledger reference;
- the negative boundary: what raw command, arbitrary graph, unsafe overwrite, implicit capability, or unverified result is rejected;
- the evidence that will prove compliance.

Silence is not compliance. A deferred item must be named; it must not be silently omitted.

## Mandatory media execution chain

For every stage that probes, transforms, previews, exports, muxes, or verifies media, the contract and implementation must preserve:

```text
probe
→ typed operation
→ capability check
→ safe execute
→ verify
→ provenance
```

The assistant/planner may produce only a schema-validated, allow-listed typed operation. It MUST NOT provide raw FFmpeg commands or arbitrary filter graphs to the executor.

Minimum safety requirements, when applicable:

- structured `ffprobe` JSON first; text parsing only as an explicit fallback;
- capability states are `available`, `missing`, or `unknown`; missing is not pass;
- no overwrite by default, with atomic replacement and rollback where output is replaced;
- workspace/path boundary enforcement;
- playable output and declared stream/duration/codec checks;
- structured result and provenance record;
- explicit offline and Windows behavior.

## Mandatory UI/state execution chain

For every stage that edits the timeline or project state, the contract must identify the single store action that records the edit. Direct component-level mutation of the canonical timeline state is forbidden when it bypasses Immer/temporal history. The required path is:

```text
domain operation
→ store action
→ Immer
→ temporal history
→ UI evidence
```

Undo/redo evidence must cover the real UI path, not only a pure domain helper.

## Evidence and status rule

A local unit test, a static check, or a successful build does not replace the required browser, media, Windows, installer, or CI evidence. `skip`, `missing`, `unverified`, and dependency hold are not pass.

A Builder may report a stage as `REVIEW` with incomplete evidence, but MUST NOT mark it `GREEN`. Only the independent Overseer review may authorize the next ledger decision. This gate never authorizes a ledger change by itself.

## Handoff format

At the start of every new stage, Builder must report:

```text
Forward-knowledge gate:
- Read: <contracts/reviews/architecture/bugs>
- Applied here: <specific principles>
- Deferred: <item → owning stage>
- Rejected inputs: <unsafe/raw/untyped cases>
- Evidence plan: <tests/CI/artifacts>
- Status: REVIEW until independent verdict
```

If a newly discovered gap changes the current stage's contract, stop implementation, record the gap in the stage evidence, and ask for independent review rather than silently continuing.
