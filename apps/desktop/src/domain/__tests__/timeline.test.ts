/**
 * S-013 real test: random edits never overlap a track, and undo(n) restores the prior snapshot.
 */

import {
  type Clip,
  addClip,
  addMarker,
  addTrack,
  deleteClips,
  emptySequence,
  hasOverlap,
  identityTransform,
  moveClip,
  removeTrack,
  setSelection,
  setTrackFlag,
  splitClip,
  trimClip,
} from '@/domain/timeline';
import { redoTimeline, undoTimeline, useTimelineStore } from '@/stores/timelineStore';
import fc from 'fast-check';
import { beforeEach, describe, expect, it } from 'vitest';

function clip(partial: Partial<Clip> & Pick<Clip, 'id' | 'trackId' | 'start' | 'duration'>): Clip {
  return {
    mediaId: 'media-1',
    inPoint: 0,
    sourceDuration: 20_000,
    transform: identityTransform(),
    effects: [],
    label: partial.id,
    ...partial,
  };
}

function snapshot(): string {
  const { sequence, nextId } = useTimelineStore.getState();
  return JSON.stringify({ sequence, nextId });
}

describe('timeline domain', () => {
  it('rejects an overlapping move and a cross-kind move', () => {
    let sequence = addClip(emptySequence(), clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 1000 }));
    sequence = addClip(sequence, clip({ id: 'b', trackId: 'track-v1', start: 1000, duration: 1000 }));
    expect(moveClip(sequence, 'b', 500)).toBe(sequence);
    expect(moveClip(sequence, 'a', 0, 'track-a1')).toBe(sequence);
    expect(moveClip(sequence, 'missing', 0)).toBe(sequence);
    expect(hasOverlap(sequence)).toBe(false);
  });

  it('trims inside the source and ripples later clips', () => {
    let sequence = addClip(emptySequence(), clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 2000 }));
    sequence = addClip(sequence, clip({ id: 'b', trackId: 'track-v1', start: 2000, duration: 1000 }));
    const trimmed = trimClip(sequence, 'a', 'out', 1500, true);
    expect(trimmed.clips.find((item) => item.id === 'a')?.duration).toBe(1500);
    expect(trimmed.clips.find((item) => item.id === 'b')?.start).toBe(1500);
    expect(trimClip(sequence, 'a', 'out', 50_000, false)).toBe(sequence);
    expect(hasOverlap(trimmed)).toBe(false);
  });

  it('splits with continuous source in and out points', () => {
    const sequence = addClip(
      emptySequence(),
      clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 10_000, inPoint: 100, sourceDuration: 20_000 })
    );
    const split = splitClip(sequence, 'a', 4500, 'a-right');
    const left = split.clips.find((item) => item.id === 'a');
    const right = split.clips.find((item) => item.id === 'a-right');
    expect(left?.duration).toBe(4500);
    expect(right?.start).toBe(4500);
    expect(right?.duration).toBe(5500);
    expect(right?.inPoint).toBe(4600);
    expect(splitClip(sequence, 'a', 0, 'nope')).toBe(sequence);
  });

  it('trims the in point without leaving the source or going negative', () => {
    const sequence = addClip(
      emptySequence(),
      clip({ id: 'a', trackId: 'track-v1', start: 1000, duration: 2000, inPoint: 500 })
    );
    const trimmed = trimClip(sequence, 'a', 'in', 1000, true);
    const item = trimmed.clips[0];
    expect(item?.start).toBe(2000);
    expect(item?.inPoint).toBe(1500);
    expect(item?.duration).toBe(1000);
    expect(trimClip(sequence, 'a', 'in', 0, false)).toBe(sequence);
    expect(trimClip(sequence, 'a', 'in', 1.5, false)).toBe(sequence);
    const nearZero = addClip(
      emptySequence(),
      clip({ id: 'a', trackId: 'track-v1', start: 100, duration: 2000, inPoint: 500 })
    );
    expect(trimClip(nearZero, 'a', 'in', 2200, false)).toBe(nearZero);
    let crowded = addClip(emptySequence(), clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 1000 }));
    crowded = addClip(
      crowded,
      clip({ id: 'b', trackId: 'track-v1', start: 2000, duration: 1000, inPoint: 2000 })
    );
    expect(trimClip(crowded, 'b', 'in', 2500, true)).toBe(crowded);
  });

  it('rejects locked tracks, duplicate ids, and a track that still has clips', () => {
    let sequence = setTrackFlag(emptySequence(), 'track-v1', 'locked', true);
    const blocked = clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 1000 });
    expect(addClip(sequence, blocked)).toBe(sequence);
    sequence = setTrackFlag(sequence, 'track-v1', 'locked', false);
    sequence = addClip(sequence, blocked);
    expect(removeTrack(sequence, 'track-v1')).toBe(sequence);
    expect(removeTrack(sequence, 'missing')).toBe(sequence);
    const extra = addTrack(sequence, {
      id: 'track-t1',
      kind: 'text',
      name: 'متن',
      muted: false,
      solo: false,
      locked: false,
      order: 2,
    });
    expect(extra.tracks).toHaveLength(3);
    const added = extra.tracks[2];
    if (!added) throw new Error('track missing');
    expect(addTrack(extra, added)).toBe(extra);
    expect(removeTrack(extra, 'track-t1').tracks.map((track) => track.id)).not.toContain('track-t1');
    expect(setTrackFlag(sequence, 'missing', 'solo', true)).toBe(sequence);
  });

  it('keeps markers and selection inside the sequence', () => {
    let sequence = addClip(emptySequence(), clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 1000 }));
    sequence = addMarker(sequence, { id: 'm1', time: 250, label: 'نقطه' });
    expect(addMarker(sequence, { id: 'm1', time: 250, label: 'تکرار' })).toBe(sequence);
    expect(addMarker(sequence, { id: 'bad', time: -1, label: 'رد' })).toBe(sequence);
    sequence = setSelection(sequence, ['a', 'ghost']);
    expect(sequence.selection).toEqual(['a']);
    const removed = deleteClips(sequence, ['a'], false);
    expect(removed.clips).toHaveLength(0);
    expect(removed.selection).toEqual([]);
    expect(deleteClips(removed, ['a'], true)).toBe(removed);
  });

  it('ripple-deletes the first clip so the next one starts at zero', () => {
    let sequence = addClip(emptySequence(), clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 1000 }));
    sequence = addClip(sequence, clip({ id: 'b', trackId: 'track-v1', start: 1000, duration: 1000 }));
    const next = deleteClips(sequence, ['a'], true);
    expect(next.clips.map((item) => item.id)).toEqual(['b']);
    expect(next.clips[0]?.start).toBe(0);
  });
});

