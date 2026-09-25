'use client';

import { SHORTCUT_REGISTRY } from '@/lib/shortcuts';

export function ShortcutsModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 p-4">
      <dialog
        open
        aria-label="راهنمای میانبر"
        data-testid="shortcuts-modal"
        data-count={SHORTCUT_REGISTRY.length}
        dir="rtl"
        className="w-full max-w-md rounded-md border border-surface-border bg-surface-raised p-4 text-white"
      >
        <h2 className="text-sm font-bold">میانبرها</h2>
        <ul className="mt-3 space-y-2">
          {SHORTCUT_REGISTRY.map((item) => (
            <li
              key={item.action}
              className="flex items-center justify-between gap-3 text-sm"
              data-shortcut={item.action}
            >
              <span>{item.label}</span>
              <span dir="ltr">{item.chord}</span>
            </li>
          ))}
        </ul>
        <button
          type="button"
          className="mt-4 rounded-md border border-surface-border px-2 py-1 text-sm"
          onClick={onClose}
        >
          بستن
        </button>
      </dialog>
    </div>
  );
}
