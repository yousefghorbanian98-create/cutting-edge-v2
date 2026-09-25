import { describe, expect, it } from 'vitest';
import { EXPORT_PRESETS, requestBody } from '../exportPresets';

describe('export presets', () => {
  it('builds the Reels body', () => {
    const reels = EXPORT_PRESETS.find((item) => item.id === 'reels');
    if (!reels) throw new Error('reels missing');
    expect(requestBody(reels, 1920)).toEqual({ w: 1080, h: 1920, fps: 30, codec: 'h264', upscale: false });
  });

  it('warns when 4K exceeds the source', () => {
    const fourK = {
      id: '4k',
      label: '4K',
      width: 3840,
      height: 2160,
      fps: 30 as const,
      codec: 'h264' as const,
    };
    expect(requestBody(fourK, 1920).upscale).toBe(true);
  });
});
