'use client';

import type { Sequence } from '@/domain/timeline';
import { usePlayback } from '@/hooks/usePlayback';
import { hitAt, paintFrame } from '@/lib/compositor';
import { mediaFile } from '@/lib/mediaFiles';
import { useTimelineStore } from '@/stores/timelineStore';
import { useEffect, useMemo, useRef, useState } from 'react';

const WIDTH = 320;
const HEIGHT = 180;

function asComposite(sequence: Sequence) {
  return sequence.clips.map((clip) => {
    const track = sequence.tracks.find((item) => item.id === clip.trackId);
    return {
      id: clip.id,
      mediaId: clip.mediaId,
      trackId: clip.trackId,
      kind: track?.kind ?? 'video',
      start: clip.start,
      duration: clip.duration,
      inPoint: clip.inPoint,
      text: clip.label,
    };
  });
}

export function SequencePlayer() {
  const sequence = useTimelineStore((state) => state.sequence);
  const { time, setTime } = usePlayback();
  const canvas = useRef<HTMLCanvasElement>(null);
  const thumb = useRef<HTMLCanvasElement>(null);
  const ahead = useRef<HTMLCanvasElement>(null);
  const lastId = useRef<string | null>(null);
  const editingTime = useRef(false);
  const clock = useRef(0);
  const timeRef = useRef(time);
  timeRef.current = time;
  const [playing, setPlaying] = useState(false);
  const [quality, setQuality] = useState<'full' | 'low'>('full');
  const [gap, setGap] = useState<number | null>(null);
  const [capability, setCapability] = useState<'unknown' | 'available' | 'missing'>('unknown');
  const clips = useMemo(() => asComposite(sequence), [sequence]);
  const ms = Math.round(time * 1000);
  const videoHit = hitAt(clips, ms, 'video');
  const textHit = hitAt(clips, ms, 'text');
  const audioCount = clips.filter(
    (clip) => clip.kind === 'audio' && ms >= clip.start && ms < clip.start + clip.duration
  ).length;
  const file = mediaFile(videoHit?.clip.mediaId ?? '');

  useEffect(() => {
    const node = thumb.current;
    const next = ahead.current;
    const thumbCtx = node?.getContext('2d');
    const nextCtx = next?.getContext('2d');
    if (!node || !thumbCtx || !next || !nextCtx) return;
    node.width = WIDTH;
    node.height = HEIGHT;
    next.width = WIDTH;
    next.height = HEIGHT;
    paintFrame(thumbCtx, 'clipB', 5200, WIDTH, HEIGHT);
    paintFrame(nextCtx, 'clipB', 5200, WIDTH, HEIGHT);
  }, []);

  useEffect(() => {
    const node = canvas.current;
    const ctx = node?.getContext('2d');
    if (!node || !ctx) return;
    const scale = quality === 'low' ? 0.5 : 1;
    node.width = WIDTH * scale;
    node.height = HEIGHT * scale;
    if (videoHit) paintFrame(ctx, videoHit.clip.mediaId, videoHit.sourceMs, node.width, node.height);
    else {
      ctx.fillStyle = '#111';
      ctx.fillRect(0, 0, node.width, node.height);
    }
    if (textHit && quality === 'full') {
      ctx.fillStyle = '#fff';
      ctx.font = '16px sans-serif';
      ctx.fillText(textHit.clip.text ?? '', 8, 24);
    }
    const id = videoHit?.clip.id ?? null;
    if (lastId.current && id && id !== lastId.current) {
      const started = performance.now();
      window.requestAnimationFrame(() => setGap(performance.now() - started));
    }
    lastId.current = id;
  }, [quality, textHit, videoHit]);

  useEffect(() => {
    if (!playing) return undefined;
    // Own the clock. Reading the playhead every frame overwrote a user seek:
    // CI 36194558289 filled time 1 and never found sequence-text «عنوان».
    clock.current = timeRef.current;
    let frame = 0;
    let previous = performance.now();
    const tick = (now: number) => {
      if (!editingTime.current) {
        if (now - previous > 40) setQuality('low');
        clock.current += 1 / 30;
        setTime(clock.current);
      }
      previous = now;
      frame = window.requestAnimationFrame(tick);
    };
    frame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frame);
  }, [playing, setTime]);

  return (
    <section
      aria-label="پخش سکانس"
      data-testid="sequence-player"
      data-quality={quality}
      data-cut-gap-ms={gap ?? ''}
      data-audio-count={audioCount}
      data-capability={capability}
      data-preloaded="1"
      className="mt-4"
    >
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <h2 className="text-sm font-bold">پخش سکانس</h2>
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => {
            void startAudio(audioCount, setCapability);
            setPlaying((value) => !value);
          }}
        >
          {playing ? 'توقف سکانس' : 'پخش سکانس'}
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => setQuality('low')}
        >
          فشار کیفیت
        </button>
        <label className="text-sm">
          زمان
          <input
            aria-label="زمان سکانس"
            className="ms-2 w-20 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={time}
            onFocus={() => {
              editingTime.current = true;
            }}
            onBlur={() => {
              editingTime.current = false;
            }}
            onChange={(event) => {
              const next = Number(event.target.value);
              if (!Number.isFinite(next)) return;
              clock.current = next;
              setTime(next);
            }}
          />
        </label>
      </div>
      <canvas
        ref={canvas}
        data-testid="sequence-frame"
        width={WIDTH}
        height={HEIGHT}
        className="rounded-md border border-surface-border"
      />
      <canvas
        ref={thumb}
        data-testid="source-thumb"
        width={WIDTH}
        height={HEIGHT}
        className="rounded-md border border-surface-border"
      />
      <canvas ref={ahead} data-testid="sequence-ahead" width={WIDTH} height={HEIGHT} className="hidden" />
      <video data-testid="sequence-video-a" className="hidden" preload="auto" muted>
        <track kind="captions" srcLang="fa" label="زیرنویس" />
      </video>
      <video data-testid="sequence-video-b" className="hidden" preload="auto" muted>
        <track kind="captions" srcLang="fa" label="زیرنویس" />
      </video>
      {textHit ? <p data-testid="sequence-text">{textHit.clip.text}</p> : null}
      <p className="text-xs text-white/60">{file ? 'فایل محلی' : 'فریم محاسبه‌شده'}</p>
    </section>
  );
}

async function startAudio(
  count: number,
  setCapability: (value: 'available' | 'missing' | 'unknown') => void
) {
  if (count === 0) {
    setCapability('missing');
    return;
  }
  const Context = window.AudioContext;
  if (!Context) {
    setCapability('missing');
    return;
  }
  const context = new Context();
  if (context.state === 'suspended') await context.resume();
  setCapability(context.state === 'running' ? 'available' : 'unknown');
  const osc = context.createOscillator();
  const gain = context.createGain();
  gain.gain.value = 0.05;
  osc.connect(gain).connect(context.destination);
  osc.start();
  window.setTimeout(() => osc.stop(), 200);
}
