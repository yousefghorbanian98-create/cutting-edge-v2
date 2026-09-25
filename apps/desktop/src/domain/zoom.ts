/** View zoom math (S-023). This does not edit the sequence. */

export const BASE_PX = 100;
export const MIN_PX = 20;
export const MAX_PX = 400;

export function clampPx(px: number): number {
  if (!Number.isFinite(px)) return BASE_PX;
  return Math.min(MAX_PX, Math.max(MIN_PX, px));
}

/** Keep the time under `cursorX` fixed. Pixel error stays within 1 when unclamped. */
export function zoomAround(
  px: number,
  scrollLeft: number,
  cursorX: number,
  factor: number
): { pxPerSecond: number; scrollLeft: number } {
  const current = px > 0 ? px : BASE_PX;
  const time = (scrollLeft + cursorX) / current;
  const next = clampPx(current * (factor > 0 ? factor : 1));
  return { pxPerSecond: next, scrollLeft: Math.max(0, time * next - cursorX) };
}

export function fitPx(seconds: number, viewport: number): number {
  if (!(seconds > 0) || !(viewport > 0)) return BASE_PX;
  return clampPx(viewport / seconds);
}

/** The track header sits in the same scroll row, so fit cannot use the full client width. */
export function fitViewport(clientWidth: number, headerWidth: number): number {
  return Math.max(1, clientWidth - Math.max(0, headerWidth));
}

/** Wide enough that the browser can apply `scrollLeft` instead of clamping it to 0. */
export function sheetWidth(sequenceWidth: number, viewport: number, scrollLeft: number): number {
  const room = Math.max(0, viewport) + Math.max(0, scrollLeft);
  return Math.ceil(Math.max(sequenceWidth, room));
}

export function pixelError(
  beforePx: number,
  beforeScroll: number,
  afterPx: number,
  afterScroll: number,
  cursorX: number
): number {
  const before = (beforeScroll + cursorX) / beforePx;
  const after = (afterScroll + cursorX) / afterPx;
  return Math.abs(before - after) * afterPx;
}
