import { describe, expect, it } from 'vitest';
import { hitAt, paintColor } from '../compositor';

const clips = [
  {
    id: 'A',
    mediaId: 'clipA',
    trackId: 'v',
    kind: 'video' as const,
    start: 0,
    duration: 3000,
    inPoint: 0,
  },
  {
    id: 'B',
    mediaId: 'clipB',
    trackId: 'v',
    kind: 'video' as const,
    start: 3000,
    duration: 3000,
    inPoint: 5000,
  },
];

describe('sequence map', () => {
  it('maps 3.2s to clip B source 5.2s', () => {
    const hit = hitAt(clips, 3200, 'video');
    expect(hit?.clip.id).toBe('B');
    expect(hit?.sourceMs).toBe(5200);
  });

  it('changes the frame when the source time is wrong', () => {
    expect(paintColor('clipB', 5200)).not.toEqual(paintColor('clipB', 0));
  });
});
