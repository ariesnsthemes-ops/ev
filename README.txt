ev-srbija.rs - static site

The published website is the site/ folder: open site/index.html to view it. Everything else is the source used to build it.
Rebuild after any change:  python3 build/build_site.py  (run from the project folder; writes site/)

Cloudflare Pages:
  Upload the contents of site/ (direct upload), or connect the GitHub repo with
  build output directory "site" and no build command (commit site/ after each rebuild).
  404.html is used automatically for unknown addresses. site/_headers sets security and cache headers.
  Redirect https://ev-srbija.rs to https://www.ev-srbija.rs (301) so search engines see one address.

Sources of truth:
  build/homepage-template.html homepage source (layout, hero ads, featured cards, FAQ); not a page to open
  data/brands.json            brands and models (ranges, batteries, what is listed)
  build/brand_content.json    brand texts, importers and dealers
  build/model_content.json    model descriptions, battery and range text
  build/model_dims.json       dimensions and seats (official sources only)
  img/, logos/                photos and logos

Switches in build/build_site.py (section "SWITCHES"):
  NOINDEX       True  = private preview: every page gets a noindex tag and _headers sends X-Robots-Tag noindex.
                False = public: search engines and AI crawlers may index the site.
  ADS_ENABLED   False = everything for selling ads is left out: Oglašavanje page, demo page (primer-oglasa.html),
                        oglasi@ev-srbija.rs, "Zakupi" buttons, ad codes, links to Oglašavanje. The ad spots on the
                        homepage stay as neutral "Slobodna pozicija" placeholders.
                True  = all of it is back. The build stops with an error if ads are off but an ad reference remains.
  GA_ID         Google Analytics 4 ID ('G-...'); empty = analytics never loads.

To turn ads ON later (any Claude account): attach the latest project zip and ask:
  "Set ADS_ENABLED = True in build/build_site.py, rebuild with python3 build/build_site.py, check that the
   Oglašavanje page, demo page, oglasi@ev-srbija.rs and the Zakupi links are back, test the pages, and give
   me the updated zip."

Public launch:
  1. Set NOINDEX = False (and add GA_ID), rebuild, publish site/.
  2. Remove the Cloudflare Access password protection.
  3. Add the site to Google Search Console and Bing Webmaster Tools and submit sitemap.xml.
