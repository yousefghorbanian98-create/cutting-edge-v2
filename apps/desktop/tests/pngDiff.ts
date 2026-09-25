import { inflateSync } from 'node:zlib';

function paeth(left: number, up: number, upLeft: number): number {
  const estimate = left + up - upLeft;
  const leftDistance = Math.abs(estimate - left);
  const upDistance = Math.abs(estimate - up);
  const diagonal = Math.abs(estimate - upLeft);
  if (leftDistance <= upDistance && leftDistance <= diagonal) return left;
  if (upDistance <= diagonal) return up;
  return upLeft;
}

export function pixelDiffRatio(left: Buffer, right: Buffer): number {
  const a = decode(left);
  const b = decode(right);
  if (a.width !== b.width || a.height !== b.height) return 1;
  let changed = 0;
  for (let i = 0; i < a.data.length; i += 1) {
    if (a.data[i] !== b.data[i]) changed += 1;
  }
  return changed / a.data.length;
}

function decode(buf: Buffer): { width: number; height: number; data: Buffer } {
  let offset = 8;
  let width = 0;
  let height = 0;
  let colorType = 6;
  const chunks: Buffer[] = [];
  while (offset + 8 < buf.length) {
    const length = buf.readUInt32BE(offset);
    const type = buf.toString('ascii', offset + 4, offset + 8);
    const data = buf.subarray(offset + 8, offset + 8 + length);
    if (type === 'IHDR') {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      colorType = data[9] ?? 6;
    } else if (type === 'IDAT') chunks.push(data);
    else if (type === 'IEND') break;
    offset += 12 + length;
  }
  const channels = colorType === 6 ? 4 : 3;
  const raw = inflateSync(Buffer.concat(chunks));
  const stride = width * channels;
  const out = Buffer.alloc(height * stride);
  let src = 0;
  let prev = Buffer.alloc(stride);
  for (let y = 0; y < height; y += 1) {
    const filter = raw[src] ?? 0;
    src += 1;
    const row = Buffer.from(raw.subarray(src, src + stride));
    src += stride;
    for (let i = 0; i < stride; i += 1) {
      const left = i >= channels ? (row[i - channels] ?? 0) : 0;
      const up = prev[i] ?? 0;
      const upLeft = i >= channels ? (prev[i - channels] ?? 0) : 0;
      const value = row[i] ?? 0;
      if (filter === 1) row[i] = (value + left) & 255;
      else if (filter === 2) row[i] = (value + up) & 255;
      else if (filter === 3) row[i] = (value + Math.floor((left + up) / 2)) & 255;
      else if (filter === 4) row[i] = (value + paeth(left, up, upLeft)) & 255;
    }
    row.copy(out, y * stride);
    prev = row;
  }
  return { width, height, data: out };
}
