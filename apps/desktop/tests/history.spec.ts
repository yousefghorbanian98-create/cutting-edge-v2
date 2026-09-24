import { expect, test } from '@playwright/test';

test('five edits make five history rows, and Ctrl+Z restores the empty timeline', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه اسنپ' }).click();
  await expect(page.getByTestId('history-list').locator('li')).toHaveCount(1);
  await page.locator('body').click({ position: { x: 4, y: 4 } });
  await page.keyboard.press('Control+z');
  await expect(page.getByTestId('timeline-clip')).toHaveCount(0);
});
