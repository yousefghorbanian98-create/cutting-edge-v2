'use client';

import { ExportDialog } from '@/components/export/ExportDialog';
import { ExportProgress } from '@/components/export/ExportProgress';
import { MediaBin } from '@/components/media-bin/MediaBin';
import { SequencePlayer } from '@/components/preview/SequencePlayer';
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
        <SequencePlayer />
        <ExportDialog />
        <ExportProgress />
        <Timeline />
        <HistoryPanel />
      </main>
    </PlaybackProvider>
  );
}
