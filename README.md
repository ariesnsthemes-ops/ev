# evomobil.rs – Astro

The evomobil.rs website, rebuilt in [Astro](https://astro.build/). The build writes the finished site
into `site/`, in exactly the form the old Python generator produced: same pages, same addresses
(`modeli.html`, `brendovi/kia.html`, …), same markup, CSS, scripts, breakpoints and data.

```
npm install        # once
npm run build      # writes site/
npm run dev        # local preview with live reload (http://localhost:4321)
```

`npm run build` needs Node 18.17 or newer. The switches are in `site.config.mjs`:

- `NOINDEX` – on: every page carries a `noindex` tag and `_headers` sends `X-Robots-Tag` (private preview).
- `ADS_ENABLED` – off (as published now): nothing about selling ads is in the site. Set it to `true` and
  rebuild to get the Oglašavanje page, the demo page `primer-oglasa.html` with the fictional advertisers
  (creatives in `src/assets/demo`, published as `img/demo/`), the "Zakupi" buttons and owner notes in the
  homepage ad spots, the oglasi@evomobil.rs address and the related sentences on the contact, about and
  privacy pages. With ads off the build fails if an ad reference slips through.
- `AD_PLACEHOLDER_TEXT` – off: the empty ad spots on the homepage show only their photos (no "Ovde može
  biti vaš model", "Slobodna pozicija", "Brend meseca", "LOGO"…; the brand-of-the-month tile and the
  test-drive box keep their text invisibly so the layout stays the same size). On: the texts are back.
  With `ADS_ENABLED` on, the texts are always shown.
- `PH_STYLE`, `GA_ID` – as before.

Change a switch with one command (or edit `site.config.mjs` by hand), then commit and push:

```
npm run switch                             # list the switches
npm run switch -- AD_PLACEHOLDER_TEXT on   # texts on the ad spots back
npm run switch -- AD_PLACEHOLDER_TEXT off  # photos only (current)
```

## Where things are

| What | Where |
| --- | --- |
| Site switches (domain, `NOINDEX`, `ADS_ENABLED`, `AD_PLACEHOLDER_TEXT`, `PH_STYLE`, `GA_ID`) | `site.config.mjs` (`npm run switch`) |
| Brands and models (ranges, batteries, what is listed) | `src/data/brands.json` |
| Brand texts, importers and dealers | `src/data/brand_content.json` |
| Model descriptions, battery and range text | `src/data/model_content.json` |
| Dimensions and seats (official sources only) | `src/data/model_dims.json` |
| Fuel prices for the calculator | `src/data/gorivo.json` |
| Charger data (Open Charge Map, OpenStreetMap, extra) | `src/data/chargers-*.json`, `src/data/chargers-osm.geojson` |
| Photos, logos, icons, stylesheet, MapLibre | `public/img`, `public/logos`, `public/assets` |
| Cloudflare headers | written at build time by `scripts/html-polish.mjs` (`X-Robots-Tag` follows `NOINDEX`) |
| The catalogue logic (model ids, names, tags, ordering) | `src/lib/site.ts` |
| Shared markup (cards, tables, breadcrumbs, dealer cards, JSON-LD) | `src/lib/html.ts` |
| Charger merging and the Serbia outline for the map | `src/lib/chargers.ts` |
| Dealers grouped by city | `src/lib/dealers.ts` |
| sitemap, robots, llms.txt, llms-full.txt, podaci/modeli.json | `src/lib/textdata.ts` + `src/pages/*.ts` |
| Page shell (head, header, footer, shared scripts) | `src/layouts/Base.astro`, `src/components/` |
| Pages | `src/pages/` (`[lista].astro` = the five category pages + najveci-domet) |
| Browser scripts (unchanged from the old site) | `src/scripts/*.js` |
| Calculator markup and CSS | `src/fragments/kalkulator-*.html` |
| Advertising page, demo page and creatives (only with `ADS_ENABLED`) | `src/pages/[oglasavanje].astro`, `src/pages/[demo].html.ts`, `src/fragments/oglasavanje.html`, `src/assets/demo/`, `scripts/make_demo_creatives.js` |
| Post-build cosmetics, `_headers`, demo images, ads-off check | `scripts/html-polish.mjs` (an Astro integration) |

Edit the JSON files and rebuild; every page, the search data, the sitemap and the text/JSON
exports follow from them. The homepage's featured models are the `FEATURED_HOME` list in
`src/pages/index.astro`.

## Checking a build against a reference

`scripts/compare.mjs` compares two site folders file by file (the build date is ignored):

```
node scripts/compare.mjs ../old-project/site site
```

`scripts/visual-check.mjs` renders a set of pages from both folders at 1440, 1180, 900, 760, 560
and 390 px and saves screenshots for a pixel comparison (needs `npm i -D playwright`).

## Publishing (Cloudflare Workers, connected to GitHub)

Cloudflare builds the site on every push to `main`:

- Build command: `npm run build` (writes `site/`)
- Deploy command: `npx wrangler deploy` (publishes `site/` with the settings in `wrangler.jsonc`:
  clean addresses, `404.html` for unknown addresses, `_headers`)

`site/` is therefore not committed (see `.gitignore`). `cene-goriva.yml` checks the fuel prices every
day (and Friday afternoon) and commits `src/data/gorivo.json` when something changed; that push makes
Cloudflare rebuild.

## Notes on fidelity

The build was verified against the last Python build in both modes (ads off: 543 files, ads on: 555 files
including the Oglašavanje and demo pages): all generated files are byte-identical,
except the homepage, where the old build had accidentally inlined the Dongfeng and Leapmotor
logos as base64 (the same SVG files with Windows line endings) – the Astro build links
`logos/dongfeng.svg` and `logos/leapmotor.svg` like every other page. `BUILD_DATE=YYYY-MM-DD`
pins the date written into the sitemap and the data exports.
