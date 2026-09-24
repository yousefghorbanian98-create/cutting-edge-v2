import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';

interface PlaybackFixture {
  name: string;
  fps: number;
  b64: string;
}

const fixtures = JSON.parse(
  readFileSync(path.join(__dirname, 'fixtures/playback-clips.json'), 'utf8')
) as PlaybackFixture[];

async function load(page: import('@playwright/test').Page, fixture: PlaybackFixture) {
  const dir = test.info().outputDir;
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, fixture.name);
  writeFileSync(file, Buffer.from(fixture.b64, 'base64'));
  await page.goto('/editor');
  await page.getByTestId('preview-file').setInputFiles(file);
  await expect(page.getByTestId('preview-video')).toHaveAttribute('data-ready', '1', { timeout: 20_000 });
  await expect(page.getByTestId('preview-video')).toHaveAttribute('data-fps', String(fixture.fps));
}

test('playhead stays within one frame, and ten arrow steps match fps', async ({ page }) => {
  for (const fixture of fixtures) {
    await load(page, fixture);
    await page.getByRole('button', { name: 'پخش' }).click();
    await page.waitForFunction(() => {
      const video = document.querySelector('[data-testid=preview-video]');
      return video instanceof HTMLVideoElement && video.currentTime >= 3;
    });
    const drift = await page.evaluate(() => {
      const video = document.querySelector('[data-testid=preview-video]');
      const head = document.querySelector('[data-testid=playhead]');
      const lane = document.querySelector('[data-testid=timeline-scroll]');
      if (
        !(video instanceof HTMLVideoElement) ||
        !(head instanceof HTMLElement) ||
        !(lane instanceof HTMLElement)
      ) {
        return 999;
      }
      const x =
        head.getBoundingClientRect().left -
        lane.getBoundingClientRect().left -
        lane.clientLeft +
        lane.scrollLeft;
      return Math.abs(x / 100 - video.currentTime);
    });
    expect(drift).toBeLessThan(1 / fixture.fps);

    await page.keyboard.press('k');
    await page.evaluate(() => {
      const video = document.querySelector('[data-testid=preview-video]');
      if (video instanceof HTMLVideoElement) video.currentTime = 0;
    });
    await page.locator('body').click({ position: { x: 4, y: 4 } });
    for (let i = 0; i < 10; i += 1) await page.keyboard.press('ArrowRight');
    const current = await page
      .getByTestId('preview-video')
      .evaluate((node) => (node instanceof HTMLVideoElement ? node.currentTime : -1));
    expect(Math.abs(current - 10 / fixture.fps)).toBeLessThan(0.001);
  }
});
