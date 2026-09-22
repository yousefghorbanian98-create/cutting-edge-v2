#!/usr/bin/env node
/**
 * check-design-tokens.js — S-099 three-way design-token drift check.
 *
 *   DESIGN.md  ⇄  apps/desktop/src/app/globals.css (@theme static)  ⇄  packages/design-system/tokens.ts
 *
 * DESIGN.md is the human/agent-facing authority; the CSS block is what
 * generates Tailwind utilities; tokens.ts is what JS/framer-motion reads.
 * Any value that exists in one place and not the others — or exists with a
 * different value — is a defect, not a style choice. Exit 1 on drift.
 *
 * Dependency-free on purpose (runs inside `gate.py --stage static` and the
 * `ci / ubuntu` job before pnpm install may have happened for a tool step).
 *
 * Usage:
 *   node scripts/check-design-tokens.js [--design DESIGN.md] [--css globals.css]
 *                                       [--tokens tokens.ts] [--json]
 */
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const DEFAULTS = {
  design: path.join(ROOT, 'DESIGN.md'),
  css: path.join(ROOT, 'apps/desktop/src/app/globals.css'),
  tokens: path.join(ROOT, 'packages/design-system/tokens.ts'),
};

function parseArgs(argv) {
  const opts = { ...DEFAULTS, json: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') opts.json = true;
    else if (a === '--design' || a === '--css' || a === '--tokens') {
      const v = argv[++i];
      if (!v) throw new Error(`${a} needs a path`);
      opts[a.slice(2)] = path.resolve(v);
    } else throw new Error(`unknown argument ${a}`);
  }
  return opts;
}

