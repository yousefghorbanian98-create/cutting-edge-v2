import { expect, test } from '@playwright/test';

test('Ctrl+wheel at x=400 keeps the time, and fit shows the sequence', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه برش' }).click();
  const scroller = page.getByTestId('timeline-scroll');
  const box = await scroller.boundingBox();
  if (!box) throw new Error('timeline missing');
  expect(box.x).toBeLessThan(400);
  expect(box.x + box.width).toBeGreaterThan(400);

  const read = async () => {
    return scroller.evaluate((node, clientX) => {
      const el = node as HTMLElement;
      const rect = el.getBoundingClientRect();
      const px = Number(el.dataset.px);
      const scroll = el.scrollLeft;
      const cursor = clientX - rect.left;
      return { px, scroll, time: (scroll + cursor) / px, cursor };
    }, 400);
  };

  await page.mouse.move(400, box.y + 40);
  const before = await read();
  await page.keyboard.down('Control');
  await page.mouse.wheel(0, -120);
  await page.keyboard.up('Control');
  const after = await read();
  expect(after.px).not.toBe(before.px);
  expect(Math.abs(before.time - after.time) * after.px).toBeLessThanOrEqual(1);

  await page.getByRole('button', { name: 'اندازه سکانس' }).click();
  await expect(scroller).toHaveAttribute('data-fit', '1');
  const fitted = await scroller.evaluate((node) => ({
    scrollWidth: node.scrollWidth,
    clientWidth: node.clientWidth,
  }));
  expect(fitted.scrollWidth).toBeLessThanOrEqual(fitted.clientWidth + 1);
  await expect(page.getByTestId('timeline-minimap')).toBeVisible();
  await expect(page.getByRole('slider', { name: 'زوم' })).toBeVisible();
});
