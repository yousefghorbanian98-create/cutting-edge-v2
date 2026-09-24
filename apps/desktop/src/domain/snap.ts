/**
 * Pixel snap for clip moves (S-017).
 * 8px is the magnetic threshold. Shift disables it.
 */

export interface SnapTarget {
  time: number;
  label: string;
}

export function pxToMs(px: number, pxPerSecond: number): number {
  return (px / pxPerSecond) * 1000;
}

export function snapTime(
  timeMs: number,
  targets: SnapTarget[],
  pxPerSecond: number,
  thresholdPx = 8,
  disabled = false
): number {
  if (disabled || pxPerSecond <= 0) return timeMs;
  const threshold = pxToMs(thresholdPx, pxPerSecond);
  let best = timeMs;
  let bestDist = threshold;
  for (const target of targets) {
    const dist = Math.abs(target.time - timeMs);
    if (dist <= bestDist) {
      best = target.time;
      bestDist = dist;
    }
  }
  return best;
}

export function snapTargetsFor(
  clips: { id: string; start: number; duration: number }[],
  exceptId: string,
  playheadMs: number,
  markerTimes: number[]
): SnapTarget[] {
  const targets: SnapTarget[] = [{ time: playheadMs, label: 'playhead' }];
  for (const time of markerTimes) targets.push({ time, label: 'marker' });
  for (const clip of clips) {
    if (clip.id === exceptId) continue;
    targets.push({ time: clip.start, label: `${clip.id}-start` });
    targets.push({ time: clip.start + clip.duration, label: `${clip.id}-end` });
  }
  return targets;
}
