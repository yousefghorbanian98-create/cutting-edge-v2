import { expect, test } from '@playwright/test';

test('Reels preset posts the typed body and 4K warns on a smaller source', async ({ page }) => {
  let body: {
    w?: number;
    h?: number;
    fps?: number;
    codec?: string;
    raw_command?: string;
    filter_graph?: string;
  } = {};
  await page.route('http://127.0.0.1:8001/export', async (route) => {
    body = route.request().postDataJSON();
    await route.fulfill({ json: { job_id: 'job-reels', status: 'queued' } });
  });
  await page.goto('/editor');
  await page.getByLabel('پریست خروجی').selectOption('reels');
  await page.getByRole('button', { name: 'ساخت خروجی' }).click();
  await expect.poll(() => body.w).toBe(1080);
  expect(body).toMatchObject({ w: 1080, h: 1920, fps: 30, codec: 'h264' });
  expect(body.raw_command).toBeUndefined();
  expect(body.filter_graph).toBeUndefined();

  await page.getByLabel('عرض منبع').fill('1920');
  await page.getByLabel('رزولوشن').selectOption('4k');
  await expect(page.getByTestId('upscale-warning')).toBeVisible();
});
