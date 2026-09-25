/** Timeline time → source time (S-024). Drawing uses this map, not a fake attribute. */

export interface CompositeClip {
  id: string;
  mediaId: string;
  trackId: string;
  kind: 'video' | 'audio' | 'text';
  start: number;
  duration: number;
  inPoint: number;
  text?: string;
}

export interface Hit {
  clip: CompositeClip;
  sourceMs: number;
}

export function hitAt(clips: CompositeClip[], timeMs: number, kind: CompositeClip['kind']): Hit | null {
  const found = clips.find(
    (clip) => clip.kind === kind && timeMs >= clip.start && timeMs < clip.start + clip.duration
  );
  if (!found) return null;
  return { clip: found, sourceMs: found.inPoint + (timeMs - found.start) };
}

export function paintColor(mediaId: string, sourceMs: number): [number, number, number] {
  const seed = Math.round(sourceMs) + (mediaId.codePointAt(0) ?? 0) * 17;
  return [(seed * 13) % 256, (seed * 29) % 256, (seed * 47) % 256];
}

export function paintFrame(
  ctx: CanvasRenderingContext2D,
  mediaId: string,
  sourceMs: number,
  width: number,
  height: number
): void {
  const [r, g, b] = paintColor(mediaId, sourceMs);
  ctx.fillStyle = `rgb(${r} ${g} ${b})`;
  ctx.fillRect(0, 0, width, height);
  const bar = Math.abs(Math.round(sourceMs)) % Math.max(1, width);
  ctx.fillStyle = '#fff';
  ctx.fillRect(bar, 0, 2, height);
}
