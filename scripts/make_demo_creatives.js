// Builds the demo ad creatives (fictional advertisers) as images: HTML template -> screenshot -> WebP via sharp.
// Run: NODE_PATH=$(npm root -g) node scripts/make_demo_creatives.js   (photos in scripts/demo-src, output in src/assets/demo)
const { chromium } = require('playwright');
const sharp = require('sharp');
const path = require('path');
const ROOT = path.resolve(__dirname);
const src = f => 'file://' + path.join(ROOT, 'demo-src', f);

const LOGOS = {
  nova: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="17" fill="none" stroke="currentColor" stroke-width="4"/><path d="M13 27V13l14 14V13" fill="none" stroke="#f5b301" stroke-width="4" stroke-linejoin="round"/></svg><span>AutoCentar <b>Nova</b></span></div>`,
  voltdom: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><path d="M5 19 20 6l15 13v15H5z" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"/><path d="M22 14l-6 10h5l-2 8 7-11h-5z" fill="#ff7a1a"/></svg><span>Volt<b>Dom</b></span></div>`,
  punionica: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><rect x="4" y="4" width="32" height="32" rx="9" fill="#14b8a6"/><path d="M14 11v18M14 11h7a5 5 0 0 1 0 10h-7M27 25v8M23 29h8" stroke="#fff" stroke-width="3.4" fill="none" stroke-linecap="round"/></svg><span>Punionica<b>+</b></span></div>`,
  eko: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><path d="M8 32C8 16 18 7 34 6c0 17-9 26-26 26z" fill="#22c55e"/><path d="M8 32 24 16" stroke="#0b3d1f" stroke-width="3" stroke-linecap="round"/></svg><span>Eko<b>Lizing</b></span></div>`,
  putuj: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><path d="M20 4c7 0 12 5 12 12 0 9-12 20-12 20S8 25 8 16C8 9 13 4 20 4z" fill="#8b5cf6"/><path d="M21 9l-5 8h4l-2 7 6-9h-4z" fill="#fff"/></svg><span>Putuj<b>EV</b></span></div>`,
  sigurna: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><path d="M20 3 34 8v11c0 9-6 15-14 18C12 34 6 28 6 19V8z" fill="#2563eb"/><path d="M22 10l-7 11h5l-2 9 8-12h-5z" fill="#fff"/></svg><span>Sigurna <b>Struja</b></span></div>`,
  solar: (c = '#fff') => `<div class="logo" style="color:${c}"><svg viewBox="0 0 40 40"><circle cx="20" cy="15" r="7" fill="#f59e0b"/><path d="M20 2v4M20 24v4M7 15H3M37 15h-4M10.8 5.8l2.8 2.8M26.4 21.4l2.8 2.8M29.2 5.8l-2.8 2.8M13.6 21.4l-2.8 2.8" stroke="#f59e0b" stroke-width="2.6" stroke-linecap="round"/><path d="M6 37l4-8h20l4 8z" fill="currentColor"/></svg><span>Solar<b>Kuća</b></span></div>`,
};

const BASE = `*{box-sizing:border-box;margin:0;padding:0}html,body{width:100%;height:100%;overflow:hidden;font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.c{position:relative;width:100%;height:100%;overflow:hidden;background:#111;color:#fff}
.c img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.shade{position:absolute;inset:0}
.in{position:absolute;display:flex;flex-direction:column;align-items:flex-start}
.logo{display:flex;align-items:center;gap:.45em;font-weight:500;letter-spacing:-.01em;white-space:nowrap}
.logo svg{width:1.5em;height:1.5em;flex:none}.logo b{font-weight:800}
h1{font-weight:800;letter-spacing:-.035em;line-height:1.02}
p{font-weight:500;line-height:1.35;opacity:.92}
.cta{display:inline-flex;align-items:center;gap:.5em;border-radius:999px;font-weight:700;white-space:nowrap}
.price{font-weight:800;letter-spacing:-.02em}
.fine{position:absolute;opacity:.65;font-weight:500}`;

// geometry helpers: each creative gets explicit sizes so it reads well at its slot size
const C = [];
const add = (name, w, h, body, css) => C.push({ name, w, h, html: `<!doctype html><html><head><meta charset="utf-8"><style>${BASE}${css}</style></head><body><div class="c">${body}</div></body></html>` });

