'use client';

import { useJob } from '@/hooks/useJob';
import { useEffect, useState } from 'react';

interface HistoryItem {
  id: string;
  status: string;
  percent: number;
}

export function ExportProgress() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [toast, setToast] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const { message, cancel } = useJob(jobId);

  useEffect(() => {
    const onJob = (event: Event) => {
      const id = (event as CustomEvent<string>).detail;
      if (id) setJobId(id);
    };
    window.addEventListener('ce-export-job', onJob);
    return () => window.removeEventListener('ce-export-job', onJob);
  }, []);

  useEffect(() => {
    if (!message || !jobId) return;
    setHistory((current) => {
      const next = current.filter((item) => item.id !== jobId);
      return [...next, { id: jobId, status: message.stage, percent: message.percent }];
    });
  }, [jobId, message]);

  const outputReady = message?.stage === 'done';

  return (
    <section
      aria-label="پیشرفت خروجی"
      className="mt-2"
      data-testid="export-progress"
      data-output-present={outputReady ? '1' : '0'}
    >
      <p data-testid="export-percent">{message ? `${message.percent}٪` : '۰٪'}</p>
      <p className="text-xs text-white/60">
        {message?.fps ?? '—'} fps · {message?.eta ?? '—'}s · {message?.stage ?? 'idle'}
      </p>
      <button
        type="button"
        className="mt-2 rounded-md border border-surface-border px-2 py-1 text-sm"
        onClick={() => {
          void cancel().then(() => setToast('خروجی لغو شد'));
        }}
      >
        لغو خروجی
      </button>
      {outputReady ? (
        <a href={`http://127.0.0.1:8001/muscle/download/${jobId}`} className="ms-2 text-sm">
          دانلود
        </a>
      ) : null}
      {toast ? <output data-testid="export-toast">{toast}</output> : null}
      <ul data-testid="export-history" className="mt-2 text-sm">
        {history.map((item) => (
          <li key={item.id}>
            {item.id} · {item.status} · {item.percent}
          </li>
        ))}
      </ul>
    </section>
  );
}
