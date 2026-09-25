'use client';
import { shortcutAction } from '@/lib/shortcuts';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { Brain, Dumbbell, Mic, Palette, Scissors, Search, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';

export const COMMANDS = [
  { id: 'cut', label: 'برش هوشمند ویدیو', icon: Scissors, category: 'Editor', shortcut: 'Ctrl+X' },
  { id: 'beat-sync', label: 'Beat Sync خودکار', icon: Zap, category: 'Editor', shortcut: 'از پالت' },
  { id: 'voice-edit', label: 'فرمان صوتی', icon: Mic, category: 'Editor', shortcut: 'Ctrl+M' },
  { id: 'style-match', label: 'مچ کردن استایل', icon: Palette, category: 'Style', shortcut: 'Ctrl+Shift+S' },
  { id: 'mood-dna', label: 'استخراج Mood DNA', icon: Brain, category: 'Style', shortcut: 'از پالت' },
  {
    id: 'muscle-enhance',
    label: 'شارپ و تعریف عضلات',
    icon: Dumbbell,
    category: 'Muscle',
    shortcut: 'Ctrl+Shift+M',
  },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (shortcutAction(e) === 'palette') {
        e.preventDefault();
        setOpen((v) => !v);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  const filtered = COMMANDS.filter(
    (c) => c.label.includes(query) || c.category.toLowerCase().includes(query.toLowerCase())
  );

  /** WIG: honour prefers-reduced-motion — the panel fades instead of scaling/sliding. */
  const reduceMotion = useReducedMotion();
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-start justify-center pt-28 bg-black/60 backdrop-blur-sm"
          // wig-ignore div-click: backdrop dismiss is supplementary — Escape closes via the window listener above; native dialog element lands in S-084 (S-084)
          onClick={(e) => {
            if (e.target === e.currentTarget) setOpen(false);
          }}
        >
          <motion.div
            initial={reduceMotion ? { opacity: 0 } : { scale: 0.95, y: -20 }}
            animate={reduceMotion ? { opacity: 1 } : { scale: 1, y: 0 }}
            exit={reduceMotion ? { opacity: 0 } : { scale: 0.95, y: -20 }}
            className="w-[520px] bg-[#121217] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
            dir="rtl"
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5">
              <Search className="w-4 h-4 text-white/30" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="دستور یا ویژگی را جستجو کنید…"
                aria-label="جستجوی دستور"
                className="flex-1 bg-transparent text-sm text-white outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/50 rounded"
              />
              <kbd className="text-[10px] text-white/40 bg-white/5 px-2 py-0.5 rounded">ESC</kbd>
            </div>
            <div className="max-h-72 overflow-y-auto p-2">
              {filtered.map((cmd) => (
                <button
                  type="button"
                  key={cmd.id}
                  onClick={() => setOpen(false)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-right transition-colors group"
                >
                  <cmd.icon className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs text-white/80 flex-1">{cmd.label}</span>
                  <span className="text-[10px] text-white/30 bg-white/5 px-2 py-0.5 rounded">
                    {cmd.category}
                  </span>
                  <span className="text-[10px] text-white/20 font-mono">{cmd.shortcut}</span>
                </button>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
