/**
 * Split and ripple-delete at the playhead (S-019).
 */

import { type Sequence, deleteClips, splitClip } from './timeline';

export function clipsUnderPlayhead(sequence: Sequence, timeMs: number, selectedOnly: boolean): string[] {
  return sequence.clips
    .filter((clip) => {
      if (selectedOnly && !sequence.selection.includes(clip.id)) return false;
      return timeMs > clip.start && timeMs < clip.start + clip.duration;
    })
    .map((clip) => clip.id);
}

export function splitAtPlayhead(
  sequence: Sequence,
  timeMs: number,
  ids: string[],
  selectedOnly: boolean
): Sequence {
  const targets = clipsUnderPlayhead(sequence, timeMs, selectedOnly).filter(
    (id) => ids.includes(id) || ids.length === 0
  );
  const chosen = ids.length === 0 ? clipsUnderPlayhead(sequence, timeMs, selectedOnly) : targets;
  let next = sequence;
  let n = 0;
  for (const id of chosen) {
    const split = splitClip(next, id, timeMs, `${id}-split-${n}`);
    if (split !== next) {
      next = split;
      n += 1;
    }
  }
  return next;
}

export function removeClips(sequence: Sequence, ids: string[], ripple: boolean): Sequence {
  return deleteClips(sequence, ids, ripple);
}
