import { describe, expect, it } from 'vitest';
import { fitPx, pixelError, zoomAround } from '../zoom';

describe('zoom around the cursor', () => {
  it('keeps x=400 within 1px when zooming in', () => {
    const next = zoomAround(100, 0, 400, 1.25);
    expect(pixelError(100, 0, next.pxPerSecond, next.scrollLeft, 400)).toBeLessThanOrEqual(1);
    expect(next.pxPerSecond).toBeGreaterThan(100);
  });

  it('fits a 10s sequence inside an 800px viewport', () => {
    expect(fitPx(10, 800)).toBe(80);
  });
});
