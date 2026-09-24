import { expect, test } from '@playwright/test';

test('a 4px drop snaps to the other clip end, and a video clip is rejected on audio', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه اسنپ' }).click();
  const clipB = page.locator('[data-clip-id=B]');
  const box = await clipB.boundingBox();
  if (!box) throw new Error('clip B has no box');
  const gripX = box.x + box.width / 2;
  const gripY = box.y + box.height / 2;
  await page.mouse.move(gripX, gripY);
  await page.mouse.down();
  await page.mouse.move(gripX - 304, gripY, { steps: 8 });
  await page.mouse.up();
  await expect(clipB).toHaveAttribute('data-start', '5000');

  const audio = page.locator('[data-track-id=track-a1]');
  const audioBox = await audio.boundingBox();
  if (!audioBox) throw new Error('audio track missing');
  const again = await clipB.boundingBox();
  if (!again) throw new Error('clip B missing after snap');
  const againX = again.x + again.width / 2;
  const againY = again.y + again.height / 2;
  await page.mouse.move(againX, againY);
  await page.mouse.down();
  await page.mouse.move(againX, audioBox.y + 8, { steps: 6 });
  await page.mouse.up();
  await expect(page.getByTestId('drag-reject')).toBeVisible();
  await expect(clipB).toHaveAttribute('data-track', 'track-v1');
});
