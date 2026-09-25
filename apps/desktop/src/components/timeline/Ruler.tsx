import type { PointerEvent as ReactPointerEvent } from 'react';
import { PX_PER_SECOND } from './window';

export function Ruler({
  startSec,
  endSec,
  width,
  pxPerSecond = PX_PER_SECOND,
  onScrub,
}: {
  startSec: number;
  endSec: number;
  width: number;
  pxPerSecond?: number;
  onScrub: (event: ReactPointerEvent<HTMLDivElement>) => void;
}) {
  const ticks: number[] = [];
  const first = Math.max(0, Math.floor(startSec));
  const last = Math.ceil(endSec);
  for (let second = first; second <= last; second += 1) ticks.push(second);
  return (
    <div
      className="relative h-8 border-b border-surface-border"
      style={{ width }}
      data-testid="timeline-ruler"
      onPointerDown={onScrub}
    >
      {ticks.map((second) => (
        <span
          key={second}
          className="absolute top-1 text-xs text-white/60"
          style={{ transform: `translate3d(${second * pxPerSecond}px, 0, 0)` }}
        >
          {second}s
        </span>
      ))}
    </div>
  );
}
