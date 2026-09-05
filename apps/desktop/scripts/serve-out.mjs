#!/usr/bin/env node
/**
 * Minimal dependency-free static file server for the Next.js static export.
 *
 * Used by `playwright.config.ts` (`webServer`) and by CI to serve `out/` exactly
 * as the Tauri shell will load it (S-010 / S-060). Deliberately tiny and
 * cross-platform so the same command works on ubuntu and windows runners.
 *
 * Usage: node scripts/serve-out.mjs [rootDir=out] [port=4321]
 */
import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { extname, join, resolve, sep } from 'node:path';

const ROOT = resolve(process.argv[2] ?? 'out');
const PORT = Number(process.argv[3] ?? process.env.PORT ?? 4321);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.txt': 'text/plain; charset=utf-8',
};

/** Resolve a request path to a file inside ROOT, or null when it escapes. */
async function resolveTarget(pathname) {
  const decoded = decodeURIComponent(pathname.split('?')[0]);
  const rel = decoded.replace(/^\/+/, '');
  const target = resolve(join(ROOT, rel));
  if (target !== ROOT && !target.startsWith(ROOT + sep)) return null;

  for (const candidate of [target, join(target, 'index.html'), `${target}.html`]) {
    try {
      const info = await stat(candidate);
      if (info.isFile()) return candidate;
      if (info.isDirectory() && candidate === target) continue;
    } catch {
      /* try the next candidate */
    }
  }
  return null;
}

const server = createServer(async (req, res) => {
  try {
    const file = await resolveTarget(req.url ?? '/');
    if (!file) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
      res.end('not found');
      return;
    }
    res.writeHead(200, { 'content-type': MIME[extname(file).toLowerCase()] ?? 'application/octet-stream' });
    createReadStream(file).pipe(res);
  } catch (err) {
    res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
    res.end(String(err));
  }
});

server.listen(PORT, '127.0.0.1', () => {
  process.stdout.write(`serving ${ROOT} on http://127.0.0.1:${PORT}\n`);
});
