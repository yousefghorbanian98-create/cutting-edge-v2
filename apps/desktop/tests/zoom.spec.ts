import { expect, test } from '@playwright/test';

test('Ctrl+wheel at x=400 keeps the time and names fit minimap and slider-domain', async ({ page }) => {
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
  await scroller.evaluate((node, clientX) => {
    const rect = node.getBoundingClientRect();
    node.dispatchEvent(
      new WheelEvent('wheel', {
        deltaY: -120,
        ctrlKey: true,
        clientX,
        clientY: rect.top + 40,
        bubbles: true,
        cancelable: true,
      })
    );
  }, 400);
  const after = await read();
  expect(after.px).not.toBe(before.px);
  const cursorLockPx = Math.abs(before.time - after.time) * after.px;
  console.info(
    `EVIDENCE cursor-lock-px=${cursorLockPx} threshold=1 before-time=${before.time} after-time=${after.time} seed=none`
  );
  expect(cursorLockPx).toBeLessThanOrEqual(1);

  await page.getByRole('button', { name: 'اندازه سکانس' }).click();
  await expect(scroller).toHaveAttribute('data-fit', '1');
  const fitted = await scroller.evaluate((node) => ({
    scrollWidth: node.scrollWidth,
    clientWidth: node.clientWidth,
  }));
  console.info(
    `EVIDENCE scrollWidth=${fitted.scrollWidth} clientWidth=${fitted.clientWidth} fit-threshold=clientWidth+1 seed=none`
  );
  expect(fitted.scrollWidth).toBeLessThanOrEqual(fitted.clientWidth + 1);
  const minimap = page.getByTestId('timeline-minimap').locator('span');
  const viewportLeft = Number(await minimap.getAttribute('data-viewport-left'));
  const viewportWidth = Number(await minimap.getAttribute('data-viewport-width'));
  console.info(
    [
      'EVIDENCE metric=minimap fixture=sequence-sample',
      `viewport-left=${viewportLeft} viewport-width=${viewportWidth}`,
      'threshold=width>0 seed=none',
    ].join(' ')
  );
  expect(viewportWidth).toBeGreaterThan(0);
  const beforePx = Number(await scroller.getAttribute('data-px'));
  await page.getByRole('slider', { name: 'زوم' }).fill('200');
  await expect(scroller).toHaveAttribute('data-px', '200');
  const afterPx = Number(await scroller.getAttribute('data-px'));
  console.info(
    [
      'EVIDENCE metric=slider-domain fixture=sequence-sample',
      `before-px=${beforePx} after-px=${afterPx} target=200`,
      'threshold=exact seed=none',
    ].join(' ')
  );
  expect(afterPx).toBe(200);
  expect(afterPx).not.toBe(beforePx);
});
