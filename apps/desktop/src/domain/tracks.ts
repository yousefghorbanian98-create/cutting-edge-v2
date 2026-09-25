/**
 * Track operations for S-022.
 *
 * Mutations return the same sequence when rejected. Playback asks
 * `trackIsActive` instead of inventing a second mute rule.
 */

import type { Sequence, Track, TrackKind } from '@/domain/timeline';

export type TrackDirection = -1 | 1;

const KINDS: readonly TrackKind[] = ['video', 'audio', 'text'];

export function isTrackKind(value: string): value is TrackKind {
  return KINDS.includes(value as TrackKind);
}

export function trackName(kind: TrackKind, index: number): string {
  const label = kind === 'video' ? 'ویدیو' : kind === 'audio' ? 'صدا' : 'متن';
  return `${label} ${index}`;
}

export function createTrack(kind: TrackKind, id: string, order: number, name: string): Track | null {
  if (!isTrackKind(kind) || id.trim() === '' || name.trim() === '') return null;
  if (!Number.isInteger(order)) return null;
  return { id, kind, name, muted: false, solo: false, locked: false, order };
}

export function moveTrack(sequence: Sequence, trackId: string, direction: TrackDirection): Sequence {
  const sorted = [...sequence.tracks].sort((a, b) => a.order - b.order || a.id.localeCompare(b.id));
  const index = sorted.findIndex((track) => track.id === trackId);
  const swap = index + direction;
  if (index < 0 || swap < 0 || swap >= sorted.length) return sequence;
  const next = sorted.slice();
  const current = next[index];
  const neighbor = next[swap];
  if (!current || !neighbor) return sequence;
  next[index] = neighbor;
  next[swap] = current;
  const orderOf = new Map(next.map((track, position) => [track.id, position]));
  return {
    ...sequence,
    tracks: sequence.tracks.map((track) => ({ ...track, order: orderOf.get(track.id) ?? track.order })),
  };
}

export function trackIsActive(sequence: Sequence, trackId: string): boolean {
  const track = sequence.tracks.find((item) => item.id === trackId);
  if (!track || track.muted) return false;
  const soloed = sequence.tracks.some((item) => item.kind === track.kind && item.solo);
  return !soloed || track.solo;
}

export function activeTrackIds(sequence: Sequence, kind: TrackKind): string[] {
  return sequence.tracks
    .filter((track) => track.kind === kind && trackIsActive(sequence, track.id))
    .map((track) => track.id);
}
