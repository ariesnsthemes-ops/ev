/** Small helpers shared by the pages. */

/** HTML-escape (also quotes), for text that goes into markup or attributes. */
export const E = (t: unknown): string =>
  String(t ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');

export function slugify(t: string): string {
  t = t.toLowerCase().replace(/&/g, ' ').replace(/č/g, 'c').replace(/ć/g, 'c').replace(/š/g, 's').replace(/ž/g, 'z').replace(/đ/g, 'dj')
    .replace(/ë/g, 'e').replace(/é/g, 'e').replace(/è/g, 'e');
  return t.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

/** 64.8 -> "64,8" */
export const num = (v: unknown) => String(v).replace('.', ',');

/** 4997 -> "4.997 mm" */
export const mm = (v?: number | null) => (v ? String(v).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' mm' : null);

/** Meta description: at most n characters, cut at a word. */
export function short(t: string, n = 160): string {
  t = t.replace(/\s+/g, ' ').trim();
  if (t.length <= n) return t;
  const head = t.slice(0, n - 1);
  const cut = head.slice(0, head.lastIndexOf(' ')).replace(/[,;:]+$/, '');
  return cut + '…';
}

/** ["a", "b", "c"] -> "a, b i c" */
export function joinSr(items: string[]): string {
  items = [...items];
  return items.length === 1 ? items[0] : items.slice(0, -1).join(', ') + ' i ' + items[items.length - 1];
}

export function pluralModels(n: number): string {
  if (n % 10 === 1 && n % 100 !== 11) return `${n} električni model`;
  if (n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14)) return `${n} električna modela`;
  return `${n} električnih modela`;
}

export const lst = <T,>(v: T | T[]): T[] => (Array.isArray(v) ? v : [v]);

/** Sort key without diacritics (Škoda sorts under S, Citroën under C). */
export const asciiKey = (s: string) => s.normalize('NFKD').replace(/[^\x00-\x7f]/g, '').toLowerCase();

/**
 * JSON serialiser with the spacing of Python's json.dumps: ", " and ": " separators by default,
 * `compact` for separators=(',', ':'), `indent` for indent=N. Non-ASCII text is kept as is.
 */
/** A number that Python would hold as a float: pyjson prints 52 as "52.0". */
export class PyFloat { constructor(public v: number) {} }

export function pyjson(v: unknown, opts: { compact?: boolean; indent?: number } = {}): string {
  const sepI = opts.compact ? ',' : ', ';
  const sepK = opts.compact ? ':' : ': ';
  const ind = opts.indent;
  const str = (s: string) => JSON.stringify(s);
  const walk = (x: unknown, lvl: number): string => {
    if (x === null || x === undefined) return 'null';
    if (typeof x === 'string') return str(x);
    if (x instanceof PyFloat) return Number.isInteger(x.v) ? x.v.toFixed(1) : String(x.v);
    if (typeof x === 'number') return Number.isFinite(x) ? String(x) : 'null';
    if (typeof x === 'boolean') return x ? 'true' : 'false';
    if (Array.isArray(x)) {
      if (!x.length) return '[]';
      const parts = x.map((y) => walk(y, lvl + 1));
      if (ind === undefined) return '[' + parts.join(sepI) + ']';
      const pad = '\n' + ' '.repeat(ind * (lvl + 1));
      return '[' + pad + parts.join(',' + pad) + '\n' + ' '.repeat(ind * lvl) + ']';
    }
    const keys = Object.keys(x as object);
    if (!keys.length) return '{}';
    const parts = keys.map((k) => str(k) + sepK + walk((x as any)[k], lvl + 1));
    if (ind === undefined) return '{' + parts.join(sepI) + '}';
    const pad = '\n' + ' '.repeat(ind * (lvl + 1));
    return '{' + pad + parts.join(',' + pad) + '\n' + ' '.repeat(ind * lvl) + '}';
  };
  return walk(v, 0);
}

/** Thousands with "." (4997 -> 4.997), used in the JSON-LD free text. */
export const fmtInt = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

/** Capitalise the first letter only (Python str.capitalize lower-cases the rest). */
export const capitalize = (s: string) => (s ? s[0].toUpperCase() + s.slice(1).toLowerCase() : s);

/** Serbian Cyrillic -> Latin. */
const CYR_FROM = 'АБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШабвгдђежзијклљмнњопрстћуфхцчџш';
const CYR_TO = ['A','B','V','G','D','Đ','E','Ž','Z','I','J','K','L','Lj','M','N','Nj','O','P','R','S','T','Ć','U','F','H','C','Č','Dž','Š',
  'a','b','v','g','d','đ','e','ž','z','i','j','k','l','lj','m','n','nj','o','p','r','s','t','ć','u','f','h','c','č','dž','š'];
const CYR: Record<string, string> = {};
[...CYR_FROM].forEach((c, i) => (CYR[c] = CYR_TO[i]));
export const lat = (t?: string | null) => [...(t || '')].map((ch) => CYR[ch] ?? ch).join('').trim();

/** Python's round(x, 1): on the exact binary value, ties to even (13.25 -> 13.2, 13.35 -> 13.4). */
export function pyRound1(x: number): number {
  const neg = x < 0; x = Math.abs(x);
  const [int, frac = ''] = x.toPrecision(25).replace(/e.*$/, '').split('.');
  const tenth = +(frac[0] || '0');
  const rest = (frac.slice(1) || '0').replace(/0+$/, '');
  let t = tenth, carry = 0;
  if (rest === '5') { if (tenth % 2 === 1) t++; }   // exact tie: to even
  else if (rest > '5' || (rest.length > 1 && rest[0] >= '5')) t++;
  if (t === 10) { t = 0; carry = 1; }
  const v = (+int + carry) + t / 10;
  return neg ? -v : v;
}
