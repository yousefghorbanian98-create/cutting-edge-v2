export type ShortcutAction =
  | 'split'
  | 'delete'
  | 'ripple-delete'
  | 'copy'
  | 'paste'
  | 'duplicate'
  | 'undo'
  | 'redo'
  | 'cheat-sheet'
  | 'palette';

export interface ShortcutSpec {
  action: ShortcutAction;
  chord: string;
  label: string;
}

export const SHORTCUT_REGISTRY: ShortcutSpec[] = [
  { action: 'split', chord: 'Ctrl+B', label: 'برش در پلی‌هد' },
  { action: 'copy', chord: 'Ctrl+C', label: 'کپی' },
  { action: 'paste', chord: 'Ctrl+V', label: 'چسباندن' },
  { action: 'duplicate', chord: 'Ctrl+D', label: 'تکرار' },
  { action: 'undo', chord: 'Ctrl+Z', label: 'واگرد' },
  { action: 'redo', chord: 'Ctrl+Shift+Z', label: 'ازنو' },
  { action: 'delete', chord: 'Delete', label: 'حذف انتخاب' },
  { action: 'ripple-delete', chord: 'Shift+Delete', label: 'حذف موجی' },
  { action: 'cheat-sheet', chord: '?', label: 'راهنمای میانبر' },
  { action: 'palette', chord: 'Ctrl+K', label: 'پالت دستور' },
];

export function shortcutAction(event: {
  key: string;
  code?: string;
  ctrlKey: boolean;
  metaKey: boolean;
  shiftKey: boolean;
}): ShortcutAction | null {
  const mod = event.ctrlKey || event.metaKey;
  const key = event.key.toLowerCase();
  if (mod && key === 'b' && !event.shiftKey) return 'split';
  if (mod && key === 'c' && !event.shiftKey) return 'copy';
  if (mod && key === 'v' && !event.shiftKey) return 'paste';
  if (mod && key === 'd' && !event.shiftKey) return 'duplicate';
  if (mod && key === 'z') return event.shiftKey ? 'redo' : 'undo';
  if (mod && key === 'k' && !event.shiftKey) return 'palette';
  if (event.key === 'Delete' || event.key === 'Backspace') return event.shiftKey ? 'ripple-delete' : 'delete';
  if (event.key === '?' || event.key === '؟' || (event.shiftKey && event.code === 'Slash'))
    return 'cheat-sheet';
  return null;
}
