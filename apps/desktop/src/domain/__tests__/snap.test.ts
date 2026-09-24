import { pxToMs, snapTargetsFor, snapTime } from '@/domain/snap';
import { describe, expect, it } from 'vitest';

describe('snap', () => {
  it('snaps a drop 4px from a clip end onto that end, and shift disables it', () => {
    const pxPerSecond = 100;
    const end = 5000;
    const dropped = end - pxToMs(4, pxPerSecond);
    const targets = snapTargetsFor([{ id: 'A', start: 0, duration: end }], 'B', 0, []);
    expect(snapTime(dropped, targets, pxPerSecond)).toBe(end);
    expect(snapTime(dropped, targets, pxPerSecond, 8, true)).toBe(dropped);
  });

  it('does not snap when the pointer is farther than 8px', () => {
    expect(snapTime(4500, [{ time: 5000, label: 'end' }], 100)).toBe(4500);
  });
});
