ev-srbija.rs - static site

Upload the contents of this folder to the web server root (https://www.ev-srbija.rs/).
Redirect https://ev-srbija.rs to https://www.ev-srbija.rs (301) so search engines see one address.
Rebuild after any data change:  python3 build/build_site.py  (run from the project folder)

Sources of truth:
  index.html                  homepage source (layout, hero ads, featured cards, FAQ)
  data/brands.json            brands and models (ranges, batteries, what is listed)
  build/brand_content.json    brand texts, importers and dealers
  build/model_content.json    model descriptions, battery and range text
  img/, logos/                photos and logos

After launch:
  1. Add the site to Google Search Console and Bing Webmaster Tools and submit sitemap.xml.
  2. Remove the owner preview box (details#owner in index.html) and rebuild.
  3. Replace the demo hero banners (Foton Tunland G7/V9) with real advertiser creatives.
