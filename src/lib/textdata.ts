/** The machine-readable extras: sitemap, robots.txt, llms.txt, llms-full.txt and podaci/modeli.json. */
import { ADS_ENABLED, DOMAIN, SITE, UPDATED } from '../config';
import { CATS } from './lists';
import { ALL_IDS, DIMS, ORDER, brands, citiesOf, kwhTxt, models, rangeTxt } from './site';
import { joinSr, mm, pyjson } from './util';

/** Every page address (without .html), the way the old build listed them: index first, then sorted. */
export function pageList(): string[] {
  const pages = ['brendovi', 'distributeri', 'kalkulator-troskova', 'kontakt', 'modeli', 'najveci-domet', 'o-nama', 'politika-privatnosti',
    'punjaci', 'subvencije-elektricni-automobili-2026', 'uporedi', ...(ADS_ENABLED ? ['oglasavanje'] : []), ...CATS.map((c) => c.path),
    ...ORDER.map((s) => `brendovi/${s}`), ...ALL_IDS.map((i) => `modeli/${i}`)];
  return ['index', ...pages.map((p) => p + '.html').sort().map((p) => p.slice(0, -5))];
}

export function sitemap(): string {
  const pri = (p: string) => (p === 'index' ? '1.0' : p.startsWith('brendovi/') || p.startsWith('modeli/') || p === 'modeli' || p === 'brendovi' ? '0.8' : '0.7');
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + pageList().map((p) => `  <url><loc>${DOMAIN}/${p === 'index' ? '' : p}</loc><lastmod>${UPDATED}</lastmod><priority>${pri(p)}</priority></url>\n`).join('')
    + '</urlset>\n';
}

// AI assistants and search engines are welcome: named explicitly so no crawler policy defaults block them
const AI_BOTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User',
  'Google-Extended', 'Googlebot', 'Bingbot', 'Applebot', 'Applebot-Extended', 'DuckAssistBot', 'meta-externalagent', 'MistralAI-User', 'CCBot'];
export const robots = () => AI_BOTS.map((b) => `User-agent: ${b}\n`).join('') + `Allow: /\n\nUser-agent: *\nAllow: /\n\nSitemap: ${DOMAIN}/sitemap.xml\n`;

export function llms(): string {
  const lines = [`# ${SITE}`, '', '> Nezvanični informativni sajt o potpuno električnim automobilima koji se prodaju u Srbiji: modeli, domet (WLTP), baterija i kontakti ovlašćenih distributera. Hibridi nisu uključeni.', '',
    '## Glavne stranice', `- [Svi modeli](${DOMAIN}/modeli): ${ALL_IDS.length} električnih modela`, `- [Brendovi](${DOMAIN}/brendovi)`,
    `- [Najveći domet](${DOMAIN}/najveci-domet)`, `- [Distributeri po gradovima](${DOMAIN}/distributeri)`, `- [Punjači za električne automobile (mapa)](${DOMAIN}/punjaci)`,
    `- [Subvencije 2026](${DOMAIN}/subvencije-elektricni-automobili-2026)`, `- [Kalkulator troškova](${DOMAIN}/kalkulator-troskova): trošak struje u odnosu na benzin i dizel`, `- [Uporedi modele](${DOMAIN}/uporedi): poređenje do tri modela`,
    `- [O nama](${DOMAIN}/o-nama): izvori podataka i metodologija`, `- [Kontakt](${DOMAIN}/kontakt)`, '',
    '## Kompletni podaci', `- [llms-full.txt](${DOMAIN}/llms-full.txt): svi modeli sa dometom, baterijom, dimenzijama i gradovima distributera, na jednom mestu`,
    `- [modeli.json](${DOMAIN}/podaci/modeli.json): isti podaci u JSON formatu`, '', '## Brendovi'];
  lines.push(...ORDER.map((s) => `- [${brands[s].name}](${DOMAIN}/brendovi/${s}): ` + brands[s].models.map((i) => models[i].full).join(', ')));
  lines.push('', '## Modeli');
  lines.push(...ALL_IDS.map((i) => `- [${models[i].full}](${DOMAIN}/modeli/${i}): ${models[i].cls || 'električni automobil'}`
    + (models[i].r ? `, domet ${rangeTxt(models[i], true)} (WLTP)` : '') + (models[i].kwh ? `, baterija ${kwhTxt(models[i])}` : '')));
  return lines.join('\n') + '\n';
}

