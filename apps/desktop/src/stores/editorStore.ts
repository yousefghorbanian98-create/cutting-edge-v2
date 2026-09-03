import { create } from 'zustand';

export interface Clip {
  id: string;
  start: number;
  end: number;
  energyLevel: number;
  emotionTag: string;
}

interface EditorState {
  videoPath: string | null;
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  clips: Clip[];
  selectedClipId: string | null;
  setVideoPath: (path: string | null) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (dur: number) => void;
  setIsPlaying: (playing: boolean) => void;
  setClips: (clips: Clip[]) => void;
  selectClip: (id: string | null) => void;
}

export const useEditorStore = create<EditorState>((set) => ({
  videoPath: null,
  currentTime: 0,
  duration: 0,
  isPlaying: false,
  clips: [],
  selectedClipId: null,
  setVideoPath: (path) => set({ videoPath: path }),
  setCurrentTime: (time) => set({ currentTime: time }),
  setDuration: (duration) => set({ duration }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setClips: (clips) => set({ clips }),
  selectClip: (id) => set({ selectedClipId: id }),
}));
