import { type Clip, addClip, emptySequence, identityTransform } from '@/domain/timeline';
import { clipsInRect, pasteAt } from '@/stores/selectionStore';
import { describe, expect, it } from 'vitest';

function clip(id: string, start: number): Clip {
  return {
    id,
    mediaId: 'm',
    trackId: 'track-v1',
    start,
    duration: 1000,
    inPoint: 0,
    sourceDuration: 20_000,
    transform: identityTransform(),
    effects: [],
    label: id,
  };
}

describe('selection', () => {
  it('a marquee over three of five clips selects those three', () => {
    const clips = [0, 2000, 4000, 6000, 8000].map((start, index) => clip(`c${index}`, start));
    const hit = clipsInRect(clips, { x: 0, y: 0, width: 520, height: 40 });
    expect(hit).toEqual(['c0', 'c1', 'c2']);
  });

  it('paste at 20s keeps relative offsets', () => {
    let sequence = emptySequence();
    const clips = [clip('a', 0), clip('b', 1500), clip('c', 3000)];
    for (const item of clips) sequence = addClip(sequence, item);
    const pasted = pasteAt(sequence, clips, 20_000);
    const copies = pasted.clips.filter((item) => item.id.includes('paste'));
    expect(copies.map((item) => item.start)).toEqual([20_000, 21_500, 23_000]);
  });
});
