'use client';

import type { Track } from '@/domain/timeline';
import { useTimelineStore } from '@/stores/timelineStore';
import { useState } from 'react';

export function TrackHeader({ track }: { track: Track }) {
  const setTrackFlag = useTimelineStore((state) => state.setTrackFlag);
  const removeTrack = useTimelineStore((state) => state.removeTrack);
  const moveTrack = useTimelineStore((state) => state.moveTrack);
  const occupied = useTimelineStore((state) =>
    state.sequence.clips.some((clip) => clip.trackId === track.id)
  );
  const [reject, setReject] = useState<string | null>(null);

  function toggle(flag: 'muted' | 'solo' | 'locked') {
    setTrackFlag(track.id, flag, !track[flag]);
  }

  return (
    <div className="flex flex-col gap-1 border-e border-surface-border px-2 py-1 text-xs">
      <span className="text-sm">{track.name}</span>
      <div className="flex flex-wrap gap-1">
        <button
          type="button"
          className="rounded-md border border-surface-border px-1"
          aria-pressed={track.muted}
          onClick={() => toggle('muted')}
        >
          بی‌صدا
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-1"
          aria-pressed={track.solo}
          onClick={() => toggle('solo')}
        >
          سولو
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-1"
          aria-pressed={track.locked}
          onClick={() => toggle('locked')}
        >
          قفل
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-1"
          onClick={() => moveTrack(track.id, -1)}
        >
          بالا
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-1"
          onClick={() => moveTrack(track.id, 1)}
        >
          پایین
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-1"
          onClick={() => {
            const ok = removeTrack(track.id);
            setReject(ok ? null : occupied ? 'ترک کلیپ دارد' : 'حذف رد شد');
          }}
        >
          حذف
        </button>
      </div>
      {reject ? (
        <p role="alert" className="text-error">
          {reject}
        </p>
      ) : null}
    </div>
  );
}
