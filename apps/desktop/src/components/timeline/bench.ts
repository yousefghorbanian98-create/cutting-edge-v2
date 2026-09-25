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

export function sequenceFixture(): Sequence {
  const sequence = emptySequence('seq-play', 30);
  return {
    ...sequence,
    tracks: [
      ...sequence.tracks,
      { id: 'track-t1', kind: 'text', name: 'متن ۱', muted: false, solo: false, locked: false, order: 2 },
    ],
    clips: [
      clip('A', 'clipA', 'track-v1', 0, 3000, 0),
      clip('B', 'clipB', 'track-v1', 3000, 3000, 5000),
      clip('title', 'text', 'track-t1', 0, 3000, 0, 'عنوان'),
      clip('tone', 'tone', 'track-a1', 0, 3000, 0, 'صدا'),
    ],
  };
}

function clip(
  id: string,
  mediaId: string,
  trackId: string,
  start: number,
  duration: number,
  inPoint: number,
  label = id
): Clip {
  return {
    id,
    mediaId,
    trackId,
    start,
    duration,
    inPoint,
    sourceDuration: 8000,
    transform: identityTransform(),
    effects: [],
    label,
  };
}

export function splitFixture(): Sequence {
  const sequence = emptySequence('split', 30);
  return {
    ...sequence,
    clips: [
      {
        id: 'long',
        mediaId: 'bench',
        trackId: 'track-v1',
        start: 0,
        duration: 10_000,
        inPoint: 100,
        sourceDuration: 20_000,
        transform: identityTransform(),
        effects: [],
        label: 'بلند',
      },
    ],
  };
}

export function snapFixture(): Sequence {
  const sequence = emptySequence('snap', 30);
  const base = {
    mediaId: 'bench',
    inPoint: 0,
    sourceDuration: 20_000,
    transform: identityTransform(),
    effects: [],
  };
  return {
    ...sequence,
    clips: [
      { ...base, id: 'A', trackId: 'track-v1', start: 0, duration: 5000, label: 'A' },
      { ...base, id: 'B', trackId: 'track-v1', start: 8000, duration: 1000, label: 'B' },
    ],
  };
}
