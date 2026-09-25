/** Session file handles. Not persisted and not a timeline mutation. */

const files = new Map<string, File>();

export function rememberMedia(id: string, file: File): void {
  files.set(id, file);
}

export function mediaFile(id: string): File | undefined {
  return files.get(id);
}
