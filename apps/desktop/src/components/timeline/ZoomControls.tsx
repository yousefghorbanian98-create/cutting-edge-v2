'use client';

import { MAX_PX, MIN_PX } from '@/domain/zoom';
import { useZoomStore } from '@/hooks/useZoom';

export function ZoomControls({
  seconds,
  viewport,
  onFit,
  onZoom,
}: {
  seconds: number;
  viewport: number;
  onFit: () => void;
  onZoom: (factor: number) => void;
}) {
  const px = useZoomStore((state) => state.pxPerSecond);
  const setPx = useZoomStore((state) => state.setPx);
  return (
    <div className="flex items-center gap-2" data-testid="zoom-controls">
      <button
        type="button"
        className="rounded-md border border-surface-border px-2 py-1 text-sm"
        onClick={() => onZoom(0.8)}
      >
        زوم کمتر
      </button>
      <label className="flex items-center gap-2 text-sm">
        زوم
        <input
          aria-label="زوم"
          type="range"
          min={MIN_PX}
          max={MAX_PX}
          value={px}
          onChange={(event) => setPx(Number(event.target.value))}
        />
      </label>
      <button
        type="button"
        className="rounded-md border border-surface-border px-2 py-1 text-sm"
        onClick={() => onZoom(1.25)}
      >
        زوم بیشتر
      </button>
      <button
        type="button"
        className="rounded-md border border-surface-border px-2 py-1 text-sm"
        onClick={onFit}
      >
        اندازه سکانس
      </button>
      <p className="text-xs text-white/60" data-testid="zoom-px">
        {Math.round(px)} px/s · {seconds.toFixed(1)}s / {viewport}px
      </p>
    </div>
  );
}

export function Minimap({
  content,
  viewport,
  scrollLeft,
}: {
  content: number;
  viewport: number;
  scrollLeft: number;
}) {
  const scale = content > 0 ? 160 / content : 1;
  const left = Math.max(0, scrollLeft * scale);
  const width = Math.max(4, Math.min(160, viewport * scale));
  return (
    <div
      data-testid="timeline-minimap"
      className="relative mt-2 h-3 w-40 rounded-sm bg-surface-overlay"
      aria-hidden
    >
      <span
        data-viewport-left={left}
        data-viewport-width={width}
        className="absolute top-0 h-3 rounded-sm bg-white/70"
        style={{ width, transform: `translate3d(${left}px, 0, 0)` }}
      />
    </div>
  );
}
