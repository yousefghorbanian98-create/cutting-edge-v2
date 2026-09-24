import { type Clip, addClip, emptySequence, identityTransform } from '@/domain/timeline';
import { rollTrim, trimBy } from '@/domain/trim';
import { describe, expect, it } from 'vitest';

function make(partial: Partial<Clip> & Pick<Clip, 'id' | 'start' | 'duration' | 'inPoint'>): Clip {
  return {
    mediaId: 'm',
    trackId: 'track-v1',
    sourceDuration: 20_000,
    transform: identityTransform(),
    effects: [],
    label: partial.id,
    ...partial,
  };
}

describe('trim', () => {
  it('ripple-trims the out handle by exactly 2 seconds', () => {
    let sequence = addClip(emptySequence(), make({ id: 'A', start: 0, duration: 4000, inPoint: 0 }));
    sequence = addClip(sequence, make({ id: 'B', start: 4000, duration: 2000, inPoint: 0 }));
    const next = trimBy(sequence, 'A', 'out', -2000, true);
    expect(next.clips.find((clip) => clip.id === 'A')?.duration).toBe(2000);
    expect(next.clips.find((clip) => clip.id === 'B')?.start).toBe(2000);
    expect(trimBy(sequence, 'A', 'out', 50_000, false)).toBe(sequence);
  });

  it('roll trim keeps the cut and moves both durations', () => {
    let sequence = addClip(emptySequence(), make({ id: 'A', start: 0, duration: 4000, inPoint: 0 }));
    sequence = addClip(sequence, make({ id: 'B', start: 4000, duration: 2000, inPoint: 4000 }));
    const next = rollTrim(sequence, 'A', 'B', 2000);
    expect(next.clips.find((clip) => clip.id === 'A')?.duration).toBe(2000);
    expect(next.clips.find((clip) => clip.id === 'B')?.start).toBe(2000);
    expect(next.clips.find((clip) => clip.id === 'B')?.duration).toBe(4000);
    expect(next.clips.find((clip) => clip.id === 'B')?.inPoint).toBe(2000);
  });
});
