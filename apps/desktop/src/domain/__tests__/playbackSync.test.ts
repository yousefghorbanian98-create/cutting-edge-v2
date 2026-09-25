import { describe, expect, it } from 'vitest';
import { maxPlayheadLeadSeconds, playheadTranslate } from '../playbackSync';

describe('playhead lead stays inside one frame', () => {
  it('caps 60fps lead strictly under 1/60', () => {
    const lead = maxPlayheadLeadSeconds(60);
    expect(lead).toBeLessThan(1 / 60);
    expect(lead).toBeGreaterThan(0);
  });

  it('does not widen the cap for a slower file', () => {
    expect(maxPlayheadLeadSeconds(30)).toBeLessThan(1 / 60);
    expect(maxPlayheadLeadSeconds(24)).toBeLessThan(1 / 60);
  });

  it('places the head on the media time, not a predicted second', () => {
    expect(playheadTranslate(3, 100)).toBe('translate3d(300px, 0, 0)');
  });
});
