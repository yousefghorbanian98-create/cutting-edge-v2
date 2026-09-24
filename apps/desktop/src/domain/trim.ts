/**
 * Trim, ripple, and roll (S-018). Times are milliseconds.
 * A rejected edit returns the same sequence.
 */

import { type Sequence, trimClip } from './timeline';

export function trimBy(
  sequence: Sequence,
  clipId: string,
  edge: 'in' | 'out',
  deltaMs: number,
  ripple: boolean
): Sequence {
  const clip = sequence.clips.find((item) => item.id === clipId);
  if (!clip) return sequence;
  return trimClip(sequence, clipId, edge, clip.duration + deltaMs, ripple);
}

export function rollTrim(sequence: Sequence, leftId: string, rightId: string, cut: number): Sequence {
  const left = sequence.clips.find((item) => item.id === leftId);
  const right = sequence.clips.find((item) => item.id === rightId);
  if (!left || !right || left.trackId !== right.trackId) return sequence;
  if (right.start !== left.start + left.duration) return sequence;
  if (!Number.isInteger(cut) || cut <= left.start || cut >= right.start + right.duration) return sequence;
  const leftDuration = cut - left.start;
  const delta = cut - right.start;
  const rightDuration = right.duration - delta;
  const rightIn = right.inPoint + delta;
  if (left.inPoint + leftDuration > left.sourceDuration) return sequence;
  if (rightIn < 0 || rightIn + rightDuration > right.sourceDuration) return sequence;
  return {
    ...sequence,
    clips: sequence.clips.map((clip) => {
      if (clip.id === leftId) return { ...clip, duration: leftDuration };
      if (clip.id === rightId) return { ...clip, start: cut, duration: rightDuration, inPoint: rightIn };
      return clip;
    }),
  };
}
