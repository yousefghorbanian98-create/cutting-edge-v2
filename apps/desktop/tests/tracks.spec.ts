import { type Page, expect, test } from '@playwright/test';

const AUDIBLE_RMS = 0.02;
const SILENT_RMS = 0.001;

async function analyserRms(page: Page): Promise<number> {
  return page.evaluate(() => {
    const meter = document.querySelector('[data-testid=track-audio]');
    const analyser = meter instanceof HTMLElement ? meter.__ceAnalyser : undefined;
    if (!analyser) return Number.NaN;
    const data = new Float32Array(analyser.fftSize);
    analyser.getFloatTimeDomainData(data);
    let sum = 0;
    for (const sample of data) sum += sample * sample;
    return Math.sqrt(sum / data.length);
  });
}

test('lock ignores a clip drag, and mute silences the audio analyser', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه اسنپ' }).click();
  const clip = page.locator('[data-clip-id=B]');
  await expect(clip).toHaveAttribute('data-start', '8000');
  await page.locator('[data-track-id=track-v1]').getByRole('button', { name: 'قفل' }).click();
  await expect(page.locator('[data-track-id=track-v1]')).toHaveAttribute('data-locked', '1');

  const box = await clip.boundingBox();
  if (!box) throw new Error('clip B has no box');
  const gripX = box.x + box.width / 2;
  const gripY = box.y + box.height / 2;
  await page.mouse.move(gripX, gripY);
  await page.mouse.down();
  await page.mouse.move(gripX + 180, gripY, { steps: 8 });
  await page.mouse.up();
  await expect(clip).toHaveAttribute('data-start', '8000');
  await expect(clip).toHaveAttribute('data-track', 'track-v1');

  await page.getByRole('button', { name: 'پخش', exact: true }).click();
  const meter = page.getByTestId('track-audio');
  await expect(meter).toHaveAttribute('data-capability', 'available');
  await expect(meter).toHaveAttribute('data-context-state', 'running', { timeout: 3_000 });
  await expect.poll(() => analyserRms(page), { timeout: 3_000 }).toBeGreaterThan(AUDIBLE_RMS);

  await page.locator('[data-track-id=track-a1]').getByRole('button', { name: 'بی‌صدا' }).click();
  await expect(page.locator('[data-track-id=track-a1]')).toHaveAttribute('data-muted', '1');
  await expect(page.locator('[data-track-id=track-a1]')).toHaveAttribute('data-active', '0');
  await expect.poll(() => analyserRms(page), { timeout: 3_000 }).toBeLessThan(SILENT_RMS);
});

test('adds a text track, reorders it, and refuses to remove a track that still has clips', async ({
  page,
}) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'ترک متن' }).click();
  const text = page.locator('[data-kind=text]');
  await expect(text).toHaveAttribute('data-order', '2');
  await text.getByRole('button', { name: 'بالا' }).click();
  await expect(text).toHaveAttribute('data-order', '1');

  await page.getByRole('button', { name: 'نمونه اسنپ' }).click();
  await page.locator('[data-track-id=track-v1]').getByRole('button', { name: 'برداشتن' }).click();
  await expect(page.locator('[data-track-id=track-v1]').getByRole('alert')).toContainText('ترک کلیپ دارد');
  await expect(page.locator('[data-track-id=track-v1]')).toHaveCount(1);
});
