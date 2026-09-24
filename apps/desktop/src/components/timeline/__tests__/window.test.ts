import { describe, expect, it } from 'vitest';
import { benchSequence } from '../bench';
import { timeFromPointer, visibleClips } from '../window';

describe('timeline window', () => {
  it('renders only clips inside the scroll window of a 200-clip sequence', () => {
    const sequence = benchSequence(200);
    expect(sequence.clips).toHaveLength(200);
    const shown = visibleClips(sequence.clips, 10, 12);
    expect(shown.length).toBeGreaterThan(0);
    expect(shown.length).toBeLessThan(8);
    for (const clip of shown) {
      const start = clip.start / 1000;
      const end = (clip.start + clip.duration) / 1000;
      expect(start < 12 && end > 10).toBe(true);
    }
  });

  it('a 1px lane border does not shift a ruler click by 10ms', () => {
    expect(timeFromPointer(551, 100, 1, 0)).toBe(4.5);
    expect(timeFromPointer(550, 100, 0, 0)).toBe(4.5);
  });
});
