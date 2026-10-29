/**
 * Charger locations for the map page: Open Charge Map exports (data/chargers-ocm*.json), the
 * OpenStreetMap export (data/chargers-osm.geojson) and hand-added spots (data/chargers-extra.json),
 * merged so the same spot (within 60 m) is kept once.
 */
import ocm from '../data/chargers-ocm.json';
import ocmKos from '../data/chargers-ocm-kosovo.json';
import osm from '../data/chargers-osm.geojson?raw';
import extra from '../data/chargers-extra.json';
import srb from '../data/srb-outline.geo.json';
import kos from '../data/kos-outline.geo.json';
import { lat } from './util';

export interface Charger {
  id: string; name: string; lat: number; lng: number; addr: string; town: string; kw: number | null;
  conn: string[]; points: number | null; acc: string; app: boolean; down: boolean; seen: string;
}

const TOWN_FIX: Record<string, string> = {
  Belgrade: 'Beograd', Cacak: 'Čačak', Vrcin: 'Vrčin', Presevo: 'Preševo',
  // Kosovo and Metohija: Serbian place names
  Prishtina: 'Priština', 'Prishtinë': 'Priština', Ferizaj: 'Uroševac', Gjilan: 'Gnjilane', Lipjan: 'Lipljan',
  'Suharekë': 'Suva Reka', 'Fushë Kosovë': 'Kosovo Polje', Gracanica: 'Gračanica', Parallove: 'Paralovo',
  'Komuna e Drenasit / Opština Glogovac': 'Glogovac', 'Çagllavicë (Prishtinë)': 'Čaglavica', 'Pejë': 'Peć', Peja: 'Peć',
};
function town(t?: string | null): string {
  let s = lat(t);
  s = s.replace(/\s*Municipality$/, '');
  s = s.replace(/^Gradska opština\s+/, '');
  return TOWN_FIX[s] ?? s;
}

const CONN: Record<number, string> = { 33: 'CCS', 25: 'Tip 2', 1036: 'Tip 2', 2: 'CHAdeMO', 27: 'Tesla', 30: 'Tesla', 1: 'Tip 1' };
const ACCESS: Record<number, string> = { 1: 'javni', 4: 'javni', 5: 'javni', 7: 'javni', 6: 'gosti' }; // 2, 3 = private: left out
export const ACCESS_LAB: Record<string, string> = { javni: 'Javni', gosti: 'Za goste i kupce', nepoznato: 'Nepoznat pristup' };

const osmData = JSON.parse(osm as string);
export const HAS_OSM = Array.isArray(osmData.features) && osmData.features.length > 0;
const inSerbia = (la: number, ln: number) => la >= 41.8 && la <= 46.3 && ln >= 18.8 && ln <= 23.1;
const uniqSorted = (a: string[]) => [...new Set(a)].sort();

