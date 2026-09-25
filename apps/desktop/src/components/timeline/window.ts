/**
 * Visible-window math for the timeline (S-015).
 * Time in the view is seconds. The domain stores milliseconds.
 */

export const PX_PER_SECOND = 100;

export interface WindowClip {
  id: string;
  start: number;
  duration: number;
}

export function msToSeconds(ms: number): number {
  return ms / 1000;
}

export function visibleClips(clips: WindowClip[], startSec: number, endSec: number): WindowClip[] {
  return clips.filter((clip) => {
    const start = msToSeconds(clip.start);
    const end = msToSeconds(clip.start + clip.duration);
    return start < endSec && end > startSec;
  });
}

/** Pointer time inside the scroll content, ignoring the lane's border box. */
export function timeFromPointer(
  clientX: number,
  laneLeft: number,
  borderLeft: number,
  scrollLeft: number,
  pxPerSecond = PX_PER_SECOND
): number {
  if (pxPerSecond <= 0) return 0;
  return Math.max(0, (clientX - laneLeft - borderLeft + scrollLeft) / pxPerSecond);
}

export function contentWidth(clips: WindowClip[], pxPerSecond = PX_PER_SECOND): number {
  const end = clips.reduce((max, clip) => Math.max(max, msToSeconds(clip.start + clip.duration)), 1);
  return Math.ceil(end * pxPerSecond);
}

export function barsFor(id: string, count = 16): number[] {
  let seed = 0;
  for (let i = 0; i < id.length; i += 1) seed = (seed * 33 + id.charCodeAt(i)) % 997;
  return Array.from({ length: count }, (_, i) => {
    seed = (seed * 17 + i * 13) % 997;
    return 20 + (seed % 80);
  });
}
