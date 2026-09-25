'use client';

import {
  EXPORT_PRESETS,
  type ExportCodec,
  FRAME_RATES,
  RESOLUTIONS,
  estimateBytes,
} from '@/domain/exportPresets';
import { postExport } from '@/lib/api';
import { useState } from 'react';

export function ExportDialog() {
  const [presetId, setPresetId] = useState('reels');
  const [width, setWidth] = useState(1080);
  const [height, setHeight] = useState(1920);
  const [fps, setFps] = useState<(typeof FRAME_RATES)[number]>(30);
  const [codec, setCodec] = useState<ExportCodec>('h264');
  const [crf, setCrf] = useState(23);
  const [name, setName] = useState('خروجی.mp4');
  const [sourceWidth, setSourceWidth] = useState(1920);
  const [body, setBody] = useState('');
  const [error, setError] = useState('');
  const upscale = width > sourceWidth;
  const bytes = estimateBytes(8, width >= 3840 ? 12_000_000 : 4_000_000);

  return (
    <section
      aria-label="خروجی"
      className="mt-4 rounded-md border border-surface-border p-3"
      data-testid="export-dialog"
    >
      <h2 className="text-sm font-bold">خروجی</h2>
      <div className="mt-2 flex flex-wrap gap-2">
        <label className="text-sm">
          پریست
          <select
            aria-label="پریست خروجی"
            className="ms-2 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={presetId}
            onChange={(event) => {
              const next = EXPORT_PRESETS.find((item) => item.id === event.target.value);
              if (!next) return;
              setPresetId(next.id);
              setWidth(next.width);
              setHeight(next.height);
              setFps(next.fps);
              setCodec(next.codec);
            }}
          >
            {EXPORT_PRESETS.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          رزولوشن
          <select
            aria-label="رزولوشن"
            className="ms-2 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={RESOLUTIONS.find((item) => item.width === width)?.id ?? 'custom'}
            onChange={(event) => {
              const next = RESOLUTIONS.find((item) => item.id === event.target.value);
              if (!next) return;
              setWidth(next.width);
              setHeight(next.height);
            }}
          >
            {RESOLUTIONS.map((item) => (
              <option key={item.id} value={item.id}>
                {item.id}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          فریم
          <select
            aria-label="فریم‌ریت"
            className="ms-2 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={fps}
            onChange={(event) => setFps(Number(event.target.value) as (typeof FRAME_RATES)[number])}
          >
            {FRAME_RATES.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          کدک
          <select
            aria-label="کدک"
            className="ms-2 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={codec}
            onChange={(event) => setCodec(event.target.value as ExportCodec)}
          >
            <option value="h264">H.264</option>
            <option value="h265">H.265</option>
          </select>
        </label>
        <label className="text-sm">
          CRF
          <input
            aria-label="CRF"
            type="number"
            min={1}
            max={51}
            className="ms-2 w-16 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={crf}
            onChange={(event) => setCrf(Number(event.target.value))}
          />
        </label>
        <label className="text-sm">
          نام فایل
          <input
            aria-label="نام فایل خروجی"
            className="ms-2 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </label>
        <label className="text-sm">
          عرض منبع
          <input
            aria-label="عرض منبع"
            type="number"
            className="ms-2 w-24 rounded-md border border-surface-border bg-surface-base px-2 py-1"
            value={sourceWidth}
            onChange={(event) => setSourceWidth(Number(event.target.value))}
          />
        </label>
      </div>
      <p className="mt-2 text-sm" data-testid="export-estimate">
        {new Intl.NumberFormat('fa').format(bytes)} بایت
      </p>
      {upscale ? (
        <p role="alert" data-testid="upscale-warning">
          منبع 4K نیست و بزرگ‌نمایی می‌شود
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-error">
          {error}
        </p>
      ) : null}
      <button
        type="button"
        className="mt-2 rounded-md border border-surface-border px-2 py-1 text-sm"
        onClick={() => {
          const payload = {
            w: width,
            h: height,
            fps,
            codec,
            clips: [],
            output_name: name,
            overwrite: false,
            crf,
            pace: 'fast' as const,
            mix: 'copy' as const,
            audio_codec: 'aac' as const,
          };
          setBody(JSON.stringify({ w: width, h: height, fps, codec }));
          void postExport({ body: payload }).then((result) => {
            if (result.error) setError('خروجی رد شد');
            const job = result.data?.job_id;
            if (job) window.dispatchEvent(new CustomEvent('ce-export-job', { detail: job }));
          });
        }}
      >
        ساخت خروجی
      </button>
      <pre data-testid="export-body">{body}</pre>
    </section>
  );
}
