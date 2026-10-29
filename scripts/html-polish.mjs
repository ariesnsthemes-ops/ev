/**
 * Astro integration run after the build:
 *   - writes the HTML the way the site has always been published: "<!doctype html>" in lower case
 *     (Astro writes "<!DOCTYPE html>"), empty SVG elements self-closed ("<path .../>"), "&amp;" for an
 *     ampersand in attribute values (Astro writes "&#38;") and a final newline in each file;
 *   - writes site/_headers (security and cache headers for Cloudflare; X-Robots-Tag while NOINDEX is on);
 *   - with ADS_ENABLED copies the demo ad creatives (src/assets/demo) to site/img/demo; without it checks
 *     that nothing about selling ads is left in the site.
 */
import { copyFileSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const SELF = /<(path|circle|rect|use|ellipse|line|polyline|polygon|stop)((?:\s[^<>]*)?)><\/\1>/g;
const walk = (d) => readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(d, e.name)) : [join(d, e.name)]));

export default function htmlPolish({ noindex, ads, demoDir }) {
  return {
    name: 'html-polish',
    hooks: {
      'astro:build:done': ({ dir }) => {
        const out = fileURLToPath(dir);
        for (const f of walk(out)) {
          if (!f.endsWith('.html')) continue;
          const src = readFileSync(f, 'utf8');
          let polished = src.replace(/^<!DOCTYPE html>/, '<!doctype html>').replace(SELF, '<$1$2/>').replace(/&#38;/g, '&amp;');
          if (!polished.endsWith('\n')) polished += '\n';
          if (polished !== src) writeFileSync(f, polished);
        }
        writeFileSync(join(out, '_headers'), '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n'
          + '  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()\n' + (noindex ? '  X-Robots-Tag: noindex, nofollow\n' : '')
          + '\n/img/*\n  Cache-Control: public, max-age=2592000\n\n/logos/*\n  Cache-Control: public, max-age=2592000\n\n/assets/*\n  Cache-Control: public, max-age=2592000\n');
        if (ads) {
          mkdirSync(join(out, 'img', 'demo'), { recursive: true });
          for (const f of readdirSync(demoDir)) copyFileSync(join(demoDir, f), join(out, 'img', 'demo', f));
        } else {
          // nothing about selling ads may be left (only words like "oglas" in the privacy policy)
          const left = [];
          for (const f of walk(out)) {
            if (!/\.(html|txt|xml|json)$/.test(f)) continue;
            const t = readFileSync(f, 'utf8');
            for (const w of ['oglasavanje', 'oglasi@', 'Zakupi', 'zakup-0', 'primer-oglasa', 'rs-note">', 'mesečni zakup']) if (t.includes(w)) left.push([relative(out, f), w]);
            const body = f.endsWith('.html') ? t.replace(/<script[\s\S]*?<\/script>/g, '') : t;
            for (const m of body.matchAll(/ogla[sš]|sponzor|reklam/gi)) left.push([relative(out, f), body.slice(Math.max(0, m.index - 30), m.index + 20)]);
          }
          if (left.length) throw new Error('ADS_ENABLED is false but ad references remain: ' + JSON.stringify(left.slice(0, 10)));
        }
      },
    },
  };
}
