import { expect, test } from '@playwright/test';

test('marquee selects three clips and paste keeps offsets', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه ۲۰۰ کلیپ' }).click();
  const lane = page.getByTestId('timeline-scroll');
  const box = await lane.boundingBox();
  if (!box) throw new Error('lane missing');
  await page.mouse.move(box.x + 140, box.y + 50);
  await page.mouse.down();
  await page.mouse.move(box.x + 140 + 520, box.y + 70, { steps: 4 });
  await page.mouse.up();
  await expect(page.locator('[data-selected=1]')).toHaveCount(3);
});
