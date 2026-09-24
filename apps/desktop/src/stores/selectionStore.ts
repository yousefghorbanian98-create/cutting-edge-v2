/**
 * Selection and clipboard (S-020).
 * Geometry is in timeline pixels. Paste keeps relative offsets.
 */

import { PX_PER_SECOND, msToSeconds } from '@/components/timeline/window';
import { type Clip, type Sequence, addClip } from '@/domain/timeline';
import { useTimelineStore } from '@/stores/timelineStore';
import { create } from 'zustand';

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function clipsInRect(clips: Clip[], rect: Rect): string[] {
  const left = Math.min(rect.x, rect.x + rect.width);
  const right = Math.max(rect.x, rect.x + rect.width);
  const start = (left / PX_PER_SECOND) * 1000;
  const end = (right / PX_PER_SECOND) * 1000;
  return clips
    .filter((clip) => clip.start < end && clip.start + clip.duration > start)
    .map((clip) => clip.id);
}

export function pasteAt(sequence: Sequence, clips: Clip[], atMs: number): Sequence {
  if (clips.length === 0) return sequence;
  const origin = Math.min(...clips.map((clip) => clip.start));
  let next = sequence;
  clips.forEach((clip, index) => {
    const copy: Clip = {
      ...clip,
      id: `${clip.id}-paste-${index}-${atMs}`,
      start: atMs + (clip.start - origin),
    };
    const added = addClip(next, copy);
    if (added !== next) next = added;
  });
  return next;
}

export function duplicateClips(sequence: Sequence, ids: string[]): Sequence {
  const chosen = sequence.clips.filter((clip) => ids.includes(clip.id));
  const end = chosen.reduce((max, clip) => Math.max(max, clip.start + clip.duration), 0);
  return pasteAt(sequence, chosen, end);
}

interface SelectionState {
  clipboard: Clip[];
  copy: () => void;
  paste: (atMs: number) => void;
  duplicate: () => void;
  selectRect: (rect: Rect, additive: boolean) => void;
}

export const useSelectionStore = create<SelectionState>()((set, get) => ({
  clipboard: [],
  copy: () => {
    const sequence = useTimelineStore.getState().sequence;
    set({ clipboard: sequence.clips.filter((clip) => sequence.selection.includes(clip.id)) });
  },
  paste: (atMs) => {
    const sequence = useTimelineStore.getState().sequence;
    const next = pasteAt(sequence, get().clipboard, atMs);
    const added = Math.max(0, next.clips.length - sequence.clips.length);
    useTimelineStore.getState().commitEdit(next, added);
  },
  duplicate: () => {
    const sequence = useTimelineStore.getState().sequence;
    const next = duplicateClips(sequence, sequence.selection);
    const added = Math.max(0, next.clips.length - sequence.clips.length);
    useTimelineStore.getState().commitEdit(next, added);
  },
  selectRect: (rect, additive) => {
    const sequence = useTimelineStore.getState().sequence;
    const hit = clipsInRect(sequence.clips, rect);
    const selection = additive ? [...new Set([...sequence.selection, ...hit])] : hit;
    useTimelineStore.getState().setSelection(selection);
  },
}));

export function clipLeftPx(clip: Clip): number {
  return msToSeconds(clip.start) * PX_PER_SECOND;
}