// ---- AD-01 hero (1600 x 900) ----
add('hero-1-nova', 1600, 900,
  `<img class="bg" src="${src('p1.jpg')}" style="object-position:58% 40%;transform:scaleX(-1)"><div class="shade" style="background:linear-gradient(90deg,rgba(9,16,28,.86) 0%,rgba(9,16,28,.55) 38%,rgba(9,16,28,0) 62%)"></div>
   <div class="in" style="left:90px;top:90px;bottom:90px;justify-content:space-between;width:620px">${LOGOS.nova()}
   <div><h1 style="font-size:84px">Električni SUV.<br>Spreman odmah.</h1><p style="font-size:30px;margin-top:22px">Više od 20 električnih modela na lageru u Beogradu i Novom Sadu.</p></div>
   <span class="cta" style="font-size:28px;padding:22px 38px;background:#f5b301;color:#111">Zakažite test vožnju →</span></div>`, '.logo{font-size:38px}');
add('hero-2-voltdom', 1600, 900,
  `<img class="bg" src="${src('p4.jpg')}" style="object-position:50% 62%"><div class="shade" style="background:linear-gradient(90deg,rgba(20,12,4,.88) 0%,rgba(20,12,4,.6) 40%,rgba(20,12,4,0) 66%)"></div>
   <div class="in" style="left:90px;top:90px;bottom:90px;justify-content:space-between;width:660px">${LOGOS.voltdom()}
   <div><h1 style="font-size:80px">Kućni punjač<br>sa ugradnjom</h1><p class="price" style="font-size:64px;margin-top:18px;color:#ff9a4d">od 690 €</p><p style="font-size:28px;margin-top:14px">11 kW wallbox, montaža i atest za 3 dana.</p></div>
   <span class="cta" style="font-size:28px;padding:22px 38px;background:#ff7a1a;color:#fff">Zatražite ponudu →</span></div>`, '.logo{font-size:38px}');
add('hero-3-punionica', 1600, 900,
  `<img class="bg" src="${src('p7.jpg')}" style="object-position:50% 38%"><div class="shade" style="background:linear-gradient(90deg,rgba(4,26,27,.9) 0%,rgba(4,26,27,.62) 42%,rgba(4,26,27,0) 70%)"></div>
   <div class="in" style="left:90px;top:90px;bottom:90px;justify-content:space-between;width:680px">${LOGOS.punionica()}
   <div><h1 style="font-size:82px">500+ punjača.<br>Jedna aplikacija.</h1><p style="font-size:30px;margin-top:22px">Pronađite, pokrenite i platite punjenje u Srbiji i regionu.</p></div>
   <span class="cta" style="font-size:28px;padding:22px 38px;background:#14b8a6;color:#fff">Preuzmite aplikaciju →</span></div>`, '.logo{font-size:38px}');
add('hero-4-eko', 1600, 900,
  `<img class="bg" src="${src('p5.jpg')}" style="object-position:30% 50%"><div class="shade" style="background:linear-gradient(270deg,rgba(6,24,14,.9) 0%,rgba(6,24,14,.6) 42%,rgba(6,24,14,0) 70%)"></div>
   <div class="in" style="right:90px;top:90px;bottom:90px;justify-content:space-between;width:640px">${LOGOS.eko()}
   <div><h1 style="font-size:82px">Lizing za<br>električna vozila</h1><p class="price" style="font-size:60px;margin-top:18px;color:#4ade80">učešće od 0%</p><p style="font-size:28px;margin-top:14px">Odobrenje za 24 sata, za fizička i pravna lica.</p></div>
   <span class="cta" style="font-size:28px;padding:22px 38px;background:#22c55e;color:#062312">Izračunajte ratu →</span></div>`, '.logo{font-size:38px}');
add('hero-5-putuj', 1600, 900,
  `<img class="bg" src="${src('p2.jpg')}" style="object-position:50% 60%"><div class="shade" style="background:linear-gradient(90deg,rgba(20,10,40,.82) 0%,rgba(20,10,40,.5) 40%,rgba(20,10,40,0) 62%)"></div>
   <div class="in" style="left:90px;top:90px;bottom:90px;justify-content:space-between;width:640px">${LOGOS.putuj()}
   <div><h1 style="font-size:82px">Na more bez<br>brige o dometu</h1><p style="font-size:30px;margin-top:22px">Planer puta koji zna gde su punjači i koliko ćete čekati.</p></div>
   <span class="cta" style="font-size:28px;padding:22px 38px;background:#8b5cf6;color:#fff">Isplanirajte put →</span></div>`, '.logo{font-size:38px}');

