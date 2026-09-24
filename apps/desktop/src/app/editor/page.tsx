import { MediaBin } from '@/components/media-bin/MediaBin';
import { Timeline } from '@/components/timeline/Timeline';

export default function EditorPage() {
  return (
    <main className="min-h-screen bg-surface-base p-4 text-white">
      <MediaBin />
      <Timeline />
    </main>
  );
}
