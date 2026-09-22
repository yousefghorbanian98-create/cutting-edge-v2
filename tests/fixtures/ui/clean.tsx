// Fixture for tests/unit/test_design_audit.py — zero findings, incl. one justified wig-ignore.
import { motion, useReducedMotion } from 'framer-motion';
import { Play } from 'lucide-react';

const fmt = new Intl.DateTimeFormat('fa-IR', { dateStyle: 'medium' });

export function Clean({ when, onPlay }: { when: Date; onPlay: () => void }) {
  const reduce = useReducedMotion();
  return (
    <div>
      <button type="button" aria-label="پخش" onClick={onPlay} className="focus-visible:ring-2">
        <Play className="w-4 h-4" aria-hidden="true" />
      </button>
      <label htmlFor="q">جستجو</label>
      <input id="q" name="q" className="outline-none focus-visible:ring-2 transition-colors" placeholder="جستجو…" />
      <button type="button" onClick={onPlay} className="transition-opacity hover:opacity-80">
        متن
      </button>
      <img src="/poster.png" alt="" width={320} height={180} />
      <span>{fmt.format(when)}</span>
      <motion.div animate={reduce ? undefined : { opacity: 1 }} />
      {/* wig-ignore input-label: label is rendered by the parent form row (S-084) */}
      <textarea rows={3} />
    </div>
  );
}
