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
- `HERO_LAYOUT` – the homepage hero while ads are off: `'single'` (one full-width photo, rotating every 5 s) or
  `'triple'` (large photo plus two side tiles). With `ADS_ENABLED` on the hero is always the 3-field ad carousel.
  With ads off the homepage also leaves out the two partner-offer spots (AD-04A/B), shows a taller leaderboard
  photo and puts the photo behind the test-drive band instead of the sponsor box (AD-05); `ADS_ENABLED: true`
  brings all of them back.
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
| Brand texts, importers and dealers (optional `intro` replaces the generated hero sentence) | `src/data/brand_content.json` |
| Model descriptions, battery and range text; optional `intro` (hero paragraphs), `gearbox` and `faq` (`range`, `battery`, `buy`, `hybrid` answers) replace the generated texts, see Geely E5 | `src/data/model_content.json` |
| Dimensions and seats (official sources only) | `src/data/model_dims.json` |
| Fuel prices for the calculator | `src/data/gorivo.json` |
| Car "from" prices for the footnote on model pages (monthly check) | `src/data/prices.json`, `scripts/update_prices.py`, `.github/workflows/cene-automobila.yml` |
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

## Adding a new model (checklist)

1. `src/data/brands.json`: add the model to the brand (name, body, `range_wltp_km`, `battery_kwh`).
2. `src/data/model_content.json`: battery and range text (`kwh`, `range_text`).
3. **Always research dimensions and seats yourself** and add them to `src/data/model_dims.json`
   (length, width, height and seats; ground clearance is not shown), only from the brand's official websites for European countries (e.g. byd.fr, byd.ch — never byd.ru, byd.au):
   their price lists, technical sheets and press rooms. Put the URLs in `sources` and anything
   unclear in `notes`. If no official source states a figure, leave it `null` (the page shows a dash).
4. Photo: `python3 scripts/photos.py <folder>` with the file named `evomobil-<model-id>.<ext>`
   (writes the 1280 px and 640 px WebP into `public/img`), then add the id to `PHOTO_IDS` in `src/lib/site.ts`.
5. **Replacing an existing photo or logo: never reuse the file name.** Add `-new` to the new file
   (`evomobil-leapmotor-b05-new.webp`; a later replacement `-new-2`, `-new-3`…), register model photos in
   `PHOTO_RENAMED` in `src/lib/site.ts`, and delete the old file. `img/` and `logos/` are cached for
   30 days, so a reused name keeps showing the old picture.
6. Hand-written brand texts in `src/data/brand_content.json` that list models by name (e.g. "O brendu")
   must get the new model too.

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

`site/` is therefore not committed (see `.gitignore`). `cene-goriva.yml` checks the fuel prices once a
week, on Friday at 15:10 Belgrade time (or by hand: Actions → Cene goriva → Run workflow), and commits `src/data/gorivo.json` when something changed; that push makes
Cloudflare rebuild.

## Notes on fidelity

The build was verified against the last Python build in both modes (ads off: 543 files, ads on: 555 files
including the Oglašavanje and demo pages): all generated files are byte-identical,
except the homepage, where the old build had accidentally inlined the Dongfeng and Leapmotor
logos as base64 (the same SVG files with Windows line endings) – the Astro build links
`logos/dongfeng.svg` and `logos/leapmotor.svg` like every other page. `BUILD_DATE=YYYY-MM-DD`
pins the date written into the sitemap and the data exports.

## Car prices (footnote on model pages)

Every model page can show one light-grey line at the very bottom: "Početna cena … od X € (prema zvaničnom sajtu
uvoznika). Cena proverena: [datum] …". The price is in `src/data/prices.json` and is shown only when it was checked
within the last 120 days; older prices disappear on their own. With a price, the page title also gets "cena" (without the number).

`scripts/update_prices.py` reads the prices from the importers' sites (model page, price-list page or PDF) and from
the dealer sites listed per brand in `brand_content.json`, and cross-checks them: a price counts as confirmed when the
importer and at least one dealer agree (or two dealers, when the importer shows none). Disagreements are not applied.
GitHub runs it on the first Wednesday of the month (Actions > Cene automobila) and opens a pull request with the report
table: what changed, what to check, what was not found. The same table as PDF: the run's page > Artifacts > izvestaj-cene.
Merge the pull request and Cloudflare publishes the site. More dealer websites in `brand_content.json` = more cross-checks.

- A model without `url`: the script looks for it on the brand's site (`_brand_sites`), saves the page it found
  and marks it "review": check the address in the pull request.
- A change larger than 15 % is NOT applied (status "review"); fix the url or the price by hand if it is real.
- Wrong page or wrong name: edit `url` or `match` for that model in `prices.json`.
- Local run: `pip install playwright pypdf && python3 -m playwright install chromium`, then
  `python3 scripts/update_prices.py --brand byd --dry-run` (prints the report, writes nothing).
- Evidence: every price found is kept as a dated screenshot (or the PDF itself) on the branch `dokazi-cena`, and the
  page is saved in the Internet Archive (links in the report).
- A price set by hand: add `"lock": {"price_eur": 26890, "since": "2026-11-27", "note": "…"}` to the model; the
  script then never changes it and only reports what the sources say.
- When the monthly runs have proved reliable, set `AUTO_PUBLISH: 'true'` in the workflow: it then publishes without a pull request.
