'use client';

import { BASE_PX, fitPx, zoomAround } from '@/domain/zoom';
import { create } from 'zustand';

/** View state only. Sequence edits stay on the timeline store. */
export interface ZoomState {
  pxPerSecond: number;
  zoomBy: (
    scrollLeft: number,
    cursorX: number,
    factor: number
  ) => { pxPerSecond: number; scrollLeft: number };
  fitTo: (seconds: number, viewport: number) => { pxPerSecond: number; scrollLeft: number };
  setPx: (px: number) => void;
}

export const useZoomStore = create<ZoomState>()((set, get) => ({
  pxPerSecond: BASE_PX,
  zoomBy: (scrollLeft, cursorX, factor) => {
    const next = zoomAround(get().pxPerSecond, scrollLeft, cursorX, factor);
    set({ pxPerSecond: next.pxPerSecond });
    return next;
  },
  fitTo: (seconds, viewport) => {
    const px = fitPx(seconds, viewport);
    set({ pxPerSecond: px });
    return { pxPerSecond: px, scrollLeft: 0 };
  },
  setPx: (px) => set({ pxPerSecond: px }),
}));

export function useZoom(): ZoomState {
  return useZoomStore();
}
