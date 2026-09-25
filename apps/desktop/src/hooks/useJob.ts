'use client';

import { cancelJob, getJob } from '@/lib/api';
import { type ChannelMode, type JobMessage, fallbackAfterClose } from '@/lib/jobChannel';
import { useEffect, useRef, useState } from 'react';

const BASE = 'http://127.0.0.1:8001';

export function useJob(jobId: string | null): {
  message: JobMessage | null;
  mode: ChannelMode;
  cancel: () => Promise<void>;
} {
  const [message, setMessage] = useState<JobMessage | null>(null);
  const [mode, setMode] = useState<ChannelMode>('missing');
  const stage = useRef('running');

  useEffect(() => {
    if (!jobId) return undefined;
    let closed = false;
    let timer = 0;
    const apply = (next: JobMessage, nextMode: ChannelMode) => {
      if (closed) return;
      stage.current = next.stage;
      setMessage(next);
      setMode(nextMode);
    };
    const poll = () => {
      void getJob({ path: { job_id: jobId } }).then((result) => {
        if (closed || result.error || !result.data) return;
        const data = result.data;
        apply(
          {
            percent: data.percent,
            fps: null,
            eta: data.eta_s ?? null,
            stage: data.status,
            log: data.error ?? '',
          },
          'poll'
        );
        if (data.status === 'queued' || data.status === 'running') timer = window.setTimeout(poll, 200);
      });
    };
    const socket = new WebSocket(`${BASE.replace(/^http/, 'ws')}/ws/jobs/${jobId}`);
    socket.onopen = () => setMode('ws');
    socket.onmessage = (event) => {
      const body = JSON.parse(String(event.data)) as JobMessage;
      apply(body, 'ws');
    };
    socket.onerror = () => {
      setMode('missing');
      poll();
    };
    socket.onclose = () => {
      if (fallbackAfterClose(stage.current) === 'poll') poll();
    };
    return () => {
      closed = true;
      window.clearTimeout(timer);
      socket.close();
    };
  }, [jobId]);

  return {
    message,
    mode,
    cancel: async () => {
      if (!jobId) return;
      await cancelJob({ path: { job_id: jobId } });
    },
  };
}
