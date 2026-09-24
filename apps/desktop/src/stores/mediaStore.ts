/**
 * Media bin store (S-014). The snapshot is what a reload restores, including renames.
 */

import type { MediaProbe } from '@/lib/probe';
import { create } from 'zustand';

export type MediaStatus = 'reading' | 'ready' | 'error';

export interface MediaItem {
  id: string;
  name: string;
  status: MediaStatus;
  duration: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  thumbnails: string[];
  error: string | null;
}

export interface MediaSnapshot {
  items: MediaItem[];
}

export const MEDIA_SNAPSHOT_KEY = 'ce-media-bin-v1';

export interface MediaState {
  items: MediaItem[];
  query: string;
  addPending: (id: string, name: string) => void;
  complete: (id: string, probe: MediaProbe) => void;
  fail: (id: string, error: string) => void;
  rename: (id: string, name: string) => void;
  remove: (id: string) => void;
  setQuery: (query: string) => void;
  hydrate: (snapshot: MediaSnapshot) => void;
  snapshot: () => MediaSnapshot;
}

function readyItems(items: MediaItem[]): MediaItem[] {
  return items.filter((item) => item.status === 'ready');
}

function writeSnapshot(items: MediaItem[]): void {
  if (typeof localStorage === 'undefined') return;
  const snapshot: MediaSnapshot = { items: readyItems(items) };
  localStorage.setItem(MEDIA_SNAPSHOT_KEY, JSON.stringify(snapshot));
}

export function readSnapshot(): MediaSnapshot | null {
  if (typeof localStorage === 'undefined') return null;
  const raw = localStorage.getItem(MEDIA_SNAPSHOT_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as MediaSnapshot;
    if (!parsed || !Array.isArray(parsed.items)) return null;
    return { items: parsed.items.filter((item) => item.status === 'ready') };
  } catch {
    return null;
  }
}

export const useMediaStore = create<MediaState>()((set, get) => ({
  items: [],
  query: '',
  addPending: (id, name) => {
    set((state) => ({
      items: [
        ...state.items,
        {
          id,
          name,
          status: 'reading',
          duration: null,
          width: null,
          height: null,
          fps: null,
          thumbnails: [],
          error: null,
        },
      ],
    }));
  },
  complete: (id, probe) => {
    set((state) => ({
      items: state.items.map((item) =>
        item.id === id
          ? {
              ...item,
              status: 'ready',
              duration: probe.duration,
              width: probe.width,
              height: probe.height,
              fps: probe.fps,
              thumbnails: probe.thumbnails,
              error: null,
            }
          : item
      ),
    }));
    writeSnapshot(get().items);
  },
  fail: (id, error) => {
    set((state) => ({
      items: state.items.map((item) => (item.id === id ? { ...item, status: 'error', error } : item)),
    }));
  },
  rename: (id, name) => {
    set((state) => ({
      items: state.items.map((item) => (item.id === id ? { ...item, name } : item)),
    }));
    writeSnapshot(get().items);
  },
  remove: (id) => {
    set((state) => ({ items: state.items.filter((item) => item.id !== id) }));
    writeSnapshot(get().items);
  },
  setQuery: (query) => set({ query }),
  hydrate: (snapshot) => set({ items: snapshot.items, query: '' }),
  snapshot: () => ({ items: readyItems(get().items) }),
}));
