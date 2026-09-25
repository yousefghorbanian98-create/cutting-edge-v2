import { readFileSync } from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';
import { pixelDiffRatio } from '../tests/pngDiff';

interface ClipFixture {
  name: string;
  duration: number;
  b64: string;
}

const clips = JSON.parse(
  readFileSync(path.join(__dirname, '../tests/fixtures/media-clips.json'), 'utf8')
) as ClipFixture[];

test('import, arrange, trim, split, undo, and preview stay within 0.1% three times', async ({ page }) => {
  test.setTimeout(180_000);
  const shots: Buffer[] = [];
  for (let run = 0; run < 3; run += 1) {
    await page.goto('/editor');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    const wide = clips.find((item) => item.name === 'wide.mp4');
    if (!wide) throw new Error('wide fixture missing');
    await page.locator('[data-testid=media-drop]').evaluate((el, payload: ClipFixture) => {
      const bytes = Uint8Array.from(atob(payload.b64), (char) => char.charCodeAt(0));
      const transfer = new DataTransfer();
      transfer.items.add(new File([bytes], payload.name, { type: 'video/mp4' }));
      el.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: transfer }));
    }, wide);
    await expect(page.getByTestId('media-card')).toHaveCount(1, { timeout: 20_000 });
    await page.getByRole('button', { name: 'به تایم‌لاین' }).click();
    const clip = page.getByTestId('timeline-clip');
    await expect(clip).toHaveCount(1);
    const handle = clip.getByTestId('trim-out');
    const box = await handle.boundingBox();
    if (!box) throw new Error('trim handle missing');
    await page.mouse.move(box.x + 1, box.y + 4);
    await page.mouse.down();
    await page.mouse.move(box.x + 1 - 40, box.y + 4, { steps: 4 });
    await page.mouse.up();
    const ruler = page.getByTestId('timeline-ruler');
    const rulerBox = await ruler.boundingBox();
    if (!rulerBox) throw new Error('ruler missing');
    await page.mouse.click(rulerBox.x + 80, rulerBox.y + 8);
    await page.keyboard.press('Control+b');
    await page.keyboard.press('Control+z');
    await expect(page.getByTestId('timeline-clip')).toHaveCount(1);
    await expect(page.getByTestId('sequence-player')).toBeVisible();
    await page.evaluate(async () => {
      const active = document.activeElement;
      if (active instanceof HTMLElement) active.blur();
      await document.fonts.ready;
      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
      });
    });
    shots.push(await page.getByTestId('timeline-scroll').screenshot());
  }
  expect(pixelDiffRatio(shots[0] ?? Buffer.alloc(0), shots[1] ?? Buffer.alloc(0))).toBeLessThan(0.001);
  expect(pixelDiffRatio(shots[1] ?? Buffer.alloc(0), shots[2] ?? Buffer.alloc(0))).toBeLessThan(0.001);
});
