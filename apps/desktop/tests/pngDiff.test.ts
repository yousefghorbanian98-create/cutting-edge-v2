import { deflateSync } from 'node:zlib';
import { describe, expect, it } from 'vitest';
import { pixelDiffRatio, visualDiffRatio } from './pngDiff';

const THRESHOLD = 0.001;

function chunk(type: string, data: Buffer): Buffer {
  const out = Buffer.alloc(12 + data.length);
  out.writeUInt32BE(data.length, 0);
  out.write(type, 4, 4, 'ascii');
  data.copy(out, 8);
  return out;
}

function rgbaPng(width: number, height: number, pixels: Buffer): Buffer {
  const stride = width * 4;
  if (pixels.length !== stride * height) throw new Error('bad fixture');
  const raw = Buffer.alloc((stride + 1) * height);
  for (let y = 0; y < height; y += 1) {
    raw[y * (stride + 1)] = 0;
    pixels.copy(raw, y * (stride + 1) + 1, y * stride, y * stride + stride);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(raw)),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

function report(name: string, fixture: string, baseline: string, measured: number): void {
  const condition = measured < THRESHOLD ? 'passed' : 'failed';
  console.info(
    [
      `EVIDENCE test=${name} metric=visual-diff fixture=${fixture} baseline=${baseline}`,
      `measured=${measured} threshold=<0.001 condition-result=${condition}`,
      'alpha-policy=count-any-channel-including-alpha resize=none color-conversion=none',
      'tolerance=none pixelDiffRatio-is-not-this-metric=true ssim-is-not-this-metric=true seed=none',
    ].join(' ')
  );
}

describe('direct visual diff', () => {
  it('visual-diff identical images is 0', () => {
    const png = rgbaPng(2, 1, Buffer.from([1, 2, 3, 4, 5, 6, 7, 8]));
    const measured = visualDiffRatio(png, png);
    report('visual-diff identical images is 0', 'synthetic-rgba-2x1', 'same-png', measured);
    expect(measured).toBe(0);
    expect(measured < THRESHOLD).toBe(true);
  });

  it('visual-diff one changed channel among 2 pixels', () => {
    const leftPx = Buffer.from([1, 2, 3, 4, 5, 6, 7, 8]);
    const rightPx = Buffer.from(leftPx);
    rightPx[0] = 9;
    const measured = visualDiffRatio(rgbaPng(2, 1, leftPx), rgbaPng(2, 1, rightPx));
    report('visual-diff one changed channel among 2 pixels', 'synthetic-rgba-2x1', 'one-channel', measured);
    expect(measured).toBe(0.5);
    expect(measured < THRESHOLD).toBe(false);
  });

  it('visual-diff one changed pixel among 1000 fails lt 0.001', () => {
    const width = 40;
    const height = 25;
    const leftPx = Buffer.alloc(width * height * 4, 8);
    const rightPx = Buffer.from(leftPx);
    rightPx[0] = 9;
    const left = rgbaPng(width, height, leftPx);
    const right = rgbaPng(width, height, rightPx);
    const measured = visualDiffRatio(left, right);
    const bytes = pixelDiffRatio(left, right);
    report(
      'visual-diff one changed pixel among 1000 fails lt 0.001',
      'synthetic-rgba-40x25',
      'one-channel-of-one-pixel',
      measured
    );
    console.info(
      [
        `EVIDENCE metric=channel-byte-ratio measured=${bytes}`,
        'channel-byte-ratio-is-not-visual-diff=true seed=none',
      ].join(' ')
    );
    expect(measured).toBe(0.001);
    expect(measured < THRESHOLD).toBe(false);
    expect(bytes).toBeLessThan(THRESHOLD);
    expect(measured).not.toBe(bytes);
  });

  it('visual-diff alpha-only change', () => {
    const leftPx = Buffer.from([1, 2, 3, 4, 5, 6, 7, 8]);
    const rightPx = Buffer.from(leftPx);
    rightPx[3] = 5;
    const measured = visualDiffRatio(rgbaPng(2, 1, leftPx), rgbaPng(2, 1, rightPx));
    report('visual-diff alpha-only change', 'synthetic-rgba-2x1', 'alpha-only', measured);
    expect(measured).toBe(0.5);
    expect(measured < THRESHOLD).toBe(false);
  });

  it('visual-diff one-byte difference', () => {
    const leftPx = Buffer.from([1, 2, 3, 4, 5, 6, 7, 8]);
    const rightPx = Buffer.from(leftPx);
    rightPx[0] = 2;
    const measured = visualDiffRatio(rgbaPng(2, 1, leftPx), rgbaPng(2, 1, rightPx));
    report('visual-diff one-byte difference', 'synthetic-rgba-2x1', 'plus-one-red', measured);
    expect(measured).toBe(0.5);
    expect(measured < THRESHOLD).toBe(false);
  });

  it('visual-diff dimension mismatch', () => {
    const small = rgbaPng(1, 1, Buffer.from([1, 2, 3, 4]));
    const wide = rgbaPng(2, 1, Buffer.from([1, 2, 3, 4, 1, 2, 3, 4]));
    const measured = visualDiffRatio(small, wide);
    report('visual-diff dimension mismatch', 'synthetic-rgba-1x1', 'synthetic-rgba-2x1', measured);
    expect(measured).toBe(1);
    expect(measured < THRESHOLD).toBe(false);
  });

  it('visual-diff empty or unreadable input', () => {
    const measured = visualDiffRatio(Buffer.alloc(0), Buffer.alloc(0));
    report('visual-diff empty or unreadable input', 'empty', 'empty', measured);
    expect(measured).toBe(1);
    expect(Number.isNaN(measured)).toBe(false);
    expect(measured < THRESHOLD).toBe(false);
  });
});
