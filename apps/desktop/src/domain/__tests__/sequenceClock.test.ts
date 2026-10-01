import { describe, expect, it } from 'vitest';
import { advanceSequenceClock } from '../sequenceClock';

describe('sequence playback clock', () => {
  it('holds the playhead while the sequence-time input owns focus', () => {
    expect(advanceSequenceClock(1, true)).toBe(1);
  });

  it('advances one sequence frame after the time input loses focus', () => {
    expect(advanceSequenceClock(1, false)).toBeCloseTo(1 + 1 / 30);
  });
});
