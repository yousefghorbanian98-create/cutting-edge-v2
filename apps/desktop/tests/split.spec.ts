import { expect, test } from '@playwright/test';

test('Ctrl+B at 4.5s splits a 10s clip', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه برش' }).click();
  const ruler = page.getByTestId('timeline-ruler');
  const box = await ruler.boundingBox();
  if (!box) throw new Error('ruler missing');
  await page.mouse.click(box.x + 450, box.y + 8);
  await page.keyboard.press('Control+b');
  const durations = await page
    .getByTestId('timeline-clip')
    .evaluateAll((nodes) =>
      nodes.map((node) => Number(node.getAttribute('data-duration'))).sort((a, b) => a - b)
    );
  expect(durations).toEqual([4500, 5500]);
});
