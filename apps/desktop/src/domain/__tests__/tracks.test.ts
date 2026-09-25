import { emptySequence, setTrackFlag } from '@/domain/timeline';
import { activeTrackIds, createTrack, moveTrack, trackIsActive, trackName } from '@/domain/tracks';
import { undoTimeline, useTimelineStore } from '@/stores/timelineStore';
import { beforeEach, describe, expect, it } from 'vitest';

describe('track activity', () => {
  it('rejects a blank id and names each kind', () => {
    expect(createTrack('video', '  ', 0, 'ویدیو')).toBeNull();
    expect(createTrack('audio', 'a', 1.5, 'صدا')).toBeNull();
    expect(trackName('text', 2)).toBe('متن 2');
  });

  it('mute wins over solo, and solo limits only the same kind', () => {
    let sequence = emptySequence();
    const text = createTrack('text', 'track-t1', 2, 'متن 1');
    if (!text) throw new Error('text track missing');
    sequence = { ...sequence, tracks: [...sequence.tracks, text] };
    expect(trackIsActive(sequence, 'track-a1')).toBe(true);

    sequence = setTrackFlag(sequence, 'track-a1', 'muted', true);
    sequence = setTrackFlag(sequence, 'track-a1', 'solo', true);
    expect(trackIsActive(sequence, 'track-a1')).toBe(false);
    expect(activeTrackIds(sequence, 'audio')).toEqual([]);

    sequence = setTrackFlag(sequence, 'track-a1', 'muted', false);
    expect(trackIsActive(sequence, 'track-a1')).toBe(true);
    expect(trackIsActive(sequence, 'track-v1')).toBe(true);
    expect(trackIsActive(sequence, 'missing')).toBe(false);
  });

  it('swaps order and rejects a move past the ends', () => {
    const sequence = emptySequence();
    const down = moveTrack(sequence, 'track-v1', 1);
    expect(down.tracks.find((track) => track.id === 'track-v1')?.order).toBe(1);
    expect(down.tracks.find((track) => track.id === 'track-a1')?.order).toBe(0);
    expect(moveTrack(sequence, 'track-v1', -1)).toBe(sequence);
    expect(moveTrack(sequence, 'missing', 1)).toBe(sequence);
  });
});

describe('track store path', () => {
  beforeEach(() => {
    useTimelineStore.temporal.getState().clear();
    useTimelineStore.getState().reset();
    useTimelineStore.temporal.getState().clear();
  });

  it('inserts, reorders, flags, and removes through undoable actions', () => {
    const store = useTimelineStore.getState();
    expect(store.insertTrack('text')).toBe(true);
    const added = useTimelineStore.getState().sequence.tracks.find((track) => track.kind === 'text');
    if (!added) throw new Error('text track missing');
    expect(added.name).toBe('متن 1');
    const afterInsert = useTimelineStore.getState().sequence;

    expect(store.moveTrack('track-v1', 1)).toBe(true);
    undoTimeline(1);
    expect(useTimelineStore.getState().sequence.tracks.map((track) => track.order)).toEqual(
      afterInsert.tracks.map((track) => track.order)
    );

    expect(store.setTrackFlag(added.id, 'locked', true)).toBe(true);
    expect(store.setTrackFlag(added.id, 'locked', true)).toBe(false);
    expect(store.removeTrack(added.id)).toBe(true);
    undoTimeline(1);
    expect(useTimelineStore.getState().sequence.tracks.some((track) => track.id === added.id)).toBe(true);
  });
});
