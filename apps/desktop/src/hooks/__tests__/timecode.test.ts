import { formatTimecode } from '@/hooks/usePlayback';
import { describe, expect, it } from 'vitest';

describe('timecode', () => {
  it('formats HH:MM:SS:FF at 30 and 60 fps', () => {
    expect(formatTimecode(0, 30)).toBe('00:00:00:00');
    expect(formatTimecode(10 / 30, 30)).toBe('00:00:00:10');
    expect(formatTimecode(10 / 60, 60)).toBe('00:00:00:10');
    expect(formatTimecode(61.5, 30)).toBe('00:01:01:15');
  });
});
