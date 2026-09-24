/**
 * Timeline store (S-013). Edits go through the pure domain, then immer, then zundo.
 * Undo restores the sequence and the id counter, not the action functions.
 */

import {
  type Clip,
  type Marker,
  type Sequence,
  type Track,
  addClip,
  addMarker,
  addTrack,
  deleteClips,
  emptySequence,
  moveClip,
  removeTrack,
  setSelection,
  setTrackFlag,
  splitClip,
  trimClip,
} from '@/domain/timeline';
import { temporal } from 'zundo';
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export interface TimelineSnapshot {
  sequence: Sequence;
  nextId: number;
}

export interface TimelineState extends TimelineSnapshot {
  addClip: (clip: Clip) => boolean;
  moveClip: (clipId: string, start: number, trackId?: string) => boolean;
  trimClip: (clipId: string, edge: 'in' | 'out', nextDuration: number, ripple: boolean) => boolean;
  splitAt: (clipId: string, time: number) => string | null;
  deleteClips: (ids: string[], ripple: boolean) => boolean;
  addTrack: (track: Track) => boolean;
  removeTrack: (trackId: string) => boolean;
  setTrackFlag: (trackId: string, flag: 'muted' | 'solo' | 'locked', value: boolean) => boolean;
  addMarker: (marker: Marker) => boolean;
  setSelection: (ids: string[]) => void;
  commitEdit: (next: Sequence, addedIds?: number) => boolean;
  reset: (sequence?: Sequence) => void;
}

function commit(
  current: Sequence,
  next: Sequence,
  set: (recipe: (state: TimelineState) => void) => void
): boolean {
  if (next === current) return false;
  set((state) => {
    state.sequence = next;
  });
  return true;
}

export const useTimelineStore = create<TimelineState>()(
  temporal(
    immer((set, get) => ({
      sequence: emptySequence(),
      nextId: 1,
      addClip: (clip) => commit(get().sequence, addClip(get().sequence, clip), set),
      moveClip: (clipId, start, trackId) =>
        commit(get().sequence, moveClip(get().sequence, clipId, start, trackId), set),
      trimClip: (clipId, edge, nextDuration, ripple) =>
        commit(get().sequence, trimClip(get().sequence, clipId, edge, nextDuration, ripple), set),
      splitAt: (clipId, time) => {
        const id = `clip-${get().nextId}`;
        const next = splitClip(get().sequence, clipId, time, id);
        if (next === get().sequence) return null;
        set((state) => {
          state.sequence = next;
          state.nextId += 1;
        });
        return id;
      },
      deleteClips: (ids, ripple) => commit(get().sequence, deleteClips(get().sequence, ids, ripple), set),
      addTrack: (track) => commit(get().sequence, addTrack(get().sequence, track), set),
      removeTrack: (trackId) => commit(get().sequence, removeTrack(get().sequence, trackId), set),
      setTrackFlag: (trackId, flag, value) =>
        commit(get().sequence, setTrackFlag(get().sequence, trackId, flag, value), set),
      addMarker: (marker) => commit(get().sequence, addMarker(get().sequence, marker), set),
      setSelection: (ids) => {
        set((state) => {
          state.sequence = setSelection(state.sequence, ids);
        });
      },
      commitEdit: (next, addedIds = 0) => {
        if (next === get().sequence && addedIds === 0) return false;
        set((state) => {
          state.sequence = next;
          state.nextId += addedIds;
        });
        return true;
      },
      reset: (sequence) => {
        set((state) => {
          state.sequence = sequence ?? emptySequence();
          state.nextId = 1;
        });
      },
    })),
    {
      limit: 100,
      partialize: (state) => ({ sequence: state.sequence, nextId: state.nextId }),
    }
  )
);

export function undoTimeline(steps = 1): void {
  useTimelineStore.temporal.getState().undo(steps);
}

export function redoTimeline(steps = 1): void {
  useTimelineStore.temporal.getState().redo(steps);
}
