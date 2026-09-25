import { expect, test } from '@playwright/test';

const CHORDS = [
  'Control+b',
  'Control+c',
  'Control+v',
  'Control+d',
  'Control+z',
  'Control+Shift+z',
  'Delete',
  'Shift+Delete',
  'Control+k',
];

test('every registered shortcut fires once and the cheat sheet matches the registry', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه برش' }).click();
  for (const chord of CHORDS) {
    await page.keyboard.press(chord);
  }
  await page.keyboard.press('Shift+Slash');
  const counts = await page.getByTestId('shortcut-log').getAttribute('data-counts');
  const parsed = JSON.parse(counts ?? '{}') as Record<string, number>;
  for (const value of Object.values(parsed)) expect(value).toBe(1);
  const modal = page.getByTestId('shortcuts-modal');
  await expect(modal).toBeVisible();
  const listed = await modal.locator('[data-shortcut]').count();
  const registry = Number(await modal.getAttribute('data-count'));
  expect(listed).toBe(registry);
  expect(Object.keys(parsed)).toHaveLength(registry);
});
