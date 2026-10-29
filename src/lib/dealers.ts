/** Dealers grouped by city for the Distributeri page: the same showroom listed under several brands is kept once. */
import { ORDER, brands, type Dealer } from './site';
import { lst } from './util';

export interface CityEntry { d: Dealer; brands: string[] }

const byCity: Record<string, Record<string, CityEntry>> = {};
for (const s of ORDER) {
  for (const d of brands[s].dealers) {
    if (d.city === 'Srbija') continue;
    const key = d.name.toLowerCase().replaceAll('d.o.o', '').replaceAll('doo', '').replace(/[^a-z0-9]/g, '') + '|' + lst(d.phone || ['']) [0].replace(/\D/g, '').slice(-6);
    const city = (byCity[d.city] ??= {});
    const entry = (city[key] ??= { d, brands: [] });
    if (!entry.brands.includes(brands[s].name)) entry.brands.push(brands[s].name);
  }
}

/** Cities: Beograd, Novi Sad, Niš first, then alphabetical. */
export const cityOrder = Object.keys(byCity).sort((a, b) => {
  const k = (c: string) => [c !== 'Beograd' ? 1 : 0, c !== 'Novi Sad' ? 1 : 0, c !== 'Niš' ? 1 : 0];
  const ka = k(a), kb = k(b);
  for (let i = 0; i < 3; i++) if (ka[i] !== kb[i]) return ka[i] - kb[i];
  return a < b ? -1 : a > b ? 1 : 0;
});
export const dealersByCity = byCity;
export const cityEntries = (c: string) => Object.values(byCity[c]);
export const dealerCount = cityOrder.reduce((n, c) => n + cityEntries(c).length, 0);
