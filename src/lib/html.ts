/**
 * Markup building blocks shared by several pages (model cards, comparison tables, breadcrumbs,
 * FAQ blocks, dealer cards) and the JSON-LD helpers. They return HTML strings; the pages insert
 * them with <Fragment set:html={...} />.
 */
import { DOMAIN, NOTE } from '../config';
import { brands, citiesOf, kwhTxt, models, rangeTxt, type Dealer, type Model } from './site';
import { E, lst } from './util';

/** Address of a page without ".html" (Cloudflare serves /modeli from modeli.html). `pre` is '', '../' or '/'. */
export const link = (pre: string, path: string, hash = '') => {
  path = path.replace(/\.html$/, '');
  if (path === 'index' || path === '') return (pre || './') + (hash ? '#' + hash : '');
  return pre + path + (hash ? '#' + hash : '');
};
export const abs = (path: string) => DOMAIN + '/' + path.replace(/\.html$/, '').replace(/^index$/, '');

export const logoStyle = (slug: string, pre: string) => `--l:url(${pre}logos/${brands[slug].logo})`;

/** Brand logo as an <img> (dark in the light theme, white in the dark theme, see .blogo.has-img in site.css). */
export function logoSpan(slug: string, pre: string, cls = ''): string {
  const sq = ['dongfeng.svg', 'geely.svg', 'jmev.png', 'leapmotor.svg', 'mg.svg'].includes(brands[slug].logo) && cls !== 'nosq' ? ' sq' : '';
  return `<span class="blogo${sq} has-img" aria-hidden="true"><img src="${pre}logos/${brands[slug].logo}" alt="" decoding="async"></span>`;
}

const VB: Record<string, string> = { sedan: '0 0 320 112', hatch: '0 0 320 112', suv: '0 0 320 120' };

export type PictureKind = 'photo' | 'lg' | 'sil' | 'ph';
/** Photo (with 640 px variant), faded brand logo, silhouette or "FOTOGRAFIJA USKORO". */
export function picture(m: Model, pre: string): [string, PictureKind] {
  if (m.photo) {
    const big = `${pre}img/${m.photo}`, small = big.slice(0, -5) + '-640.webp';
    return [`<img src="${small}" srcset="${small} 640w, ${big} 1280w" sizes="(max-width: 620px) 48vw, (max-width: 1000px) 46vw, 400px" alt="${E(m.full)}" loading="lazy" decoding="async">`, 'photo'];
  }
  if (m.lg) return [`<span class="blogo has-img" aria-hidden="true"><img src="${pre}logos/${brands[m.b].logo}" alt="" decoding="async"></span>`, 'lg'];
  if (m.sil) return [`<svg viewBox="${VB[m.sil]}" aria-hidden="true"><use href="#car-${m.sil}"/></svg>`, 'sil'];
  return ['FOTOGRAFIJA USKORO', 'ph'];
}

export const CMP_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h14m0 0-3.5-3.5M18 8l-3.5 3.5M20 16H6m0 0 3.5-3.5M6 16l3.5 3.5"/></svg>';

/** Model card. `attrs` adds data attributes to <article class="mcard"> (homepage and catalogue filters read them). */
export function card(mid: string, pre: string, bigSpecs = true, attrs = ''): string {
  const m = models[mid], b = brands[m.b];
  const href = link(pre, `modeli/${mid}`);
  const [inner, kind] = picture(m, pre);
  const kcls = { photo: ' photo', lg: ' lg', sil: '', ph: ' ph' }[kind];
  const f = (k: string, v: string | null) => `<div><dt>${k}</dt><dd${v ? '' : ' class=na'}>${v ? E(v) : 'Na upit'}</dd></div>`;
  const specs = f('DOMET (WLTP)', rangeTxt(m)) + f('KLASA', m.cls) + (bigSpecs ? f('BATERIJA', kwhTxt(m)) + f('POGON', 'Električni') : '');
  return `<article class="mcard"${attrs}><button type="button" class="cmp-add" data-cmp="${mid}" aria-pressed="false" aria-label="Dodaj u poređenje" title="Dodaj u poređenje">${CMP_ICON}</button><a class="img${kcls}" href="${href}" tabindex="-1" aria-hidden="true">${inner}</a><div class="body">`
    + `<div><div class="mk">${E(b.name.toUpperCase())}</div><h3><a href="${href}">${E(m.n)}</a></h3></div>`
    + `<div class="tags"><span class="tag">100% EV</span>${m.cls ? `<span class="tag gray">${E(m.cls.toUpperCase())}</span>` : ''}</div>`
    + `<dl class="feat">${specs}</dl>`
    + `<a href="${href}" class="btn btn-dark">Detalji modela <span class="arr">→</span></a></div></article>`;
}

