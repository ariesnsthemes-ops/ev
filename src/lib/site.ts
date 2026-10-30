/**
 * The catalogue: brands and their electric models, built from
 *   data/brands.json         brands and models (ranges, batteries, what is listed)
 *   data/brand_content.json  brand texts, importers and dealers
 *   data/model_content.json  model descriptions, battery and range text
 *   data/model_dims.json     dimensions and seats (official sources only)
 */
import brandsJson from '../data/brands.json';
import contentJson from '../data/brand_content.json';
import mcontentJson from '../data/model_content.json';
import dimsJson from '../data/model_dims.json';
import { asciiKey, num, slugify } from './util';

export interface Dealer {
  city: string; name: string; role?: string; address?: string; zip?: string;
  phone?: string | string[]; phone_label?: string; email?: string | string[]; website?: string; hours?: string;
}
export interface Brand {
  slug: string; name: string; data_slug: string; logo: string; founded?: string | null; hq?: string | null;
  importer?: string | null; intro?: string; about: string[]; dealers: Dealer[]; models: string[];
}
export interface Model {
  id: string; b: string; n: string; full: string; cls: string | null; sil: string | null;
  r: number | null; rt: string | null; kwh: number | null; desc: string[] | null; lg: boolean;
  photo: string | null; tags: string[]; body: string | undefined;
  /** optional hand-written texts from model_content.json: hero paragraphs, gearbox wording, FAQ answers (range, battery, buy, hybrid) */
  intro?: string[]; gearbox?: string; faq?: Record<string, string>;
}
export interface Dims {
  id: string; length_mm?: number | null; width_mm?: number | null; height_mm?: number | null; clearance_mm?: number | null;
  seats?: number | null; length_txt?: string | null; height_txt?: string | null; width_folded?: boolean; clearance_laden?: boolean;
}

const ID_KEEP: Record<string, string> = { 'toyota|C-HR+': 'toyota-c-hr-plus', 'bmw|i4 M60': 'bmw-i4-m50', 'bmw|iX M70': 'bmw-ix-m-model', 'bmw|i5 M60': 'bmw-i5' };

function modelId(brandSlug: string, brandName: string, modelName: string): string {
  let n = modelName;
  if (n.toLowerCase().startsWith(brandName.toLowerCase() + ' ')) n = n.slice(brandName.length + 1);
  // renamed models keep their original page address
  return ID_KEEP[brandSlug + '|' + n] ?? brandSlug + '-' + slugify(n);
}

/** Photo file per model id (img/<file> and img/<file minus .webp>-640.webp). */
const PHOTO_IDS = ['kia-ev9', 'porsche-cayenne-turbo-electric', 'bmw-i4-m50', 'bmw-ix-m-model', 'bmw-i7-m70', 'bmw-i4', 'bmw-i5', 'bmw-ix', 'bmw-ix3', 'bmw-ix5', 'bmw-i3', 'bmw-ix1', 'bmw-i7',
  'hyundai-ioniq-5', 'hyundai-ioniq-6', 'hyundai-ioniq-6-n', 'hyundai-ioniq-9', 'hyundai-inster', 'cupra-tavascan', 'mazda-cx-6e', 'mazda-6e', 'cupra-raval', 'dacia-spring', 'kia-ev6', 'kia-ev4', 'kia-ev3', 'kia-ev2',
  'porsche-macan-4', 'porsche-taycan-4', 'ford-explorer', 'toyota-bz4x', 'toyota-bz4x-touring', 'toyota-c-hr-plus', 'ford-mustang-mach-e', 'ford-puma-gen-e', 'renault-twingo-e-tech', 'renault-5-e-tech', 'renault-4-e-tech',
  'suzuki-e-vitara', 'volkswagen-id-polo', 'volkswagen-id-3-neo', 'volkswagen-id-4', 'volkswagen-id-5', 'volkswagen-id-7', 'foton-etunland', 'byd-dolphin-surf', 'byd-atto-2-comfort', 'byd-atto-3-evo', 'byd-seal', 'byd-sealion-7',
  'mg-mg4-electric', 'mg-mg5-electric', 'mg-mgs5-ev', 'changan-deepal-s05', 'changan-deepal-s07', 'geely-e5', 'dongfeng-box', 'jac-t9-ev', 'jac-e30x', 'jmev-ev3', 'jmev-elight', 'leapmotor-b03x', 'leapmotor-b05', 'leapmotor-b10',
  'leapmotor-c10', 'leapmotor-t03', 'mini-countryman', 'mini-aceman', 'mini-cooper', 'opel-astra-electric', 'opel-frontera-electric', 'opel-mokka-electric', 'citroen-e-c3', 'citroen-e-c3-aircross', 'citroen-e-c4', 'citroen-e-c4-x',
  'skoda-elroq', 'skoda-enyaq', 'skoda-enyaq-coupe', 'volvo-ex30', 'volvo-ex60', 'volvo-ex90', 'volvo-es90', 'porsche-macan-4s', 'peugeot-e-208', 'peugeot-e-2008', 'peugeot-e-308', 'peugeot-e-3008'];
const PHOTO_FILES: Record<string, string> = Object.fromEntries(PHOTO_IDS.map((i) => [i, `evomobil-${i}.webp`]));

