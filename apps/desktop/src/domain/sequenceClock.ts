/** Advance sequence playback without overwriting a time value being edited. */
export function advanceSequenceClock(currentSeconds: number, timeFieldFocused: boolean): number {
  return timeFieldFocused ? currentSeconds : currentSeconds + 1 / 30;
}
