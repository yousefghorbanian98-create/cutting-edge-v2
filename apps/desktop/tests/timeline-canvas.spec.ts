import { expect, test } from '@playwright/test';

interface TraceEvent {
  name?: string;
  dur?: number;
}

test('scrolling 200 clips stays inside the frame budget', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه ۲۰۰ کلیپ' }).click();
  await expect(page.getByTestId('timeline-scroll')).toHaveAttribute('data-total', '200');
  const rendered = Number(await page.getByTestId('timeline-scroll').getAttribute('data-rendered'));
  expect(rendered).toBeGreaterThan(0);
  expect(rendered).toBeLessThan(40);

  const session = await page.context().newCDPSession(page);
  const events: TraceEvent[] = [];
  session.on('Tracing.dataCollected', (payload) => {
    events.push(...payload.value);
  });
  await session.send('Tracing.start', {
    categories: 'devtools.timeline,disabled-by-default-devtools.timeline.frame',
  });

  const frames = await page.getByTestId('timeline-scroll').evaluate(async (el) => {
    let dropped = 0;
    let seen = 0;
    let x = 0;
    let last = performance.now();
    await new Promise<void>((resolve) => {
      const step = (now: number) => {
        const delta = now - last;
        seen += 1;
        if (delta > 16.7 * 1.5) dropped += Math.max(1, Math.round(delta / 16.7) - 1);
        last = now;
        x += 240;
        el.scrollLeft = x;
        if (x < 12000) requestAnimationFrame(step);
        else resolve();
      };
      requestAnimationFrame(step);
    });
    return { dropped, seen };
  });

  await new Promise<void>((resolve) => {
    session.once('Tracing.tracingComplete', () => resolve());
    void session.send('Tracing.end');
  });

  const longTasks = events.filter((event) => event.name === 'RunTask' && (event.dur ?? 0) > 50_000);
  const droppedFrames = events.filter((event) => event.name === 'DroppedFrame' || event.name === 'DropFrame');
  const drawn = events.filter((event) => event.name === 'DrawFrame' || event.name === 'BeginFrame');
  const cdpDroppedRatio =
    drawn.length === 0 ? frames.dropped / frames.seen : droppedFrames.length / drawn.length;

  expect(events.length).toBeGreaterThan(0);
  expect(longTasks).toHaveLength(0);
  expect(frames.seen).toBeGreaterThan(10);
  expect(frames.dropped / frames.seen).toBeLessThan(0.05);
  expect(cdpDroppedRatio).toBeLessThan(0.05);
});
