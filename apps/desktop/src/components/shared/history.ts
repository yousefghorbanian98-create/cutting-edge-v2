let nextId = 1;
const labels: { id: number; label: string }[] = [];
const future: { id: number; label: string }[] = [];

export function describeEdit(
  before: { clips: readonly unknown[]; tracks: readonly unknown[] },
  after: { clips: readonly unknown[]; tracks: readonly unknown[] }
): string {
  if (after.clips.length > before.clips.length) return 'افزودن کلیپ / add clip';
  if (after.clips.length < before.clips.length) return 'حذف کلیپ / delete clip';
  if (after.tracks.length !== before.tracks.length) return 'ترک / track';
  return 'ویرایش / edit';
}

export function noteHistory(pastCount: number, previousCount: number, label: string, redo: boolean): void {
  if (pastCount > previousCount) {
    const restored = redo ? future.pop() : undefined;
    labels.push(restored ?? { id: nextId, label });
    nextId += 1;
    if (!redo) future.length = 0;
    return;
  }
  if (pastCount < previousCount) {
    const popped = labels.pop();
    if (popped) future.push(popped);
  }
}

export function historyLabels(): readonly { id: number; label: string }[] {
  return labels;
}

export function resetHistory(): void {
  labels.length = 0;
  future.length = 0;
  nextId = 1;
}
