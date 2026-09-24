import { resetHistory } from '@/components/shared/history';
import { type Clip, identityTransform } from '@/domain/timeline';
import { redoTimeline, undoTimeline, useTimelineStore } from '@/stores/timelineStore';
import { beforeEach, describe, expect, it } from 'vitest';

function clip(id: string, start: number): Clip {
  return {
    id,
    mediaId: 'm',
    trackId: 'track-v1',
    start,
    duration: 1000,
    inPoint: 0,
    sourceDuration: 5000,
    transform: identityTransform(),
    effects: [],
    label: id,
  };
}

function hash(): string {
  return JSON.stringify(useTimelineStore.getState().sequence.clips.map((item) => [item.id, item.start]));
}

describe('history', () => {
  beforeEach(() => {
    resetHistory();
    useTimelineStore.temporal.getState().clear();
    useTimelineStore.getState().reset();
    useTimelineStore.temporal.getState().clear();
  });

  it('five edits undo back to the initial hash and redo to the final hash', () => {
    const initial = hash();
    for (let i = 0; i < 5; i += 1) {
      useTimelineStore.getState().addClip(clip(`c${i}`, i * 2000));
    }
    const finalHash = hash();
    expect(useTimelineStore.temporal.getState().pastStates).toHaveLength(5);
    undoTimeline(5);
    expect(hash()).toBe(initial);
    redoTimeline(5);
    expect(hash()).toBe(finalHash);
  });
});
