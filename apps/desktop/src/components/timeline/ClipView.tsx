import type { Clip } from '@/domain/timeline';
import { PX_PER_SECOND, barsFor, msToSeconds } from './window';

export function ClipView({ clip }: { clip: Clip }) {
  const bars = barsFor(clip.id);
  const width = Math.max(8, msToSeconds(clip.duration) * PX_PER_SECOND - 4);
  return (
    <div
      data-testid="timeline-clip"
      data-clip-id={clip.id}
      className="absolute top-1 h-12 overflow-hidden rounded-md border border-surface-border bg-surface-overlay"
      style={{
        width,
        transform: `translate3d(${msToSeconds(clip.start) * PX_PER_SECOND}px, 0, 0)`,
      }}
    >
      <div className="h-4 bg-surface-hover" aria-hidden />
      <div className="flex h-8 items-end gap-px px-1" aria-hidden>
        {bars.map((height, index) => (
          <span
            key={`${clip.id}-${index}`}
            className="w-1 bg-energy-medium"
            style={{ height: `${height}%` }}
          />
        ))}
      </div>
    </div>
  );
}
