'use client';

import { removeClips, splitAtPlayhead } from '@/domain/split';
import { usePlayback } from '@/hooks/usePlayback';
import { shortcutAction } from '@/lib/shortcuts';
import { useSelectionStore } from '@/stores/selectionStore';
import { redoTimeline, undoTimeline, useTimelineStore } from '@/stores/timelineStore';
import { useEffect } from 'react';

export function Shortcuts() {
  const { time } = usePlayback();
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const tag = (event.target as HTMLElement | null)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      const action = shortcutAction(event);
      if (!action) return;
      event.preventDefault();
      const sequence = useTimelineStore.getState().sequence;
      if (action === 'copy') {
        useSelectionStore.getState().copy();
        return;
      }
      if (action === 'paste') {
        useSelectionStore.getState().paste(Math.round(time * 1000));
        return;
      }
      if (action === 'duplicate') {
        useSelectionStore.getState().duplicate();
        return;
      }
      if (action === 'undo') {
        undoTimeline(1);
        return;
      }
      if (action === 'redo') {
        redoTimeline(1);
        return;
      }
      if (action === 'split') {
        const head = document.querySelector('[data-testid=playhead]');
        const fromHead = Number(head instanceof HTMLElement ? head.dataset.time : time);
        const at = Number.isFinite(fromHead) ? Math.round(fromHead * 1000) : Math.round(time * 1000);
        const next = splitAtPlayhead(sequence, at, sequence.selection, sequence.selection.length > 0);
        if (next !== sequence) useTimelineStore.setState({ sequence: next });
        return;
      }
      const ids = sequence.selection.length > 0 ? sequence.selection : [];
      if (ids.length === 0) return;
      const next = removeClips(sequence, ids, action === 'ripple-delete');
      if (next !== sequence) useTimelineStore.setState({ sequence: next });
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [time]);
  return null;
}
