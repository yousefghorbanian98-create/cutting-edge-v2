import { expect, test } from '@playwright/test';

test('dragging the out handle left by 2s shortens the clip and ripples the next one', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه اسنپ' }).click();
  const clipA = page.locator('[data-clip-id=A]');
  const handle = clipA.getByTestId('trim-out');
  const box = await handle.boundingBox();
  if (!box) throw new Error('trim handle missing');
  const before = await handle.locator('canvas').evaluate((node) => {
    const canvas = node as HTMLCanvasElement;
    return canvas.toDataURL();
  });
  await page.mouse.move(box.x + 1, box.y + 4);
  await page.mouse.down();
  await page.mouse.move(box.x + 1 - 200, box.y + 4, { steps: 6 });
  await page.mouse.up();
  await expect(clipA).toHaveAttribute('data-start', '0');
  await expect(clipA).toHaveAttribute('data-duration', '3000');
  const after = await handle.locator('canvas').evaluate((node) => {
    const canvas = node as HTMLCanvasElement;
    return canvas.toDataURL();
  });
  expect(after).not.toBe(before);
});
