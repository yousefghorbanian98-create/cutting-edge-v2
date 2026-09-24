import type { Clip, Track as TrackModel } from '@/domain/timeline';
import { ClipView } from './ClipView';

export function Track({ track, clips, width }: { track: TrackModel; clips: Clip[]; width: number }) {
  return (
    <div
      className="grid grid-cols-[8rem_1fr] border-b border-surface-border"
      data-testid="timeline-track"
      data-track-id={track.id}
    >
      <div className="border-e border-surface-border px-2 py-3 text-sm">{track.name}</div>
      <div data-testid="timeline-lane" className="relative h-14" style={{ width }}>
        {clips.map((clip) => (
          <ClipView key={clip.id} clip={clip} />
        ))}
      </div>
    </div>
  );
}
