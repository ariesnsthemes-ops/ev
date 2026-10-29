// Site-wide settings: the switches from site.config.mjs plus derived constants.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import switches from '../site.config.mjs';

export const DOMAIN: string = switches.DOMAIN;
export const SITE = 'evomobil.rs';
export const UPDATED_TXT = 'oktobar 2026';

/** Build date (sitemap <lastmod>, structured data, podaci/modeli.json). BUILD_DATE=YYYY-MM-DD pins it. */
export const UPDATED = process.env.BUILD_DATE || new Date().toISOString().slice(0, 10);

// the switches live in site.config.mjs (see the comments there)
export const NOINDEX: boolean = switches.NOINDEX;
export const ADS_ENABLED: boolean = switches.ADS_ENABLED;
export const AD_PLACEHOLDER_TEXT: boolean = switches.ADS_ENABLED || switches.AD_PLACEHOLDER_TEXT;
export const PH_STYLE: 'photo' | 'fade' | 'multiply' = switches.PH_STYLE as any;
export const GA_ID: string = switches.GA_ID;

const pub = (p: string) => resolve('public', p); // astro runs from the project root
const md5 = (b: Buffer | string) => createHash('md5').update(b).digest('hex');

/** Cache-busters: the stylesheet hash and the favicon hash, same recipe as before. */
export const CSS_V = md5(readFileSync(pub('assets/site.css'), 'utf8')).slice(0, 8);
export const FAV_V = md5(Buffer.concat([readFileSync(pub('favicon.ico')), readFileSync(pub('img/favicon-32.png'))])).slice(0, 8);

export const OG_DEFAULT = 'img/og-evomobil.jpg';
export const NOTE = 'Test vožnju i dostupnost modela dogovarate direktno sa distributerom. Kontakt podaci su preuzeti sa zvaničnih sajtova uvoznika i distributera i mogu se promeniti.';
