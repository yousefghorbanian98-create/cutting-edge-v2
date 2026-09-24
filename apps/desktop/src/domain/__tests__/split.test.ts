import { removeClips, splitAtPlayhead } from '@/domain/split';
import { type Clip, addClip, emptySequence, identityTransform } from '@/domain/timeline';
import { shortcutAction } from '@/lib/shortcuts';
import { describe, expect, it } from 'vitest';

function tenSecond(): Clip {
  return {
    id: 'A',
    mediaId: 'm',
    trackId: 'track-v1',
    start: 0,
    duration: 10_000,
    inPoint: 100,
    sourceDuration: 20_000,
    transform: identityTransform(),
    effects: [],
    label: 'A',
  };
}

describe('split', () => {
  it('splits a 10s clip at 4.5s and ripple-deletes the first half back to zero', () => {
    const sequence = addClip(emptySequence(), tenSecond());
    const split = splitAtPlayhead(sequence, 4500, [], false);
    const left = split.clips.find((clip) => clip.id === 'A');
    const right = split.clips.find((clip) => clip.id !== 'A');
    expect(left?.duration).toBe(4500);
    expect(right?.start).toBe(4500);
    expect(right?.duration).toBe(5500);
    expect(right?.inPoint).toBe(4600);
    const removed = removeClips(split, ['A'], true);
    expect(removed.clips).toHaveLength(1);
    expect(removed.clips[0]?.start).toBe(0);
    expect(shortcutAction({ key: 'b', ctrlKey: true, metaKey: false, shiftKey: false })).toBe('split');
  });
});
