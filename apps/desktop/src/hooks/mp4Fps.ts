/** Read a constant video frame rate from an MP4 container. Display sampling is not fps. */

const STANDARDS = [24, 25, 30, 50, 60];

export function fpsFromMp4(bytes: Uint8Array): number | null {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const timing = videoTiming(view, 0, bytes.byteLength);
  if (!timing || timing.timescale <= 0 || timing.sampleDelta <= 0) return null;
  const raw = timing.timescale / timing.sampleDelta;
  if (!Number.isFinite(raw) || raw <= 0) return null;
  for (const standard of STANDARDS) {
    if (Math.abs(raw - standard) <= 0.51) return standard;
  }
  return Math.round(raw);
}

function videoTiming(
  view: DataView,
  start: number,
  end: number
): { timescale: number; sampleDelta: number } | null {
  let offset = start;
  while (offset + 8 <= end) {
    const size = view.getUint32(offset);
    const type = fourcc(view, offset + 4);
    if (size < 8 || offset + size > end) break;
    if (type === 'moov') {
      const found = videoTiming(view, offset + 8, offset + size);
      if (found) return found;
    } else if (type === 'trak') {
      const trak = readTrak(view, offset + 8, offset + size);
      if (trak.handler === 'vide' && trak.timescale && trak.sampleDelta) {
        return { timescale: trak.timescale, sampleDelta: trak.sampleDelta };
      }
    }
    offset += size;
  }
  return null;
}

function readTrak(
  view: DataView,
  start: number,
  end: number
): { handler?: string; timescale?: number; sampleDelta?: number } {
  const found: { handler?: string; timescale?: number; sampleDelta?: number } = {};
  let offset = start;
  while (offset + 8 <= end) {
    const size = view.getUint32(offset);
    const type = fourcc(view, offset + 4);
    if (size < 8 || offset + size > end) break;
    if (type === 'mdia' || type === 'minf' || type === 'stbl') {
      const nested = readTrak(view, offset + 8, offset + size);
      found.handler ??= nested.handler;
      found.timescale ??= nested.timescale;
      found.sampleDelta ??= nested.sampleDelta;
    } else if (type === 'hdlr' && offset + 20 <= end) {
      found.handler = fourcc(view, offset + 16);
    } else if (type === 'mdhd' && view.getUint8(offset + 8) === 0 && offset + 24 <= end) {
      found.timescale = view.getUint32(offset + 20);
    } else if (type === 'stts' && offset + 24 <= end && view.getUint32(offset + 12) > 0) {
      found.sampleDelta = view.getUint32(offset + 20);
    }
    offset += size;
  }
  return found;
}

function fourcc(view: DataView, offset: number): string {
  return String.fromCharCode(
    view.getUint8(offset),
    view.getUint8(offset + 1),
    view.getUint8(offset + 2),
    view.getUint8(offset + 3)
  );
}
