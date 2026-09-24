# S-013 evidence

Builder. Status: REVIEW (not GREEN). `verified_on`: local-linux. CI run of the new vitest step is not claimed here.

| AC | Red | Green | Command |
| --- | --- | --- | --- |
| AC-1..AC-4 | First `vitest run --coverage` failed: line coverage 81.52% < 90 on `timeline.ts` | 9/9 passed. Line coverage 98.94% (threshold 90). Property: 40 random runs, no overlap, `undo(n)` matched the recorded snapshot | `pnpm --filter cutting-edge-desktop exec vitest run --coverage` |

- Domain: `apps/desktop/src/domain/timeline.ts`. Store: `apps/desktop/src/stores/timelineStore.ts` (immer + zundo, limit 100).
- Pins: immer 10.1.1, zundo 2.3.0, vitest 3.2.4, @vitest/coverage-v8 3.2.4, fast-check 3.23.2. Lockfile updated.
- `primary` scale was not promoted. S-099 tests lock `threeWay == 27` and `tsOnly >= 16`.
- No REVIEW.md. Overseer writes that.
