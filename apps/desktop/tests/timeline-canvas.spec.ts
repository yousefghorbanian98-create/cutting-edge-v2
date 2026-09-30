import { expect, test } from '@playwright/test';

interface TraceEvent {
  name?: string;
  dur?: number;
}

test('scrolling 200 clips names RunTask ruler and waveform inside the frame budget', async ({ page }) => {
  await page.goto('/editor');
  await page.getByRole('button', { name: 'نمونه ۲۰۰ کلیپ' }).click();
  await expect(page.getByTestId('timeline-scroll')).toHaveAttribute('data-total', '200');
  const rendered = Number(await page.getByTestId('timeline-scroll').getAttribute('data-rendered'));
  expect(rendered).toBeGreaterThan(0);
  expect(rendered).toBeLessThan(40);

  const ruler = await page.getByTestId('timeline-ruler').evaluate((node) => {
    const ticks = [...node.querySelectorAll('span')];
    const translated = ticks.filter((tick) =>
      (tick.getAttribute('style') ?? '').includes('translate3d')
    ).length;
    return { ticks: ticks.length, translated };
  });
  console.info(
    [
      'EVIDENCE metric=ruler fixture=bench-200',
      `tick-count=${ruler.ticks} translated=${ruler.translated}`,
      'threshold=tick-count>0 seed=none',
    ].join(' ')
  );
  expect(ruler.ticks).toBeGreaterThan(0);
  expect(ruler.translated).toBe(ruler.ticks);

  const waveform = await page.getByTestId('waveform-bars').evaluateAll((nodes) =>
    nodes.map((node) => Number(node.getAttribute('data-count')))
  );
  const bars = waveform.reduce((sum, count) => sum + count, 0);
  console.info(
    [
      'EVIDENCE metric=waveform fixture=bench-200',
      `rendered-clips=${waveform.length} bars=${bars} bars-per-clip=16`,
      'threshold=count=16 seed=none',
    ].join(' ')
  );
  expect(waveform.length).toBeGreaterThan(0);
  expect(waveform.every((count) => count === 16)).toBe(true);

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

  const runTasks = events.filter((event) => event.name === 'RunTask');
  const longTasks = runTasks.filter((event) => (event.dur ?? 0) > 50_000);
  const maxDurUs = runTasks.reduce((max, event) => Math.max(max, event.dur ?? 0), 0);
  const droppedFrames = events.filter((event) => event.name === 'DroppedFrame' || event.name === 'DropFrame');
  const drawn = events.filter((event) => event.name === 'DrawFrame' || event.name === 'BeginFrame');
  const cdpDroppedRatio =
    drawn.length === 0 ? frames.dropped / frames.seen : droppedFrames.length / drawn.length;

  expect(events.length).toBeGreaterThan(0);
  console.info(
    [
      'EVIDENCE metric=runtask fixture=bench-200',
      `measured-long-count=${longTasks.length} max-dur-us=${maxDurUs}`,
      'threshold=<=50ms threshold-us=<=50000 seed=none',
    ].join(' ')
  );
  expect(longTasks).toHaveLength(0);
  expect(maxDurUs).toBeLessThanOrEqual(50_000);
  expect(frames.seen).toBeGreaterThan(10);
  console.info(
    `EVIDENCE fixture=bench-200 rendered=${rendered} rendered-threshold=<40 frames-seen=${frames.seen} dropped=${frames.dropped} drop-ratio=${frames.dropped / frames.seen} cdp-drop-ratio=${cdpDroppedRatio} threshold=0.05 seed=none`
  );
  expect(frames.dropped / frames.seen).toBeLessThan(0.05);
  expect(cdpDroppedRatio).toBeLessThan(0.05);
});
