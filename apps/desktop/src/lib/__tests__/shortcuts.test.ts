import { COMMANDS } from '@/components/shared/CommandPalette';
import { describe, expect, it } from 'vitest';
import { SHORTCUT_REGISTRY, shortcutAction } from '../shortcuts';

describe('shortcut registry', () => {
  it('keeps Ctrl+B as split and does not share chords with the palette', () => {
    expect(shortcutAction({ key: 'b', ctrlKey: true, metaKey: false, shiftKey: false })).toBe('split');
    const owned = new Set(SHORTCUT_REGISTRY.map((item) => item.chord));
    for (const command of COMMANDS) {
      if (command.shortcut === 'Ctrl+K') continue;
      expect(owned.has(command.shortcut)).toBe(false);
    }
  });

  it('opens the cheat sheet for Persian question mark', () => {
    expect(shortcutAction({ key: '؟', ctrlKey: false, metaKey: false, shiftKey: false })).toBe('cheat-sheet');
  });
});
