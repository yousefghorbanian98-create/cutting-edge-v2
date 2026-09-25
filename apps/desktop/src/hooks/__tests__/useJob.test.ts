import { fallbackAfterClose, monotonic } from '@/lib/jobChannel';
import { describe, expect, it } from 'vitest';

describe('job channel', () => {
  it('falls back to polling when the socket closes mid-job', () => {
    expect(fallbackAfterClose('running')).toBe('poll');
    expect(fallbackAfterClose('done')).toBe('missing');
  });

  it('requires ten increasing percents', () => {
    expect(monotonic([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])).toBe(true);
    expect(monotonic([1, 2, 1])).toBe(false);
  });
});
