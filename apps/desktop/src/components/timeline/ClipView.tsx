import type { Clip } from '@/domain/timeline';
import { TrimHandle } from './TrimHandle';
import { useClipDrag } from './useClipDrag';
import { PX_PER_SECOND, barsFor, msToSeconds } from './window';

export function ClipView({ clip }: { clip: Clip }) {
  const { onPointerDown, reject } = useClipDrag(clip.id);
  const bars = barsFor(clip.id);
  const width = Math.max(8, msToSeconds(clip.duration) * PX_PER_SECOND - 4);
  return (
    <div
      data-testid="timeline-clip"
      data-clip-id={clip.id}
      data-start={clip.start}
      data-duration={clip.duration}
      data-track={clip.trackId}
      onPointerDown={onPointerDown}
      className="absolute top-1 h-12 overflow-hidden rounded-md border border-surface-border bg-surface-overlay"
      style={{
        width,
        transform: `translate3d(${msToSeconds(clip.start) * PX_PER_SECOND}px, 0, 0)`,
      }}
    >
      <div className="h-4 bg-surface-hover" aria-hidden />
      {reject ? (
        <p role="alert" data-testid="drag-reject" className="absolute inset-x-0 bottom-0 text-xs text-error">
          {reject}
        </p>
      ) : null}
      <TrimHandle clipId={clip.id} edge="in" />
      <TrimHandle clipId={clip.id} edge="out" />
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