describe('timeline store undo', () => {
  beforeEach(() => {
    useTimelineStore.temporal.getState().clear();
    useTimelineStore.getState().reset();
    useTimelineStore.temporal.getState().clear();
  });

  it('undo(n) restores the exact snapshot, then redo returns', () => {
    const store = useTimelineStore.getState();
    expect(store.addClip(clip({ id: 'a', trackId: 'track-v1', start: 0, duration: 4000 }))).toBe(true);
    const afterAdd = snapshot();
    expect(useTimelineStore.getState().splitAt('a', 1500)).toBe('clip-1');
    expect(useTimelineStore.getState().moveClip('clip-1', 5000)).toBe(true);
    undoTimeline(1);
    expect(snapshot()).not.toBe(afterAdd);
    undoTimeline(1);
    expect(snapshot()).toBe(afterAdd);
    redoTimeline(2);
    expect(useTimelineStore.getState().sequence.clips).toHaveLength(2);
    expect(hasOverlap(useTimelineStore.getState().sequence)).toBe(false);
  });
});

describe('random timeline ops', () => {
  beforeEach(() => {
    useTimelineStore.temporal.getState().clear();
    useTimelineStore.getState().reset();
    useTimelineStore.temporal.getState().clear();
  });

  it('keeps tracks non-overlapping and undo(n) restores the prior state', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            kind: fc.constantFrom('move', 'trim', 'split', 'delete'),
            index: fc.integer({ min: 0, max: 5 }),
            amount: fc.integer({ min: 1, max: 8 }),
          }),
          { minLength: 1, maxLength: 24 }
        ),
        fc.integer({ min: 0, max: 24 }),
        (ops, undoRequest) => {
          useTimelineStore.temporal.getState().clear();
          useTimelineStore.getState().reset();
          useTimelineStore.temporal.getState().clear();
          const store = useTimelineStore.getState();
          store.addClip(clip({ id: 'seed-a', trackId: 'track-v1', start: 0, duration: 3000 }));
          store.addClip(clip({ id: 'seed-b', trackId: 'track-v1', start: 4000, duration: 3000 }));
          store.addClip(clip({ id: 'seed-c', trackId: 'track-a1', start: 0, duration: 2000 }));
          useTimelineStore.temporal.getState().clear();
          const history = [snapshot()];
          for (const op of ops) {
            const clips = useTimelineStore.getState().sequence.clips;
            if (clips.length === 0) break;
            const target = clips[op.index % clips.length];
            if (!target) break;
            const api = useTimelineStore.getState();
            const before = snapshot();
            if (op.kind === 'move') api.moveClip(target.id, target.start + op.amount * 100);
            else if (op.kind === 'trim')
              api.trimClip(target.id, 'out', Math.max(1, target.duration - op.amount * 50), true);
            else if (op.kind === 'split')
              api.splitAt(target.id, target.start + Math.floor(target.duration / 2));
            else api.deleteClips([target.id], op.amount % 2 === 0);
            expect(hasOverlap(useTimelineStore.getState().sequence)).toBe(false);
            const after = snapshot();
            if (after !== before) history.push(after);
          }
          const steps = Math.min(undoRequest, history.length - 1);
          if (steps > 0) undoTimeline(steps);
          expect(snapshot()).toBe(history[history.length - 1 - steps]);
        }
      ),
      { numRuns: 40 }
    );
  });
});
