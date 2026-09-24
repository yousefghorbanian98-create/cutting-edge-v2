'use client';

import { formatTimecode, usePlayback } from '@/hooks/usePlayback';
import type { PointerEvent as ReactPointerEvent } from 'react';
import { PX_PER_SECOND } from './window';

export function PlaybackBar() {
  const { videoRef, time, fps, playing, ready, loadFile, toggle } = usePlayback();
  return (
    <div className="mb-2 flex flex-wrap items-center gap-3">
      <video
        ref={videoRef}
        data-testid="preview-video"
        data-fps={fps}
        data-ready={ready ? '1' : '0'}
        className="h-16 w-28 rounded-md bg-black"
        muted
        playsInline
        width={112}
        height={64}
      />
      <button
        type="button"
        className="rounded-md border border-surface-border px-2 py-1 text-sm"
        onClick={toggle}
      >
        {playing ? 'توقف' : 'پخش'}
      </button>
      <output data-testid="timecode" className="font-mono text-sm">
        {formatTimecode(time, fps)}
      </output>
      <label className="text-sm">
        پیش‌نمایش
        <input
          data-testid="preview-file"
          className="sr-only"
          type="file"
          accept="video/*"
          onChange={(event) => {
            const file = event.target.files?.[0];
            event.target.value = '';
            if (file) void loadFile(file);
          }}
        />
      </label>
    </div>
  );
}

export function Playhead() {
  const { headRef, setTime } = usePlayback();
  return (
    <div
      ref={headRef}
      data-testid="playhead"
      data-time="0"
      className="pointer-events-none absolute top-0 z-10 h-full w-px bg-info"
      style={{ transform: 'translate3d(0px, 0, 0)' }}
    >
      <span className="sr-only">پلی‌هد</span>
      <button
        type="button"
        className="pointer-events-auto absolute -top-1 h-3 w-3 -translate-x-1/2 rounded-full bg-info"
        aria-label="اسکراب پلی‌هد"
        onPointerDown={(event) => {
          const lane = event.currentTarget.closest('[data-testid=timeline-scroll]');
          if (!(lane instanceof HTMLElement)) return;
          event.currentTarget.setPointerCapture(event.pointerId);
          const move = (point: { clientX: number }) => {
            const rect = lane.getBoundingClientRect();
            setTime(Math.max(0, (point.clientX - rect.left + lane.scrollLeft) / PX_PER_SECOND));
          };
          move(event);
          const onMove = (next: PointerEvent) => move(next);
          const onUp = () => {
            event.currentTarget.removeEventListener('pointermove', onMove);
            event.currentTarget.removeEventListener('pointerup', onUp);
          };
          event.currentTarget.addEventListener('pointermove', onMove);
          event.currentTarget.addEventListener('pointerup', onUp);
        }}
      />
    </div>
  );
}

export function scrubFromRuler(event: ReactPointerEvent<HTMLDivElement>, setTime: (seconds: number) => void) {
  const lane = event.currentTarget.closest('[data-testid=timeline-scroll]');
  if (!(lane instanceof HTMLElement)) return;
  const target = event.currentTarget;
  target.setPointerCapture(event.pointerId);
  const move = (point: { clientX: number }) => {
    const rect = lane.getBoundingClientRect();
    setTime(Math.max(0, (point.clientX - rect.left + lane.scrollLeft) / PX_PER_SECOND));
  };
  move(event);
  const onMove = (next: PointerEvent) => move(next);
  const onUp = () => {
    target.removeEventListener('pointermove', onMove);
    target.removeEventListener('pointerup', onUp);
  };
  target.addEventListener('pointermove', onMove);
  target.addEventListener('pointerup', onUp);
}