function dims(i: string): Record<string, string | number> {
  const d = DIMS[i] ?? ({} as any);
  const out: Record<string, string | number> = {};
  if (d.length_txt || d.length_mm) out.duzina = d.length_txt || mm(d.length_mm)!;
  if (d.width_mm) out.sirina = mm(d.width_mm) + (d.width_folded ? ' (sa sklopljenim retrovizorima)' : '');
  if (d.height_txt || d.height_mm) out.visina = d.height_txt || mm(d.height_mm)!;
  if (d.clearance_mm) out.klirens = mm(d.clearance_mm) + (d.clearance_laden ? ' (pod opterećenjem)' : '');
  if (d.seats) out.broj_sedista = d.seats;
  return out;
}
const LABELS: Record<string, string> = { duzina: 'Dužina', sirina: 'Širina', visina: 'Visina', klirens: 'Klirens', broj_sedista: 'Broj sedišta' };

/** llms-full.txt and podaci/modeli.json share one pass over the catalogue. */
export function fullData(): { text: string; json: string } {
  const nBrands = ORDER.filter((x) => brands[x].models.length).length;
  const full = [`# ${SITE}: kompletni podaci`, '',
    '> Nezavisan informativni sajt o potpuno električnim automobilima (BEV) koji se zvanično prodaju u Srbiji. Bez hibrida. Bez cena.',
    '> Domet je po WLTP normi, za verziju sa najvećim dometom. Podaci su sa zvaničnih sajtova proizvođača i uvoznika. Prazno polje znači da proizvođač podatak ne objavljuje.',
    `> Ukupno: ${ALL_IDS.length} modela, ${nBrands} brendova. Poslednje ažuriranje: ${UPDATED}.`, ''];
  const data: unknown[] = [];
  for (const s of ORDER) {
    const b = brands[s];
    if (!b.models.length) continue;
    const cities = citiesOf(s);
    full.push(`## ${b.name}`, `Stranica: ${DOMAIN}/brendovi/${s}`,
      cities.length ? `Ovlašćeni distributeri u gradovima: ${joinSr(cities)}.` : 'Ovlašćeni distributeri: lista nije objavljena.', '');
    for (const i of b.models) {
      const m = models[i], dd = dims(i);
      full.push(`### ${m.full}`, `- Stranica: ${DOMAIN}/modeli/${i}`, `- Klasa: ${m.cls || 'električni automobil'}`, '- Pogon: 100% električni');
      if (m.r) full.push(`- Domet (WLTP): ${rangeTxt(m, true)}`);
      if (m.kwh) full.push(`- Baterija: ${kwhTxt(m)}`);
      full.push(...Object.entries(dd).map(([k, v]) => `- ${LABELS[k]}: ${v}`));
      full.push('');
      data.push({ id: i, brend: b.name, model: m.full, url: `${DOMAIN}/modeli/${i}`, klasa: m.cls,
        domet_wltp_km: m.r, domet_tekst: m.r ? rangeTxt(m, true) : null, baterija: m.kwh ? kwhTxt(m) : null,
        gradovi_distributera: cities, ...dd });
    }
  }
  full.push('## Ostalo', `- Subvencije 2026: ${DOMAIN}/subvencije-elektricni-automobili-2026`,
    `- Distributeri po gradovima: ${DOMAIN}/distributeri`, `- Kalkulator troškova (struja i gorivo): ${DOMAIN}/kalkulator-troskova`, `- Mapa punjača: ${DOMAIN}/punjaci`, `- Uporedi modele: ${DOMAIN}/uporedi`,
    '- Kontakt i ispravke podataka: office@evomobil.rs', '');
  const json = pyjson({ izvor: SITE, url: DOMAIN + '/', azurirano: UPDATED, napomena: 'Domet po WLTP normi; podaci sa zvaničnih sajtova proizvođača i uvoznika; null = nije objavljeno.', modeli: data }, { indent: 1 });
  return { text: full.join('\n'), json };
}
