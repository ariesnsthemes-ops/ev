// @ts-check
import { defineConfig } from 'astro/config';
import htmlPolish from './scripts/html-polish.mjs';
import switches from './site.config.mjs';

// Static build that mirrors the original site/ layout exactly:
//   build.format 'file'  -> modeli.html, brendovi/kia.html, modeli/byd-seal.html, 404.html
//   compressHTML false   -> markup is written out as authored (no whitespace rewriting)
export default defineConfig({
  site: 'https://www.evomobil.rs',
  output: 'static',
  outDir: './site',
  build: { format: 'file', assets: '_astro', inlineStylesheets: 'never' },
  compressHTML: false,
  integrations: [htmlPolish({ noindex: switches.NOINDEX, ads: switches.ADS_ENABLED, demoDir: './src/assets/demo' })],
  trailingSlash: 'never',
  devToolbar: { enabled: false },
  vite: { build: { assetsInlineLimit: 0 } },
});
