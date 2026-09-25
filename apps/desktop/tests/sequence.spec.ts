import { expect, test } from '@playwright/test';

test('sequence frame at 3.2s matches clip B at 5.2s and the cut gap stays under 100ms', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه سکانس' }).click();
  await page.getByLabel('زمان سکانس').fill('3.2');
  await expect(page.getByTestId('sequence-text')).toHaveCount(0);
  const ssim = await page.evaluate(() => {
    const player = document.querySelector('[data-testid=sequence-frame]');
    const thumb = document.querySelector('[data-testid=source-thumb]');
    if (!(player instanceof HTMLCanvasElement) || !(thumb instanceof HTMLCanvasElement)) return 0;
    const a = player.getContext('2d')?.getImageData(0, 0, player.width, player.height).data;
    const b = thumb.getContext('2d')?.getImageData(0, 0, thumb.width, thumb.height).data;
    if (!a || !b || a.length !== b.length) return 0;
    let acc = 0;
    const windows = 8;
    for (let y = 0; y + windows < player.height; y += windows) {
      for (let x = 0; x + windows < player.width; x += windows) {
        let meanA = 0;
        let meanB = 0;
        const count = windows * windows;
        for (let dy = 0; dy < windows; dy += 1) {
          for (let dx = 0; dx < windows; dx += 1) {
            const index = ((y + dy) * player.width + (x + dx)) * 4;
            meanA += a[index] ?? 0;
            meanB += b[index] ?? 0;
          }
        }
        meanA /= count;
        meanB /= count;
        let varA = 0;
        let varB = 0;
        let cov = 0;
        for (let dy = 0; dy < windows; dy += 1) {
          for (let dx = 0; dx < windows; dx += 1) {
            const index = ((y + dy) * player.width + (x + dx)) * 4;
            const va = (a[index] ?? 0) - meanA;
            const vb = (b[index] ?? 0) - meanB;
            varA += va * va;
            varB += vb * vb;
            cov += va * vb;
          }
        }
        varA /= count;
        varB /= count;
        cov /= count;
        const c1 = 6.5025;
        const c2 = 58.5225;
        acc +=
          ((2 * meanA * meanB + c1) * (2 * cov + c2)) /
          ((meanA * meanA + meanB * meanB + c1) * (varA + varB + c2));
      }
    }
    const cells = Math.floor(player.height / windows) * Math.floor(player.width / windows);
    return cells ? acc / cells : 0;
  });
  expect(ssim).toBeGreaterThan(0.9);

  await page.getByLabel('زمان سکانس').fill('2.9');
  await page.getByRole('button', { name: 'پخش سکانس' }).click();
  await expect
    .poll(async () => page.getByTestId('sequence-player').getAttribute('data-cut-gap-ms'), { timeout: 4_000 })
    .not.toBe('');
  const gap = Number(await page.getByTestId('sequence-player').getAttribute('data-cut-gap-ms'));
  expect(gap).toBeLessThan(100);
  await page.getByLabel('زمان سکانس').fill('1');
  await expect(page.getByTestId('sequence-text')).toHaveText('عنوان');
  await page.getByRole('button', { name: 'فشار کیفیت' }).click();
  await expect(page.getByTestId('sequence-player')).toHaveAttribute('data-quality', 'low');
  await expect(page.getByTestId('sequence-frame')).toBeVisible();
});
