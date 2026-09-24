/**
 * Timeline sequence model (S-013).
 *
 * Time is integer milliseconds so split, trim, and undo compare exactly.
 * Clips on one track never overlap. A rejected edit returns the same object.
 */

export type TrackKind = 'video' | 'audio' | 'text';

export interface Transform {
  x: number;
  y: number;
  scale: number;
  rotation: number;
}

export interface Effect {
  id: string;
  type: string;
  amount: number;
}

export interface Clip {
  id: string;
  mediaId: string;
  trackId: string;
  start: number;
  duration: number;
  inPoint: number;
  sourceDuration: number;
  transform: Transform;
  effects: Effect[];
  label: string;
}

export interface Track {
  id: string;
  kind: TrackKind;
  name: string;
  muted: boolean;
  solo: boolean;
  locked: boolean;
  order: number;
}

export interface Marker {
  id: string;
  time: number;
  label: string;
}

export interface Sequence {
  id: string;
  fps: number;
  tracks: Track[];
  clips: Clip[];
  markers: Marker[];
  selection: string[];
}

export const identityTransform = (): Transform => ({ x: 0, y: 0, scale: 1, rotation: 0 });

export function emptySequence(id = 'seq-1', fps = 30): Sequence {
  return {
    id,
    fps,
    tracks: [
      { id: 'track-v1', kind: 'video', name: 'ویدیو ۱', muted: false, solo: false, locked: false, order: 0 },
      { id: 'track-a1', kind: 'audio', name: 'صدا ۱', muted: false, solo: false, locked: false, order: 1 },
    ],
    clips: [],
    markers: [],
    selection: [],
  };
}

export function clipEnd(clip: Clip): number {
  return clip.start + clip.duration;
}

export function overlaps(a: Clip, b: Clip): boolean {
  if (a.id === b.id || a.trackId !== b.trackId) return false;
  return a.start < clipEnd(b) && b.start < clipEnd(a);
}

export function hasOverlap(sequence: Sequence): boolean {
  const byTrack = new Map<string, Clip[]>();
  for (const clip of sequence.clips) {
    const list = byTrack.get(clip.trackId) ?? [];
    list.push(clip);
    byTrack.set(clip.trackId, list);
  }
  for (const list of byTrack.values()) {
    const sorted = [...list].sort((a, b) => a.start - b.start || a.id.localeCompare(b.id));
    for (let i = 1; i < sorted.length; i += 1) {
      const prev = sorted[i - 1];
      const cur = sorted[i];
      if (prev && cur && cur.start < clipEnd(prev)) return true;
    }
  }
  return false;
}

function trackOf(sequence: Sequence, trackId: string): Track | undefined {
  return sequence.tracks.find((track) => track.id === trackId);
}

function replaceClip(sequence: Sequence, clipId: string, next: Clip): Sequence {
  return {
    ...sequence,
    clips: sequence.clips.map((clip) => (clip.id === clipId ? next : clip)),
  };
}

function shiftLater(
  sequence: Sequence,
  trackId: string,
  at: number,
  delta: number,
  exceptId: string
): Sequence {
  if (delta === 0) return sequence;
  return {
    ...sequence,
    clips: sequence.clips.map((clip) => {
      if (clip.trackId !== trackId || clip.id === exceptId || clip.start < at) return clip;
      return { ...clip, start: clip.start + delta };
    }),
  };
}

export function addClip(sequence: Sequence, clip: Clip): Sequence {
  const track = trackOf(sequence, clip.trackId);
  if (!track || track.locked) return sequence;
  if (!Number.isInteger(clip.start) || clip.start < 0) return sequence;
  if (!Number.isInteger(clip.duration) || clip.duration < 1) return sequence;
  if (clip.inPoint < 0 || clip.inPoint + clip.duration > clip.sourceDuration) return sequence;
  if (sequence.clips.some((other) => other.id === clip.id || overlaps(clip, other))) return sequence;
  return { ...sequence, clips: [...sequence.clips, clip] };
}

export function moveClip(sequence: Sequence, clipId: string, start: number, trackId?: string): Sequence {
  const clip = sequence.clips.find((item) => item.id === clipId);
  if (!clip) return sequence;
  const destId = trackId ?? clip.trackId;
  const source = trackOf(sequence, clip.trackId);
  const dest = trackOf(sequence, destId);
  if (!source || !dest || source.locked || dest.locked) return sequence;
  if (source.kind !== dest.kind) return sequence;
  if (!Number.isInteger(start) || start < 0) return sequence;
  if (start === clip.start && destId === clip.trackId) return sequence;
  const moved: Clip = { ...clip, start, trackId: destId };
  if (sequence.clips.some((other) => other.id !== clipId && overlaps(moved, other))) return sequence;
  return replaceClip(sequence, clipId, moved);
}

