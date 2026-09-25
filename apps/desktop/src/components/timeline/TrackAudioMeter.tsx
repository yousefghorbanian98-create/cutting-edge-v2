'use client';

import { attachTrackMeter, isTrackAudioPlaying, syncTrackOutput } from '@/lib/trackAudio';
import { useTimelineStore } from '@/stores/timelineStore';
import { useEffect, useRef } from 'react';

export function TrackAudioMeter() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    attachTrackMeter(ref.current);
    return useTimelineStore.subscribe((state) => {
      syncTrackOutput(state.sequence, isTrackAudioPlaying());
    });
  }, []);

  return <div ref={ref} data-testid="track-audio" data-capability="unknown" className="sr-only" />;
}
