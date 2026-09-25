import { expect, test } from '@playwright/test';

test('progress text increases and cancel shows a Persian toast without an output', async ({ page }) => {
  let percent = 10;
  let status = 'running';
  await page.route('http://127.0.0.1:8001/export', async (route) => {
    await route.fulfill({ json: { job_id: 'job-progress', status: 'queued' } });
  });
  await page.route('http://127.0.0.1:8001/jobs/job-progress', async (route) => {
    percent = Math.min(80, percent + 15);
    await route.fulfill({
      json: {
        id: 'job-progress',
        status,
        progress: percent / 100,
        percent,
        eta_s: 2,
        error: null,
        result: null,
        output_filename: null,
        partial_removed: false,
      },
    });
  });
  await page.route('http://127.0.0.1:8001/jobs/job-progress/cancel', async (route) => {
    status = 'cancelled';
    await route.fulfill({
      json: {
        id: 'job-progress',
        status: 'cancelled',
        progress: percent / 100,
        percent,
        eta_s: null,
        error: null,
        result: null,
        output_filename: null,
        partial_removed: true,
      },
    });
  });
  await page.goto('/editor');
  await page.getByRole('button', { name: 'ساخت خروجی' }).click();
  const label = page.getByTestId('export-percent');
  await expect.poll(async () => Number((await label.textContent())?.replace('٪', ''))).toBeGreaterThan(10);
  const first = Number((await label.textContent())?.replace('٪', ''));
  await expect.poll(async () => Number((await label.textContent())?.replace('٪', ''))).toBeGreaterThan(first);
  await page.getByRole('button', { name: 'لغو خروجی' }).click();
  await expect(page.getByTestId('export-toast')).toHaveText('خروجی لغو شد');
  await expect(page.getByTestId('export-progress')).toHaveAttribute('data-output-present', '0');
  await expect(page.getByTestId('export-history')).toContainText('job-progress');
});
