evomobil.rs - static site

The published website is the site/ folder: open site/index.html to view it. Everything else is the source used to build it.
Rebuild after any change:  python3 build/build_site.py  (run from the project folder; writes site/)

Cloudflare (Workers, connected to GitHub):
  wrangler.jsonc (project root) publishes the site/ folder as it is: no build command,
  deploy command "npx wrangler deploy". Addresses have no .html (evomobil.rs/modeli): Cloudflare serves
  /modeli from modeli.html and redirects old /modeli.html addresses to /modeli. Unknown addresses show
  404.html (status 404). site/_headers sets security and cache headers.
  With CLEAN_URLS = True the links work on Cloudflare only, not when opening the files from disk.
  After each rebuild, commit the updated site/ folder; Cloudflare publishes it automatically.
  Direct upload instead: upload the contents of site/ (evomobil-cloudflare-upload.zip).
  Redirect https://evomobil.rs to https://www.evomobil.rs (301) so search engines see one address.

Sources of truth:
  build/homepage-template.html homepage source (layout, hero ads, featured cards, FAQ); not a page to open
  data/brands.json            brands and models (ranges, batteries, what is listed)
  build/brand_content.json    brand texts, importers and dealers
  build/model_content.json    model descriptions, battery and range text
  build/model_dims.json       dimensions and seats (official sources only)
  build/kalkulator.html       cost calculator page (markup, CSS, JS); not a page to open
  data/gorivo.json            fuel prices for the calculator (BMB 95, Evrodizel, date of the Ministry decision)
  img/, logos/                photos and logos

Switches in build/build_site.py (section "SWITCHES"):
  NOINDEX       True  = private preview: every page gets a noindex tag and _headers sends X-Robots-Tag noindex.
                False = public: search engines and AI crawlers may index the site.
  ADS_ENABLED   False = everything for selling ads is left out: Oglašavanje page, demo page (primer-oglasa.html),
                        oglasi@evomobil.rs, "Zakupi" buttons, ad codes, links to Oglašavanje. The ad spots on the
                        homepage stay as neutral "Slobodna pozicija" placeholders.
                True  = all of it is back. The build stops with an error if ads are off but an ad reference remains.
  CLEAN_URLS    True  = addresses without .html (for Cloudflare). False = .html addresses (any host, or opening files from disk).
  PH_STYLE      Look of demo photos in empty ad spots: 'photo' (regular photo, dark scrim, white text), 'fade', 'multiply'.
  GA_ID         Google Analytics 4 ID ('G-...'); empty = analytics never loads.

To turn ads ON later (any Claude account): attach the latest project zip and ask:
  "Set ADS_ENABLED = True in build/build_site.py, rebuild with python3 build/build_site.py, check that the
   Oglašavanje page, demo page, oglasi@evomobil.rs and the Zakupi links are back, test the pages, and give
   me the updated zip."

Public launch:
  1. Set NOINDEX = False (and add GA_ID), rebuild, publish site/.
  2. Remove the Cloudflare Access password protection.
  3. Add the site to Google Search Console and Bing Webmaster Tools and submit sitemap.xml.

Fuel prices (calculator):
  .github/workflows/cene-goriva.yml runs build/update_fuel.py every Friday after 15:00 (several tries until 18:20,
  plus Saturday morning). It reads BMB 95 and Evrodizel from nafta.hr/sr/cene-goriva-srbija, checks them
  (150-320 RSD, at least 3 companies with the same top price, at most 20 RSD change in a week) and, only if a price
  changed, writes data/gorivo.json, rebuilds the site and pushes; Cloudflare then publishes.
  If a check fails, nothing changes and GitHub emails "Run failed: Cene goriva". Results: GitHub > Actions > Cene goriva.
  Manual check: Actions > Cene goriva > Run workflow. Manual price change: edit data/gorivo.json and rebuild.