function chargerRows(): Charger[] {
  let raw: any[] = [...(ocm as any[]), ...(ocmKos as any[])];
  // drop entries with coordinates outside Serbia (some are entered with wrong coordinates)
  raw = raw.filter((x) => inSerbia(x.AddressInfo.Latitude, x.AddressInfo.Longitude));
  const rows: Charger[] = [];
  for (const x of raw) {
    if (x.UsageTypeID === 2 || x.UsageTypeID === 3) continue;
    const a = x.AddressInfo;
    const conns: any[] = x.Connections || [];
    const kws = conns.map((c) => c.PowerKW || 0);
    const mx = kws.length ? Math.max(...kws) : 0;
    rows.push({
      id: String(x.ID), name: lat(a.Title) || 'Punjač', lat: a.Latitude, lng: a.Longitude,
      addr: lat(a.AddressLine1), town: town(a.Town),
      kw: mx ? Math.round(mx) : null,
      conn: uniqSorted(conns.filter((c) => c.ConnectionTypeID in CONN).map((c) => CONN[c.ConnectionTypeID])),
      points: x.NumberOfPoints || conns.length || null,
      acc: ACCESS[x.UsageTypeID] ?? 'nepoznato',
      app: x.UsageTypeID === 4,
      down: !(x.StatusTypeID === 50 || x.StatusTypeID == null),
      seen: (x.DateLastVerified || x.DateLastStatusUpdate || x.DateCreated || '').slice(0, 10),
    });
  }
  // OpenStreetMap export (overpass-turbo.eu; see README "Punjači iz OpenStreetMap")
  if (HAS_OSM) {
    const OSM_SOCK: Record<string, string> = { type2_combo: 'CCS', type2: 'Tip 2', type2_cable: 'Tip 2', chademo: 'CHAdeMO',
      tesla_supercharger: 'Tesla', tesla_supercharger_ccs: 'CCS', type1: 'Tip 1', type1_combo: 'CCS' };
    const kwOf = (v: unknown) => {
      let nums = [...String(v ?? '').matchAll(/\d+(?:[.,]\d+)?/g)].map((m) => parseFloat(m[0].replace(',', '.')));
      nums = nums.map((n) => (n > 1000 ? n / 1000 : n));
      return nums.length ? Math.max(...nums) : 0;
    };
    for (const x of osmData.features || []) {
      let t = x.properties || {};
      t = t.tags || t; // overpass-turbo puts tags at the top level; some tools nest them under "tags"
      if (t.amenity !== 'charging_station' || t.access === 'private' || t.access === 'no' || t.disused === 'yes') continue;
      const g = x.geometry || {};
      const c = g.coordinates;
      if (!c) continue;
      let lng_: number, lat_: number;
      if (g.type === 'Point') { lng_ = c[0]; lat_ = c[1]; }
      else { // a way drawn as an area: use the middle of its outline
        const ring: number[][] = g.type === 'Polygon' ? c[0] : g.type === 'MultiPolygon' ? c[0][0] : c;
        lng_ = ring.reduce((s, p) => s + p[0], 0) / ring.length; lat_ = ring.reduce((s, p) => s + p[1], 0) / ring.length;
      }
      if (!inSerbia(lat_, lng_)) continue;
      const conns = uniqSorted(Object.entries(OSM_SOCK).filter(([k]) => ![undefined, '', 'no', '0'].includes(t['socket:' + k])).map(([, lab]) => lab));
      const kw = Math.max(...Object.keys(t).filter((k) => k.startsWith('socket:') && k.endsWith(':output')).map((k) => kwOf(t[k])), kwOf(t['charging_station:output']), kwOf(t.maxpower));
      let name = lat(t.name || t['name:sr-Latn'] || t.brand || t.operator || '') || 'Punjač';
      if (t.operator && !name.includes(lat(t.operator)) && name !== 'Punjač') name = `${name} (${lat(t.operator)})`;
      const street = [lat(t['addr:street']), t['addr:housenumber'] || ''].filter(Boolean).join(' ');
      const pts = String(t.capacity || '').match(/\d+/g);
      rows.push({ id: `o${x.id ?? rows.length}`.replace(/\//g, ''), name, lat: lat_, lng: lng_,
        addr: street, town: town(t['addr:city'] || t['addr:place'] || ''),
        kw: kw ? Math.round(kw) : null, conn: conns, points: pts ? parseInt(pts[0], 10) : null,
        acc: t.access === 'customers' ? 'gosti' : 'javni',
        app: String(t['authentication:app'] || '').includes('app') || t['authentication:app'] === 'yes',
        down: ['closed', 'broken', 'out_of_order'].includes(t.operational_status),
        seen: String(t.check_date || t['survey:date'] || '2000-01-01').slice(0, 10) });
    }
  }
  // extra chargers added by hand; they win over an Open Charge Map entry at the same spot (within 60 m)
  (extra as any[]).forEach((x, k) => {
    rows.push({ id: `x${k + 1}`, name: x.name, lat: parseFloat(x.lat), lng: parseFloat(x.lng),
      addr: x.address || '', town: x.town || '', kw: x.kw ?? null,
      conn: uniqSorted(x.connectors || []), points: x.points ?? null,
      acc: x.access || 'javni', app: !!x.app, down: !!x.down, seen: '9999-12-31' });
  });
  // the same place is often entered more than once: keep one entry per spot (within 60 m), the most recently checked
  rows.sort((a, b) => (a.seen < b.seen ? 1 : a.seen > b.seen ? -1 : 0));
  const kept: Charger[] = [];
  for (const r of rows) {
    const twin = kept.find((k) => Math.hypot((k.lat - r.lat) * 111000, (k.lng - r.lng) * 111000 * Math.cos((r.lat * Math.PI) / 180)) < 60);
    if (twin) {
      twin.conn = uniqSorted([...twin.conn, ...r.conn]);
      twin.kw = Math.max(twin.kw || 0, r.kw || 0) || null;
      twin.town = twin.town || r.town;
      twin.addr = twin.addr || r.addr;
      continue;
    }
    kept.push(r);
  }
  kept.sort((a, b) => ((b.kw || 0) - (a.kw || 0)) || (a.name.toLowerCase() < b.name.toLowerCase() ? -1 : a.name.toLowerCase() > b.name.toLowerCase() ? 1 : 0));
  return kept;
}

export const CHARGERS: Charger[] = chargerRows();
export const KW_STEPS = [22, 50, 100, 150].filter((s) => CHARGERS.some((r) => (r.kw || 0) >= s));
export const CONN_ORDER = ['CCS', 'Tip 2', 'CHAdeMO', 'Tesla', 'Tip 1'].filter((c) => CHARGERS.some((r) => r.conn.includes(c)));

// Serbia outline (with Kosovo and Metohija) for the map, and a thin zone along the administrative line to hide it on the street map
const _srb = (srb as any).features[0].geometry.coordinates;
const _kos = (kos as any).features[0].geometry.coordinates;
export const OUTLINE = { type: 'Feature', properties: {}, geometry: { type: 'MultiPolygon', coordinates: [_srb, _kos] } };
function zone(line: number[][], km = 14) {
  const left: number[][] = [], right: number[][] = [];
  const rad = (d: number) => (d * Math.PI) / 180;
  line.forEach(([x, y], k) => {
    const a = line[Math.max(k - 1, 0)], b = line[Math.min(k + 1, line.length - 1)];
    const dx = (b[0] - a[0]) * Math.cos(rad(y)), dy = b[1] - a[1], n = Math.hypot(dx, dy) || 1;
    const ox = (-dy / n) * km / 111 / Math.cos(rad(y)), oy = (dx / n) * km / 111;
    left.push([x + ox, y + oy]); right.push([x - ox, y - oy]);
  });
  const ring = [...left, ...right.reverse(), left[0]];
  return { type: 'Polygon', coordinates: [ring] };
}
export const BORDER_ZONE = zone(_kos[0].slice(6, 19));
