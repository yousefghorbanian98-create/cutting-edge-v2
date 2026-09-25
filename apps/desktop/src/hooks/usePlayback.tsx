'use client';

import { PX_PER_SECOND } from '@/components/timeline/window';
import { fpsFromMp4 } from '@/hooks/mp4Fps';
import { pauseTrackAudio, resumeTrackAudio } from '@/lib/trackAudio';
import { useTimelineStore } from '@/stores/timelineStore';
import {
  type ReactNode,
  type RefObject,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

export function formatTimecode(seconds: number, fps: number): string {
  const safeFps = fps > 0 ? Math.round(fps) : 30;
  const frame = Math.max(0, Math.round(seconds * safeFps));
  const ff = frame % safeFps;
  const total = Math.floor(frame / safeFps);
  const ss = total % 60;
  const mm = Math.floor(total / 60) % 60;
  const hh = Math.floor(total / 3600);
  const pad = (value: number) => String(value).padStart(2, '0');
  return `${pad(hh)}:${pad(mm)}:${pad(ss)}:${pad(ff)}`;
}

interface PlaybackValue {
  videoRef: RefObject<HTMLVideoElement | null>;
  headRef: RefObject<HTMLDivElement | null>;
  time: number;
  fps: number;
  playing: boolean;
  ready: boolean;
  loadFile: (file: File) => Promise<void>;
  toggle: () => void;
  pause: () => void;
  step: (direction: 1 | -1) => void;
  setTime: (seconds: number) => void;
  nudgeRate: (direction: -1 | 1) => void;
}

const PlaybackContext = createContext<PlaybackValue | null>(null);

function paint(head: HTMLDivElement | null, seconds: number) {
  if (!head) return;
  head.style.transform = `translate3d(${seconds * PX_PER_SECOND}px, 0, 0)`;
  head.dataset.time = String(seconds);
}

async function sampleFps(video: HTMLVideoElement): Promise<number> {
  if (typeof video.requestVideoFrameCallback !== 'function') return 30;
  await video.play().catch(() => undefined);
  const times: number[] = [];
  await new Promise<void>((resolve) => {
    const timer = window.setTimeout(resolve, 500);
    let left = 6;
    const step = (_now: number, meta: VideoFrameCallbackMetadata) => {
      times.push(meta.mediaTime);
      left -= 1;
      if (left <= 0) {
        window.clearTimeout(timer);
        resolve();
        return;
      }
      video.requestVideoFrameCallback(step);
    };
    video.requestVideoFrameCallback(step);
  });
  video.pause();
  video.currentTime = 0;
  const first = times[0];
  const last = times[times.length - 1];
  if (first === undefined || last === undefined || last <= first) return 30;
  const raw = Math.max(1, Math.round((times.length - 1) / (last - first)));
  for (const standard of [24, 25, 30, 60]) {
    if (Math.abs(raw - standard) <= 2) return standard;
  }
  return raw;
}

export function PlaybackProvider({ children }: { children: ReactNode }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const headRef = useRef<HTMLDivElement>(null);
  const [time, setTimeState] = useState(0);
  const [fps, setFps] = useState(30);
  const [playing, setPlaying] = useState(false);
  const [ready, setReady] = useState(false);
  const rate = useRef(0);

  const applyTime = useCallback((seconds: number) => {
    const video = videoRef.current;
    const next = Math.max(0, seconds);
    if (video) video.currentTime = next;
    paint(headRef.current, next);
    setTimeState(next);
  }, []);

  function pause() {
    const video = videoRef.current;
    pauseTrackAudio(useTimelineStore.getState().sequence);
    video?.pause();
    rate.current = 0;
    setPlaying(false);
    if (video) applyTime(video.currentTime);
  }

  function toggle() {
    const video = videoRef.current;
    if (!video) return;
    if (playing) {
      pause();
      return;
    }
    resumeTrackAudio(useTimelineStore.getState().sequence);
    rate.current = 1;
    video.playbackRate = 1;
    void video.play();
    setPlaying(true);
  }

  function step(direction: 1 | -1) {
    const video = videoRef.current;
    if (!video) return;
    pause();
    applyTime(video.currentTime + direction / fps);
  }

  function nudgeRate(direction: -1 | 1) {
    const video = videoRef.current;
    if (!video) return;
    const next = rate.current === 0 || Math.sign(rate.current) !== direction ? direction : rate.current * 2;
    rate.current = Math.max(-8, Math.min(8, next));
    if (rate.current > 0) {
      video.playbackRate = rate.current;
      void video.play();
      setPlaying(true);
    } else {
      video.pause();
      setPlaying(true);
    }
  }

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !playing || rate.current <= 0) return;
    let handle = 0;
    const onFrame = () => {
      const now = video.currentTime;
      paint(headRef.current, now);
      setTimeState(now);
      handle = video.requestVideoFrameCallback(onFrame);
    };
    handle = video.requestVideoFrameCallback(onFrame);
    return () => video.cancelVideoFrameCallback(handle);
  }, [playing]);

  useEffect(() => {
    if (!playing) return;
    let raf = 0;
    let last = performance.now();
    const tick = (now: number) => {
      if (rate.current < 0) {
        const video = videoRef.current;
        if (video) applyTime(video.currentTime + (rate.current * (now - last)) / 1000);
      }
      last = now;
      raf = window.requestAnimationFrame(tick);
    };
    raf = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(raf);
  }, [playing, applyTime]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const tag = (event.target as HTMLElement | null)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      if (event.key === 'j' || event.key === 'J') nudgeRate(-1);
      else if (event.key === 'k' || event.key === 'K') pause();
      else if (event.key === 'l' || event.key === 'L') nudgeRate(1);
      else if (event.key === 'ArrowLeft') step(-1);
      else if (event.key === 'ArrowRight') step(1);
      else return;
      event.preventDefault();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  async function loadFile(file: File) {
    const video = videoRef.current;
    if (!video) return;
    pause();
    video.src = URL.createObjectURL(file);
    await new Promise<void>((resolve, reject) => {
      video.onloadeddata = () => resolve();
      video.onerror = () => reject(new Error('پیش‌نمایش باز نشد'));
    });
    // Container rate, not the display sample. Headless Chromium presented the
    // 60fps fixture at 33fps and then 43fps; sampleFps must not overwrite a
    // parsed constant rate, and its ±2 snap stays unchanged.
    const parsed = fpsFromMp4(new Uint8Array(await file.arrayBuffer()));
    setFps(parsed ?? (await sampleFps(video)));
    setReady(true);
    applyTime(0);
  }

  return (
    <PlaybackContext.Provider
      value={{
        videoRef,
        headRef,
        time,
        fps,
        playing,
        ready,
        loadFile,
        toggle,
        pause,
        step,
        setTime: applyTime,
        nudgeRate,
      }}
    >
      {children}
    </PlaybackContext.Provider>
  );
}

export function usePlayback(): PlaybackValue {
  const value = useContext(PlaybackContext);
  if (!value) throw new Error('usePlayback خارج از PlaybackProvider');
  return value;
}
