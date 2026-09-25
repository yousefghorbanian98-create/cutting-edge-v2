import type { Clip, Track as TrackModel } from '@/domain/timeline';
import { trackIsActive } from '@/domain/tracks';
import { useTimelineStore } from '@/stores/timelineStore';
import { ClipView } from './ClipView';
import { TrackHeader } from './TrackHeader';

export function Track({
  track,
  clips,
  width,
  pxPerSecond,
}: {
  track: TrackModel;
  clips: Clip[];
  width: number;
  pxPerSecond: number;
}) {
  const active = useTimelineStore((state) => trackIsActive(state.sequence, track.id));
  return (
    <div
      className="grid grid-cols-[11rem_minmax(0,1fr)] border-b border-surface-border"
      data-testid="timeline-track"
      data-track-id={track.id}
      data-kind={track.kind}
      data-order={track.order}
      data-muted={track.muted ? '1' : '0'}
      data-solo={track.solo ? '1' : '0'}
      data-locked={track.locked ? '1' : '0'}
      data-active={active ? '1' : '0'}
    >
      <div data-testid="track-header" className="w-[11rem] min-w-[11rem] max-w-[11rem] overflow-hidden">
        <TrackHeader track={track} />
      </div>
      <div data-testid="timeline-lane" className="relative h-14 min-w-0" style={{ width }}>
        {clips.map((clip) => (
          <ClipView key={clip.id} clip={clip} pxPerSecond={pxPerSecond} />
        ))}
      </div>
    </div>
  );
}
