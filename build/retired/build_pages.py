"""Builds brend.html (all brands, chosen by #brand-slug) and model.html (all electric models,
chosen by #model-id) from index.html styles, build/brand_content.json, build/model_content.json,
data/brands.json, logos/ and img/. Run from the ev-china folder: python3 build/build_pages.py"""
import base64, json, re

ROOT = '.'
index = open(f'{ROOT}/index.html', encoding='utf-8').read()
content = json.load(open(f'{ROOT}/build/brand_content.json', encoding='utf-8'))
mcontent = json.load(open(f'{ROOT}/build/model_content.json', encoding='utf-8'))
data = {b['slug']: b for b in json.load(open(f'{ROOT}/data/brands.json', encoding='utf-8'))['brands']}

style = re.search(r'<style>(.*?)</style>', index, re.S).group(1)
sprite = re.search(r'(<svg width="0" height="0" style="position:absolute" aria-hidden="true">.*?</svg>\n)(?=\n<header)', index, re.S).group(1)
header = re.search(r'<header class="site">.*?</header>', index, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', index, re.S).group(0)

def relink(html):
    # only real links (<a>) go back to the homepage, never <use href="#symbol">
    html = re.sub(r'(<a\b[^>]*?)href="#top"', r'\1href="index.html"', html)
    return re.sub(r'(<a\b[^>]*?)href="#', r'\1href="index.html#', html)
header, footer = relink(header), relink(footer)

def uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def slugify(t):
    t = t.lower().replace('&', ' ').replace('č', 'c').replace('ć', 'c').replace('š', 's').replace('ž', 'z').replace('đ', 'dj')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def model_id(brand_slug, brand_name, model_name):
    n = model_name
    if n.lower().startswith(brand_name.lower() + ' '):
        n = n[len(brand_name) + 1:]
    return brand_slug + '-' + slugify(n)

# model photos on a white studio background (files in img/), keyed by model id
PHOTO_FILES = {'foton-etunland': 'foton-etunland.webp', 'byd-dolphin-surf': 'byd-dolphin-surf.webp',
               'byd-atto-2-comfort': 'byd-atto-2.webp', 'byd-atto-3-evo': 'byd-atto-3-evo.webp',
               'byd-seal': 'byd-seal.webp', 'byd-sealion-7': 'byd-sealion-7.webp',
               'mg-mg4-electric': 'mg-mg4-electric.webp', 'mg-mg5-electric': 'mg-mg5-electric.webp',
               'mg-mgs5-ev': 'mg-mgs5-ev.webp', 'changan-deepal-s05': 'changan-deepal-s05.webp',
               'changan-deepal-s07': 'changan-deepal-s07.webp', 'geely-e5': 'geely-e5.webp', 'dongfeng-box': 'dongfeng-box.webp',
               'jac-t9-ev': 'jac-t9-ev.webp', 'jac-e30x': 'jac-e30x.webp',
               'jmev-ev3': 'jmev-ev3.webp', 'jmev-elight': 'jmev-elight.webp',
               'leapmotor-b03x': 'leapmotor-b03x.webp', 'leapmotor-b05': 'leapmotor-b05.webp', 'leapmotor-b10': 'leapmotor-b10.webp', 'leapmotor-c10': 'leapmotor-c10.webp', 'leapmotor-t03': 'leapmotor-t03.webp'}
PHOTOS = {k: uri(f'{ROOT}/img/{f}', 'image/webp') for k, f in PHOTO_FILES.items()}
BODY = {'SUV': ('SUV', 'suv'), 'Hečbek': ('Hečbek', 'hatch'), 'Sedan': ('Sedan', 'sedan'), 'Karavan': ('Karavan', 'sedan'),
        'Gradski automobil': ('Gradski', 'hatch'), 'Pikap': ('Pikap', None), 'Kombi': ('Kombi', None),
        'Kamion': ('Kamion', None), 'Autobus': ('Autobus', None)}

NOT_PASSENGER = {'Kombi', 'Kamion', 'Autobus'}
# models shown with the brand logo instead of a car picture (no usable photo yet)
LOGO_IMG = {'jmev-ewind', 'lynk-co-02'}
brands, models = {}, {}
for slug, c in content.items():
    d = data[c['data_slug']]
    ids = []
    for m in d['models']:
        if not (m.get('powertrain') or '').startswith('EV'):
            continue
        if m.get('listed_on_site') is False:
            continue
        if m.get('body') in NOT_PASSENGER:  # vans, trucks and buses are kept in the data but not listed
            continue
        mid = model_id(slug, c['name'], m['name'])
        cls, sil = BODY.get(m.get('body'), (None, None))
        mc = mcontent.get(mid, {})
        models[mid] = {'b': slug, 'n': m['name'], 'cls': cls, 'sil': sil, 'r': m.get('range_wltp_km'), 'lg': mid in LOGO_IMG,
                       'kwh': mc.get('kwh'), 'rt': mc.get('range_text'), 'desc': mc.get('desc')}
        ids.append(mid)
    mime = 'image/png' if c['logo'].endswith('.png') else 'image/svg+xml'
    brands[slug] = {'name': c['name'], 'logo': uri(f"{ROOT}/logos/{c['logo']}", mime), 'founded': c['founded'], 'hq': c['hq'],
                    'importer': c['importer'], 'about': c['about'], 'dealers': c['dealers'], 'models': ids,
                    'pending': False}
if 'lynk-co-02' in models: models['lynk-co-02']['cls'] = 'Crossover'  # matches the homepage card
json.dump({k: v for k, v in sorted(models.items())}, open(f'{ROOT}/build/model_ids.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- shared CSS
common_css = r'''
.crumbs{display:flex;gap:8px;flex-wrap:wrap;font-size:13px;color:var(--muted)}
.crumbs a:hover{color:var(--ink)}
.crumbs span[aria-current]{color:var(--ink);font-weight:600}
.bhero{padding-block:32px 72px}
.bhero-grid{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:48px;align-items:center;margin-top:28px}
.bhero-logo{aspect-ratio:16/10;border-radius:var(--r-xl);background:var(--bg-alt);border:1px solid var(--line);display:grid;place-items:center;color:var(--ink);padding:14%}
.bhero-logo .blogo{max-width:none;width:100%;height:100%}
.bhero h1{font-size:clamp(36px,4.4vw,56px);line-height:1.05;letter-spacing:-.035em}
.bhero .lede{font-size:17px;color:var(--muted);margin-top:14px;max-width:56ch}
.facts{display:flex;flex-wrap:wrap;gap:12px 32px;margin-top:24px;padding-top:20px;border-top:1px solid var(--line)}
.facts div{display:flex;flex-direction:column;gap:2px;min-width:0}
.facts dt{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.facts dd{margin:0;font-size:15px;font-weight:600;color:var(--ink)}
.bhero .ctas{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.b-about{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:48px;align-items:start}
.b-about h2{font-size:clamp(26px,3vw,36px)}
.b-about p{color:var(--text);font-size:16px;max-width:62ch}
.b-about p+p{margin-top:14px}
.feat{display:grid;grid-template-columns:1fr 1fr;gap:10px 16px;margin:2px 0 0;padding-top:14px;border-top:1px solid var(--line)}
.feat div{display:flex;flex-direction:column;gap:2px;min-width:0}
.feat dt{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.feat dd{margin:0;font-size:13px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.feat dd.na{color:var(--muted);font-weight:500}
.mcard .img.ph{place-items:center;color:var(--faint);font-size:12px;font-weight:600;letter-spacing:.08em;padding:0}
.mcard h3 a:hover{text-decoration:underline;text-underline-offset:3px}
.models-empty{grid-column:1/-1;text-align:center;color:var(--muted);padding:56px 16px;border:1.5px dashed var(--line);border-radius:var(--r-lg)}
.models-empty strong{display:block;color:var(--ink);font-size:18px;margin-bottom:6px}
.models-empty a{color:var(--green-ink);font-weight:600}
/* dealer contact (wireframe) */
.dealer{display:grid;grid-template-columns:minmax(0,280px) minmax(0,1fr);gap:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);margin-top:28px}
.dealer-side{padding:24px;border-right:1px solid var(--line)}
.dealer-side .lbl{display:block;font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--muted);margin-bottom:8px}
.city{position:relative}
.city .dd-btn{height:44px;padding:0 14px;border:1px solid var(--line);border-radius:10px;background:var(--bg-alt);color:var(--ink);font-weight:600}
.city.open .dd-btn{border-color:var(--green)}
.city .dd-pop{top:calc(100% + 6px)}
.dealer-side .hint{font-size:12px;color:var(--muted);margin-top:12px}
.dealer-main{padding:8px 32px 24px;min-width:0}
.dealer.single{grid-template-columns:1fr}
.dealer.single .dealer-side{display:none}
.dcard+.dcard{border-top:1px solid var(--line)}
.dcard{padding-block:20px}
.dcard-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding-bottom:14px;border-bottom:1px solid var(--line)}
.dcard h3{font-size:18px}
.dgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px 24px;margin:16px 0 0}
.dgrid div{min-width:0}
.dgrid dt{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.dgrid dd{margin:4px 0 0;font-size:14px;color:var(--ink);overflow-wrap:anywhere}
.dgrid dd.na{color:var(--muted)}
.dgrid a{color:var(--green-ink);font-weight:600}
.dgrid a:hover{text-decoration:underline}
.dnote{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}
.dnote dt{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.dnote dd{margin:6px 0 0;font-size:13px;color:var(--muted);max-width:70ch}
/* other brands */
.others{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
.others a{display:flex;flex-direction:column;align-items:center;gap:8px;padding:14px;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);font-size:13px;font-weight:600;color:var(--ink);transition:border-color .2s,transform .2s cubic-bezier(.16,1,.3,1)}
.others a:hover{border-color:var(--green);transform:translateY(-2px)}
.others .ol{width:100%;height:36px;display:grid;place-items:center;color:var(--ink)}
.others .blogo{max-width:96px}
/* model page */
.mhero{padding-block:32px 72px}
.mhero-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:48px;align-items:center;margin-top:28px}
.mhero-img{aspect-ratio:16/10;border-radius:var(--r-xl);border:1px solid var(--line);background:#ffffff;display:grid;place-items:center;overflow:hidden;padding:5%}
.mhero-img img{width:100%;height:100%;object-fit:contain}
.mhero-img.sil{background:var(--surface-2);color:var(--ink);padding:10%}
.mhero-img.sil svg{width:100%;height:auto}
.mhero-img.lg{background:#ffffff;color:#16202e;padding:16% 24%}
.mhero-img.lg .blogo{width:100%;height:100%;max-width:none;opacity:.3}
.mhero-img.ph{background:var(--surface-2);color:var(--faint);font-size:13px;font-weight:600;letter-spacing:.08em}
.mbrand{display:inline-flex;align-items:center;padding:8px 18px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink);transition:border-color .2s}
.mbrand:hover{border-color:var(--green)}
.mbrand-logo{width:96px;height:26px;display:grid;place-items:center;color:var(--ink)}
.mbrand-logo .blogo{max-width:none;width:100%;height:100%}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.mhero h1{font-size:clamp(34px,4.2vw,54px);line-height:1.05;letter-spacing:-.035em;margin-top:18px}
.mhero .tags{margin-top:14px}
.mhero .lede{font-size:17px;color:var(--muted);margin-top:16px;max-width:52ch}
.mhero .ctas{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.specs-tbl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 48px;margin:28px 0 0}
.specs-tbl div{display:flex;justify-content:space-between;gap:24px;padding:16px 0;border-bottom:1px solid var(--line);min-width:0}
.specs-tbl dt{color:var(--muted);font-size:14px}
.specs-tbl dd{margin:0;color:var(--ink);font-weight:600;font-size:14px;text-align:right;font-variant-numeric:tabular-nums}
.specs-tbl dd.na{color:var(--muted);font-weight:500}
@media (max-width:900px){
  .bhero-grid,.b-about,.mhero-grid{grid-template-columns:1fr;gap:28px}
  .bhero-logo{max-width:320px}
  .dealer{grid-template-columns:1fr}
  .dealer-side{border-right:0;border-bottom:1px solid var(--line)}
  .dealer-main{padding:8px 20px 20px}
  .specs-tbl{grid-template-columns:1fr}
}
@media (max-width:560px){.dgrid{grid-template-columns:1fr 1fr}}
'''

contact_html = '''
  <section class="sec alt" id="kontakt-distributera">
    <div class="wrap">
      <h2 style="font-size:clamp(26px,3vw,36px)" id="contact-title">Kontaktirajte distributera</h2>
      <div class="dealer">
        <div class="dealer-side">
          <span class="lbl" id="city-lbl">IZABERITE GRAD</span>
          <div class="city" id="city"></div>
          <p class="hint" id="city-hint"></p>
        </div>
        <div class="dealer-main" id="dealer-main" aria-live="polite"></div>
      </div>
    </div>
  </section>
'''

# ---------------------------------------------------------------- shared JS
common_js = r'''
  const BRANDS=__BRANDS__, MODELS=__MODELS__, PHOTOS=__PHOTOS__;
  const $=id=>document.getElementById(id);
  const esc=t=>String(t??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const plural=n=>n===1?'1 električni model':(n%10>=2&&n%10<=4&&(n%100<12||n%100>14))?n+' električna modela':n+' električnih modela';
  const logo=(u,cls)=>'<span class="blogo'+(cls?' '+cls:'')+'" aria-hidden="true" style="--l:url('+u+')"></span>';
  const VB={sedan:'0 0 320 112',hatch:'0 0 320 112',suv:'0 0 320 120'};
  const NOTE='Test vožnju i dostupnost modela dogovarate direktno sa distributerom. Kontakt podaci su preuzeti sa zvaničnog sajta uvoznika i mogu se promeniti.';
  const mb=$('menu-btn'),nl=$('nav-links');
  if(mb){mb.addEventListener('click',()=>{const o=nl.classList.toggle('open');mb.setAttribute('aria-expanded',o)})}

  // model card (brand page grid and "related models")
  function card(id){
    const m=MODELS[id], b=BRANDS[m.b], label=b.name+' '+m.n, href='model.html#'+id;
    const img=PHOTOS[id]?'<div class="img photo"><img src="'+PHOTOS[id]+'" alt="'+esc(label)+'" loading="lazy"></div>'
      :m.lg?'<div class="img lg" role="img" aria-label="'+esc(label)+'">'+logo(b.logo)+'</div>'
      :m.sil?'<div class="img"><svg viewBox="'+VB[m.sil]+'" role="img" aria-label="'+esc(label)+'"><use href="#car-'+m.sil+'"/></svg></div>'
      :'<div class="img ph">FOTOGRAFIJA USKORO</div>';
    const f=(k,v)=>'<div><dt>'+k+'</dt><dd'+(v?'':' class="na"')+'>'+(v?esc(v):'Na upit')+'</dd></div>';
    const link=img.replace(/^<div /,'<a href="'+href+'" tabindex="-1" aria-hidden="true" ').replace(/ role="img"/,'').replace(/<\/div>$/,'</a>');
    return '<article class="mcard">'+link+'<div class="body"><div><div class="mk">'+esc(b.name.toUpperCase())+'</div><h3><a href="'+href+'">'+esc(m.n)+'</a></h3></div>'
      +'<div class="tags"><span class="tag">100% EV</span>'+(m.cls?'<span class="tag gray">'+esc(m.cls.toUpperCase())+'</span>':'')+'</div>'
      +'<dl class="feat">'+f('DOMET (WLTP)',m.r?'do '+m.r+' km':null)+f('KLASA',m.cls)+f('MENJAČ','Automatski')+f('POGON','Električni')+'</dl>'
      +'<a href="'+href+'" class="btn btn-dark">Detalji modela <span class="arr">→</span></a></div></article>';
  }

  // dealer contact
  let dealerBrand=null, city=null;
  const tel=n=>'<a href="tel:'+esc(n.replace(/\(0\)/,'').replace(/[^+\d]/g,''))+'">'+esc(n)+'</a>';
  const val=(v,link)=>!v?'<dd class="na">Nije objavljeno</dd>':'<dd>'+(link||esc(v))+'</dd>';
  // a dealer detail that is not published is left out entirely
  // a field may hold one value or a list (several phone numbers or emails)
  const list=v=>Array.isArray(v)?v:[v];
  const tels=v=>list(v).map(tel).join('<br>'), lines=v=>list(v).map(esc).join('<br>');
  const row=(label,v,link)=>v?'<div><dt>'+label+'</dt><dd>'+(link||esc(v))+'</dd></div>':'';
  function initDealers(b){
    dealerBrand=b;
    const cities=[...new Set(b.dealers.map(d=>d.city))].sort((a,c)=>(a==='Beograd'?-1:c==='Beograd'?1:a==='Srbija'?1:c==='Srbija'?-1:a.localeCompare(c,'sr')));
    city=cities[0]; buildCity(cities); showDealers();
    document.querySelector('.dealer').classList.toggle('single',cities.length===1);
    $('city-hint').textContent=cities.length>4?'Distributeri u '+cities.length+' gradova.':cities.length>1?'Distributeri u '+cities.length+' grada.':'';
  }
  function showDealers(){
    const list=dealerBrand.dealers.filter(d=>d.city===city);
    $('dealer-main').innerHTML=list.map(d=>'<article class="dcard"><div class="dcard-head"><h3>'+esc(d.name)+'</h3><span class="tag gray">'+esc((d.role||'').toUpperCase())+'</span></div>'
      +'<dl class="dgrid">'
      +row('ADRESA',d.address)
      +row('GRAD',d.zip||(d.city!=='Srbija'?d.city:null))
      +row((d.phone_label||'TELEFON'),d.phone,d.phone?tels(d.phone):'')
      +row('WEBSITE',d.website,d.website?'<a href="https://'+esc(d.website)+'" target="_blank" rel="noopener">'+esc(d.website)+' ↗</a>':'')
      +row('EMAIL',d.email,d.email?lines(d.email):'')
      +'<div><dt>RADNO VREME</dt>'+(d.hours?'<dd>'+esc(d.hours)+'</dd>':'<dd class="na">Proverite kod distributera</dd>')+'</div>'
      +(d.assist?'<div><dt>PODRŠKA NA PUTU</dt><dd>'+tel(d.assist)+'</dd></div>':'')
      +row('SERVIS · TELEFON',d.service_phone,d.service_phone?tels(d.service_phone):'')
      +row('SERVIS · EMAIL',d.service_email,d.service_email?lines(d.service_email):'')
      +row('SERVIS · RADNO VREME',d.service_hours)
      +row('REZERVNI DELOVI',d.parts_phone,d.parts_phone?tels(d.parts_phone):'')
      +'</dl></article>').join('')
      +'<dl class="dnote"><dt>NAPOMENA</dt><dd>'+NOTE+'</dd></dl>';
  }
  const check='<svg class="dd-check" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 7.5 5.8 10 11 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  let cityOutside=null;
  function buildCity(cities){
    const box=$('city');
    box.innerHTML='<button type="button" class="dd-btn set" id="city-btn" aria-haspopup="listbox" aria-expanded="false" aria-labelledby="city-lbl city-btn"><span class="dd-val">'+esc(city)+'</span><svg class="dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'
      +'<div class="dd-pop" hidden><div class="dd-list" role="listbox" aria-labelledby="city-lbl">'+cities.map(c=>'<div class="dd-opt" role="option" tabindex="-1" data-v="'+esc(c)+'" aria-selected="'+(c===city)+'"><span class="dd-txt">'+esc(c)+'</span>'+check+'</div>').join('')+'</div></div>';
    const btn=$('city-btn'), pop=box.querySelector('.dd-pop'), list=box.querySelector('.dd-list');
    const open=()=>{pop.hidden=false;btn.setAttribute('aria-expanded','true');box.classList.add('open');(list.querySelector('[aria-selected="true"]')||list.firstChild).focus()};
    const close=back=>{if(pop.hidden)return;pop.hidden=true;btn.setAttribute('aria-expanded','false');box.classList.remove('open');if(back)btn.focus()};
    const choose=v=>{city=v;btn.querySelector('.dd-val').textContent=v;list.querySelectorAll('.dd-opt').forEach(o=>o.setAttribute('aria-selected',o.dataset.v===v));close(true);showDealers()};
    btn.onclick=()=>pop.hidden?open():close();
    btn.onkeydown=e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();open()}};
    list.onclick=e=>{const o=e.target.closest('.dd-opt');if(o)choose(o.dataset.v)};
    pop.onkeydown=e=>{const os=[...list.children],k=os.indexOf(document.activeElement);
      if(e.key==='ArrowDown'){e.preventDefault();(os[k+1]||os[0]).focus()}
      else if(e.key==='ArrowUp'){e.preventDefault();(os[k-1]||os[os.length-1]).focus()}
      else if(e.key==='Enter'){e.preventDefault();if(os[k])choose(os[k].dataset.v)}
      else if(e.key==='Escape'){e.preventDefault();close(true)}
      else if(e.key==='Tab')close()};
    if(cityOutside)document.removeEventListener('click',cityOutside);
    cityOutside=e=>{if(!box.contains(e.target))close()};document.addEventListener('click',cityOutside);
  }
'''

# ---------------------------------------------------------------- brand page
brand_body = '''
<main id="top">
  <section class="bhero">
    <div class="wrap">
      <nav class="crumbs" aria-label="Putanja"><a href="index.html">Početna</a><span aria-hidden="true">/</span><a href="index.html#brendovi">Brendovi</a><span aria-hidden="true">/</span><span aria-current="page" id="b-crumb">Brend</span></nav>
      <div class="bhero-grid">
        <div class="bhero-logo" id="b-logo"></div>
        <div>
          <h1 id="b-name">Brend</h1>
          <p class="lede" id="b-lede"></p>
          <dl class="facts" id="b-facts"></dl>
          <div class="ctas">
            <a href="#modeli-brenda" class="btn btn-dark">Električni modeli <span class="arr">→</span></a>
            <a href="#kontakt-distributera" class="btn btn-ghost">Kontaktirajte distributera</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="sec alt" id="o-brendu">
    <div class="wrap b-about">
      <h2 id="b-about-title">O brendu</h2>
      <div id="b-about"></div>
    </div>
  </section>

  <section class="sec" id="modeli-brenda">
    <div class="wrap">
      <div class="head"><div><h2 id="b-models-title">Električni modeli</h2><p id="b-models-sub"></p></div></div>
      <div class="models" id="b-models"></div>
      <p class="price-note">Domet je po WLTP normi za verziju sa najvećim dometom, prema podacima proizvođača, oktobar 2026.</p>
    </div>
  </section>
''' + contact_html + '''
  <section class="sec">
    <div class="wrap">
      <div class="head"><h2 style="font-size:clamp(24px,2.6vw,32px)">Ostali brendovi</h2></div>
      <div class="others" id="others"></div>
    </div>
  </section>
</main>
'''

brand_js = r'''
  let cur=null;
  function render(slug){
    const b=BRANDS[slug]; if(!b)return render('byd');
    cur=slug;
    document.title=b.name+' električni automobili u Srbiji | ev-china.rs';
    $('b-crumb').textContent=b.name; $('b-name').textContent=b.name;
    $('b-logo').innerHTML=logo(b.logo); $('b-logo').setAttribute('aria-label',b.name+' logo'); $('b-logo').setAttribute('role','img');
    $('b-lede').textContent=b.models.length?'Svi električni modeli brenda '+b.name+' u Srbiji, sa dometom, klasom vozila i kontaktom distributera.':'Brend '+b.name+' u Srbiji: informacije o brendu i kontakt distributera.';
    const facts=[['OSNOVAN',b.founded],['SEDIŠTE',b.hq],['UVOZNIK U SRBIJI',b.importer],['EV MODELA',b.models.length||(b.pending?'Proveravamo':'Trenutno nema')]];
    $('b-facts').innerHTML=facts.filter(f=>f[1]).map(f=>'<div><dt>'+f[0]+'</dt><dd>'+esc(f[1])+'</dd></div>').join('');
    $('b-about-title').textContent='O brendu '+b.name;
    $('b-about').innerHTML=b.about.map(p=>'<p>'+esc(p)+'</p>').join('');
    $('b-models-title').textContent='Električni modeli '+b.name;
    $('b-models-sub').textContent=b.models.length?plural(b.models.length)+' dostupno u Srbiji.':'';
    $('b-models').innerHTML=b.models.length?b.models.map(card).join('')
      :(b.pending?'<div class="models-empty"><strong>Podatke još proveravamo</strong>Ponudu ovog brenda u Srbiji još nismo proverili. Dodaćemo električne modele ako ih uvoznik bude nudio.</div>'
        :'<div class="models-empty"><strong>Trenutno bez električnih modela</strong>Uvoznik trenutno ne nudi potpuno električne putničke automobile u Srbiji. Dodaćemo ih čim budu dostupni.</div>');
    initDealers(b);
    $('others').innerHTML=Object.entries(BRANDS).filter(([s])=>s!==slug).map(([s,o])=>'<a href="#'+s+'"><span class="ol">'+logo(o.logo)+'</span>'+esc(o.name)+'</a>').join('');
  }
  function route(){
    const s=(location.hash||'').slice(1);
    if(BRANDS[s]){render(s);window.scrollTo({top:0,behavior:'auto'})}
    else if(!cur)render('byd');
  }
'''

# ---------------------------------------------------------------- model page
model_body = '''
<main id="top">
  <section class="mhero">
    <div class="wrap">
      <nav class="crumbs" aria-label="Putanja"><a href="index.html">Početna</a><span aria-hidden="true">/</span><a href="index.html#brendovi">Brendovi</a><span aria-hidden="true">/</span><a id="m-crumb-brand" href="brend.html">Brend</a><span aria-hidden="true">/</span><span aria-current="page" id="m-crumb">Model</span></nav>
      <div class="mhero-grid">
        <div class="mhero-img" id="m-img"></div>
        <div>
          <a class="mbrand" id="m-brand" href="brend.html"></a>
          <h1 id="m-name">Model</h1>
          <div class="tags" id="m-tags"></div>
          <p class="lede" id="m-lede"></p>
          <dl class="facts" id="m-keys"></dl>
          <div class="ctas">
            <a href="#kontakt-distributera" class="btn btn-dark">Kontaktirajte distributera <span class="arr">→</span></a>
            <a href="brend.html" class="btn btn-ghost" id="m-all">Svi modeli brenda</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="sec alt" id="o-modelu">
    <div class="wrap b-about">
      <h2 id="m-about-title">O modelu</h2>
      <div id="m-about"></div>
    </div>
  </section>

  <section class="sec" id="specifikacije">
    <div class="wrap">
      <h2 style="font-size:clamp(26px,3vw,36px)">Osnovne specifikacije</h2>
      <dl class="specs-tbl" id="m-specs"></dl>
      <p class="price-note">Domet je po WLTP normi za verziju sa najvećim dometom, prema podacima proizvođača, oktobar 2026. Opremu i tehničke podatke proverite kod distributera.</p>
    </div>
  </section>
''' + contact_html + '''
  <section class="sec">
    <div class="wrap">
      <div class="head"><div><h2 style="font-size:clamp(24px,2.6vw,32px)" id="m-rel-title">Ostali modeli brenda</h2></div><a class="link" id="m-rel-link" href="brend.html">Stranica brenda →</a></div>
      <div class="models" id="m-related"></div>
    </div>
  </section>
</main>
'''

model_js = r'''
  let cur=null;
  const kwh=v=>v?(String(v).replace('.',',')+' kWh'):null;
  function render(id){
    const m=MODELS[id]; if(!m)return render('byd-seal');
    cur=id;
    const b=BRANDS[m.b], full=b.name+' '+m.n.replace(new RegExp('^'+b.name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\s','i'),'');
    document.title=full+' | ev-china.rs';
    $('m-crumb').textContent=m.n; $('m-crumb-brand').textContent=b.name; $('m-crumb-brand').href='brend.html#'+m.b;
    $('m-brand').href='brend.html#'+m.b; $('m-brand').innerHTML='<span class="mbrand-logo">'+logo(b.logo)+'</span><span class="sr-only">'+esc(b.name)+'</span>'; $('m-brand').title='Svi modeli brenda '+b.name;
    $('m-all').href='brend.html#'+m.b; $('m-rel-link').href='brend.html#'+m.b;
    $('m-name').textContent=m.n;
    $('m-tags').innerHTML='<span class="tag">100% EV</span>'+(m.cls?'<span class="tag gray">'+esc(m.cls.toUpperCase())+'</span>':'');
    const box=$('m-img'); box.className='mhero-img';
    if(PHOTOS[id]){box.innerHTML='<img src="'+PHOTOS[id]+'" alt="'+esc(full)+'">'}
    else if(m.lg){box.classList.add('lg');box.setAttribute('role','img');box.setAttribute('aria-label',full);box.innerHTML=logo(BRANDS[m.b].logo)}
    else if(m.sil){box.classList.add('sil');box.innerHTML='<svg viewBox="'+VB[m.sil]+'" role="img" aria-label="'+esc(full)+'"><use href="#car-'+m.sil+'"/></svg>'}
    else{box.classList.add('ph');box.textContent='FOTOGRAFIJA USKORO'}
    const clsWord=m.cls?(m.cls==='Gradski'?'gradski automobil':m.cls==='Hečbek'?'hečbek':m.cls==='Karavan'?'karavan':m.cls==='Pikap'?'pikap':m.cls==='Kombi'?'kombi':m.cls==='Kamion'?'kamion':m.cls==='Autobus'?'autobus':m.cls==='Sedan'?'sedan':'SUV'):'model';
    $('m-lede').textContent='Potpuno električni '+clsWord+' brenda '+b.name+', dostupan u Srbiji preko ovlašćenog distributera.';
    const keys=[['DOMET (WLTP)',m.r?'do '+m.r+' km':'Na upit'],['KLASA',m.cls||'Na upit'],['MENJAČ','Automatski'],['POGON','Električni']];
    $('m-keys').innerHTML=keys.map(k=>'<div><dt>'+k[0]+'</dt><dd>'+esc(k[1])+'</dd></div>').join('');
    $('m-about-title').textContent='O modelu '+m.n;
    const desc=m.desc||[m.n+' je potpuno električni '+clsWord+' brenda '+b.name+' koji je dostupan na srpskom tržištu.','Detaljne tehničke podatke i opremu dodajemo čim ih uvoznik objavi. Do tada informacije proverite kod ovlašćenog distributera.'];
    $('m-about').innerHTML=desc.map(p=>'<p>'+esc(p)+'</p>').join('');
    const sp=[['Brend',b.name],['Model',m.n],['Klasa vozila',m.cls],['Pogon','100% električni'],['Domet (WLTP)',m.rt?'do '+m.rt:(m.r?'do '+m.r+' km':null)],['Baterija',kwh(m.kwh)],['Menjač','Automatski, jedan stepen prenosa'],['Uvoznik u Srbiji',b.importer]];
    $('m-specs').innerHTML=sp.map(s=>'<div><dt>'+s[0]+'</dt><dd'+(s[1]?'':' class="na"')+'>'+esc(s[1]||'Na upit')+'</dd></div>').join('');
    $('contact-title').textContent='Kontaktirajte distributera za '+m.n;
    initDealers(b);
    const rel=b.models.filter(x=>x!==id);
    $('m-rel-title').textContent='Ostali električni modeli '+b.name;
    $('m-related').innerHTML=rel.length?rel.map(card).join('')
      :'<div class="models-empty"><strong>Ovo je trenutno jedini električni model brenda '+esc(b.name)+' u Srbiji.</strong>Pogledajte <a href="index.html#brendovi">ostale brendove</a> i njihove električne modele.</div>';
  }
  function route(){
    const s=(location.hash||'').slice(1);
    if(MODELS[s]){render(s);window.scrollTo({top:0,behavior:'auto'})}
    else if(!cur)render('byd-seal');
  }
'''

def page(title, desc, body, js):
    script = ('<script>\n(function(){\n' + common_js + js +
              "  window.addEventListener('hashchange',route);\n  route();\n})();\n</script>\n")
    script = (script.replace('__BRANDS__', json.dumps(brands, ensure_ascii=False))
                    .replace('__MODELS__', json.dumps(models, ensure_ascii=False))
                    .replace('__PHOTOS__', json.dumps(PHOTOS)))
    return ('<!doctype html>\n<html lang="sr">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<title>{title}</title>\n<meta name="description" content="{desc}">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">\n'
            '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}'
            + style + common_css + '</style>\n</head>\n<body>\n' + sprite + header + body + footer + script + '</body>\n</html>\n')

for fname, html in [('brend.html', page('Brend | ev-china.rs', 'Kineski električni automobili u Srbiji po brendovima: modeli, domet i kontakt distributera.', brand_body, brand_js)),
                    ('model.html', page('Model | ev-china.rs', 'Kineski električni automobil u Srbiji: opis, osnovne specifikacije i kontakt distributera.', model_body, model_js))]:
    open(f'{ROOT}/{fname}', 'w', encoding='utf-8').write(html)
    print(fname, len(html) // 1024, 'KB')
print(len(brands), 'brands,', len(models), 'models')

# ---------------------------------------------------------------- homepage data (brand counts, model list, search data)
# The homepage search covers every listed model, not only the featured cards.
DISPLAY = {'byd-atto-2-comfort': 'Atto 2'}
TAGS = {'SUV': 'suv', 'Hečbek': 'hatch', 'Sedan': 'sedan', 'Pikap': 'pickup', 'Gradski automobil': 'city hatch', 'Karavan': 'wagon'}
CITY = {'byd-dolphin-surf', 'jmev-ev3', 'leapmotor-t03', 'dongfeng-box', 'jac-e30x'}
NO_DATA_YET = set()  # brands whose importer site could not be checked
def esc_html(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
def disp(mid):
    m, b = models[mid], brands[models[mid]['b']]
    n = m['n']
    if n.lower().startswith(b['name'].lower() + ' '):
        n = n[len(b['name']) + 1:]
    return DISPLAY.get(mid, n)
home = open(f'{ROOT}/index.html', encoding='utf-8').read()
featured = set(re.findall(r'<article class="mcard"[^>]*>.*?href="model\.html#([a-z0-9-]+)"', home, re.S))
# 1. brand tile counts
def count_label(slug):
    n = len(brands[slug]['models'])
    if n:
        return '<span class="count">' + (f'{n} EV model' if n == 1 else f'{n} EV modela') + '</span>'
    return '<span class="count soon">' + ('Podaci uskoro' if slug in NO_DATA_YET else 'Trenutno bez EV modela') + '</span>'
for slug in brands:
    home, k = re.subn(r'(<a class="btile" href="brend\.html#' + slug + r'".*?)<span class="count[^"]*">[^<]*</span>',
                      lambda mm: mm.group(1) + count_label(slug), home, count=1, flags=re.S)
    assert k == 1, slug
# 2. model dropdown
groups = ''
for slug, b in brands.items():
    if b['models']:
        groups += '\n            <optgroup label="' + esc_html(b['name']) + '">' + ''.join('<option>' + esc_html(disp(i)) + '</option>' for i in b['models']) + '</optgroup>'
home, k = re.subn(r'(<select id="f-model"><option value="">Svi modeli</option>).*?(\n\s*</select>)',
                  lambda mm: mm.group(1) + groups + mm.group(2), home, count=1, flags=re.S)
assert k == 1
# 3. search data
rows = []
for slug, b in brands.items():
    for i in b['models']:
        m = models[i]
        body = next((x.get('body') for x in data[content[slug]['data_slug']]['models'] if model_id(slug, b['name'], x['name']) == i), None)
        tags = TAGS.get(body, '') + (' city' if i in CITY and 'city' not in TAGS.get(body, '') else '')
        rows.append({'id': i, 'b': b['name'], 'n': disp(i), 't': tags.split(), 'r': m['r'], 'cls': ('Crossover' if i == 'lynk-co-02' else m['cls']),
                     'sil': m['sil'], 'img': PHOTOS.get(i) if i not in featured else None, 'lg': m['lg']})
blob = '<script type="application/json" id="ev-models">' + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + '</script>'
if 'id="ev-models"' in home:
    home = re.sub(r'<script type="application/json" id="ev-models">.*?</script>', lambda mm: blob, home, count=1, flags=re.S)
else:
    home = home.replace('\n<footer>', '\n' + blob + '\n<footer>', 1)
open(f'{ROOT}/index.html', 'w', encoding='utf-8').write(home)
print('index.html updated:', len(rows), 'searchable models,', len(featured), 'featured')
