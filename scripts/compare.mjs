#!/usr/bin/env node
/**
 * Compares the Astro build (site/) with a reference build of the old generator, file by file.
 *   node scripts/compare.mjs <reference-dir> [built-dir=site] [--show=path]
 * Text files are compared byte for byte (the build date is normalised). Binary files by size and hash.
 */
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const [ref, out = 'site', ...rest] = process.argv.slice(2);
const show = (rest.find((a) => a.startsWith('--show=')) || '').slice(7);
if (!ref) { console.error('usage: compare.mjs <reference-dir> [built-dir]'); process.exit(2); }

const walk = (d) => readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(d, e.name)) : [join(d, e.name)]));
const files = (d) => new Set(walk(d).map((f) => relative(d, f)));
const A = files(ref), B = files(out);
const TEXT = /\.(html|css|js|txt|xml|json|svg|geojson)$|^_headers$/;
const norm = (s) => s.replace(/\d{4}-\d{2}-\d{2}/g, 'DATE');

let same = 0, diff = [], onlyA = [...A].filter((f) => !B.has(f)), onlyB = [...B].filter((f) => !A.has(f));
for (const f of [...A].filter((f) => B.has(f)).sort()) {
  const a = readFileSync(join(ref, f)), b = readFileSync(join(out, f));
  if (TEXT.test(f)) {
    const ta = norm(a.toString('utf8')), tb = norm(b.toString('utf8'));
    if (ta === tb) same++; else diff.push([f, firstDiff(ta, tb)]);
  } else if (a.length === b.length && createHash('md5').update(a).digest('hex') === createHash('md5').update(b).digest('hex')) same++;
  else diff.push([f, `binary ${a.length} vs ${b.length} bytes`]);
}
function firstDiff(a, b) {
  let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++;
  const la = a.slice(0, i).split('\n').length;
  return `line ${la}: ref ${JSON.stringify(a.slice(Math.max(0, i - 60), i + 100))}\n           new ${JSON.stringify(b.slice(Math.max(0, i - 60), i + 100))}`;
}
console.log(`identical: ${same}   different: ${diff.length}   only in reference: ${onlyA.length}   only in build: ${onlyB.length}`);
for (const [f, d] of diff) console.log(`\n✗ ${f}\n   ${d}`);
if (onlyA.length) console.log('\nonly in reference:', onlyA.join(', '));
if (onlyB.length) console.log('\nonly in build:', onlyB.join(', '));
if (show) {
  const { execSync } = await import('node:child_process');
  try { execSync(`diff <(sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/DATE/g' "${join(ref, show)}") <(sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/DATE/g' "${join(out, show)}") | head -80`, { shell: '/bin/bash', stdio: 'inherit' }); } catch {}
}
process.exit(diff.length || onlyA.length || onlyB.length ? 1 : 0);
