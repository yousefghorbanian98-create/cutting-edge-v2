import { describe, expect, it } from 'vitest';
import { fitPx, fitViewport, pixelError, sheetWidth, zoomAround } from '../zoom';

describe('zoom around the cursor', () => {
  it('keeps x=400 within 1px when zooming in', () => {
    const next = zoomAround(100, 0, 400, 1.25);
    expect(pixelError(100, 0, next.pxPerSecond, next.scrollLeft, 400)).toBeLessThanOrEqual(1);
    expect(next.pxPerSecond).toBeGreaterThan(100);
  });

  it('fits a 10s sequence inside an 800px viewport', () => {
    expect(fitPx(10, 800)).toBe(80);
  });

  it('keeps scroll room when a 10s sequence is narrower than the viewport', () => {
    const next = zoomAround(100, 0, 384, 1.25);
    const width = sheetWidth(10 * next.pxPerSecond, 1408, next.scrollLeft);
    expect(width - 1408).toBeGreaterThanOrEqual(next.scrollLeft);
  });

  it('fits a 10s lane plus an 11rem header inside a 1406px scroller', () => {
    const client = 1406;
    const header = 176;
    const lane = Math.ceil(10 * fitPx(10, fitViewport(client, header)));
    expect(header + lane).toBeLessThanOrEqual(client + 1);
  });
});
