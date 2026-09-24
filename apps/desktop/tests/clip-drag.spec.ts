import { expect, test } from '@playwright/test';

test('a 4px drop snaps to the other clip end, and a video clip is rejected on audio', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه اسنپ' }).click();
  const clipB = page.locator('[data-clip-id=B]');
  const box = await clipB.boundingBox();
  if (!box) throw new Error('clip B has no box');
  await page.mouse.move(box.x + 8, box.y + 8);
  await page.mouse.down();
  await page.mouse.move(box.x + 8 - 304, box.y + 8, { steps: 8 });
  await page.mouse.up();
  await expect(clipB).toHaveAttribute('data-start', '5000');

  const audio = page.locator('[data-track-id=track-a1]');
  const audioBox = await audio.boundingBox();
  if (!audioBox) throw new Error('audio track missing');
  const again = await clipB.boundingBox();
  if (!again) throw new Error('clip B missing after snap');
  await page.mouse.move(again.x + 8, again.y + 8);
  await page.mouse.down();
  await page.mouse.move(again.x + 8, audioBox.y + 8, { steps: 6 });
  await page.mouse.up();
  await expect(page.getByTestId('drag-reject')).toBeVisible();
  await expect(clipB).toHaveAttribute('data-track', 'track-v1');
});
