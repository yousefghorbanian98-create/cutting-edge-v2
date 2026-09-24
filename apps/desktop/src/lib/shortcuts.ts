export type ShortcutAction = 'split' | 'delete' | 'ripple-delete' | 'copy' | 'paste' | 'duplicate';

export function shortcutAction(event: {
  key: string;
  ctrlKey: boolean;
  metaKey: boolean;
  shiftKey: boolean;
}): ShortcutAction | null {
  const mod = event.ctrlKey || event.metaKey;
  if (mod && event.key.toLowerCase() === 'b') return 'split';
  if (mod && event.key.toLowerCase() === 'c') return 'copy';
  if (mod && event.key.toLowerCase() === 'v') return 'paste';
  if (mod && event.key.toLowerCase() === 'd') return 'duplicate';
  if (event.key === 'Delete' || event.key === 'Backspace') return event.shiftKey ? 'ripple-delete' : 'delete';
  return null;
}
