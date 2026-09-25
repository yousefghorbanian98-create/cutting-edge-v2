'use client';

import type { TrackKind } from '@/domain/timeline';
import { usePlayback } from '@/hooks/usePlayback';
import { useSelectionStore } from '@/stores/selectionStore';
import { useTimelineStore } from '@/stores/timelineStore';
import { type PointerEvent as ReactPointerEvent, useMemo, useRef, useState } from 'react';
import { Marquee } from './Marquee';
import { PlaybackBar, Playhead, scrubFromRuler } from './Playhead';
import { Ruler } from './Ruler';
import { Track } from './Track';
import { TrackAudioMeter } from './TrackAudioMeter';
import { benchSequence, snapFixture, splitFixture } from './bench';
import { PX_PER_SECOND, contentWidth, visibleClips } from './window';

export function Timeline() {
  const sequence = useTimelineStore((state) => state.sequence);
  const reset = useTimelineStore((state) => state.reset);
  const { setTime } = usePlayback();
  const selectRect = useSelectionStore((state) => state.selectRect);
  const [marquee, setMarquee] = useState<{ x: number; y: number; width: number; height: number } | null>(
    null
  );
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
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => reset(splitFixture())}
        >
          نمونه برش
        </button>
        <TrackInsert kind="video" label="ترک ویدیو" />
        <TrackInsert kind="audio" label="ترک صدا" />
        <TrackInsert kind="text" label="ترک متن" />
      </div>
      <PlaybackBar />
      <TrackAudioMeter />
      <div
        data-testid="timeline-scroll"
        data-total={sequence.clips.length}
        data-rendered={shown.length}
        className="relative overflow-x-auto rounded-md border border-surface-border bg-surface-raised"
        onPointerDown={(event) => startMarquee(event, selectRect, setMarquee)}
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
        <Marquee rect={marquee} />
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

function TrackInsert({ kind, label }: { kind: TrackKind; label: string }) {
  const insertTrack = useTimelineStore((state) => state.insertTrack);
  return (
    <button
      type="button"
      className="rounded-md border border-surface-border px-2 py-1 text-sm"
      onClick={() => insertTrack(kind)}
    >
      {label}
    </button>
  );
}

function startMarquee(
  event: ReactPointerEvent<HTMLDivElement>,
  selectRect: (rect: { x: number; y: number; width: number; height: number }, additive: boolean) => void,
  setMarquee: (rect: { x: number; y: number; width: number; height: number } | null) => void
) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  if (target.closest('[data-testid=timeline-clip],button,[data-testid=timeline-ruler]')) return;
  const lane = event.currentTarget.querySelector('[data-testid=timeline-lane]');
  if (!(lane instanceof HTMLElement)) return;
  const originX = event.clientX - lane.getBoundingClientRect().left;
  const onMove = (next: PointerEvent) => {
    const x = next.clientX - lane.getBoundingClientRect().left + lane.scrollLeft;
    setMarquee({ x: originX, y: 0, width: x - originX, height: 40 });
  };
  const onUp = (next: PointerEvent) => {
    window.removeEventListener('pointermove', onMove);
    window.removeEventListener('pointerup', onUp);
    const x = next.clientX - lane.getBoundingClientRect().left;
    selectRect({ x: originX, y: 0, width: x - originX, height: 40 }, next.shiftKey);
    setMarquee(null);
  };
  window.addEventListener('pointermove', onMove);
  window.addEventListener('pointerup', onUp);
}
