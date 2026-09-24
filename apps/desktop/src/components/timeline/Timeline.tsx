'use client';

import { usePlayback } from '@/hooks/usePlayback';
import { useTimelineStore } from '@/stores/timelineStore';
import { useMemo, useRef, useState } from 'react';
import { PlaybackBar, Playhead, scrubFromRuler } from './Playhead';
import { Ruler } from './Ruler';
import { Track } from './Track';
import { benchSequence, snapFixture } from './bench';
import { PX_PER_SECOND, contentWidth, visibleClips } from './window';

export function Timeline() {
  const sequence = useTimelineStore((state) => state.sequence);
  const reset = useTimelineStore((state) => state.reset);
  const { setTime } = usePlayback();
  const [scrollLeft, setScrollLeft] = useState(0);
  const [viewport, setViewport] = useState(800);
  const frame = useRef(0);
  const pending = useRef({ left: 0, width: 800 });
  const width = contentWidth(sequence.clips);
  const startSec = Math.max(0, scrollLeft / PX_PER_SECOND - 1);
  const endSec = (scrollLeft + viewport) / PX_PER_SECOND + 1;
  const shown = useMemo(
    () => visibleClips(sequence.clips, startSec, endSec),
    [sequence.clips, startSec, endSec]
  );
  const shownIds = new Set(shown.map((clip) => clip.id));

  return (
    <section aria-label="تایم‌لاین" className="mt-4" dir="ltr">
      <div className="mb-2 flex items-center justify-between gap-3">
        <h2 className="text-sm font-bold">تایم‌لاین</h2>
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => reset(benchSequence(200))}
        >
          نمونه ۲۰۰ کلیپ
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => reset(snapFixture())}
        >
          نمونه اسنپ
        </button>
      </div>
      <PlaybackBar />
      <div
        data-testid="timeline-scroll"
        data-total={sequence.clips.length}
        data-rendered={shown.length}
        className="relative overflow-x-auto rounded-md border border-surface-border bg-surface-raised"
        onScroll={(event) => {
          const target = event.currentTarget;
          pending.current = { left: target.scrollLeft, width: target.clientWidth };
          if (frame.current) return;
          frame.current = window.requestAnimationFrame(() => {
            frame.current = 0;
            setScrollLeft(pending.current.left);
            setViewport(pending.current.width);
          });
        }}
      >
        <Playhead />
        <Ruler
          startSec={startSec}
          endSec={endSec}
          width={width}
          onScrub={(event) => scrubFromRuler(event, setTime)}
        />
        {sequence.tracks
          .slice()
          .sort((a, b) => a.order - b.order)
          .map((track) => (
            <Track
              key={track.id}
              track={track}
              width={width}
              clips={sequence.clips.filter((clip) => clip.trackId === track.id && shownIds.has(clip.id))}
            />
          ))}
      </div>
    </section>
  );
}