// ---- AD-02 leaderboard: desktop 2480 x 360, mobile 720 x 500 ----
add('lb-putuj', 2480, 360,
  `<img class="bg" src="${src('p2.jpg')}" style="object-position:50% 58%"><div class="shade" style="background:linear-gradient(90deg,rgba(20,10,40,.9) 0%,rgba(20,10,40,.7) 40%,rgba(20,10,40,0) 70%)"></div>
   <div class="in" style="left:90px;top:0;bottom:0;justify-content:center;gap:22px">${LOGOS.putuj()}<h1 style="font-size:76px">Planirajte put, ne punjenje.</h1></div>
   <div class="in" style="right:90px;top:0;bottom:0;justify-content:center"><span class="cta" style="font-size:36px;padding:26px 46px;background:#fff;color:#2e1065">Besplatna aplikacija →</span></div>`, '.logo{font-size:40px}');
add('lb-putuj-m', 720, 500,
  `<img class="bg" src="${src('p2.jpg')}" style="object-position:62% 60%"><div class="shade" style="background:linear-gradient(180deg,rgba(20,10,40,.88) 0%,rgba(20,10,40,.45) 55%,rgba(20,10,40,.2) 100%)"></div>
   <div class="in" style="left:44px;right:44px;top:44px;bottom:44px;justify-content:space-between">${LOGOS.putuj()}<h1 style="font-size:52px">Planirajte put,<br>ne punjenje.</h1><span class="cta" style="font-size:24px;padding:16px 28px;background:#fff;color:#2e1065">Besplatna aplikacija →</span></div>`, '.logo{font-size:28px}');

// ---- AD-04 partner offers: desktop 1220 x 480, mobile 690 x 440 ----
const offer = (name, w, h, img, pos, logo, head, priceTxt, sub, cta, ctaBg, ctaFg, shade, big) => add(name, w, h,
  `<img class="bg" src="${src(img)}" style="object-position:${pos}"><div class="shade" style="background:${shade}"></div>
   <div class="in" style="left:${big ? 64 : 44}px;top:${big ? 56 : 40}px;bottom:${big ? 56 : 40}px;justify-content:space-between;width:${big ? 620 : 520}px">${logo}
   <div><h1 style="font-size:${big ? 56 : 46}px">${head}</h1><p class="price" style="font-size:${big ? 44 : 38}px;margin-top:10px">${priceTxt}</p><p style="font-size:${big ? 22 : 20}px;margin-top:8px">${sub}</p></div>
   <span class="cta" style="font-size:${big ? 22 : 20}px;padding:${big ? '16px 30px' : '14px 24px'};background:${ctaBg};color:${ctaFg}">${cta}</span></div>`, `.logo{font-size:${big ? 30 : 26}px}`);
const sh1 = 'linear-gradient(90deg,rgba(6,20,52,.92) 0%,rgba(6,20,52,.66) 45%,rgba(6,20,52,0) 75%)';
const sh2 = 'linear-gradient(90deg,rgba(40,24,2,.9) 0%,rgba(40,24,2,.6) 45%,rgba(40,24,2,0) 75%)';
offer('of-sigurna', 1220, 480, 'p6.jpg', '70% 50%', LOGOS.sigurna(), 'Kasko za<br>električna vozila', '−15% prve godine', 'Pokrivena i baterija i kućni punjač.', 'Izračunajte premiju →', '#fff', '#1e3a8a', sh1, true);
offer('of-sigurna-m', 690, 440, 'p6.jpg', '72% 50%', LOGOS.sigurna(), 'Kasko za<br>električna vozila', '−15% prve godine', 'Pokrivena i baterija i punjač.', 'Izračunajte premiju →', '#fff', '#1e3a8a', sh1, false);
offer('of-solar', 1220, 480, 'p3.jpg', '50% 55%', LOGOS.solar(), 'Punite automobil<br>energijom sa krova', 'solarna + punjač od 4.900 €', 'Projekat, montaža i priključenje.', 'Besplatna procena →', '#f59e0b', '#2a1a00', sh2, true);
offer('of-solar-m', 690, 440, 'p3.jpg', '58% 45%', LOGOS.solar(), 'Punite automobil<br>energijom sa krova', 'od 4.900 €', 'Solarna elektrana + kućni punjač.', 'Besplatna procena →', '#f59e0b', '#2a1a00', sh2, false);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files'] });
  for (const c of C) {
    const p = await b.newPage({ viewport: { width: c.w, height: c.h } });
    const fs = require('fs'); const f = path.join(ROOT, 'tmp', c.name + '.html'); fs.writeFileSync(f, c.html);
    await p.goto('file://' + f, { waitUntil: 'load' });
    await p.waitForTimeout(150);
    const buf = await p.screenshot({ type: 'png' });
    await sharp(buf).webp({ quality: 80, effort: 6 }).toFile(path.join(ROOT, '..', 'src', 'assets', 'demo', `demo-${c.name}.webp`));
    await p.close();
    console.log('ok', c.name);
  }
  await b.close();
})();
