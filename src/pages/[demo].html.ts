/**
 * Demo page for advertisers (primer-oglasa.html): the homepage with every rentable spot filled with
 * FICTIONAL advertisers. Not linked, noindex, not in the sitemap. Built only while ADS_ENABLED is on.
 * Creatives: src/assets/demo/*.webp (made with scripts/make_demo_creatives.js), published as img/demo/.
 *
 * The homepage is rendered with Astro's container API and the ad spots are swapped in the markup,
 * exactly as the previous generator did.
 */
import type { APIRoute } from 'astro';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import Index from './index.astro';
import { ADS_ENABLED, NOINDEX } from '../config';

export const getStaticPaths = () => (ADS_ENABLED ? [{ params: { demo: 'primer-oglasa' } }] : []);

const D = 'img/demo/demo-';
const HERO: [string, string, string][] = [['AutoCentar Nova', 'Električni SUV', 'hero-1-nova'], ['VoltDom', 'Kućni punjač', 'hero-2-voltdom'],
  ['Punionica+', 'Aplikacija', 'hero-3-punionica'], ['EkoLizing', 'Lizing', 'hero-4-eko'], ['PutujEV', 'Planer puta', 'hero-5-putuj']];

const pic = (big: string, small: string, alt: string, w: number, h: number) =>
  `<a class="demo-ad" href="#" aria-label="${alt}"><picture><source media="(max-width: 640px)" srcset="${D}${small}.webp">`
  + `<img src="${D}${big}.webp" alt="${alt}" width="${w}" height="${h}" decoding="async"></picture></a>`;

/** Replaces the <div class="house …">…</div> that follows data-pos="<pos>" with the creative. */
function swapHouse(doc: string, pos: string, html: string): string {
  const k = doc.indexOf(`data-pos="${pos}"`);
  const a = doc.indexOf('<div class="house', k);
  let depth = 0, p = a;
  for (;;) {
    const o = doc.indexOf('<div', p), c = doc.indexOf('</div>', p);
    if (o !== -1 && o < c) { depth++; p = o + 4; }
    else { depth--; p = c + 6; if (depth === 0) break; }
  }
  return doc.slice(0, a) + html + doc.slice(p);
}

const one = (doc: string, from: string, to: string) => {
  if (!doc.includes(from)) throw new Error('demo page: homepage markup changed, cannot find: ' + from.slice(0, 60));
  return doc.replace(from, () => to);
};

const DEMO_CSS = '<style>.demo-top{position:sticky;top:0;z-index:60}.demo-top header.site{position:relative;top:0}.demo-bar{position:relative;z-index:90;display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap;padding:9px 16px;background:#16202e;color:#fff;font:500 13px var(--font);text-align:center}'
  + '.demo-back{color:#fff;font-weight:700;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:3px 12px;text-decoration:none;white-space:nowrap}.demo-back:hover{background:#fff;color:#16202e}.demo-bar b{background:#f5b301;color:#16202e;border-radius:999px;padding:2px 10px;font-weight:800;letter-spacing:.08em;font-size:11px}'
  + '.demo-ad{display:block;border-radius:var(--r-lg);overflow:hidden;line-height:0;box-shadow:0 1px 0 var(--line)}.demo-ad img{width:100%;height:auto}'
  + '.offers .demo-ad{flex:none}'
  + '.demo-logo{border-style:solid!important;background:#0b0f17!important;border-color:#0b0f17!important}'
  + '.voltra{font:800 clamp(16px,1.6vw,22px)/1 var(--font-head);letter-spacing:.24em;color:#fff;padding-left:.24em;white-space:nowrap}'
  + '.demo-sponsor{border-style:solid!important;border-color:rgba(255,255,255,.18)!important;text-decoration:none}'
  + '.nova{display:inline-flex;align-items:center;gap:10px;color:#fff;font:500 20px var(--font);letter-spacing:-.01em}.nova b{font-weight:800}.nova svg{width:30px;height:30px}'
  + '</style>\n';
// the demo is a picture of the site: nothing on it can be clicked, opened or typed into
const LOCK = '<style>main a,main button,main input,main select,main label,main summary,main [role=button],.cmp-bar,.cmp-bar *,header.site a,footer a{cursor:default!important}#prev,#next,.demo-bar a,a[href^=mailto]{cursor:pointer!important}.ck{display:none!important}</style>'
  + '<script>(function(){var free=function(t){return t&&t.closest&&t.closest(".demo-bar a,#prev,#next,#theme-btn,#menu-btn,a[href^=mailto]")};'
  + 'var stop=function(e){if(free(e.target))return;e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();return false};'
  + "['click','auxclick','dblclick','submit','contextmenu'].forEach(function(t){document.addEventListener(t,stop,true)});"
  + "document.addEventListener('mousedown',function(e){if(!free(e.target)&&e.target.closest('input,select,textarea,button,a,label,summary'))stop(e)},true);"
  + "document.addEventListener('keydown',function(e){if((e.key==='Enter'||e.key===' ')&&!free(e.target)){if(e.target.closest('a,button,input,select,textarea,summary'))stop(e)}},true);"
  + "document.addEventListener('DOMContentLoaded',function(){[].forEach.call(document.querySelectorAll('main a,main button,main input,main select,main textarea,main summary'),function(el){if(el.id!=='prev'&&el.id!=='next')el.setAttribute('tabindex','-1')})});"
  + '})();</script>\n';

