import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fpsFromMp4 } from '@/hooks/mp4Fps';
import { describe, expect, it } from 'vitest';

describe('mp4 fps', () => {
  it('reads 30 and 60 from the playback fixtures, not a display sample', () => {
    const here = dirname(fileURLToPath(import.meta.url));
    const fixtures = JSON.parse(
      readFileSync(resolve(here, '../../../tests/fixtures/playback-clips.json'), 'utf8')
    ) as { name: string; fps: number; b64: string }[];
    for (const fixture of fixtures) {
      const bytes = Uint8Array.from(Buffer.from(fixture.b64, 'base64'));
      expect(fpsFromMp4(bytes), fixture.name).toBe(fixture.fps);
    }
  });
});
