'use client';

import { formatSeconds, probeVideo } from '@/lib/probe';
import { readSnapshot, useMediaStore } from '@/stores/mediaStore';
import { useEffect, useRef } from 'react';

async function importFiles(files: File[]) {
  const { addPending, complete, fail } = useMediaStore.getState();
  for (const file of files) {
    const id = crypto.randomUUID();
    addPending(id, file.name);
    try {
      complete(id, await probeVideo(file));
    } catch (err) {
      fail(id, err instanceof Error ? err.message : 'خواندن فایل ناموفق بود');
    }
  }
}

export function MediaBin() {
  const zoneRef = useRef<HTMLDivElement>(null);
  const items = useMediaStore((state) => state.items);
  const query = useMediaStore((state) => state.query);
  const rename = useMediaStore((state) => state.rename);
  const remove = useMediaStore((state) => state.remove);
  const setQuery = useMediaStore((state) => state.setQuery);
  const hydrate = useMediaStore((state) => state.hydrate);

  useEffect(() => {
    const saved = readSnapshot();
    if (saved && saved.items.length > 0) hydrate(saved);
  }, [hydrate]);

  useEffect(() => {
    const zone = zoneRef.current;
    if (!zone) return;
    const onDragOver = (event: DragEvent) => event.preventDefault();
    const onDrop = (event: DragEvent) => {
      event.preventDefault();
      void importFiles([...(event.dataTransfer?.files ?? [])]);
    };
    zone.addEventListener('dragover', onDragOver);
    zone.addEventListener('drop', onDrop);
    return () => {
      zone.removeEventListener('dragover', onDragOver);
      zone.removeEventListener('drop', onDrop);
    };
  }, []);

  const needle = query.trim();
  const visible = needle ? items.filter((item) => item.name.includes(needle)) : items;

  return (
    <section aria-label="سطل رسانه" className="flex flex-col gap-3">
      <header className="flex items-end justify-between gap-3">
        <h1 className="text-lg font-bold">سطل رسانه</h1>
        <label className="text-sm text-white/80">
          جستجو
          <input
            data-testid="media-search"
            className="ms-2 rounded-md border border-surface-border bg-surface-raised px-2 py-1"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </header>
      <div
        ref={zoneRef}
        data-testid="media-drop"
        className="rounded-md border border-dashed border-surface-border bg-surface-raised p-4"
      >
        <p className="text-sm text-white/80">فایل‌ها را اینجا رها کنید، یا از دیالوگ انتخاب کنید.</p>
        <label className="mt-2 inline-block rounded-md bg-surface-overlay px-3 py-2 text-sm">
          انتخاب فایل
          <input
            data-testid="media-file"
            className="sr-only"
            type="file"
            multiple
            accept="video/*,audio/*"
            onChange={(event) => {
              const picked = [...(event.target.files ?? [])];
              event.target.value = '';
              void importFiles(picked);
            }}
          />
        </label>
      </div>
      <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2" style={{ contentVisibility: 'auto' }}>
        {visible.map((item) => (
          <li
            key={item.id}
            data-testid="media-card"
            data-status={item.status}
            className="rounded-md border border-surface-border bg-surface-raised p-3"
          >
            {item.thumbnails[0] ? (
              <img
                data-testid="media-thumb"
                alt={`پیش‌نمایش ${item.name}`}
                width={160}
                height={90}
                src={item.thumbnails[0]}
              />
            ) : null}
            <p data-testid="media-duration" data-duration={item.duration ?? ''} className="mt-2 text-sm">
              {item.duration == null ? '…' : formatSeconds(item.duration)}
            </p>
            {item.fps != null ? <p className="text-xs text-white/60">{item.fps} فریم در ثانیه</p> : null}
            {item.status === 'reading' ? (
              <output className="text-sm text-white/80">در حال خواندن</output>
            ) : null}
            {item.status === 'error' ? (
              <p role="alert" className="text-sm text-error">
                {item.error}
              </p>
            ) : null}
            <label className="mt-2 block text-sm">
              نام
              <input
                data-testid="media-name"
                className="mt-1 w-full rounded-md border border-surface-border bg-surface-base px-2 py-1"
                value={item.name}
                onChange={(event) => rename(item.id, event.target.value)}
              />
            </label>
            <button type="button" className="mt-2 text-sm text-white/80" onClick={() => remove(item.id)}>
              حذف
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
