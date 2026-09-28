/** Playhead lead budget (S-024). Official drift bound is `< 1/60`. This lead never reaches it. */

export const STRICT_PLAYHEAD_FPS = 60;

/** Half a frame at the strictest played rate. A full frame fails the official `< 1/60`. */
export function maxPlayheadLeadSeconds(fps = STRICT_PLAYHEAD_FPS): number {
  const safe = fps > 0 ? fps : STRICT_PLAYHEAD_FPS;
  // A 30fps file must not widen the lead to 1/60. CI's failing bound was 60fps.
  return 0.5 / Math.max(safe, STRICT_PLAYHEAD_FPS);
}

export function playheadTranslate(seconds: number, pxPerSecond: number): string {
  const px = pxPerSecond > 0 ? pxPerSecond : 100;
  return `translate3d(${seconds * px}px, 0, 0)`;
}
