'use client';

import { MediaBin } from '@/components/media-bin/MediaBin';
import { HistoryPanel } from '@/components/shared/HistoryPanel';
import { Shortcuts } from '@/components/timeline/Shortcuts';
import { Timeline } from '@/components/timeline/Timeline';
import { PlaybackProvider } from '@/hooks/usePlayback';

export function EditorShell() {
  return (
    <PlaybackProvider>
      <main className="min-h-screen bg-surface-base p-4 text-white">
        <Shortcuts />
        <MediaBin />
        <Timeline />
        <HistoryPanel />
      </main>
    </PlaybackProvider>
  );
}
