import { create } from 'zustand';

export interface RehealHealth {
  ramPercent: number;
  cpuPercent: number;
  isHealthy: boolean;
}

export interface RehealFixEvent {
  id: string;
  component: string;
  message: string;
  success: boolean;
  timestamp: number;
}

interface RehealState {
  health: RehealHealth;
  fixesCount: number;
  recentFixes: RehealFixEvent[];
  setHealth: (health: RehealHealth) => void;
  addFixEvent: (fix: RehealFixEvent) => void;
}

export const useRehealStore = create<RehealState>((set) => ({
  health: { ramPercent: 0, cpuPercent: 0, isHealthy: true },
  fixesCount: 0,
  recentFixes: [],
  setHealth: (health) => set({ health }),
  addFixEvent: (fix) => set((s) => ({
    fixesCount: s.fixesCount + 1,
    recentFixes: [fix, ...s.recentFixes].slice(0, 10),
  })),
}));
