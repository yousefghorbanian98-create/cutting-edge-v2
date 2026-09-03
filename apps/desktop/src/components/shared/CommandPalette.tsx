"use client";
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Scissors, Palette, Brain, Dumbbell, Mic, Zap } from "lucide-react";

const COMMANDS = [
  { id: "cut", label: "برش هوشمند ویدیو", icon: Scissors, category: "Editor", shortcut: "Ctrl+X" },
  { id: "beat-sync", label: "Beat Sync خودکار", icon: Zap, category: "Editor", shortcut: "Ctrl+B" },
  { id: "voice-edit", label: "فرمان صوتی", icon: Mic, category: "Editor", shortcut: "Ctrl+M" },
  { id: "style-match", label: "مچ کردن استایل", icon: Palette, category: "Style", shortcut: "Ctrl+Shift+S" },
  { id: "mood-dna", label: "استخراج Mood DNA", icon: Brain, category: "Style", shortcut: "Ctrl+D" },
  { id: "muscle-enhance", label: "شارپ و تعریف عضلات", icon: Dumbbell, category: "Muscle", shortcut: "Ctrl+Shift+M" },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  const filtered = COMMANDS.filter(
    (c) => c.label.includes(query) || c.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-start justify-center pt-28 bg-black/60 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        >
          <motion.div
            initial={{ scale: 0.95, y: -20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: -20 }}
            className="w-[520px] bg-[#121217] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
            dir="rtl"
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5">
              <Search className="w-4 h-4 text-white/30" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="دستور یا ویژگی را جستجو کنید..."
                className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/30"
                autoFocus
              />
              <kbd className="text-[10px] text-white/40 bg-white/5 px-2 py-0.5 rounded">ESC</kbd>
            </div>
            <div className="max-h-72 overflow-y-auto p-2">
              {filtered.map((cmd) => (
                <button
                  key={cmd.id}
                  onClick={() => setOpen(false)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-right transition-all group"
                >
                  <cmd.icon className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs text-white/80 flex-1">{cmd.label}</span>
                  <span className="text-[10px] text-white/30 bg-white/5 px-2 py-0.5 rounded">{cmd.category}</span>
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