const BODY: Record<string, [string, string | null]> = {
  SUV: ['SUV', 'suv'], 'Hečbek': ['Hečbek', 'hatch'], Sedan: ['Sedan', 'sedan'], Karavan: ['Karavan', 'sedan'],
  'Gradski automobil': ['Gradski', 'hatch'], Pikap: ['Pikap', null],
};
const NOT_PASSENGER = new Set(['Kombi', 'Kamion', 'Autobus']);
const LOGO_IMG = new Set(['jmev-ewind', 'lynk-co-02', 'audi-rs-e-tron-gt']); // shown with the faded brand logo until a photo exists
const DISPLAY: Record<string, string> = { 'byd-atto-2-comfort': 'Atto 2' };
const TAGS: Record<string, string> = { SUV: 'suv', 'Hečbek': 'hatch', Sedan: 'sedan', Pikap: 'pickup', 'Gradski automobil': 'city hatch', Karavan: 'wagon' };
const CITY = new Set(['byd-dolphin-surf', 'jmev-ev3', 'leapmotor-t03', 'dongfeng-box', 'jac-e30x']);
export const CLS_WORD: Record<string, string> = {
  Gradski: 'gradski automobil', 'Hečbek': 'hečbek', Karavan: 'karavan', Pikap: 'pikap', Sedan: 'sedan', SUV: 'SUV', Crossover: 'crossover',
};

const data: Record<string, any> = Object.fromEntries((brandsJson as any).brands.map((b: any) => [b.slug, b]));
const content = contentJson as Record<string, any>;
const mcontent = mcontentJson as Record<string, any>;

export const brands: Record<string, Brand> = {};
export const models: Record<string, Model> = {};

for (const [slug, c] of Object.entries(content)) {
  if (slug.startsWith('_')) continue;
  const d = data[c.data_slug];
  const ids: string[] = [];
  for (const m of d.models) {
    if (!(m.powertrain || '').startsWith('EV') || m.listed_on_site === false || NOT_PASSENGER.has(m.body)) continue;
    const mid = modelId(slug, c.name, m.name);
    let [cls, sil] = BODY[m.body] ?? [null, null];
    if (mid === 'lynk-co-02') cls = 'Crossover';
    const mc = mcontent[mid] ?? {};
    let n = m.name.toLowerCase().startsWith(c.name.toLowerCase() + ' ') ? m.name.slice(c.name.length + 1) : m.name;
    n = DISPLAY[mid] ?? n;
    let full = m.name.toLowerCase().startsWith(c.name.toLowerCase()) ? m.name : c.name + ' ' + n;
    if (mid === 'byd-atto-2-comfort') full = 'BYD Atto 2';
    const t = TAGS[m.body] ?? '';
    const tags = t + (CITY.has(mid) && !t.includes('city') ? ' city' : '');
    models[mid] = {
      id: mid, b: slug, n, full, cls, sil, r: m.range_wltp_km ?? null, rt: mc.range_text ?? null, kwh: mc.kwh ?? null,
      desc: mc.desc ?? null, lg: LOGO_IMG.has(mid), photo: PHOTO_FILES[mid] ?? null, tags: tags.split(' ').filter(Boolean), body: m.body,
      ...(mc.intro ? { intro: mc.intro } : {}), ...(mc.gearbox ? { gearbox: mc.gearbox } : {}), ...(mc.faq ? { faq: mc.faq } : {}),
    };
    ids.push(mid);
  }
  brands[slug] = { ...c, slug, models: ids };
}

/** Brand slugs in alphabetical order (diacritics ignored). */
export const ORDER: string[] = Object.keys(brands).sort((a, b) => (asciiKey(brands[a].name) < asciiKey(brands[b].name) ? -1 : asciiKey(brands[a].name) > asciiKey(brands[b].name) ? 1 : 0));
/** Every listed model id, brand by brand. */
export const ALL_IDS: string[] = ORDER.flatMap((s) => brands[s].models);

export const DIMS: Record<string, Dims> = Object.fromEntries((dimsJson as Dims[]).map((r) => [r.id, r]));

export const rangeTxt = (m: Model, long = false): string | null => {
  if (long && m.rt) return 'do ' + m.rt;
  return m.r ? `do ${m.r} km` : null;
};
export const kwhTxt = (m: Model): string | null => (m.kwh ? num(m.kwh) + ' kWh' : null);

/** Dealer cities of a brand, Beograd first, then alphabetical. */
export function citiesOf(slug: string): string[] {
  const seen: string[] = [];
  for (const d of brands[slug].dealers) if (!seen.includes(d.city) && d.city !== 'Srbija') seen.push(d.city);
  return seen.sort((a, b) => {
    const ka = a !== 'Beograd' ? 1 : 0, kb = b !== 'Beograd' ? 1 : 0;
    if (ka !== kb) return ka - kb;
    return a < b ? -1 : a > b ? 1 : 0;
  });
}

export const modelsOf = (ids: string[]) => ids.map((i) => models[i]);
export const byRangeDesc = (ids: string[]) => [...ids].sort((a, b) => (models[b].r || 0) - (models[a].r || 0));
