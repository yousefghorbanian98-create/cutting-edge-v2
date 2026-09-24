import { formatSeconds } from '@/lib/probe';
import { useMediaStore } from '@/stores/mediaStore';
import { beforeEach, describe, expect, it } from 'vitest';

describe('media snapshot', () => {
  beforeEach(() => {
    useMediaStore.setState({ items: [], query: '' });
  });

  it('keeps a rename in the snapshot that a fresh hydrate restores', () => {
    const store = useMediaStore.getState();
    store.addPending('m1', 'کلیپ تمرین ۱.mp4');
    store.complete('m1', {
      duration: 1,
      width: 64,
      height: 36,
      fps: 30,
      thumbnails: ['data:image/jpeg;base64,aa'],
    });
    store.rename('m1', 'نام جدید');
    const snapshot = useMediaStore.getState().snapshot();
    useMediaStore.setState({ items: [], query: 'پاک' });
    useMediaStore.getState().hydrate(snapshot);
    expect(useMediaStore.getState().items[0]?.name).toBe('نام جدید');
    expect(useMediaStore.getState().query).toBe('');
    expect(formatSeconds(1)).toBe('1.0 ثانیه');
  });
});
