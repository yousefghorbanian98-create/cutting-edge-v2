// Fixture for tests/unit/test_design_audit.py — exactly 8 known violations, one per rule.
// Line numbers are asserted by the test; keep the layout stable.
import { motion } from 'framer-motion';
import { Play } from 'lucide-react';

export function Violations({ when }: { when: Date }) {
  return (
    <div>
      <button type="button" onClick={() => undefined}>
        <Play className="w-4 h-4" />
      </button>
      <input aria-label="جستجو" className="bg-transparent outline-none" placeholder="جستجو…" />
      <a href="/x" className="transition-all hover:opacity-80">
        link
      </a>
      <div onClick={() => undefined}>click me</div>
      <img src="/poster.png" />
      <span>{when.toLocaleDateString()}</span>
      <motion.div animate={{ opacity: 1 }} />
      <textarea rows={3} />
    </div>
  );
}