export const GET: APIRoute = async () => {
  const container = await AstroContainer.create();
  let d = await container.renderToString(Index);
  if (!/^<!doctype html>/i.test(d)) d = '<!doctype html>\n' + d;
  // head: noindex, own title, no canonical to the homepage
  if (NOINDEX) d = one(d, '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', '<meta charset="utf-8">');
  d = d.replace(/<link rel="canonical"[^>]*>\n?/, '');
  d = one(d, '<head>', '<head>\n<meta name="robots" content="noindex, nofollow">');
  d = d.replace(/<title>[^<]*<\/title>/, '<title>Primer reklamnih mesta | evomobil.rs</title>');
  // hero: 5 filled rotation positions
  const i = d.indexOf('  const slides=['), j = d.indexOf('  ];', i);
  d = d.slice(0, i) + '  const slides=[\n' + HERO.map(([b, m, f]) => `    {b:'${b}',m:'${m}',img:'${D}${f}.webp',alt:'Oglas: ${b}',href:'#'}`).join(',\n') + '\n' + d.slice(j);
  d = one(d, '<a id="h-link" class="hero-img" href="#" hidden><img id="h-img" src="data:," alt="" width="1600" height="900"></a>',
    `<a id="h-link" class="hero-img" href="#"><img id="h-img" src="${D}hero-1-nova.webp" alt="Oglas: AutoCentar Nova" width="1600" height="900"></a>`);
  d = one(d, '<div class="free ph-bg" id="h-free" style="--ph:url(../img/evomobil-bg-auto.webp)">', '<div class="free ph-bg" id="h-free" style="--ph:url(../img/evomobil-bg-auto.webp)" hidden>');
  d = one(d, '<span class="rs-chip"><span id="h-brand">SLOBODNA POZICIJA</span></span>', '<span class="rs-chip" hidden><span id="h-brand">AUTOCENTAR NOVA</span></span>');
  d = swapHouse(d, 'AD-02', pic('lb-putuj', 'lb-putuj-m', 'Oglas: PutujEV', 2480, 360));
  d = swapHouse(d, 'AD-04A', pic('of-sigurna', 'of-sigurna-m', 'Oglas: Sigurna Struja', 1220, 480));
  d = swapHouse(d, 'AD-04B', pic('of-solar', 'of-solar-m', 'Oglas: SolarKuća', 1220, 480));
  // AD-03 brand of the month: fictional brand
  d = one(d, '<span class="rs-label">Brend meseca · Oglas</span>\n            <h3>Ovde može stajati vaš brend</h3>\n            <p>Prvo mesto u listi brendova, sa logom i linkom ka vašoj EV ponudi.</p>',
    '<span class="rs-label">Brend meseca</span>\n            <h3>Voltra: novi električni SUV stiže u Srbiju</h3>\n            <p>Voltra X5 sa dometom do 560 km. Predstavljanje u salonima od 1. novembra.</p>');
  d = one(d, '<div class="logo-slot">LOGO BRENDA</div>', '<div class="logo-slot demo-logo"><span class="voltra">VOLTRA</span></div>');
  d = one(d, '<a href="oglasavanje#zakup-03" class="btn btn-dark">Zakupi ovaj prostor <span class="arr">→</span></a>', '<a href="#" class="btn btn-dark">Pogledaj Voltra X5 <span class="arr">→</span></a>');
  // AD-05 test drive sponsor
  d = one(d, '<div class="slot">LOGO SPONZORA</div>\n          <p>Mesto za jednog distributera ili brend, uz link ka zakazivanju test vožnje.</p>',
    '<a class="slot demo-sponsor" href="#"><span class="nova"><svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="17" fill="none" stroke="currentColor" stroke-width="4"/><path d="M13 27V13l14 14V13" fill="none" stroke="#f5b301" stroke-width="4" stroke-linejoin="round"/></svg><span>AutoCentar <b>Nova</b></span></span></a>\n'
    + '          <p>Zakažite besplatnu test vožnju bilo kog električnog modela iz naše ponude, u Beogradu i Novom Sadu.</p>');
  // demo banner + styles
  d = one(d, '</head>', DEMO_CSS + '</head>');
  d = one(d, '<header class="site"', '<div class="demo-top">' + '<div class="demo-bar"><b>DEMO</b><span>Primer kako izgledaju popunjena reklamna mesta na evomobil.rs. Oglašivači i ponude su izmišljeni. Zakup: oglasi@evomobil.rs</span><a class="demo-back" href="oglasavanje">← Nazad na Oglašavanje</a></div>' + '\n<header class="site"');
  d = d.replace('</header>', '</header></div>');
  d = d.replaceAll('href="#"', 'href="#" onclick="return false"');
  d = one(d, '</head>', LOCK + '</head>');
  return new Response(d, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
};