/** Normalise a CSS/TS value so quoting and whitespace differences do not count as drift. */
function norm(v) {
  return String(v)
    .trim()
    .replace(/^["']|["']$/g, '')
    .replace(/["']/g, '')
    .replace(/\s*,\s*/g, ', ')
    .replace(/\s+/g, ' ')
    .replace(/\s*\/\s*/g, ' / ')
    .toLowerCase();
}

// ── DESIGN.md ────────────────────────────────────────────────────────────────
/**
 * Reads every fenced block whose first line is `# tokens: <group>` and returns
 * a flat map `{ "--color-surface-base": "#09090b", "ts:colors.primary.500": "#6366f1", ... }`.
 * Block lines are `key: value` (value may be quoted); `#` starts a comment.
 */
function parseDesign(text) {
  const out = new Map();
  const groups = [];
  const fence = /```yaml\n# tokens: ([a-z0-9-]+)\n([\s\S]*?)```/g;
  for (const m of text.matchAll(fence)) {
    const group = m[1];
    groups.push(group);
    for (const raw of m[2].split('\n')) {
      const line = raw.replace(/\s#(?!\w*[0-9a-f]{3,8}\b).*$/i, '').trim(); // strip trailing comments (keep #hex)
      if (!line || line.startsWith('#')) continue;
      // `key: value` — the separator is the first `:` followed by whitespace, so
      // `ts:colors.primary.50: "#eef2ff"` keeps its `ts:` prefix in the key.
      const kv = line.match(/^(\S+?):\s+(.+)$/);
      if (!kv) continue;
      const key = kv[1].trim();
      const val = kv[2].trim();
      if (out.has(key)) throw new Error(`DESIGN.md: duplicate token ${key}`);
      out.set(key, val);
    }
  }
  return { map: out, groups };
}

// ── globals.css ──────────────────────────────────────────────────────────────
function parseCss(text) {
  const m = text.match(/@theme static\s*\{([\s\S]*?)\n\}/);
  if (!m) throw new Error('globals.css: no `@theme static { … }` block');
  const out = new Map();
  for (const line of m[1].split('\n')) {
    const mm = line.match(/^\s*(--[a-z0-9-]+):\s*([^;]+);/);
    if (mm) out.set(mm[1], mm[2]);
  }
  return out;
}

// ── tokens.ts ────────────────────────────────────────────────────────────────
/**
 * Minimal reader for the `designTokens` object literal: walks nested
 * `key: { … }` / `key: 'value'` pairs and returns flat dotted paths.
 * Arrays and non-string scalars are kept as their source text.
 */
function parseTokens(text) {
  const start = text.indexOf('export const designTokens = {');
  if (start < 0) throw new Error('tokens.ts: `export const designTokens` not found');
  let i = text.indexOf('{', start);
  const flat = new Map();
  const stack = [];
  let key = null;
  const buf = [];
  const flush = () => {
    if (key !== null && buf.length) {
      flat.set(
        [...stack, key].join('.'),
        buf
          .join('')
          .trim()
          .replace(/,$/, '')
          .replace(/\s+as const$/, '')
      );
    }
    buf.length = 0;
  };
  // Tokeniser: enough for this file (strings, brackets, identifiers, numbers).
  for (; i < text.length; i++) {
    const c = text[i];
    if (c === '{') {
      if (key !== null) {
        stack.push(key);
        key = null;
      }
      buf.length = 0;
      continue;
    }
    if (c === '}') {
      flush();
      key = null;
      if (stack.length === 0) break;
      stack.pop();
      continue;
    }
    if (c === "'" || c === '"') {
      const end = text.indexOf(c, i + 1);
      buf.push(text.slice(i, end + 1));
      i = end;
      continue;
    }
    if (c === '[') {
      const end = text.indexOf(']', i);
      buf.push(text.slice(i, end + 1));
      i = end;
      continue;
    }
    if (c === ':' && key === null) {
      const k = buf
        .join('')
        .trim()
        .replace(/^['"]|['"]$/g, '');
      key = k;
      buf.length = 0;
      continue;
    }
    if (c === ',' && key !== null) {
      flush();
      key = null;
      continue;
    }
    if (c === '\n' && key === null) {
      buf.length = 0;
      continue;
    }
    buf.push(c);
  }
  const cssTheme = new Map();
  const mapBlock = text.match(/export const cssTheme = \{([\s\S]*?)\n\} as const;/);
  if (!mapBlock) throw new Error('tokens.ts: `export const cssTheme` map not found');
  for (const mm of mapBlock[1].matchAll(/'([a-z0-9.]+)':\s*'(--[a-z0-9-]+)'/g)) cssTheme.set(mm[1], mm[2]);
  return { flat, cssTheme };
}

function stripQuotes(s) {
  return String(s).replace(/^['"]|['"]$/g, '');
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const design = parseDesign(fs.readFileSync(opts.design, 'utf8'));
  const css = parseCss(fs.readFileSync(opts.css, 'utf8'));
  const ts = parseTokens(fs.readFileSync(opts.tokens, 'utf8'));

  const problems = [];
  let threeWay = 0;
  let tsOnly = 0;

  // 1. Every CSS var must be mapped from tokens.ts (cssTheme) and vice versa.
  const mappedVars = new Set(ts.cssTheme.values());
  for (const v of css.keys())
    if (!mappedVars.has(v))
      problems.push(`${v}: declared in globals.css but absent from tokens.ts cssTheme map`);
  for (const [p, v] of ts.cssTheme) {
    if (!css.has(v))
      problems.push(`${v}: in tokens.ts cssTheme (${p}) but not declared in globals.css @theme`);
    if (!ts.flat.has(p)) problems.push(`${v}: cssTheme maps ${p} but designTokens has no such path`);
  }

  // 2. Three-way value equality for every mapped var.
  for (const [p, v] of ts.cssTheme) {
    const cssVal = css.get(v);
    const tsVal = ts.flat.get(p);
    const dVal = design.map.get(v);
    if (cssVal === undefined || tsVal === undefined) continue; // already reported
    if (dVal === undefined) {
      problems.push(
        `${v}: missing from DESIGN.md (globals.css=${cssVal.trim()} tokens.ts=${stripQuotes(tsVal)})`
      );
      continue;
    }
    const a = norm(dVal);
    const b = norm(cssVal);
    const c = norm(stripQuotes(tsVal));
    if (a !== b || b !== c) {
      problems.push(
        `${v}: DESIGN.md=${stripQuotes(dVal)} globals.css=${cssVal.trim()} tokens.ts=${stripQuotes(tsVal)}`
      );
    } else threeWay++;
  }

  // 3. tokens.ts paths with no CSS var (primary scale, radius.full, motion, shadows)
  //    must still be documented in DESIGN.md as `ts:<path>`.
  for (const [p, raw] of ts.flat) {
    if (ts.cssTheme.has(p)) continue;
    const key = `ts:${p}`;
    const dVal = design.map.get(key);
    if (dVal === undefined) {
      problems.push(`${key}: in tokens.ts (${stripQuotes(raw)}) but missing from DESIGN.md`);
      continue;
    }
    if (norm(dVal) !== norm(stripQuotes(raw)))
      problems.push(`${key}: DESIGN.md=${stripQuotes(dVal)} tokens.ts=${stripQuotes(raw)}`);
    else tsOnly++;
  }

  // 4. DESIGN.md must not document tokens that do not exist in code.
  for (const k of design.map.keys()) {
    if (k.startsWith('--')) {
      if (!css.has(k)) problems.push(`${k}: documented in DESIGN.md but not declared in globals.css @theme`);
    } else if (k.startsWith('ts:')) {
      if (!ts.flat.has(k.slice(3))) problems.push(`${k}: documented in DESIGN.md but not in tokens.ts`);
    } else problems.push(`${k}: DESIGN.md token keys must be a CSS var (--…) or ts:<path>`);
  }

  const required = ['colors', 'typography', 'radius', 'motion', 'shadows'];
  for (const g of required)
    if (!design.groups.includes(g)) problems.push(`DESIGN.md: missing \`# tokens: ${g}\` block`);

  const report = {
    ok: problems.length === 0,
    threeWay,
    tsOnly,
    cssVars: css.size,
    designKeys: design.map.size,
    groups: design.groups,
    problems,
  };
  if (opts.json) console.log(JSON.stringify(report));
  else {
    for (const p of problems) console.log(`✗ ${p}`);
    console.log(
      `${report.ok ? '✓' : '✗'} design tokens — three-way ${threeWay} / tokens.ts-only ${tsOnly} / drift ${problems.length} (css vars ${css.size}, DESIGN.md keys ${design.map.size})`
    );
  }
  process.exit(report.ok ? 0 : 1);
}

try {
  main();
} catch (err) {
  console.error(`✗ design tokens — ${err.message}`);
  process.exit(2);
}
