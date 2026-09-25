/** Job channel decisions (S-029). A closed socket is not a pass. */

export interface JobMessage {
  percent: number;
  fps: number | null;
  eta: number | null;
  stage: string;
  log: string;
}

export type ChannelMode = 'ws' | 'poll' | 'missing';

export function fallbackAfterClose(status: string): ChannelMode {
  if (status === 'done' || status === 'cancelled' || status === 'error') return 'missing';
  return 'poll';
}

export function monotonic(percents: number[]): boolean {
  if (percents.length < 10) return false;
  for (let i = 1; i < percents.length; i += 1) {
    const prev = percents[i - 1];
    const next = percents[i];
    if (prev === undefined || next === undefined || next < prev) return false;
  }
  return true;
}
