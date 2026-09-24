export type ShortcutAction = 'split' | 'delete' | 'ripple-delete';

export function shortcutAction(event: {
  key: string;
  ctrlKey: boolean;
  metaKey: boolean;
  shiftKey: boolean;
}): ShortcutAction | null {
  const mod = event.ctrlKey || event.metaKey;
  if (mod && event.key.toLowerCase() === 'b') return 'split';
  if (event.key === 'Delete' || event.key === 'Backspace') return event.shiftKey ? 'ripple-delete' : 'delete';
  return null;
}
