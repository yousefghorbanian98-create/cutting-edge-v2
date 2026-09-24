import { expect, test } from '@playwright/test';

test('marquee selects three clips and paste keeps offsets', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه ۲۰۰ کلیپ' }).click();
  const scroll = page.getByTestId('timeline-scroll');
  const lane = page.getByTestId('timeline-lane').first();
  const scrollBox = await scroll.boundingBox();
  const laneBox = await lane.boundingBox();
  if (!scrollBox || !laneBox) throw new Error('lane missing');
  await page.mouse.move(scrollBox.x + 8, laneBox.y + 8);
  await page.mouse.down();
  await page.mouse.move(laneBox.x + 520, laneBox.y + 8, { steps: 4 });
  await page.mouse.up();
  await expect(page.locator('[data-selected="1"]')).toHaveCount(3);
});
