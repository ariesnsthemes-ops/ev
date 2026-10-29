#!/usr/bin/env node
/**
 * Renders the same pages from two site folders at several viewport widths and saves screenshots
 * for a pixel comparison:  node scripts/visual-check.mjs <reference-dir> <built-dir> <out-dir>
 * Pages are served the way Cloudflare serves them (clean addresses, /modeli -> modeli.html).
 */
import http from 'node:http';
import { existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join, extname } from 'node:path';
import { chromium } from 'playwright'; // (resolved via NODE_PATH or a local install)

const [ref, built, out] = process.argv.slice(2);
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon', '.txt': 'text/plain', '.xml': 'application/xml' };
function serve(dir, port) {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      if (p === '/') p = '/index.html';
      let f = join(dir, p);
      if (!existsSync(f) || statSync(f).isDirectory()) f = join(dir, p + '.html');
      if (!existsSync(f)) { f = join(dir, '404.html'); res.statusCode = 404; }
      res.setHeader('Content-Type', MIME[extname(f)] || 'application/octet-stream');
      res.end(readFileSync(f));
    });
    srv.listen(port, () => resolve(srv));
  });
}
const PAGES = ['/', '/modeli', '/brendovi', '/brendovi/bmw', '/modeli/byd-seal', '/modeli/jmev-ewind', '/elektricni-suv', '/najveci-domet', '/distributeri',
  '/punjaci', '/uporedi?modeli=byd-seal,kia-ev6', '/kalkulator-troskova?model=byd-seal', '/subvencije-elektricni-automobili-2026', '/o-nama', '/kontakt', '/politika-privatnosti', '/nema-takve-stranice'];
const WIDTHS = [1440, 1180, 900, 760, 560, 390];

const [a, b] = await Promise.all([serve(ref, 4311), serve(built, 4312)]);
const browser = await chromium.launch();
mkdirSync(out, { recursive: true });
for (const [tag, port] of [['ref', 4311], ['new', 4312]]) {
  for (const w of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1, reducedMotion: 'reduce' });
    // block the outside world (fonts, map tiles) so both renders use the same fallbacks
    await ctx.route(/^https?:\/\/(?!localhost)/, (r) => r.abort());
    // the homepage shuffles its model cards: give both renders the same "random" sequence
    await ctx.addInitScript(() => { let s = 12345; Math.random = () => ((s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x80000000); });
    for (const p of PAGES) {
      const page = await ctx.newPage();
      await page.goto(`http://localhost:${port}${p}`, { waitUntil: 'load' });
      // load every lazy image before the full-page screenshot
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 30)); }
        window.scrollTo(0, 0);
        [...document.images].forEach((i) => { i.loading = 'eager'; });
      });
      await page.waitForLoadState('networkidle');
      await page.waitForFunction(() => [...document.images].every((i) => i.complete), null, { timeout: 15000 }).catch(() => {});
      await page.evaluate(() => new Promise((r) => setTimeout(r, 500)));
      const name = (p === '/' ? 'home' : p.replace(/^\//, '').replace(/[^a-z0-9]+/gi, '-')) + `-${w}`;
      await page.screenshot({ path: join(out, `${name}.${tag}.png`), fullPage: true, animations: 'disabled', caret: 'hide' });
      await page.close();
    }
    await ctx.close();
  }
}
await browser.close();
a.close(); b.close();
console.log('screenshots written to', out);
