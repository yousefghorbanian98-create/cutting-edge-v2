/**
 * Probe a local video file with HTMLVideoElement (S-014).
 * Duration, size, and thumbnails come from the element. FPS is sampled from
 * frame callbacks because the element has no fps property.
 */

export interface MediaProbe {
  duration: number;
  width: number;
  height: number;
  fps: number | null;
  thumbnails: string[];
}

export function formatSeconds(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '—';
  const tenths = Math.round(seconds * 10) / 10;
  return `${tenths.toFixed(1)} ثانیه`;
}

function waitFor(video: HTMLVideoElement, event: 'loadeddata'): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => {
      cleanup();
      reject(new Error('خواندن ویدیو طول کشید'));
    }, 8000);
    const onOk = () => {
      cleanup();
      resolve();
    };
    const onError = () => {
      cleanup();
      reject(new Error('فایل ویدیو باز نشد'));
    };
    const cleanup = () => {
      window.clearTimeout(timer);
      video.removeEventListener(event, onOk);
      video.removeEventListener('error', onError);
    };
    video.addEventListener(event, onOk);
    video.addEventListener('error', onError);
  });
}

function seekTo(video: HTMLVideoElement, time: number): Promise<void> {
  const limit = Number.isFinite(video.duration) ? Math.max(video.duration - 0.04, 0) : 0;
  const target = Math.min(Math.max(time, 0), limit);
  if (Math.abs(video.currentTime - target) < 0.001) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => {
      cleanup();
      reject(new Error('جابه‌جایی در ویدیو طول کشید'));
    }, 4000);
    const onSeeked = () => {
      cleanup();
      resolve();
    };
    const onError = () => {
      cleanup();
      reject(new Error('جابه‌جایی در ویدیو ناموفق بود'));
    };
    const cleanup = () => {
      window.clearTimeout(timer);
      video.removeEventListener('seeked', onSeeked);
      video.removeEventListener('error', onError);
    };
    video.addEventListener('seeked', onSeeked);
    video.addEventListener('error', onError);
    video.currentTime = target;
  });
}

function drawFrame(video: HTMLVideoElement): string {
  const canvas = document.createElement('canvas');
  canvas.width = 160;
  canvas.height = 90;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('canvas در دسترس نیست');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.7);
}

async function captureThumbnails(video: HTMLVideoElement): Promise<string[]> {
  const duration = video.duration;
  const points = [0.08, 0.5, 0.9].map((ratio) => duration * ratio);
  const thumbs: string[] = [];
  for (const point of points) {
    await seekTo(video, point);
    thumbs.push(drawFrame(video));
  }
  return thumbs;
}

async function estimateFps(video: HTMLVideoElement): Promise<number | null> {
  if (typeof video.requestVideoFrameCallback !== 'function') return null;
  try {
    await video.play();
  } catch {
    return null;
  }
  const times: number[] = [];
  await new Promise<void>((resolve) => {
    const timer = window.setTimeout(resolve, 700);
    let left = 5;
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
  if (times.length < 2) return null;
  const first = times[0];
  const last = times[times.length - 1];
  if (first === undefined || last === undefined || last <= first) return null;
  return Math.round((times.length - 1) / (last - first));
}

export async function probeVideo(file: File): Promise<MediaProbe> {
  const url = URL.createObjectURL(file);
  const video = document.createElement('video');
  video.preload = 'auto';
  video.muted = true;
  video.playsInline = true;
  video.src = url;
  try {
    await waitFor(video, 'loadeddata');
    if (!Number.isFinite(video.duration) || video.duration <= 0 || video.videoWidth < 1) {
      throw new Error('متادیتای ویدیو خوانده نشد');
    }
    const thumbnails = await captureThumbnails(video);
    const fps = await estimateFps(video);
    return {
      duration: video.duration,
      width: video.videoWidth,
      height: video.videoHeight,
      fps,
      thumbnails,
    };
  } finally {
    video.removeAttribute('src');
    video.load();
    URL.revokeObjectURL(url);
  }
}
