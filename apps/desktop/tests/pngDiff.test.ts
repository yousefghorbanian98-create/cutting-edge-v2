import { deflateSync } from 'node:zlib';
import { describe, expect, it } from 'vitest';
import { pixelDiffRatio, visualDiffRatio } from './pngDiff';

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

describe('visual diff is a pixel ratio, not a channel-byte ratio', () => {
  it('counts one changed channel as one pixel', () => {
    const width = 40;
    const height = 25;
    const pixels = Buffer.alloc(width * height * 4, 8);
    const left = rgbaPng(width, height, pixels);
    pixels[0] = 9;
    const right = rgbaPng(width, height, pixels);
    const visual = visualDiffRatio(left, right);
    const bytes = pixelDiffRatio(left, right);
    expect(visual).toBe(1 / (width * height));
    expect(visual).toBe(0.001);
    expect(visual < 0.001).toBe(false);
    expect(bytes).toBeLessThan(0.001);
    expect(visual).not.toBe(bytes);
  });

  it('is zero only when every channel of every pixel matches', () => {
    const pixels = Buffer.from([1, 2, 3, 4, 5, 6, 7, 8]);
    const png = rgbaPng(2, 1, pixels);
    expect(visualDiffRatio(png, png)).toBe(0);
    expect(pixelDiffRatio(png, png)).toBe(0);
  });

  it('counts an alpha-only change and does not tolerate a one-byte difference', () => {
    const leftPx = Buffer.from([1, 2, 3, 4, 5, 6, 7, 8]);
    const left = rgbaPng(2, 1, leftPx);
    const alpha = Buffer.from(leftPx);
    alpha[3] = 5;
    const red = Buffer.from(leftPx);
    red[0] = 2;
    expect(visualDiffRatio(left, rgbaPng(2, 1, alpha))).toBe(0.5);
    expect(visualDiffRatio(left, rgbaPng(2, 1, red))).toBe(0.5);
  });

  it('fails closed on a size mismatch or empty input and does not resize', () => {
    const small = rgbaPng(1, 1, Buffer.from([1, 2, 3, 4]));
    const wide = rgbaPng(2, 1, Buffer.from([1, 2, 3, 4, 1, 2, 3, 4]));
    expect(visualDiffRatio(small, wide)).toBe(1);
    expect(visualDiffRatio(Buffer.alloc(0), Buffer.alloc(0))).toBe(1);
    expect(Number.isNaN(visualDiffRatio(small, wide))).toBe(false);
  });
});
