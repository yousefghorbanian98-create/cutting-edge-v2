import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';

interface ClipFixture {
  name: string;
  duration: number;
  b64: string;
}

const clips = JSON.parse(
  readFileSync(path.join(__dirname, 'fixtures/media-clips.json'), 'utf8')
) as ClipFixture[];

test.beforeEach(async ({ page }) => {
  await page.goto('/editor');
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

test('drop three fixtures, then a rename survives reload', async ({ page }) => {
  await page.locator('[data-testid=media-drop]').evaluate((el, payload: ClipFixture[]) => {
    const transfer = new DataTransfer();
    for (const clip of payload) {
      const bytes = Uint8Array.from(atob(clip.b64), (char) => char.charCodeAt(0));
      transfer.items.add(new File([bytes], clip.name, { type: 'video/mp4' }));
    }
    el.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: transfer }));
  }, clips);

  await expect(page.getByTestId('media-card')).toHaveCount(3, { timeout: 20_000 });
  await expect(page.locator('[data-status=ready]')).toHaveCount(3, { timeout: 20_000 });

  const durations = await page
    .getByTestId('media-duration')
    .evaluateAll((nodes) => nodes.map((node) => Number(node.getAttribute('data-duration'))));
  for (const clip of clips) {
    expect(durations.some((value) => Math.abs(value - clip.duration) <= 0.1)).toBe(true);
  }
  const names = await page
    .getByTestId('media-name')
    .evaluateAll((nodes) => nodes.map((node) => (node as HTMLInputElement).value));
  expect(names).toContain('کلیپ تمرین ۱.mp4');

  const variances = await page.getByTestId('media-thumb').evaluateAll((nodes) =>
    nodes.map((node) => {
      const img = node as HTMLImageElement;
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth || 160;
      canvas.height = img.naturalHeight || 90;
      const ctx = canvas.getContext('2d');
      if (!ctx) return 0;
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      let sum = 0;
      const pixels = data.length / 4;
      for (let i = 0; i < data.length; i += 4) sum += data[i] ?? 0;
      const mean = sum / pixels;
      let variance = 0;
      for (let i = 0; i < data.length; i += 4) {
        const delta = (data[i] ?? 0) - mean;
        variance += delta * delta;
      }
      return variance / pixels;
    })
  );
  expect(variances).toHaveLength(3);
  for (const variance of variances) expect(variance).toBeGreaterThan(0);

  await page.locator('[data-testid=media-name]').first().fill('نام جدید');
  await page.reload();
  await expect(page.locator('[data-testid=media-name]').first()).toHaveValue('نام جدید');

  await page.getByTestId('media-search').fill('نام جدید');
  await expect(page.getByTestId('media-card')).toHaveCount(1);
  await page.getByRole('button', { name: 'حذف' }).click();
  await expect(page.getByTestId('media-card')).toHaveCount(0);
});

test('the file dialog imports a Persian-named clip', async ({ page }) => {
  const persian = clips[0];
  if (!persian) throw new Error('fixture missing');
  const dir = test.info().outputDir;
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, persian.name);
  writeFileSync(file, Buffer.from(persian.b64, 'base64'));
  await page.getByTestId('media-file').setInputFiles(file);
  await expect(page.locator('[data-status=ready]')).toHaveCount(1, { timeout: 20_000 });
  await expect(page.locator('[data-testid=media-name]')).toHaveValue(persian.name);
});
