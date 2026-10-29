/** The model categories (list pages and the category links above the tables). */
import type { Model } from './site';

interface Cat { path: string; h1: string; nav: string; test: (m: Model) => boolean; desc: string }
export const CATS: Cat[] = [
  { path: 'elektricni-suv', h1: 'Električni SUV i crossover modeli u Srbiji', nav: 'Električni SUV', test: (m) => m.tags.includes('suv'),
    desc: 'Električni SUV i crossover modeli koji se prodaju u Srbiji: domet, baterija i distributeri.' },
  { path: 'elektricni-hecbek', h1: 'Električni hečbek automobili u Srbiji', nav: 'Hečbek', test: (m) => m.tags.includes('hatch'),
    desc: 'Kompaktni i mali električni hečbek automobili u Srbiji, sa dometom i kapacitetom baterije.' },
  { path: 'elektricni-sedani', h1: 'Električni sedani i karavani u Srbiji', nav: 'Sedan', test: (m) => m.tags.includes('sedan') || m.tags.includes('wagon'),
    desc: 'Električni sedani i karavani u Srbiji: domet, baterija i gde ih kupiti.' },
  { path: 'elektricni-pikapi', h1: 'Električni pikapi u Srbiji', nav: 'Pikap', test: (m) => m.tags.includes('pickup'),
    desc: 'Potpuno električni pikapi koji se prodaju u Srbiji, sa dometom, baterijom i distributerima.' },
  { path: 'gradski-elektricni-automobili', h1: 'Gradski električni automobili u Srbiji', nav: 'Gradski', test: (m) => m.tags.includes('city'),
    desc: 'Mali gradski električni automobili u Srbiji: domet, baterija i kontakti distributera.' },
];
export const NAV_ITEMS: [string, string][] = [['modeli', 'Svi modeli'], ...CATS.map((c): [string, string] => [c.path, c.nav]), ['najveci-domet', 'Najveći domet']];

