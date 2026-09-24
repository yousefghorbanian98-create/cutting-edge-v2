# 2026-09-24 — import overseer files, not the branch

Steps: S-012 · Branch: arena/01a0c936-cutting-edge-v2

## What broke
- Overseer commit `614f4b4` parents `8b58f19`, not the builder tip `1d16e7c`.
- A branch merge would have dropped S-011 and S-012.

## Root cause
- The overseer branch was still on the S-010 review base. The architecture diff only touched three docs, and those docs had not diverged.

## Rule
- Fetch the named SHA and check out only the named files. Do not merge an overseer branch whose parent is behind the builder tip.
