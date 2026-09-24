'use client';

import type { Sequence } from '@/domain/timeline';
import { rollTrim, trimBy } from '@/domain/trim';
import { useTimelineStore } from '@/stores/timelineStore';
import { type PointerEvent as ReactPointerEvent, useEffect, useRef } from 'react';
import { PX_PER_SECOND } from './window';

export function TrimHandle({ clipId, edge }: { clipId: string; edge: 'in' | 'out' }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const clips = useTimelineStore((state) => state.sequence.clips);

  useEffect(() => {
    const canvas = canvasRef.current;
    const clip = clips.find((item) => item.id === clipId);
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx || !clip) return;
    const mark = edge === 'out' ? clip.start + clip.duration : clip.start;
    ctx.fillStyle = '#18181b';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#3b82f6';
    ctx.fillRect(mark % canvas.width, 0, 4, canvas.height);
  }, [clips, clipId, edge]);

  function onPointerDown(event: ReactPointerEvent<HTMLButtonElement>) {
    const clip = useTimelineStore.getState().sequence.clips.find((item) => item.id === clipId);
    if (!clip) return;
    const node = event.currentTarget;
    const originX = event.clientX;
    node.setPointerCapture(event.pointerId);
    const onUp = (next: PointerEvent) => {
      node.removeEventListener('pointerup', onUp);
      const delta = Math.round(((next.clientX - originX) / PX_PER_SECOND) * 1000);
      const signed = edge === 'out' ? delta : -delta;
      const sequence = useTimelineStore.getState().sequence;
      const rolled = next.shiftKey ? rollNeighbor(sequence, clipId, edge, signed) : null;
      const nextSequence = rolled ?? trimBy(sequence, clipId, edge, signed, next.altKey);
      useTimelineStore.getState().commitEdit(nextSequence);
    };
    node.addEventListener('pointerup', onUp);
    event.stopPropagation();
  }

  return (
    <button
      type="button"
      aria-label={edge === 'out' ? 'برش پایان' : 'برش آغاز'}
      data-testid={`trim-${edge}`}
      className={`absolute top-0 z-20 h-full w-2 bg-info ${edge === 'out' ? 'end-0' : 'start-0'}`}
      onPointerDown={onPointerDown}
    >
      <canvas ref={canvasRef} data-testid="trim-preview" width={32} height={16} className="sr-only" />
    </button>
  );
}

function rollNeighbor(
  sequence: Sequence,
  clipId: string,
  edge: 'in' | 'out',
  delta: number
): Sequence | null {
  const clip = sequence.clips.find((item) => item.id === clipId);
  if (!clip || edge !== 'out') return null;
  const right = sequence.clips.find(
    (item) => item.trackId === clip.trackId && item.start === clip.start + clip.duration
  );
  if (!right) return null;
  return rollTrim(sequence, clip.id, right.id, clip.start + clip.duration + delta);
}
