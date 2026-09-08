# 2026-09-08 — GitHub token expiry, Ruff extend scoping, Biome literal includes

Steps: S-007, S-008 · Branch: arena/01a07078-cutting-edge-v2 · Commits: 2b21600, d3292de (unpushed)

## What broke
- `git push` failed with `could not read Username` after S-008 was committed locally; S-008 exists only in that sandbox.
- Ruff `per-file-ignores` in `ai-engine/ruff.toml` never matched `tests/**` when the root config did `extend = "ai-engine/ruff.toml"`.
- Adding a literal path to Biome `overrides[].includes` widened scanning from 16 to 105 files and reformatted every TS file with tabs.

## Root cause
- Auth for the builder chat expires; the loop had "push after each step" but no verification that the push landed.
- Ruff anchors inherited globs to the directory of the config that declares them.
- Biome file scoping treats a literal path in `includes` as a scope change, not an addition.

## Rule
- Push gate in stage ①: `git ls-remote` must show HEAD before a new step starts; auth failure = stop and report (02 §1-①, 07 prompt).
- Declare repo-root globs in the root `ruff.toml` via `extend-per-file-ignores`; never rely on inherited globs.
- Biome `overrides[].includes` takes globs only; verify `Checked N files` is unchanged after any config edit.