export function trimClip(
  sequence: Sequence,
  clipId: string,
  edge: 'in' | 'out',
  nextDuration: number,
  ripple: boolean
): Sequence {
  const clip = sequence.clips.find((item) => item.id === clipId);
  const track = clip ? trackOf(sequence, clip.trackId) : undefined;
  if (!clip || !track || track.locked) return sequence;
  if (!Number.isInteger(nextDuration) || nextDuration < 1) return sequence;
  if (nextDuration === clip.duration) return sequence;
  const max = clip.sourceDuration - (edge === 'out' ? clip.inPoint : 0);
  if (nextDuration > max) return sequence;
  if (edge === 'in' && clip.inPoint + clip.duration - nextDuration < 0) return sequence;

  const delta = nextDuration - clip.duration;
  const trimmed: Clip =
    edge === 'out'
      ? { ...clip, duration: nextDuration }
      : {
          ...clip,
          start: clip.start - delta,
          duration: nextDuration,
          inPoint: clip.inPoint + clip.duration - nextDuration,
        };
  if (trimmed.start < 0 || trimmed.inPoint < 0) return sequence;
  const placed = replaceClip(sequence, clipId, trimmed);
  if (!ripple) {
    return hasOverlap(placed) ? sequence : placed;
  }
  const at = edge === 'out' ? clipEnd(clip) : clip.start;
  const shifted = shiftLater(placed, clip.trackId, at, delta, clipId);
  return hasOverlap(shifted) ? sequence : shifted;
}

export function splitClip(sequence: Sequence, clipId: string, time: number, newId: string): Sequence {
  const clip = sequence.clips.find((item) => item.id === clipId);
  const track = clip ? trackOf(sequence, clip.trackId) : undefined;
  if (!clip || !track || track.locked) return sequence;
  if (!Number.isInteger(time) || time <= clip.start || time >= clipEnd(clip)) return sequence;
  if (sequence.clips.some((item) => item.id === newId)) return sequence;
  const leftDuration = time - clip.start;
  const right: Clip = {
    ...clip,
    id: newId,
    start: time,
    duration: clip.duration - leftDuration,
    inPoint: clip.inPoint + leftDuration,
    label: `${clip.label} ۲`,
  };
  const left: Clip = { ...clip, duration: leftDuration };
  const clips: Clip[] = [];
  for (const item of sequence.clips) {
    if (item.id !== clipId) clips.push(item);
    else clips.push(left, right);
  }
  return { ...sequence, clips };
}

export function deleteClips(sequence: Sequence, ids: string[], ripple: boolean): Sequence {
  const drop = new Set(ids);
  if (drop.size === 0) return sequence;
  const present = sequence.clips.filter((clip) => drop.has(clip.id));
  if (present.length === 0) return sequence;
  let next: Sequence = {
    ...sequence,
    clips: sequence.clips.filter((clip) => !drop.has(clip.id)),
    selection: sequence.selection.filter((id) => !drop.has(id)),
  };
  if (!ripple) return next;
  const removed = [...present].sort((a, b) => b.start - a.start);
  for (const clip of removed) {
    next = shiftLater(next, clip.trackId, clipEnd(clip), -clip.duration, clip.id);
  }
  return next;
}

export function addTrack(sequence: Sequence, track: Track): Sequence {
  if (sequence.tracks.some((item) => item.id === track.id)) return sequence;
  return { ...sequence, tracks: [...sequence.tracks, track] };
}

export function removeTrack(sequence: Sequence, trackId: string): Sequence {
  if (sequence.clips.some((clip) => clip.trackId === trackId)) return sequence;
  if (!sequence.tracks.some((track) => track.id === trackId)) return sequence;
  return { ...sequence, tracks: sequence.tracks.filter((track) => track.id !== trackId) };
}

export function setTrackFlag(
  sequence: Sequence,
  trackId: string,
  flag: 'muted' | 'solo' | 'locked',
  value: boolean
): Sequence {
  if (!sequence.tracks.some((track) => track.id === trackId)) return sequence;
  return {
    ...sequence,
    tracks: sequence.tracks.map((track) => (track.id === trackId ? { ...track, [flag]: value } : track)),
  };
}

export function addMarker(sequence: Sequence, marker: Marker): Sequence {
  if (!Number.isInteger(marker.time) || marker.time < 0) return sequence;
  if (sequence.markers.some((item) => item.id === marker.id)) return sequence;
  return { ...sequence, markers: [...sequence.markers, marker] };
}

export function setSelection(sequence: Sequence, ids: string[]): Sequence {
  const known = new Set(sequence.clips.map((clip) => clip.id));
  const selection = ids.filter((id) => known.has(id));
  return { ...sequence, selection };
}
