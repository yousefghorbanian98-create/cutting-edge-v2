import { type Clip, type Sequence, emptySequence, identityTransform } from '@/domain/timeline';

/** A non-overlapping 200-clip sequence for the scroll budget. Not a mock renderer. */
export function benchSequence(count = 200): Sequence {
  const sequence = emptySequence('bench', 30);
  const clips: Clip[] = [];
  for (let i = 0; i < count; i += 1) {
    const video = i % 2 === 0;
    clips.push({
      id: `bench-${i}`,
      mediaId: 'bench',
      trackId: video ? 'track-v1' : 'track-a1',
      start: i * 2000,
      duration: 1500,
      inPoint: 0,
      sourceDuration: 10_000,
      transform: identityTransform(),
      effects: [],
      label: `کلیپ ${i + 1}`,
    });
  }
  return { ...sequence, clips };
}
