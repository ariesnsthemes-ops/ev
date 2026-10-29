#!/usr/bin/env node
/**
 * Shows or changes a switch in site.config.mjs from the command line:
 *   npm run switch                              list the switches and their values
 *   npm run switch -- AD_PLACEHOLDER_TEXT on    texts on the empty ad spots back on   (off = photos only)
 *   npm run switch -- ADS_ENABLED on            advertising page, demo page and "Zakupi" buttons on
 *   npm run switch -- NOINDEX off               let search engines index the site
 * on/off, true/false and yes/no all work. Commit and push site.config.mjs afterwards; Cloudflare rebuilds.
 */
import { readFileSync, writeFileSync } from 'node:fs';

const FILE = new URL('../site.config.mjs', import.meta.url);
const src = readFileSync(FILE, 'utf8');
const [name, value] = process.argv.slice(2);
const BOOL = /^\s{2}([A-Z_]+): (true|false),$/gm;

if (!name) {
  for (const m of src.matchAll(BOOL)) console.log(`${m[1].padEnd(20)} ${m[2] === 'true' ? 'on' : 'off'}`);
  process.exit(0);
}
const v = { on: true, true: true, yes: true, '1': true, off: false, false: false, no: false, '0': false }[String(value).toLowerCase()];
if (v === undefined) { console.error('Use on or off, e.g.: npm run switch -- AD_PLACEHOLDER_TEXT on'); process.exit(1); }
const re = new RegExp(`^(\\s{2}${name}: )(true|false),$`, 'm');
if (!re.test(src)) { console.error(`No on/off switch called ${name} in site.config.mjs.`); process.exit(1); }
writeFileSync(FILE, src.replace(re, `$1${v},`));
console.log(`${name} is now ${v ? 'on' : 'off'}. Run "npm run build" to check, then commit and push site.config.mjs.`);
