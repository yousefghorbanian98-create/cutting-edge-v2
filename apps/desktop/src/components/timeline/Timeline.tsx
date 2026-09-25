'use client';

import type { TrackKind } from '@/domain/timeline';
import { sheetWidth } from '@/domain/zoom';
import { usePlayback } from '@/hooks/usePlayback';
import { useZoomStore } from '@/hooks/useZoom';
import { useSelectionStore } from '@/stores/selectionStore';
import { useTimelineStore } from '@/stores/timelineStore';
import { type PointerEvent as ReactPointerEvent, useEffect, useMemo, useRef, useState } from 'react';
import { Marquee } from './Marquee';
import { PlaybackBar, Playhead, scrubFromRuler } from './Playhead';
import { Ruler } from './Ruler';
import { Track } from './Track';
import { TrackAudioMeter } from './TrackAudioMeter';
import { Minimap, ZoomControls } from './ZoomControls';
import { benchSequence, sequenceFixture, snapFixture, splitFixture } from './bench';
import { contentWidth, visibleClips } from './window';

export function Timeline() {
  const sequence = useTimelineStore((state) => state.sequence);
  const reset = useTimelineStore((state) => state.reset);
  const { setTime } = usePlayback();
  const selectRect = useSelectionStore((state) => state.selectRect);
  const [marquee, setMarquee] = useState<{ x: number; y: number; width: number; height: number } | null>(
    null
  );
  const px = useZoomStore((state) => state.pxPerSecond);
  const zoomBy = useZoomStore((state) => state.zoomBy);
  const fitTo = useZoomStore((state) => state.fitTo);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [viewport, setViewport] = useState(800);
  const frame = useRef(0);
  const scroller = useRef<HTMLDivElement>(null);
  const sheet = useRef<HTMLDivElement>(null);
  const clipsRef = useRef(sequence.clips);
  clipsRef.current = sequence.clips;
  const pending = useRef({ left: 0, width: 800 });
  const width = contentWidth(sequence.clips, px);
  const seconds = Math.max(1, width / px);
  const startSec = Math.max(0, scrollLeft / px - 1);
  const endSec = (scrollLeft + viewport) / px + 1;
  const shown = useMemo(
    () => visibleClips(sequence.clips, startSec, endSec),
    [sequence.clips, startSec, endSec]
  );
  const shownIds = new Set(shown.map((clip) => clip.id));

  useEffect(() => {
    const node = scroller.current;
    if (!node) return undefined;
    const onWheel = (event: WheelEvent) => {
      if (!event.ctrlKey) {
        node.scrollLeft += event.deltaY;
        return;
      }
      event.preventDefault();
      const rect = node.getBoundingClientRect();
      const cursorX = event.clientX - rect.left;
      const next = zoomBy(node.scrollLeft, cursorX, event.deltaY < 0 ? 1.25 : 0.8);
      const sequenceWidth = contentWidth(clipsRef.current, next.pxPerSecond);
      if (sheet.current) {
        sheet.current.style.width = `${sheetWidth(sequenceWidth, node.clientWidth, next.scrollLeft)}px`;
      }
      node.dataset.px = String(next.pxPerSecond);
      node.scrollLeft = next.scrollLeft;
    };
    node.addEventListener('wheel', onWheel, { passive: false });
    return () => node.removeEventListener('wheel', onWheel);
  }, [zoomBy]);

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
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => reset(sequenceFixture())}
        >
          نمونه سکانس
        </button>
      </div>
      <ZoomControls
        seconds={seconds}
        viewport={viewport}
        onZoom={(factor) => {
          const node = scroller.current;
          if (!node) return;
          const next = zoomBy(node.scrollLeft, 400, factor);
          node.scrollLeft = next.scrollLeft;
        }}
        onFit={() => {
          const node = scroller.current;
          if (!node) return;
          const view = node.clientWidth || viewport;
          const next = fitTo(seconds, view);
          const fitted = contentWidth(sequence.clips, next.pxPerSecond);
          if (sheet.current) sheet.current.style.width = `${fitted}px`;
          node.scrollLeft = next.scrollLeft;
          node.dataset.px = String(next.pxPerSecond);
          node.dataset.fit = fitted <= view + 1 ? '1' : '0';
        }}
      />
      <Minimap content={width} viewport={viewport} scrollLeft={scrollLeft} />
      <PlaybackBar />
      <TrackAudioMeter />
      <div
        ref={scroller}
        data-testid="timeline-scroll"
        data-total={sequence.clips.length}
        data-rendered={shown.length}
        data-px={px}
        data-scroll={scrollLeft}
        data-total-width={width}
        data-fit={width <= viewport + 1 ? '1' : '0'}
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
        <div ref={sheet} className="relative" style={{ width }}>
          <Playhead />
          <Marquee rect={marquee} />
          <Ruler
            startSec={startSec}
            endSec={endSec}
            width={width}
            pxPerSecond={px}
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
                pxPerSecond={px}
                clips={sequence.clips.filter((clip) => clip.trackId === track.id && shownIds.has(clip.id))}
              />
            ))}
        </div>
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
