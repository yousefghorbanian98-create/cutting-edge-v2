import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { type Clip, identityTransform } from '@/domain/timeline';
import { pasteAt } from '@/stores/selectionStore';
import { undoTimeline, useTimelineStore } from '@/stores/timelineStore';
import { beforeEach, describe, expect, it } from 'vitest';

function clip(id: string, start = 0, duration = 4000): Clip {
  return {
    id,
    mediaId: 'm',
    trackId: 'track-v1',
    start,
    duration,
    inPoint: 0,
    sourceDuration: 20_000,
    transform: identityTransform(),
    effects: [],
    label: id,
  };
}

function hash(): string {
  return JSON.stringify(
    useTimelineStore.getState().sequence.clips.map((item) => [item.id, item.start, item.duration])
  );
}

describe('timeline history path', () => {
  beforeEach(() => {
    useTimelineStore.temporal.getState().clear();
    useTimelineStore.getState().reset();
    useTimelineStore.temporal.getState().clear();
  });

  it('move, trim, paste, and split are undoable store actions', () => {
    const store = useTimelineStore.getState();
    expect(store.addClip(clip('A'))).toBe(true);
    const afterAdd = hash();

    expect(store.moveClip('A', 1500)).toBe(true);
    undoTimeline(1);
    expect(hash()).toBe(afterAdd);

    const trimmed = {
      ...useTimelineStore.getState().sequence,
      clips: useTimelineStore
        .getState()
        .sequence.clips.map((item) => (item.id === 'A' ? { ...item, duration: 2000 } : item)),
    };
    expect(store.commitEdit(trimmed)).toBe(true);
    undoTimeline(1);
    expect(hash()).toBe(afterAdd);

    const pasted = pasteAt(useTimelineStore.getState().sequence, [clip('A')], 20_000);
    expect(store.commitEdit(pasted, 1)).toBe(true);
    expect(useTimelineStore.getState().sequence.clips).toHaveLength(2);
    undoTimeline(1);
    expect(hash()).toBe(afterAdd);

    const split = {
      ...useTimelineStore.getState().sequence,
      clips: [clip('A', 0, 2000), clip('A-right', 2000, 2000)],
    };
    expect(store.commitEdit(split, 1)).toBe(true);
    undoTimeline(1);
    expect(hash()).toBe(afterAdd);
    expect(useTimelineStore.getState().nextId).toBe(1);
  });

  it('UI code does not write the sequence with setState', () => {
    const here = dirname(fileURLToPath(import.meta.url));
    const files = [
      resolve(here, '../../components/timeline/useClipDrag.ts'),
      resolve(here, '../../components/timeline/TrimHandle.tsx'),
      resolve(here, '../../components/timeline/Shortcuts.tsx'),
      resolve(here, '../../components/timeline/TrackHeader.tsx'),
      resolve(here, '../selectionStore.ts'),
    ];
    for (const file of files) {
      expect(readFileSync(file, 'utf8'), file).not.toContain('useTimelineStore.setState');
    }
  });
});
