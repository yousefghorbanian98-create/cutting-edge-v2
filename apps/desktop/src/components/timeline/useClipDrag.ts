'use client';

import { snapTargetsFor, snapTime } from '@/domain/snap';
import { usePlayback } from '@/hooks/usePlayback';
import { useTimelineStore } from '@/stores/timelineStore';
import { type PointerEvent as ReactPointerEvent, useState } from 'react';
import { PX_PER_SECOND } from './window';

export function useClipDrag(clipId: string) {
  const moveClip = useTimelineStore((state) => state.moveClip);
  const { time } = usePlayback();
  const [reject, setReject] = useState<string | null>(null);

  function onPointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    const sequence = useTimelineStore.getState().sequence;
    const clip = sequence.clips.find((item) => item.id === clipId);
    if (!clip) return;
    const source = sequence.tracks.find((item) => item.id === clip.trackId);
    if (source?.locked) {
      setReject('این ترک قفل است');
      return;
    }
    event.preventDefault();
    const node = event.currentTarget;
    const originX = event.clientX;
    const originY = event.clientY;
    const originStart = clip.start;
    const originTrack = clip.trackId;
    node.setPointerCapture(event.pointerId);

    const onMove = (next: PointerEvent) => {
      const lane = document.querySelector('[data-testid=timeline-scroll]');
      if (!(lane instanceof HTMLElement)) return;
      const dx = next.clientX - originX;
      const raw = Math.max(0, Math.round(originStart + (dx / PX_PER_SECOND) * 1000));
      const sequence = useTimelineStore.getState().sequence;
      const snapped = snapTime(
        raw,
        snapTargetsFor(
          sequence.clips,
          clipId,
          Math.round(time * 1000),
          sequence.markers.map((marker) => marker.time)
        ),
        PX_PER_SECOND,
        8,
        next.shiftKey
      );
      const track = trackAt(
        next.clientY,
        originY,
        originTrack,
        sequence.tracks.map((item) => item.id)
      );
      node.dataset.previewStart = String(snapped);
      node.dataset.previewTrack = track;
    };

    const onUp = () => {
      node.removeEventListener('pointermove', onMove);
      node.removeEventListener('pointerup', onUp);
      const start = Number(node.dataset.previewStart ?? originStart);
      const trackId = node.dataset.previewTrack ?? originTrack;
      const ok = moveClip(clipId, start, trackId);
      setReject(ok || trackId === originTrack ? null : 'این کلیپ روی این ترک نمی‌نشیند');
    };

    event.currentTarget.addEventListener('pointermove', onMove);
    event.currentTarget.addEventListener('pointerup', onUp);
  }

  return { onPointerDown, reject };
}

function trackAt(clientY: number, originY: number, originTrack: string, trackIds: string[]): string {
  const row = document.querySelector('[data-testid=timeline-track]');
  const height = row instanceof HTMLElement ? row.getBoundingClientRect().height : 56;
  const delta = Math.round((clientY - originY) / height);
  const index = trackIds.indexOf(originTrack);
  const next = trackIds[Math.min(trackIds.length - 1, Math.max(0, index + delta))];
  return next ?? originTrack;
}