export function cmpTable(ids: string[], pre: string, rank = false, brandCol = true): string {
  const head = (rank ? '<th class="rank">#</th>' : '') + '<th>Model</th>' + (brandCol ? '<th>Brend</th>' : '') + '<th>Klasa</th><th>Domet (WLTP)</th><th>Baterija</th>';
  let rows = '';
  ids.forEach((mid, k) => {
    const m = models[mid];
    rows += '<tr>' + (rank ? `<td class="rank">${k + 1}.</td>` : '') + `<td><a href="${link(pre, `modeli/${mid}`)}">${E(m.full)}</a></td>`
      + (brandCol ? `<td><a href="${link(pre, `brendovi/${m.b}`)}">${E(brands[m.b].name)}</a></td>` : '')
      + `<td>${E(m.cls || 'Na upit')}</td><td class="n">${E(rangeTxt(m, true) || 'Na upit')}</td><td class="n">${E(kwhTxt(m) || 'Na upit')}</td></tr>`;
  });
  return `<div class="tbl-wrap"><table class="cmp"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

export type Crumb = [string, string];
export function crumbs(items: Crumb[], pre: string): string {
  const out = items.map(([name, href], i) => i === items.length - 1 ? `<span aria-current="page">${E(name)}</span>` : `<a href="${link(pre, href)}">${E(name)}</a>`);
  return '<nav class="crumbs" aria-label="Putanja">' + out.join('<span aria-hidden="true">/</span>') + '</nav>';
}
export const ldBreadcrumbs = (items: Crumb[]) => ({
  '@context': 'https://schema.org', '@type': 'BreadcrumbList',
  itemListElement: items.map(([n, h], i) => ({ '@type': 'ListItem', position: i + 1, name: n, item: abs(h) })),
});

export type QA = [string, string];
export const qaBlock = (pairs: QA[]) =>
  '<div class="qa">' + pairs.map(([q, a]) => `<details><summary>${E(q)}<span class="pm" aria-hidden="true">+</span></summary><p>${E(a)}</p></details>`).join('') + '</div>';
export const ldFaq = (pairs: QA[]) => ({
  '@context': 'https://schema.org', '@type': 'FAQPage',
  mainEntity: pairs.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })),
});
export const ldItemList = (name: string, ids: string[], order?: string) => ({
  '@context': 'https://schema.org', '@type': 'ItemList', name,
  ...(order ? { itemListOrder: order } : {}),
  itemListElement: ids.map((i, k) => ({ '@type': 'ListItem', position: k + 1, url: abs(`modeli/${i}`), name: models[i].full })),
});

// ------------------------------------------------------------------ dealers
const tel = (n: string) => `<a href="tel:${E(n.replace('(0)', '').replace(/[^+\d]/g, ''))}">${E(n)}</a>`;
const drow = (label: string, value: string | null | undefined, lnk?: string | null) => (value ? `<div><dt>${label}</dt><dd>${lnk || E(value)}</dd></div>` : '');

/** Drop the "servis" part of a role: the site is about sales. */
function noService(t?: string): string | undefined {
  if (!t) return t;
  t = t.replace(/\s*\((?:[^)]*\bservis[\p{L}\p{N}_]*[^)]*)\)/giu, '');
  t = t.replace(/\s*(?:\bi\b|,|\/|\+|&)\s*servis[\p{L}\p{N}_]*/giu, '');
  t = t.replace(/\bservis[\p{L}\p{N}_]*\s*(?:\bi\b|,|\/|\+|&)\s*/giu, '');
  return /servis/i.test(t) ? 'Prodaja' : t.trim();
}

export function dealerCard(d0: Dealer, extraHead = '', attrs = ''): string {
  const d = { ...d0, role: noService(d0.role), phone_label: noService(d0.phone_label) };
  const emails = d.email ? lst(d.email) : [];
  const longEmail = emails.some((x) => x.length > 20); // too long for half a phone-width card: give it its own full-width row
  const emailRow = emails.length ? `<div${longEmail ? ' class=wide' : ''}><dt>EMAIL</dt><dd>${emails.map(E).join('<br>')}</dd></div>` : '';
  const hoursRow = '<div><dt>RADNO VREME</dt>' + (d.hours ? `<dd>${E(d.hours)}</dd>` : '<dd class="na">Proverite kod distributera</dd>') + '</div>';
  const rows = drow('ADRESA', d.address) + drow('GRAD', d.zip || (d.city !== 'Srbija' ? d.city : null))
    + drow(d.phone_label || 'TELEFON', d.phone ? lst(d.phone).join(',') : null, d.phone ? lst(d.phone).map(tel).join('<br>') : null)
    + drow('WEBSITE', d.website, d.website ? `<a href="https://${E(d.website)}" target="_blank" rel="nofollow noopener">${E(d.website)} ↗</a>` : null)
    + (longEmail ? hoursRow + emailRow : emailRow + hoursRow);
  return `<article class="dcard"${attrs} data-city="${E(d.city)}"><div class="dcard-head"><h3>${E(d.name)}</h3>`
    + `<span class="tag gray">${E((d.role || '').toUpperCase())}</span>${extraHead}</div><dl class="dgrid">${rows}</dl></article>`;
}

export function dealerSection(slug: string, title: string): string {
  const b = brands[slug];
  if (!b.dealers.length) {
    return '<section class="sec alt" id="kontakt-distributera"><div class="wrap"><h2>' + E(title) + '</h2>'
      + '<p class="answer">Lista ovlašćenih distributera za ovaj brend još nije objavljena. Proverite aktuelne kontakte na zvaničnom sajtu brenda ili uvoznika.</p></div></section>';
  }
  const cities = citiesOf(slug);
  const idx = (d: Dealer) => (cities.includes(d.city) ? cities.indexOf(d.city) : 99);
  const dealers = [...b.dealers].sort((x, y) => idx(x) - idx(y));
  const opts = cities.map((c) => `<option value="${E(c)}">${E(c)}</option>`).join('');
  const hint = cities.length > 1 ? (cities.length > 4 ? `Distributeri u ${cities.length} gradova.` : `Distributeri u ${cities.length} grada.`) : '';
  const single = cities.length <= 1 ? ' single' : '';
  return `
  <section class="sec alt" id="kontakt-distributera">
    <div class="wrap">
      <h2 class="h2s">${E(title)}</h2>
      <div class="dealer${single}">
        <div class="dealer-side">
          <label class="lbl" for="city-sel">IZABERITE GRAD</label>
          <div class="city"><select id="city-sel">${opts}</select></div>
          <p class="hint">${hint}</p>
        </div>
        <div class="dealer-main" id="dealer-main">${dealers.map((d) => dealerCard(d)).join('')}
          <dl class="dnote"><dt>NAPOMENA</dt><dd>${NOTE}</dd></dl>
        </div>
      </div>
    </div>
  </section>`;
}

const DAYS: Record<string, string> = { pon: 'Mo', uto: 'Tu', sre: 'We', 'čet': 'Th', pet: 'Fr', sub: 'Sa', ned: 'Su', ponedeljak: 'Mo', petak: 'Fr', subota: 'Sa', nedelja: 'Su' };
/** 'Pon-Pet 08:00-17:00, sub 09:00-14:00' -> ['Mo-Fr 08:00-17:00', 'Sa 09:00-14:00'] (skips what it can't read). */
function openingHours(text?: string): string[] {
  const out: string[] = [];
  for (let part of (text || '').split(',')) {
    part = part.trim().toLowerCase();
    const m = part.match(/^([a-zčćšžđ]+)(?:\s*-\s*([a-zčćšžđ]+))?(?:\s+i\s+([a-zčćšžđ]+))?\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$/);
    if (!m) continue;
    const [, a, b2, c2, t1, t2] = m;
    if (!(a in DAYS)) continue;
    const d = DAYS[a] + (b2 && b2 in DAYS ? '-' + DAYS[b2] : '') + (c2 && c2 in DAYS ? ',' + DAYS[c2] : '');
    out.push(`${d} ${t1.padStart(5, '0')}-${t2.padStart(5, '0')}`);
  }
  return out;
}

export function ldDealer(d: Dealer, brandNames: string[]) {
  const zipm = (d.zip || '').match(/^(\d{5})\s+(.*)/s);
  const addr: Record<string, unknown> = { '@type': 'PostalAddress', streetAddress: d.address ?? null, addressLocality: zipm ? zipm[2] : d.zip || d.city, addressCountry: 'RS' };
  if (zipm) addr.postalCode = zipm[1];
  const o: Record<string, unknown> = { '@context': 'https://schema.org', '@type': 'AutoDealer', name: d.name, address: addr, brand: brandNames.map((n) => ({ '@type': 'Brand', name: n })) };
  if (d.phone) o.telephone = lst(d.phone)[0];
  if (d.email) o.email = lst(d.email)[0];
  if (d.website) o.url = 'https://' + d.website;
  const oh = openingHours(d.hours);
  if (oh.length) o.openingHours = oh;
  return o;
}
