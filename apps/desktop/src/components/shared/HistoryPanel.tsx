'use client';

import { redoTimeline, undoTimeline, useTimelineStore } from '@/stores/timelineStore';
import { useEffect, useState } from 'react';
import { describeEdit, historyLabels, noteHistory } from './history';

export function HistoryPanel() {
  const [entries, setEntries] = useState<readonly { id: number; label: string }[]>([]);
  useEffect(() => {
    let previous = useTimelineStore.temporal.getState().pastStates.length;
    return useTimelineStore.temporal.subscribe((state) => {
      const sequence = useTimelineStore.getState().sequence;
      const past = state.pastStates.at(-1) as { sequence?: SequenceLike } | undefined;
      const label = past?.sequence ? describeEdit(past.sequence, sequence) : 'ویرایش / edit';
      noteHistory(
        state.pastStates.length,
        previous,
        label,
        state.futureStates.length > 0 && state.pastStates.length > previous
      );
      previous = state.pastStates.length;
      setEntries(historyLabels());
    });
  }, []);
  return (
    <section aria-label="تاریخچه" className="mt-3 rounded-md border border-surface-border p-2">
      <div className="mb-2 flex gap-2">
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => undoTimeline(1)}
        >
          واگرد
        </button>
        <button
          type="button"
          className="rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={() => redoTimeline(1)}
        >
          ازنو
        </button>
      </div>
      <ol data-testid="history-list">
        {entries.map((entry) => (
          <li key={entry.id} className="text-sm text-white/80">
            {entry.label}
          </li>
        ))}
      </ol>
    </section>
  );
}

interface SequenceLike {
  clips: { id: string }[];
  tracks: { id: string }[];
}
