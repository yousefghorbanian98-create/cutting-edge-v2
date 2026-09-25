/** Typed export presets (S-030). No raw command and no filter graph. */

export type ExportCodec = 'h264' | 'h265';

export interface ExportPreset {
  id: string;
  label: string;
  width: number;
  height: number;
  fps: 24 | 30 | 60;
  codec: ExportCodec;
}

export const EXPORT_PRESETS: ExportPreset[] = [
  { id: 'youtube-1080', label: 'YouTube 1080p', width: 1920, height: 1080, fps: 30, codec: 'h264' },
  { id: 'reels', label: 'Instagram Reels', width: 1080, height: 1920, fps: 30, codec: 'h264' },
  { id: 'tiktok', label: 'TikTok', width: 1080, height: 1920, fps: 30, codec: 'h264' },
  { id: 'shorts', label: 'Shorts', width: 1080, height: 1920, fps: 30, codec: 'h264' },
];

export const RESOLUTIONS = [
  { id: '720', width: 1280, height: 720 },
  { id: '1080', width: 1920, height: 1080 },
  { id: '4k', width: 3840, height: 2160 },
] as const;

export const FRAME_RATES = [24, 30, 60] as const;

export function estimateBytes(durationS: number, bitrateBps: number): number {
  if (!(durationS > 0) || !(bitrateBps > 0)) return 0;
  return Math.round((durationS * bitrateBps) / 8);
}

export function requestBody(
  preset: ExportPreset,
  sourceWidth: number
): {
  w: number;
  h: number;
  fps: number;
  codec: ExportCodec;
  upscale: boolean;
} {
  return {
    w: preset.width,
    h: preset.height,
    fps: preset.fps,
    codec: preset.codec,
    upscale: preset.width > sourceWidth,
  };
}
