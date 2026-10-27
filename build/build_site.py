"""Builds the complete static site into site/ from the homepage source (index.html), the data files
(data/brands.json, build/brand_content.json, build/model_content.json), logos/ and img/.

Every brand and model gets its own crawlable page with the content in the HTML (no JavaScript needed
to read it), its own title, description, canonical URL, Open Graph tags and JSON-LD structured data.
Run from the ev-china folder:  python3 build/build_site.py
"""
import base64, collections, hashlib, html, json, os, re, shutil

ROOT = '.'
OUT = f'{ROOT}/site'
DOMAIN = 'https://www.evomobil.rs'   # change here if the site goes live on another address
import datetime as _dt
UPDATED = _dt.date.today().isoformat()  # build date, used only in sitemap/structured data
UPDATED_TXT = 'oktobar 2026'
SITE = 'evomobil.rs'

E = lambda t: html.escape(str(t if t is not None else ''), quote=True)

src = open(f'{ROOT}/build/homepage-template.html', encoding='utf-8').read()
content = json.load(open(f'{ROOT}/build/brand_content.json', encoding='utf-8'))
mcontent = json.load(open(f'{ROOT}/build/model_content.json', encoding='utf-8'))
data = {b['slug']: b for b in json.load(open(f'{ROOT}/data/brands.json', encoding='utf-8'))['brands']}

def slugify(t):
    t = t.lower().replace('&', ' ').replace('č', 'c').replace('ć', 'c').replace('š', 's').replace('ž', 'z').replace('đ', 'dj').replace('ë', 'e').replace('é', 'e').replace('è', 'e')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def model_id(brand_slug, brand_name, model_name):
    n = model_name
    if n.lower().startswith(brand_name.lower() + ' '):
        n = n[len(brand_name) + 1:]
    # renamed models keep their original page address
    return ID_KEEP.get((brand_slug, n), brand_slug + '-' + slugify(n))

ID_KEEP = {('bmw', 'i4 M60'): 'bmw-i4-m50', ('bmw', 'iX M70'): 'bmw-ix-m-model', ('bmw', 'i5 M60'): 'bmw-i5'}

# ------------------------------------------------------------------ data
PHOTO_FILES = {'kia-ev9': 'evomobil-kia-ev9.webp', 'porsche-cayenne-turbo-electric': 'evomobil-porsche-cayenne-turbo-electric.webp', 'bmw-i4-m50': 'evomobil-bmw-i4-m50.webp', 'bmw-ix-m-model': 'evomobil-bmw-ix-m-model.webp', 'bmw-i7-m70': 'evomobil-bmw-i7-m70.webp', 'bmw-i4': 'evomobil-bmw-i4.webp', 'bmw-i5': 'evomobil-bmw-i5.webp', 'bmw-ix': 'evomobil-bmw-ix.webp', 'bmw-ix3': 'evomobil-bmw-ix3.webp', 'bmw-ix5': 'evomobil-bmw-ix5.webp', 'bmw-i3': 'evomobil-bmw-i3.webp', 'bmw-ix1': 'evomobil-bmw-ix1.webp', 'bmw-i7': 'evomobil-bmw-i7.webp', 'hyundai-ioniq-5': 'evomobil-hyundai-ioniq-5.webp', 'hyundai-ioniq-6': 'evomobil-hyundai-ioniq-6.webp', 'hyundai-ioniq-6-n': 'evomobil-hyundai-ioniq-6-n.webp', 'hyundai-ioniq-9': 'evomobil-hyundai-ioniq-9.webp', 'hyundai-inster': 'evomobil-hyundai-inster.webp', 'cupra-tavascan': 'evomobil-cupra-tavascan.webp', 'mazda-cx-6e': 'evomobil-mazda-cx-6e.webp', 'mazda-6e': 'evomobil-mazda-6e.webp', 'cupra-raval': 'evomobil-cupra-raval.webp', 'dacia-spring': 'evomobil-dacia-spring.webp', 'kia-ev6': 'evomobil-kia-ev6.webp', 'kia-ev4': 'evomobil-kia-ev4.webp', 'kia-ev3': 'evomobil-kia-ev3.webp', 'kia-ev2': 'evomobil-kia-ev2.webp', 'porsche-macan-4': 'evomobil-porsche-macan-4.webp', 'porsche-taycan-4': 'evomobil-porsche-taycan-4.webp', 'ford-explorer': 'evomobil-ford-explorer.webp', 'toyota-bz4x': 'evomobil-toyota-bz4x.webp', 'ford-mustang-mach-e': 'evomobil-ford-mustang-mach-e.webp', 'ford-puma-gen-e': 'evomobil-ford-puma-gen-e.webp', 'renault-twingo-e-tech': 'evomobil-renault-twingo-e-tech.webp', 'renault-5-e-tech': 'evomobil-renault-5-e-tech.webp', 'renault-4-e-tech': 'evomobil-renault-4-e-tech.webp', 'suzuki-e-vitara': 'evomobil-suzuki-e-vitara.webp', 'volkswagen-id-polo': 'evomobil-volkswagen-id-polo.webp', 'volkswagen-id-3-neo': 'evomobil-volkswagen-id-3-neo.webp', 'volkswagen-id-4': 'evomobil-volkswagen-id-4.webp', 'volkswagen-id-5': 'evomobil-volkswagen-id-5.webp', 'volkswagen-id-7': 'evomobil-volkswagen-id-7.webp', 'foton-etunland': 'evomobil-foton-etunland.webp', 'byd-dolphin-surf': 'evomobil-byd-dolphin-surf.webp', 'byd-atto-2-comfort': 'evomobil-byd-atto-2-comfort.webp', 'byd-atto-3-evo': 'evomobil-byd-atto-3-evo.webp', 'byd-seal': 'evomobil-byd-seal.webp', 'byd-sealion-7': 'evomobil-byd-sealion-7.webp', 'mg-mg4-electric': 'evomobil-mg-mg4-electric.webp', 'mg-mg5-electric': 'evomobil-mg-mg5-electric.webp', 'mg-mgs5-ev': 'evomobil-mg-mgs5-ev.webp', 'changan-deepal-s05': 'evomobil-changan-deepal-s05.webp', 'changan-deepal-s07': 'evomobil-changan-deepal-s07.webp', 'geely-e5': 'evomobil-geely-e5.webp', 'dongfeng-box': 'evomobil-dongfeng-box.webp', 'jac-t9-ev': 'evomobil-jac-t9-ev.webp', 'jac-e30x': 'evomobil-jac-e30x.webp', 'jmev-ev3': 'evomobil-jmev-ev3.webp', 'jmev-elight': 'evomobil-jmev-elight.webp', 'leapmotor-b03x': 'evomobil-leapmotor-b03x.webp', 'leapmotor-b05': 'evomobil-leapmotor-b05.webp', 'leapmotor-b10': 'evomobil-leapmotor-b10.webp', 'leapmotor-c10': 'evomobil-leapmotor-c10.webp', 'leapmotor-t03': 'evomobil-leapmotor-t03.webp', 'mini-countryman': 'evomobil-mini-countryman.webp', 'mini-aceman': 'evomobil-mini-aceman.webp', 'mini-cooper': 'evomobil-mini-cooper.webp', 'opel-astra-electric': 'evomobil-opel-astra-electric.webp', 'opel-frontera-electric': 'evomobil-opel-frontera-electric.webp', 'opel-mokka-electric': 'evomobil-opel-mokka-electric.webp', 'citroen-e-c3': 'evomobil-citroen-e-c3.webp', 'citroen-e-c3-aircross': 'evomobil-citroen-e-c3-aircross.webp', 'citroen-e-c4': 'evomobil-citroen-e-c4.webp', 'citroen-e-c4-x': 'evomobil-citroen-e-c4-x.webp', 'skoda-elroq': 'evomobil-skoda-elroq.webp', 'skoda-enyaq': 'evomobil-skoda-enyaq.webp', 'skoda-enyaq-coupe': 'evomobil-skoda-enyaq-coupe.webp', 'volvo-ex30': 'evomobil-volvo-ex30.webp', 'volvo-ex60': 'evomobil-volvo-ex60.webp', 'volvo-ex90': 'evomobil-volvo-ex90.webp', 'volvo-es90': 'evomobil-volvo-es90.webp', 'porsche-macan-4s': 'evomobil-porsche-macan-4s.webp', 'peugeot-e-208': 'evomobil-peugeot-e-208.webp', 'peugeot-e-2008': 'evomobil-peugeot-e-2008.webp', 'peugeot-e-308': 'evomobil-peugeot-e-308.webp', 'peugeot-e-3008': 'evomobil-peugeot-e-3008.webp'}
BODY = {'SUV': ('SUV', 'suv'), 'Hečbek': ('Hečbek', 'hatch'), 'Sedan': ('Sedan', 'sedan'), 'Karavan': ('Karavan', 'sedan'),
        'Gradski automobil': ('Gradski', 'hatch'), 'Pikap': ('Pikap', None)}
NOT_PASSENGER = {'Kombi', 'Kamion', 'Autobus'}
LOGO_IMG = {'jmev-ewind', 'lynk-co-02', 'audi-rs-e-tron-gt'}          # shown with the faded brand logo until a photo exists
DISPLAY = {'byd-atto-2-comfort': 'Atto 2'}
TAGS = {'SUV': 'suv', 'Hečbek': 'hatch', 'Sedan': 'sedan', 'Pikap': 'pickup', 'Gradski automobil': 'city hatch', 'Karavan': 'wagon'}
CITY = {'byd-dolphin-surf', 'jmev-ev3', 'leapmotor-t03', 'dongfeng-box', 'jac-e30x'}
CLS_WORD = {'Gradski': 'gradski automobil', 'Hečbek': 'hečbek', 'Karavan': 'karavan', 'Pikap': 'pikap', 'Sedan': 'sedan',
            'SUV': 'SUV', 'Crossover': 'crossover'}

brands, models = {}, {}
for slug, c in content.items():
    d = data[c['data_slug']]
    ids = []
    for m in d['models']:
        if not (m.get('powertrain') or '').startswith('EV') or m.get('listed_on_site') is False or m.get('body') in NOT_PASSENGER:
            continue
        mid = model_id(slug, c['name'], m['name'])
        cls, sil = BODY.get(m.get('body'), (None, None))
        if mid == 'lynk-co-02':
            cls = 'Crossover'
        mc = mcontent.get(mid, {})
        n = m['name'][len(c['name']) + 1:] if m['name'].lower().startswith(c['name'].lower() + ' ') else m['name']
        n = DISPLAY.get(mid, n)
        full = m['name'] if m['name'].lower().startswith(c['name'].lower()) else c['name'] + ' ' + n
        if mid == 'byd-atto-2-comfort':
            full = 'BYD Atto 2'
        tags = TAGS.get(m.get('body'), '') + (' city' if mid in CITY and 'city' not in TAGS.get(m.get('body'), '') else '')
        models[mid] = {'id': mid, 'b': slug, 'n': n, 'full': full, 'cls': cls, 'sil': sil, 'r': m.get('range_wltp_km'),
                       'rt': mc.get('range_text'), 'kwh': mc.get('kwh'), 'desc': mc.get('desc'), 'lg': mid in LOGO_IMG,
                       'photo': PHOTO_FILES.get(mid), 'tags': tags.split(), 'body': m.get('body')}
        ids.append(mid)
    brands[slug] = dict(c, slug=slug, models=ids)

import unicodedata as _ud
ORDER = sorted(brands, key=lambda s: _ud.normalize('NFKD', brands[s]['name']).encode('ascii', 'ignore').decode().lower())

# ------------------------------------------------------------------ homepage source: brand counts, model dropdown, search data
def esc_html(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
featured = set(re.findall(r'<article class="mcard"[^>]*>.*?href="modeli/([a-z0-9-]+)\.html"', src, re.S))
for slug in brands:
    n = len(brands[slug]['models'])
    lab = '<span class="count">' + (f'{n} EV model' if n == 1 else f'{n} EV modela') + '</span>' if n else '<span class="count soon">Trenutno bez EV modela</span>'
    src, k = re.subn(r'(<a class="btile" href="brendovi/' + slug + r'\.html".*?)<span class="count[^"]*">[^<]*</span>', lambda mm: mm.group(1) + lab, src, count=1, flags=re.S)
    assert k == 1, slug
groups = ''.join('\n            <optgroup label="' + esc_html(brands[s]['name']) + '">' + ''.join('<option>' + esc_html(models[i]['n']) + '</option>' for i in brands[s]['models']) + '</optgroup>'
                 for s in ORDER if brands[s]['models'])
src, k = re.subn(r'(<select id="f-model"><option value="">Svi modeli</option>).*?(\n\s*</select>)', lambda mm: mm.group(1) + groups + mm.group(2), src, count=1, flags=re.S)
assert k == 1
rows = [{'id': i, 'b': brands[m['b']]['name'], 'n': m['n'], 't': m['tags'], 'r': m['r'], 'cls': m['cls'], 'kwh': m['kwh'], 'sil': m['sil'],
         'img': ('img/' + m['photo']) if m['photo'] else None, 'lg': m['lg']} for i, m in models.items()]
blob = '<script type="application/json" id="ev-models">' + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + '</script>'
brand_opts = ''.join('<option>' + esc_html(brands[s]['name']) + '</option>' for s in ORDER if brands[s]['models'])
src, k = re.subn(r'(<select id="f-brand"><option value="">Svi brendovi</option>).*?(</select>)', lambda mm: mm.group(1) + brand_opts + mm.group(2), src, count=1, flags=re.S)
assert k == 1
src = re.sub(r'<script type="application/json" id="ev-models">.*?</script>', lambda mm: blob, src, count=1, flags=re.S)
open(f'{ROOT}/build/homepage-template.html', 'w', encoding='utf-8').write(src)

# ------------------------------------------------------------------ pieces taken from the homepage source
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
sprite = re.search(r'(<svg width="0" height="0" style="position:absolute" aria-hidden="true">.*?</svg>\n)(?=\n<header)', src, re.S).group(1)
header = re.search(r'<header class="site">.*?</header>', src, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', src, re.S).group(0)
ads_section = open(f'{ROOT}/build/oglasavanje_section.html', encoding='utf-8').read()
copy_js = open(f'{ROOT}/build/copy_email.js', encoding='utf-8').read()
# dimensions/seats: build/model_dims.json, official manufacturer/importer sources only (null = not published)
DIMS = {}
if os.path.exists(f'{ROOT}/build/model_dims.json'):
    DIMS = {r['id']: r for r in json.load(open(f'{ROOT}/build/model_dims.json', encoding='utf-8'))}

def mm(v):
    return f'{v:,}'.replace(',', '.') + ' mm' if v else None

# embedded images in the source are swapped for real files in the output
FILE_BY_HASH = {}
for folder in ('img', 'logos'):
    for f in os.listdir(f'{ROOT}/{folder}'):
        FILE_BY_HASH[hashlib.md5(base64.b64encode(open(f'{ROOT}/{folder}/{f}', 'rb').read())).hexdigest()] = f'{folder}/{f}'

def unembed(text, prefix=''):
    def sub(m):
        f = FILE_BY_HASH.get(hashlib.md5(m.group(2).encode()).hexdigest())
        return prefix + f if f else m.group(0)
    return re.sub(r'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=]+)', sub, text)

def relink(fragment, pre):
    """Make the shared header/footer links work from any folder depth."""
    if not pre and False:
        return fragment
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith(('http', 'mailto:', 'tel:', '//')):
            return m.group(0)
        if url == '#top':
            url = 'index.html'
        elif url.startswith('#'):
            url = 'index.html' + url
        return f'{attr}"{pre}{url}"'
    return re.sub(r'(<a\b[^>]*?href=)"([^"]*)"', fix, fragment)

def logo_style(slug, pre):
    return f"--l:url({pre}logos/{brands[slug]['logo']})"

def logo_span(slug, pre, cls=''):
    sq = ' sq' if brands[slug]['logo'] in ('dongfeng.svg', 'geely.svg', 'jmev.png', 'leapmotor.svg', 'mg.svg') and cls != 'nosq' else ''
    return f'<span class="blogo{sq}" aria-hidden="true" style="{logo_style(slug, pre)}"></span>'

def num(v):
    return str(v).replace('.', ',')

def range_txt(m, long=False):
    if long and m['rt']:
        return 'do ' + m['rt']
    return f"do {m['r']} km" if m['r'] else None

def kwh_txt(m):
    return num(m['kwh']) + ' kWh' if m['kwh'] else None

def plural_models(n):
    if n % 10 == 1 and n % 100 != 11:
        return f'{n} električni model'
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f'{n} električna modela'
    return f'{n} električnih modela'

def cities_of(slug):
    seen = []
    for d in brands[slug]['dealers']:
        if d['city'] not in seen and d['city'] != 'Srbija':
            seen.append(d['city'])
    seen.sort(key=lambda c: (c != 'Beograd', c))
    return seen

def join_sr(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' i ' + items[-1]

# ------------------------------------------------------------------ extra CSS for the generated pages
extra_css = r'''
/* brand logos are <img> (see "brand logos as images" in the build): dark in the light theme, white in the dark theme */
.blogo.has-img{background:none!important;-webkit-mask:none!important;mask:none!important;position:relative}
.blogo.has-img img{position:absolute;inset:0;display:block;width:100%;height:100%;max-width:none;object-fit:contain;filter:brightness(0);opacity:.92}
.mbrand-logo .blogo.has-img img{object-position:left center}
:root[data-evtheme="dark"] .blogo.has-img img{filter:brightness(0) invert(1);opacity:.95}

/* phones: no blue flash on tap (text can still be selected with a long press) */
html{-webkit-tap-highlight-color:transparent}
a,button,label,summary,[role="button"],[role="option"],input,select{-webkit-tap-highlight-color:transparent}


/* light by default for every visitor: no automatic dark mode from the phone or browser setting (dark only with the site button) */
:root{color-scheme:only light}
:root[data-evtheme="dark"]{color-scheme:dark}
/* dark buttons ("Pronađi automobil", "Prihvati"...): a little darker on hover */
.btn-dark:hover{background:color-mix(in srgb,var(--btn) 78%,#000);box-shadow:none}
:root[data-evtheme="dark"] .btn-dark:hover{background:color-mix(in srgb,var(--btn) 86%,#000)}
/* dark buttons with an arrow ("Detalji modela →" ...): stay the same black on hover, only the arrow moves */
.btn-dark:has(.arr):hover{background:var(--btn);box-shadow:none}
.btn-dark:has(.arr):active{transform:none}
.btn .arr{display:inline-block;transition:transform .25s cubic-bezier(.16,1,.3,1)}
/* outlined pills (filters, links): subtle hover */
.filters button,.link,.res-reset{transition:background-color .2s,border-color .2s,color .2s}
.filters button:not([aria-pressed="true"]):hover,.link:hover,.res-reset:hover{background:var(--bg-alt);border-color:color-mix(in srgb,var(--ink) 22%,transparent);color:var(--ink)}

/* header logo on mouse hover (class lg-play is added by the header script, desktop pointers only):
   the bolt empties, charges green from bottom to top, pulses and throws sparks; the E steps back and returns */
.brand .brand-mark{overflow:visible}
.brand-mark .lg-e,.brand-mark .lg-bolt{transform-box:fill-box;transform-origin:50% 50%}
.brand-mark .lg-lvl{fill:#3aab18;transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);opacity:0}
.brand-mark .lg-sp{fill:#3aab18;opacity:0}
.lg-play .brand-mark .lg-e{animation:lgE 1.5s cubic-bezier(.16,1,.3,1)}
.lg-play .brand-mark .lg-bolt{animation:lgBase 1.5s ease-in-out,lgPulse .5s .85s cubic-bezier(.3,0,.2,1)}
.lg-play .brand-mark .lg-lvl{animation:lgRise 1.5s cubic-bezier(.5,0,.3,1)}
.lg-play .brand-mark .lg-sp{animation:lgSpark .65s .85s ease-out}
.lg-play .brand-mark .lg-s2{animation-delay:.9s}.lg-play .brand-mark .lg-s3{animation-delay:.95s}.lg-play .brand-mark .lg-s4{animation-delay:.88s}
@keyframes lgE{0%,100%{transform:none}16%,78%{transform:translateX(-8px)}}
@keyframes lgBase{0%{fill-opacity:1}8%,56%{fill-opacity:.2}60%,100%{fill-opacity:1}}
@keyframes lgRise{0%,8%{transform:scaleY(0);opacity:1}56%{transform:scaleY(1);opacity:1}64%,100%{transform:scaleY(1);opacity:0}}
@keyframes lgPulse{0%,100%{transform:scale(1);filter:none}35%{transform:scale(1.22);filter:drop-shadow(0 0 7px rgba(76,194,38,.85))}70%{transform:scale(.96)}}
@keyframes lgSpark{0%{opacity:1;transform:translate(0,0)}100%{opacity:0;transform:translate(var(--dx),var(--dy))}}

.mcard h3 a:hover{text-decoration:none!important}   /* model name on cards: no underline on hover */

.fgroup .fopt.zero{display:none!important}
.fgroup .fmore[hidden],.fgroup[hidden]{display:none!important}

footer .about{max-width:36ch;line-height:1.6}
/* links in dealer cards: green underline on hover */
.dgrid a{text-decoration:none;text-underline-offset:3px}
.dgrid a:hover{color:var(--green-ink);text-decoration:underline;text-decoration-color:var(--green);text-decoration-thickness:1.5px}
/* dark buttons ("Prihvati", "Pronađi automobil"...): visible hover */
.btn-dark{transition:background-color .2s,box-shadow .2s,transform .2s}
.btn-dark:active{transform:translateY(1px)}
.btn-ghost{transition:border-color .2s,background-color .2s}
.btn-ghost:hover{background:var(--bg-alt)}
@media (prefers-reduced-motion:reduce){.btn-dark,.btn-ghost{transition:none}}

/* dealer city picker: button + homepage-style list (.dd-pop) */
.city select.enh{position:absolute;left:0;bottom:0;width:1px;height:1px;opacity:0;pointer-events:none}
.city-btn{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;height:46px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--surface);color:var(--ink);font:600 14px var(--font);cursor:pointer;text-align:left;transition:border-color .2s,background .2s}
.city-btn:hover{border-color:color-mix(in srgb,var(--ink) 25%,transparent)}
.city.open .city-btn{background:var(--surface-2);border-color:var(--line)}
.city.open .dd-chev{transform:rotate(180deg)}
.city-btn:focus{outline:none}
.city-btn:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.city .dd-pop{width:100%;max-width:none}
.dd-opt:focus-visible{outline:none}
/* brand logo above the model name */
.mbrand .mbrand-logo{width:84px;height:28px}

/* footer reveal: the page slides up over the footer, last section has rounded bottom corners */
body{position:relative;z-index:0}   /* own stacking context, so the footer (z-index -1) stays clickable */
main{background:var(--bg);border-radius:0 0 32px 32px}
main>section:last-of-type{border-bottom-left-radius:32px;border-bottom-right-radius:32px}
footer{position:relative;z-index:-1;box-shadow:0 -40px 0 0 #16202e}
:root[data-evtheme="dark"] footer{box-shadow:0 -40px 0 0 #0a0f16}
.ft-reveal footer{position:sticky;bottom:0}
@media (max-width:760px){main,main>section:last-of-type{border-bottom-left-radius:24px;border-bottom-right-radius:24px}}
@media (prefers-reduced-motion:reduce){.ft-reveal footer{position:relative}}

.calc-link{margin-top:14px;font-size:14px;font-weight:600}.calc-link a{color:var(--green-ink);text-decoration:none}.calc-link a:hover{text-decoration:underline;text-underline-offset:3px}

.crumbs{display:flex;gap:8px;flex-wrap:wrap;font-size:13px;color:var(--muted)}
.crumbs a:hover{color:var(--ink)}
.crumbs span[aria-current]{color:var(--ink);font-weight:600}
.bhero,.mhero,.phero{padding-block:32px 64px}
/* all-models catalog: sidebar filters + grid */
.cat-layout{display:grid;grid-template-columns:256px minmax(0,1fr);gap:40px;align-items:start}
.cat-side{position:sticky;top:96px;max-height:calc(100vh - 116px);overflow-y:auto;overflow-x:hidden;padding:2px 22px 16px 2px;display:flex;flex-direction:column;gap:22px;overscroll-behavior:contain;scrollbar-width:thin;scrollbar-color:var(--line) transparent;scrollbar-gutter:stable}
.cat-side::-webkit-scrollbar{width:6px}
.cat-side::-webkit-scrollbar-thumb{background:var(--line);border-radius:999px}
.cat-side-head{display:none}
.fgroup{border:0;margin:0;padding:0 0 18px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:2px;min-width:0}
.fgroup legend{font-size:14px;font-weight:600;color:var(--ink);margin-bottom:10px;padding:0}
.fopt{display:flex;align-items:center;gap:12px;padding:7px 10px;border-radius:10px;cursor:pointer;font-size:14px;color:var(--ink);transition:background .15s}
.fopt:hover{background:var(--bg-alt)}
.fopt span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fopt em{font-style:normal;font-size:12px;color:var(--faint);font-variant-numeric:tabular-nums}
.fopt:has(input:checked) span{font-weight:600}
.fopt:has(input:checked) em{color:var(--muted)}
/* custom checkbox + radio: ink fill, readable in both themes */
.fopt input{appearance:none;-webkit-appearance:none;width:18px;height:18px;margin:0;flex:none;display:grid;place-items:center;border:1.5px solid color-mix(in srgb,var(--ink) 30%,transparent);border-radius:5px;background:var(--surface);cursor:pointer;transition:background .15s,border-color .15s}
.fopt:hover input{border-color:color-mix(in srgb,var(--ink) 55%,transparent)}
.fopt input:checked{background:var(--ink);border-color:var(--ink)}
.fopt input:checked::after{content:"";width:4px;height:8px;border:solid var(--surface);border-width:0 2px 2px 0;transform:translateY(-1px) rotate(45deg)}
.fopt input:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.fgroup .fopt.more{display:none}
.fgroup.open-all .fopt.more{display:flex}
.fmore,.freset{align-self:flex-start;background:none;border:0;padding:6px 10px;margin-top:2px;font:600 13px var(--font);color:var(--green-ink);cursor:pointer;border-radius:999px}
.fmore:hover,.freset:hover{text-decoration:underline;text-underline-offset:3px}
.fmore:focus-visible,.freset:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.freset{color:var(--muted);margin-top:-8px}
.cat-apply,.cat-open{display:none}
.cat-bar{display:flex;align-items:center;gap:16px;margin-bottom:20px}
.cat-count{margin:0 auto 0 0;font-size:14px;color:var(--muted)}
/* sort: custom listbox in the site's pill style */
.csel{position:relative;display:flex;align-items:center;gap:10px}
.csel-lab{font-size:13px;color:var(--muted)}
.csel-btn{display:inline-flex;align-items:center;gap:10px;height:40px;padding:0 16px 0 18px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink);font:600 13px var(--font);cursor:pointer;transition:border-color .15s}
.csel-btn::after{content:"";width:6px;height:6px;border:solid var(--muted);border-width:0 1.5px 1.5px 0;transform:translateY(-2px) rotate(45deg);transition:transform .2s}
.csel-btn[aria-expanded="true"]::after{transform:translateY(1px) rotate(-135deg)}
.csel-btn:hover{border-color:color-mix(in srgb,var(--ink) 30%,transparent)}
.csel-btn:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.csel-menu{position:absolute;top:calc(100% + 8px);right:0;z-index:20;min-width:190px;margin:0;padding:6px;list-style:none;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}
.csel-menu[hidden]{display:none}
.csel-menu li{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:9px 12px;border-radius:10px;font-size:14px;color:var(--ink);cursor:pointer;outline:none}
.csel-menu li:hover,.csel-menu li:focus{background:var(--bg-alt)}
.csel-menu li[aria-selected="true"]{font-weight:600}
.csel-menu li[aria-selected="true"]::after{content:"";width:4px;height:8px;border:solid var(--green-ink);border-width:0 2px 2px 0;transform:translateY(-1px) rotate(45deg)}
.cat-main{min-width:0}
.cat-main .models{grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.cat-main .mcard[hidden]{display:none}
.cat-empty{display:flex;flex-direction:column;align-items:flex-start;gap:14px;padding:40px 28px;border:1px dashed var(--line);border-radius:var(--r-lg);color:var(--muted)}
.cat-empty[hidden]{display:none}
.cat-empty strong{color:var(--ink);font-size:16px}
.cat-scrim{position:fixed;inset:0;background:rgba(15,23,42,.45);z-index:60}
.cat-scrim[hidden]{display:none}
body.no-scroll{overflow:hidden}
@media (max-width:1180px){.cat-main .models{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:900px){
  .cat-layout{grid-template-columns:1fr;gap:0}
  .cat-side{position:fixed;top:0;bottom:0;left:0;z-index:61;width:min(340px,88vw);max-height:none;background:var(--surface);padding:20px 22px 24px 20px;transform:translateX(-102%);transition:transform .28s cubic-bezier(.16,1,.3,1);box-shadow:var(--shadow);gap:18px}
  .cat-side.open{transform:none}
  .cat-side-head{display:flex;align-items:center;justify-content:space-between}
  .cat-side-head h2{font-size:20px}
  .cat-close{width:40px;height:40px;border-radius:50%;border:1px solid var(--line);background:var(--surface);font-size:22px;line-height:1;color:var(--ink);cursor:pointer}
  .cat-apply{display:inline-flex;position:sticky;bottom:0;margin-top:auto;flex:none;box-shadow:0 -8px 0 4px var(--surface),0 -16px 12px 4px var(--surface)}
  .freset{margin:0 0 36px;padding:10px 10px}
  .cat-open{display:inline-flex;height:42px;padding:0 18px}
  .cat-bar{flex-wrap:wrap;gap:10px 12px}
  .cat-count{order:3;width:100%;margin:0}
  .csel-lab{display:none}
}
@media (prefers-reduced-motion:reduce){.cat-side,.csel-btn::after{transition:none}}
/* compare: card button, bottom bar, comparison table */
.mcard{position:relative}
.cmp-add{position:absolute;top:10px;right:10px;z-index:2;width:34px;height:34px;padding:0;display:grid;place-items:center;border-radius:50%;border:1px solid var(--line);background:color-mix(in srgb,var(--surface) 92%,transparent);color:var(--muted);cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.cmp-add svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.cmp-add:hover{color:var(--ink)}
.cmp-add:hover{border-color:color-mix(in srgb,var(--ink) 35%,transparent)}
.cmp-add[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--surface)}
.cmp-add:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.cmp-bar{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:70;display:flex;align-items:center;gap:14px;padding:8px 8px 8px 20px;border-radius:999px;background:var(--surface);border:1px solid var(--line);box-shadow:0 12px 32px rgba(15,23,42,.18);max-width:calc(100vw - 24px)}
.cmp-bar[hidden]{display:none}
.cmp-bar-t{font-size:13px;color:var(--muted)}
.cmp-bar-x{background:none;border:0;font:600 13px var(--font);color:var(--muted);cursor:pointer;padding:6px}
.cmp-bar-go{height:40px;padding:0 18px;white-space:nowrap}
@media (max-width:560px){.cmp-bar{left:12px;right:12px;transform:none;padding-left:16px;gap:8px}.cmp-bar-t{flex:1;font-size:12px;line-height:1.3}}
.cmp-pick{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.cmp-slot{display:flex;flex-direction:column;gap:6px;min-width:0}
.cmp-slot label{font-size:13px;font-weight:600;color:var(--muted)}
.cmp-slot select{height:46px;padding:0 40px 0 16px;border:1px solid var(--line);border-radius:999px;background:var(--surface) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M2.5 4.5 6 8l3.5-3.5' fill='none' stroke='%2364748b' stroke-width='1.6'/%3E%3C/svg%3E") no-repeat right 16px center;color:var(--ink);font:500 14px var(--font);appearance:none;-webkit-appearance:none;cursor:pointer;min-width:0;text-overflow:ellipsis}
.cmp-slot select:focus-visible{outline:2px solid var(--green);outline-offset:2px}
/* compare: custom model picker */
.cmp-slot{position:relative}
.cpick-native{position:absolute!important;width:1px!important;height:1px!important;opacity:0;pointer-events:none;bottom:0;left:0}
.cpick{position:relative}
.cpick-btn{width:100%;height:46px;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:0 18px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink);font:500 14px var(--font);cursor:pointer;text-align:left;transition:border-color .15s}
.cpick-btn.empty{color:var(--muted)}
.cpick-btn::after{content:"";flex:none;width:7px;height:7px;border:solid var(--muted);border-width:0 1.6px 1.6px 0;transform:translateY(-2px) rotate(45deg);transition:transform .2s}
.cpick.open .cpick-btn::after{transform:translateY(1px) rotate(-135deg)}
.cpick-btn:hover,.cpick.open .cpick-btn{border-color:color-mix(in srgb,var(--ink) 30%,transparent)}
.cpick-btn:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.cpick-val{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cpick-pop{position:absolute;top:calc(100% + 8px);left:0;right:0;z-index:30;padding:8px;background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:0 16px 40px rgba(15,23,42,.16)}
.cpick-pop[hidden]{display:none}
.cpick-q{width:100%;height:40px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--bg-alt);color:var(--ink);font:400 14px var(--font);outline:none;box-sizing:border-box}
.cpick-q:focus{border-color:var(--green);background:var(--surface)}
.cpick-list{list-style:none;margin:8px 0 0;padding:0 2px 2px;max-height:300px;overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin}
.cpick-g{padding:10px 10px 4px;font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.cpick-o{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 10px;border-radius:10px;font-size:14px;color:var(--ink);cursor:pointer;outline:none}
.cpick-o:hover,.cpick-o:focus{background:var(--bg-alt)}
.cpick-o[aria-selected="true"]{font-weight:600}
.cpick-o[aria-selected="true"]::after{content:"";width:4px;height:8px;border:solid var(--green-ink);border-width:0 2px 2px 0;transform:translateY(-1px) rotate(45deg)}
.cpick-o.off{color:var(--faint);cursor:default}
.cpick-o.off::after{content:"već izabran";font-size:11px;font-weight:500;width:auto;height:auto;border:0;transform:none}
.cpick-o.off:hover{background:none}
.cpick-o[hidden],.cpick-g[hidden]{display:none}
.cpick-none{margin:10px;font-size:13px;color:var(--muted)}
.cpick-none[hidden]{display:none}
.cmp-tools{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:18px 0 14px}
.cmp-tools .fopt{margin:0}
.cmp-tools .freset{margin:0}
.cmp-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r-lg);background:var(--surface)}
.cmp-wrap[hidden]{display:none}
.cmp-tbl{width:100%;border-collapse:collapse;table-layout:fixed;min-width:560px}
.cmp-tbl th,.cmp-tbl td{padding:14px 18px;text-align:left;border-bottom:1px solid var(--line);font-size:14px;vertical-align:top}
.cmp-tbl tbody tr:last-child th,.cmp-tbl tbody tr:last-child td{border-bottom:0}
.cmp-tbl tbody th{width:22%;font-weight:500;color:var(--muted)}
.cmp-tbl thead th:first-child{width:22%}
.cmp-tbl td{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.cmp-tbl td .na{color:var(--faint);font-weight:500}
.cmp-tbl thead th{position:relative;vertical-align:bottom;padding-top:18px}
.cmp-imgw{position:relative;width:100%;max-width:340px;margin-bottom:10px}
.cmp-img{position:relative;display:grid;place-items:center;aspect-ratio:2/1;width:100%;margin-bottom:0;border-radius:12px;background:#ffffff;border:1px solid var(--line);overflow:hidden;color:var(--faint);font-size:11px;font-weight:600}
.cmp-tbl .cmp-img img{position:absolute;inset:8% 6%;width:88%;height:84%;max-width:none;object-fit:contain;padding:0}
.cmp-img .blogo{width:60%;height:40%;background:var(--ink);opacity:.7}
.cmp-img svg{width:80%;height:80%;fill:var(--ink)}
.cmp-tbl .mk{display:block;font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.cmp-name{display:block;font:700 17px/1.25 var(--font-head);color:var(--ink);margin-top:2px;letter-spacing:-.01em}
.cmp-x{position:absolute;top:8px;right:8px;z-index:1;width:28px;height:28px;border-radius:50%;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-size:16px;line-height:1;cursor:pointer}
#cmp-empty{margin-top:4px}
#cmp-empty[hidden]{display:none}
.cmp-fn{margin:10px 0 0;font-size:12px;color:var(--muted)}
.cmp-fn[hidden]{display:none}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
@media (max-width:760px){.cmp-pick{grid-template-columns:1fr;gap:10px}
  .cmp-tbl{min-width:0}.cmp-tbl th,.cmp-tbl td{padding:10px 8px;font-size:13px;overflow-wrap:anywhere}
  .cmp-tbl tbody th,.cmp-tbl thead th:first-child{width:76px;font-size:12px}
  .cmp-tbl thead th{padding-top:12px}.cmp-imgw{margin-bottom:6px}.cmp-img{border-radius:10px;aspect-ratio:1.6/1}.cmp-tbl .cmp-img img{inset:6% 4%;width:92%;height:88%}
  .cmp-tbl thead th:not(:first-child){padding-left:5px;padding-right:5px}.cmp-name{font-size:14px}
  .cmp-x{top:4px;right:4px;width:20px;height:20px;font-size:12px;box-shadow:0 1px 3px rgba(15,23,42,.15)}}
.contact-rs .mail-link{font:600 16px var(--font);color:var(--green-ink);text-decoration:underline;text-underline-offset:3px}
/* contact + 404 */
.contact-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;max-width:none!important;margin-bottom:8px}
.ccard{display:flex;flex-direction:column;gap:6px;padding:22px 24px;border:1px solid var(--line);border-radius:var(--r-lg);background:var(--surface);color:var(--muted);font-size:14px;text-decoration:none!important;font-weight:400!important;transition:border-color .15s}
.ccard:hover{border-color:var(--green)}
.ccard-k{font-size:11px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.ccard strong{font:700 19px var(--font-head);color:var(--green-ink)}
.ccard>span:last-child{color:var(--muted)}
.ccard .ccard-more{color:var(--ink);font-weight:600}
.phero .answer a{color:var(--green-ink);font-weight:600;text-decoration:underline;text-underline-offset:3px}
@media (max-width:640px){.contact-cards{grid-template-columns:1fr}}
.nf{padding-block:72px 96px}
.nf-code{font:800 clamp(64px,10vw,120px)/1 var(--font-head);color:var(--green);letter-spacing:-.04em;margin:0 0 8px}
.nf .ctas{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
.nf-links{display:flex;flex-wrap:wrap;gap:8px 20px;list-style:none;padding:0;margin:28px 0 0;font-size:14px}
.nf-links a{color:var(--ink);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.demo-link{flex:none;align-self:flex-end}
@media (max-width:640px){.demo-link{align-self:flex-start}}
/* chargers map page */
.ch-legend{display:flex;align-items:center;gap:6px;margin:0;font-size:12px;color:var(--muted)}
.ch-legend .dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#16202e;border:2px solid var(--surface);box-shadow:0 0 0 1px var(--line);margin-left:8px}
.ch-legend .dot.fast{background:#16a34a}
.ch-map{height:520px;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--bg-alt);z-index:0}
.ch-map .maplibregl-ctrl-attrib{font-size:11px}
.ch-map .maplibregl-ctrl-group{border-radius:12px;box-shadow:var(--shadow)}
.ch-map .maplibregl-ctrl-group button{width:36px;height:36px}
.ch-map .maplibregl-cooperative-gesture-screen{font:600 15px var(--font)}
.ch-pop{display:flex;flex-direction:column;gap:3px;font:14px/1.4 var(--font);color:#16202e;min-width:180px}
.ch-pop strong{font-size:15px}
.ch-pop .k{font-weight:700;color:#15803d}
.ch-pop .a,.ch-pop .t{color:#475569;font-size:13px}
.ch-pop .a:empty,.ch-pop .t:empty{display:none}
.ch-pop a{align-self:flex-start;display:inline-flex;align-items:center;gap:6px;margin-top:8px;padding:7px 14px;border-radius:999px;background:#16202e;color:#fff;font-size:13px;font-weight:600;text-decoration:none;-webkit-tap-highlight-color:transparent}
.ch-pop a:hover{background:#2a3647}
.ch-pop a:focus{outline:none}
.ch-pop a:focus-visible{outline:2px solid #15803d;outline-offset:2px}
.maplibregl-popup-close-button:focus{outline:none}
.maplibregl-popup-content{border-radius:14px;padding:14px 18px;box-shadow:var(--shadow)}
.maplibregl-popup-close-button{font-size:18px;padding:2px 8px}
.ch-list{list-style:none;margin:20px 0 0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.ch{display:flex;flex-direction:column;gap:8px;padding:18px 20px;border:1px solid var(--line);border-radius:var(--r-lg);background:var(--surface)}
.ch{cursor:pointer;transition:border-color .15s,box-shadow .15s}.ch:hover{border-color:color-mix(in srgb,var(--green) 45%,var(--line))}.ch.sel{border-color:var(--green);box-shadow:0 0 0 1px var(--green)}
.ch[hidden]{display:none}
.ch-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.ch h3{font-size:16px;line-height:1.3;margin:0;letter-spacing:-.01em}
.ch-kw{flex:none;font-size:13px;font-weight:700;padding:3px 10px;border-radius:999px;background:var(--bg-alt);color:var(--ink);white-space:nowrap}
.ch-kw.fast{background:color-mix(in srgb,var(--green) 16%,transparent);color:var(--green-ink)}
.ch-kw.na{font-weight:500;color:var(--muted)}
.ch-addr,.ch-note{margin:0;font-size:13px;color:var(--muted)}
.ch-tags{display:flex;flex-wrap:wrap;gap:6px}
.ch-act{display:flex;align-items:center;gap:18px;margin-top:auto;padding-top:4px}
.ch-show{background:none;border:0;padding:0;font:600 13px var(--font);color:var(--green-ink);cursor:pointer}
.ch-act a{font-size:13px;font-weight:600;color:var(--ink)}
.ch-show:hover,.ch-act a:hover{text-decoration:underline;text-underline-offset:3px}
.ch-more{margin-top:16px}
.ch-more[hidden]{display:none}
@media (max-width:1180px){.ch-list{grid-template-columns:1fr}}
@media (max-width:900px){.ch-map{height:380px}.ch-legend{order:4;width:100%;margin-left:-8px}}

.bhero-grid{display:grid;grid-template-columns:minmax(0,260px) minmax(0,1fr);gap:48px;align-items:center;margin-top:28px}
.bhero-logo{aspect-ratio:16/10;border-radius:var(--r-xl);background:var(--bg-alt);border:1px solid var(--line);display:grid;place-items:center;color:var(--ink);position:relative}
.bhero-logo .blogo{position:absolute;inset:22% 20%;max-width:none;width:auto;height:auto}
.bhero h1,.phero h1{font-size:clamp(34px,4.2vw,54px);line-height:1.05;letter-spacing:-.035em}
.phero h1{margin-top:20px;max-width:22ch}
.lede{font-size:17px;color:var(--muted);margin-top:14px;max-width:62ch}
.answer{font-size:17px;color:var(--text);margin-top:16px;max-width:66ch;line-height:1.6}
.updated{font-size:12px;color:var(--faint);margin-top:12px}
.facts{display:flex;flex-wrap:wrap;gap:12px 32px;margin-top:24px;padding-top:20px;border-top:1px solid var(--line)}
.facts div{display:flex;flex-direction:column;gap:2px;min-width:0}
.facts dt{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.facts dd{margin:0;font-size:15px;font-weight:600;color:var(--ink)}
.ctas{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.b-about{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:48px;align-items:start}
.b-about h2{font-size:clamp(26px,3vw,36px)}
.b-about p{color:var(--text);font-size:16px;max-width:62ch}
.b-about p+p{margin-top:14px}
.h2s{font-size:clamp(26px,3vw,36px)}
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
.dealer{display:grid;grid-template-columns:minmax(0,280px) minmax(0,1fr);background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);margin-top:28px}
.dealer-side{padding:24px;border-right:1px solid var(--line)}
.dealer-side .lbl{display:block;font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--muted);margin-bottom:8px}
.city{position:relative}
.city select{width:100%;height:44px;padding:0 40px 0 14px;border:1px solid var(--line);border-radius:10px;background-color:var(--bg-alt);color:var(--ink);font:600 14px var(--font);cursor:pointer;appearance:none;-webkit-appearance:none;background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);background-position:calc(100% - 22px) 52%,calc(100% - 16px) 52%;background-size:6px 6px;background-repeat:no-repeat}
.dealer-side .hint{font-size:12px;color:var(--muted);margin-top:12px}
.dealer-main{padding:8px 32px 24px;min-width:0}
.dealer.single{grid-template-columns:1fr}
.dealer.single .dealer-side{display:none}
.dcard+.dcard{border-top:1px solid var(--line)}
.dcard{padding-block:20px}
.dcard-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding-bottom:14px;border-bottom:1px solid var(--line)}
.dcard h3{font-size:18px}
.dcard .brands-of{font-size:12px;color:var(--muted)}
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
.others{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
.others a{display:flex;flex-direction:column;align-items:center;gap:8px;padding:14px;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);font-size:13px;font-weight:600;color:var(--ink);transition:border-color .2s,transform .2s cubic-bezier(.16,1,.3,1)}
.others a:hover{border-color:var(--green);transform:translateY(-2px)}
.others .ol{width:100%;height:36px;display:grid;place-items:center;color:var(--ink)}
.others .blogo{max-width:96px}
.mhero-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:48px;align-items:center;margin-top:28px}
.mhero-img{aspect-ratio:16/10;border-radius:var(--r-xl);border:1px solid var(--line);background:#ffffff;display:grid;place-items:center;overflow:hidden;padding:5%}
.mhero-img img{width:100%;height:100%;object-fit:contain}
.mhero-img.sil{background:var(--surface-2);color:var(--ink);padding:10%}
.mhero-img.sil svg{width:100%;height:auto}
.mhero-img.lg{background:#ffffff;color:#16202e;padding:16% 24%}
.mhero-img.lg .blogo{width:100%;height:100%;max-width:none;opacity:.3}
.mbrand{display:inline-flex;align-items:center;padding:4px 0;color:var(--ink);transition:opacity .2s}
.mbrand:hover{opacity:.7}
.mbrand-logo{width:64px;height:22px;justify-items:start;display:grid;place-items:center;color:var(--ink)}
.mbrand-logo .blogo{max-width:none;width:100%;height:100%;-webkit-mask-position:left center;mask-position:left center}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.mhero h1{font-size:clamp(34px,4.2vw,54px);line-height:1.05;letter-spacing:-.035em;margin-top:18px}
.mhero .tags{margin-top:14px}
.specs-tbl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 48px;margin:28px 0 0}
.specs-tbl div{display:flex;justify-content:space-between;gap:24px;padding:16px 0;border-bottom:1px solid var(--line);min-width:0}
.specs-tbl dt{color:var(--muted);font-size:14px}
.specs-tbl dd{margin:0;color:var(--ink);font-weight:600;font-size:14px;text-align:right;font-variant-numeric:tabular-nums}
.specs-tbl dd.na{color:var(--muted);font-weight:500}
.tbl-wrap{overflow-x:auto;margin-top:24px;border:1px solid var(--line);border-radius:var(--r-lg);background:var(--surface)}
.cmp{width:100%;border-collapse:collapse;font-size:14px;min-width:560px}
.cmp th,.cmp td{text-align:left;padding:14px 18px;border-bottom:1px solid var(--line);vertical-align:middle}
.cmp thead th{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint);text-transform:uppercase;background:var(--bg-alt)}
.cmp tbody tr:last-child td{border-bottom:0}
.cmp td.n{font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink);white-space:nowrap}
.cmp td a{color:var(--ink);font-weight:600}
.cmp td a:hover{color:var(--green-ink);text-decoration:underline}
.cmp .rank{color:var(--faint);font-weight:600;width:40px}
.qa{display:grid;gap:12px;margin-top:24px;max-width:860px}
.qa details{border:1px solid var(--line);border-radius:var(--r);background:var(--surface);padding:16px 20px}
.qa summary{cursor:pointer;font-weight:600;color:var(--ink);list-style:none;display:flex;justify-content:space-between;align-items:center;gap:16px}
.qa .pm{flex:none;width:28px;height:28px;border-radius:50%;border:1px solid var(--line);display:grid;place-items:center;color:var(--muted);font-weight:500;transition:transform .2s,background .2s,color .2s}
.qa details[open] .pm{transform:rotate(45deg);background:var(--green);border-color:var(--green);color:#fff}
.qa summary::-webkit-details-marker{display:none}
.qa details p{margin-top:10px;color:var(--text);max-width:70ch}
.prose>*{max-width:720px}
.prose h2{font-size:clamp(22px,2.4vw,28px);margin-top:40px}
.prose h2:first-child{margin-top:0}
.prose p,.prose li{color:var(--text);font-size:16px;line-height:1.65}
.prose p{margin-top:12px}
.prose ul,.prose ol{margin:12px 0 0;padding-left:22px;display:grid;gap:6px}
.prose a{color:var(--green-ink);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.keybox{border:1px solid var(--line);border-radius:var(--r-lg);background:var(--bg-alt);padding:22px 24px;margin-top:24px;max-width:760px}
.keybox dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin:0}
.keybox dt{font-size:10px;font-weight:600;letter-spacing:.1em;color:var(--faint)}
.keybox dd{margin:4px 0 0;font-size:16px;font-weight:700;color:var(--ink)}
.sources{font-size:13px;color:var(--muted);margin-top:28px;max-width:760px}
.sources a{color:var(--green-ink)}
.city-nav{display:flex;flex-wrap:wrap;gap:8px;margin-top:24px}
.city-nav a{padding:8px 14px;border:1px solid var(--line);border-radius:999px;font-size:13px;font-weight:600;color:var(--ink);background:var(--surface)}
.city-nav a:hover{border-color:var(--green)}
.city-block{scroll-margin-top:90px}
.city-block[hidden],.dcard[hidden]{display:none}
#d-list.filtered .lede{display:none}
.cat-main .city-block h2{font-size:clamp(20px,2vw,24px)}
.cat-main .city-block+.city-block{margin-top:16px}
.cat-main .city-block .dealer-main{margin-top:0}
.city-block+.city-block{margin-top:40px}
.city-block h2{font-size:clamp(22px,2.4vw,28px)}
.city-block .dealer-main{padding:0 24px 8px;border:1px solid var(--line);border-radius:var(--r-lg);background:var(--surface);margin-top:16px}
.cat-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}
.cat-links a{padding:8px 14px;border:1px solid var(--line);border-radius:999px;font-size:13px;font-weight:600;color:var(--ink)}
.cat-links a[aria-current]{background:var(--btn);color:var(--btn-fg);border-color:var(--btn)}
.cat-links a:hover{border-color:var(--green)}
.all-link{margin-top:14px}
@media (max-width:900px){
  .bhero-grid,.b-about,.mhero-grid{grid-template-columns:1fr;gap:28px}
  .bhero-logo{max-width:180px}
  .dealer{grid-template-columns:1fr}
  .dealer-side{border-right:0;border-bottom:1px solid var(--line)}
  .dealer-main{padding:8px 20px 20px}
  .specs-tbl{grid-template-columns:1fr}
}
@media (max-width:560px){.dgrid{grid-template-columns:1fr 1fr}.dgrid .wide{grid-column:1/-1}.city-block .dealer-main{padding:0 16px 4px}}
'''

common_js = r'''
/* sidebar filters: live counts per option for the current selection; options with 0 results are hidden */
window.evcFacets=function(side,items,test){
  var inputs=[].slice.call(side.querySelectorAll('.fopt input')),cur={};
  inputs.forEach(function(i){cur[i.name]=cur[i.name]||[];if(i.checked)cur[i.name].push(i.value)});
  inputs.forEach(function(i){var f={},n=0;for(var k in cur)f[k]=cur[k];f[i.name]=[i.value];
    items.forEach(function(it){if(test(it,f))n++});
    var l=i.closest('.fopt'),em=l.querySelector('em');if(em)em.textContent=n;l.classList.toggle('zero',!n&&!i.checked)});
  [].slice.call(side.querySelectorAll('.fgroup')).forEach(function(g){
    var all=[].slice.call(g.querySelectorAll('.fopt')),vis=all.filter(function(l){return !l.classList.contains('zero')}),bt=g.querySelector('.fmore');
    if(bt){all.forEach(function(l){l.classList.remove('more')});vis.forEach(function(l,k){if(k>=4)l.classList.add('more')});
      var m=Math.max(0,vis.length-4);bt.dataset.more=m;bt.hidden=!m;if(!g.classList.contains('open-all'))bt.textContent='Prikaži više ('+m+')'}
    g.hidden=!vis.length});
};

(function(){
  // a new page always opens at its top (also inside embedding frames), unless the link points to a section
  try{if('scrollRestoration' in history)history.scrollRestoration='manual'}catch(e){}
  var toTop=function(){if(location.hash)return;var t=document.getElementById('top')||document.body;window.scrollTo(0,0);try{t.scrollIntoView({block:'start'})}catch(e){}window.scrollTo(0,0)};
  if(document.readyState!=='loading')toTop();else document.addEventListener('DOMContentLoaded',toTop);
  window.addEventListener('pageshow',function(e){if(!e.persisted)toTop()});
  /* when the page sits in an embedding frame that resizes after load, repeat the jump to the top a few times,
     unless the visitor has already started scrolling */
  var moved=false;['wheel','touchstart','keydown'].forEach(function(t){window.addEventListener(t,function(){moved=true},{passive:true,once:true})});
  var again=function(){if(!moved)toTop()};window.addEventListener('load',function(){again();setTimeout(again,150);setTimeout(again,500)});
  var mb=document.getElementById('menu-btn'),nl=document.getElementById('nav-links');
  if(mb&&nl)mb.addEventListener('click',function(){var o=nl.classList.toggle('open');mb.setAttribute('aria-expanded',o)});
  // dealer contact: every dealer is in the HTML; the city picker only shows one city at a time
  var sel=document.getElementById('city-sel');
  if(sel){var cards=[].slice.call(document.querySelectorAll('#dealer-main .dcard'));
    var show=function(){cards.forEach(function(c){c.hidden=c.getAttribute('data-city')!==sel.value})};
    sel.addEventListener('change',show);show();
    /* city picker: same dropdown list as the homepage search filters (.dd-pop / .dd-opt) instead of the system list */
    var wrap=sel.parentNode,lab=document.querySelector('label[for="city-sel"]');
    var cb=document.createElement('button');cb.type='button';cb.className='city-btn';cb.id='city-btn';
    cb.setAttribute('aria-haspopup','listbox');cb.setAttribute('aria-expanded','false');cb.setAttribute('aria-controls','city-list');
    cb.innerHTML='<span class="dd-val"></span><svg class="dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var cp=document.createElement('div');cp.className='dd-pop';cp.hidden=true;
    cp.innerHTML='<div class="dd-list" role="listbox" id="city-list" aria-label="Grad"></div>';
    sel.classList.add('enh');sel.tabIndex=-1;sel.setAttribute('aria-hidden','true');if(lab)lab.htmlFor='city-btn';
    wrap.appendChild(cb);wrap.appendChild(cp);
    var cl=cp.firstChild,ck='<svg class="dd-check" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 7.5 5.8 10 11 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var csync=function(){cb.firstChild.textContent=sel.value};
    var cclose=function(back){if(cp.hidden)return;cp.hidden=true;cb.setAttribute('aria-expanded','false');wrap.classList.remove('open');if(back)cb.focus()};
    var copen=function(){cl.innerHTML=[].map.call(sel.options,function(o){var t=document.createElement('span');t.textContent=o.text;
        return '<div class="dd-opt" role="option" tabindex="-1" data-v="'+t.innerHTML.replace(/"/g,'&quot;')+'" aria-selected="'+(o.value===sel.value)+'"><span class="dd-txt">'+t.innerHTML+'</span>'+ck+'</div>'}).join('');
      cp.hidden=false;cb.setAttribute('aria-expanded','true');wrap.classList.add('open');
      var cur=cl.querySelector('[aria-selected="true"]')||cl.querySelector('.dd-opt');if(cur){cur.scrollIntoView({block:'nearest'});cur.focus({preventScroll:true})}};
    var cchoose=function(v){sel.value=v;sel.dispatchEvent(new Event('change'));csync();cclose(true)};
    cb.addEventListener('click',function(){cp.hidden?copen():cclose()});
    cb.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();copen()}});
    cl.addEventListener('click',function(e){var o=e.target.closest('.dd-opt');if(o)cchoose(o.getAttribute('data-v'))});
    cp.addEventListener('keydown',function(e){var os=[].slice.call(cl.querySelectorAll('.dd-opt')),k=os.indexOf(document.activeElement);
      if(e.key==='ArrowDown'){e.preventDefault();(os[k+1]||os[0]).focus()}else if(e.key==='ArrowUp'){e.preventDefault();(os[k-1]||os[os.length-1]).focus()}
      else if(e.key==='Enter'||e.key===' '){e.preventDefault();if(k>=0)cchoose(os[k].getAttribute('data-v'))}else if(e.key==='Escape'){e.preventDefault();cclose(true)}else if(e.key==='Tab')cclose()});
    document.addEventListener('click',function(e){if(!wrap.contains(e.target))cclose()});
    csync();}
})();

(function(){
  /* "Uporedi": pick up to 3 models on any page, then open the comparison */
  var K='evc-cmp',base=/\/(modeli|brendovi)\//.test(location.pathname)?'../':'';
  function get(){try{return (JSON.parse(sessionStorage.getItem(K)||'[]')||[]).slice(0,3)}catch(e){return []}}
  function put(a){try{sessionStorage.setItem(K,JSON.stringify(a))}catch(e){}}
  var bar=null,msg=null;
  function sync(){
    var a=get();
    [].slice.call(document.querySelectorAll('.cmp-add')).forEach(function(b){var on=a.indexOf(b.dataset.cmp)>-1;b.setAttribute('aria-pressed',on);var l=on?'Ukloni iz poređenja':'Dodaj u poređenje';b.setAttribute('aria-label',l);b.title=l});
    if(document.getElementById('cmp-tbl'))return;
    if(!bar){bar=document.createElement('div');bar.className='cmp-bar';bar.setAttribute('role','region');bar.setAttribute('aria-label','Poređenje modela');
      bar.innerHTML='<span class="cmp-bar-t"></span><button type="button" class="cmp-bar-x">Očisti</button><a class="btn btn-dark cmp-bar-go"></a>';
      document.body.appendChild(bar);bar.querySelector('.cmp-bar-x').addEventListener('click',function(){put([]);sync()})}
    bar.hidden=!a.length;
    bar.querySelector('.cmp-bar-t').textContent=msg||(a.length===1?'Izaberite još jedan model za poređenje':'Izabrano '+a.length+' od 3 modela');
    var go=bar.querySelector('.cmp-bar-go');go.href=base+'uporedi.html?modeli='+a.join(',');go.textContent='Uporedi ('+a.length+') →';
  }
  window.evcCmpSync=sync;
  document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.cmp-add');if(!b)return;e.preventDefault();
    var a=get(),i=a.indexOf(b.dataset.cmp);msg=null;
    if(i>-1)a.splice(i,1);else if(a.length>=3)msg='Najviše 3 modela. Uklonite jedan da biste dodali novi.';else a.push(b.dataset.cmp);
    put(a);sync();if(msg)setTimeout(function(){msg=null;sync()},3500)});
  if(document.readyState!=='loading')sync();else document.addEventListener('DOMContentLoaded',sync);
  window.addEventListener('pageshow',sync);
})();
'''

NOTE = 'Test vožnju i dostupnost modela dogovarate direktno sa distributerom. Kontakt podaci su preuzeti sa zvaničnih sajtova uvoznika i distributera i mogu se promeniti.'

# ------------------------------------------------------------------ building blocks
def tel(n):
    return f'<a href="tel:{E(re.sub(r"[^+\d]", "", n.replace("(0)", "")))}">{E(n)}</a>'

def lst(v):
    return v if isinstance(v, list) else [v]

def drow(label, value, link=None):
    return f'<div><dt>{label}</dt><dd>{link or E(value)}</dd></div>' if value else ''

def no_service(t):
    if not t:
        return t
    t = re.sub(r'\s*\((?:[^)]*\bservis\w*[^)]*)\)', '', t, flags=re.I)
    t = re.sub(r'\s*(?:\bi\b|,|/|\+|&)\s*servis\w*', '', t, flags=re.I)
    t = re.sub(r'\bservis\w*\s*(?:\bi\b|,|/|\+|&)\s*', '', t, flags=re.I)
    return 'Prodaja' if re.search(r'servis', t, re.I) else t.strip()

def dealer_card(d, extra_head=''):
    d = dict(d, role=no_service(d.get('role')), phone_label=no_service(d.get('phone_label')))
    emails = lst(d['email']) if d.get('email') else []
    long_email = any(len(x) > 20 for x in emails)   # too long for half a phone-width card: give it its own full-width row
    email_row = (f'<div{" class=wide" if long_email else ""}><dt>EMAIL</dt><dd>' + '<br>'.join(E(x) for x in emails) + '</dd></div>') if emails else ''
    hours_row = '<div><dt>RADNO VREME</dt>' + (f'<dd>{E(d["hours"])}</dd>' if d.get('hours') else '<dd class="na">Proverite kod distributera</dd>') + '</div>'
    rows = (drow('ADRESA', d.get('address')) + drow('GRAD', d.get('zip') or (d['city'] if d['city'] != 'Srbija' else None))
            + drow(d.get('phone_label') or 'TELEFON', d.get('phone'), '<br>'.join(tel(x) for x in lst(d['phone'])) if d.get('phone') else None)
            + drow('WEBSITE', d.get('website'), f'<a href="https://{E(d["website"])}" target="_blank" rel="nofollow noopener">{E(d["website"])} ↗</a>' if d.get('website') else None)
            + (hours_row + email_row if long_email else email_row + hours_row))
    return (f'<article class="dcard" data-city="{E(d["city"])}"><div class="dcard-head"><h3>{E(d["name"])}</h3>'
            f'<span class="tag gray">{E((d.get("role") or "").upper())}</span>{extra_head}</div><dl class="dgrid">{rows}</dl></article>')

def dealer_section(slug, title):
    b = brands[slug]
    if not b['dealers']:
        return ('<section class="sec alt" id="kontakt-distributera"><div class="wrap"><h2>' + E(title) + '</h2>'
                '<p class="answer">Lista ovlašćenih distributera za ovaj brend još nije objavljena. Proverite aktuelne kontakte na zvaničnom sajtu brenda ili uvoznika.</p></div></section>')
    cities = cities_of(slug)
    dealers = sorted(b['dealers'], key=lambda d: (cities.index(d['city']) if d['city'] in cities else 99))
    opts = ''.join(f'<option value="{E(c)}">{E(c)}</option>' for c in cities)
    hint = (f'Distributeri u {len(cities)} gradova.' if len(cities) > 4 else f'Distributeri u {len(cities)} grada.') if len(cities) > 1 else ''
    single = ' single' if len(cities) <= 1 else ''
    return f'''
  <section class="sec alt" id="kontakt-distributera">
    <div class="wrap">
      <h2 class="h2s">{E(title)}</h2>
      <div class="dealer{single}">
        <div class="dealer-side">
          <label class="lbl" for="city-sel">IZABERITE GRAD</label>
          <div class="city"><select id="city-sel">{opts}</select></div>
          <p class="hint">{hint}</p>
        </div>
        <div class="dealer-main" id="dealer-main">{''.join(dealer_card(d) for d in dealers)}
          <dl class="dnote"><dt>NAPOMENA</dt><dd>{NOTE}</dd></dl>
        </div>
      </div>
    </div>
  </section>'''

VB = {'sedan': '0 0 320 112', 'hatch': '0 0 320 112', 'suv': '0 0 320 120'}

def picture(m, pre, cls='img'):
    label = m['full']
    if m['photo']:
        big = f'{pre}img/{m["photo"]}'; small = big[:-5] + '-640.webp'
        return (f'<img src="{small}" srcset="{small} 640w, {big} 1280w" sizes="(max-width: 620px) 48vw, (max-width: 1000px) 46vw, 400px" '
                f'alt="{E(label)}" loading="lazy" decoding="async">'), 'photo'
    if m['lg']:
        return f'<span class="blogo" aria-hidden="true" style="{logo_style(m["b"], pre)}"></span>', 'lg'
    if m['sil']:
        return f'<svg viewBox="{VB[m["sil"]]}" aria-hidden="true"><use href="#car-{m["sil"]}"/></svg>', 'sil'
    return 'FOTOGRAFIJA USKORO', 'ph'

CMP_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h14m0 0-3.5-3.5M18 8l-3.5 3.5M20 16H6m0 0 3.5-3.5M6 16l3.5 3.5"/></svg>'

def card(mid, pre, big_specs=True):
    m = models[mid]; b = brands[m['b']]
    href = f'{pre}modeli/{mid}.html'
    inner, kind = picture(m, pre)
    kcls = {'photo': ' photo', 'lg': ' lg', 'sil': '', 'ph': ' ph'}[kind]
    f = lambda k, v: f'<div><dt>{k}</dt><dd{"" if v else " class=na"}>{E(v) if v else "Na upit"}</dd></div>'
    specs = f('DOMET (WLTP)', range_txt(m)) + f('KLASA', m['cls']) + (f('BATERIJA', kwh_txt(m)) + f('POGON', 'Električni') if big_specs else '')
    return (f'<article class="mcard"><button type="button" class="cmp-add" data-cmp="{mid}" aria-pressed="false" aria-label="Dodaj u poređenje" title="Dodaj u poređenje">{CMP_ICON}</button><a class="img{kcls}" href="{href}" tabindex="-1" aria-hidden="true">{inner}</a><div class="body">'
            f'<div><div class="mk">{E(b["name"].upper())}</div><h3><a href="{href}">{E(m["n"])}</a></h3></div>'
            f'<div class="tags"><span class="tag">100% EV</span>' + (f'<span class="tag gray">{E(m["cls"].upper())}</span>' if m['cls'] else '') + '</div>'
            f'<dl class="feat">{specs}</dl>'
            f'<a href="{href}" class="btn btn-dark">Detalji modela <span class="arr">→</span></a></div></article>')

def cmp_table(ids, pre, rank=False, brand_col=True):
    head = ('<th class="rank">#</th>' if rank else '') + '<th>Model</th>' + ('<th>Brend</th>' if brand_col else '') + '<th>Klasa</th><th>Domet (WLTP)</th><th>Baterija</th>'
    rows = ''
    for i, mid in enumerate(ids, 1):
        m = models[mid]
        rows += ('<tr>' + (f'<td class="rank">{i}.</td>' if rank else '') + f'<td><a href="{pre}modeli/{mid}.html">{E(m["full"])}</a></td>'
                 + (f'<td><a href="{pre}brendovi/{m["b"]}.html">{E(brands[m["b"]]["name"])}</a></td>' if brand_col else '')
                 + f'<td>{E(m["cls"] or "Na upit")}</td><td class="n">{E(range_txt(m, True) or "Na upit")}</td><td class="n">{E(kwh_txt(m) or "Na upit")}</td></tr>')
    return f'<div class="tbl-wrap"><table class="cmp"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'

def crumbs(items, pre):
    out = []
    for i, (name, href) in enumerate(items):
        if i == len(items) - 1:
            out.append(f'<span aria-current="page">{E(name)}</span>')
        else:
            out.append(f'<a href="{pre}{href}">{E(name)}</a>')
    return '<nav class="crumbs" aria-label="Putanja">' + '<span aria-hidden="true">/</span>'.join(out) + '</nav>'

def ld_breadcrumbs(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': n, 'item': f'{DOMAIN}/{h}' if h != 'index.html' else f'{DOMAIN}/'}
        for i, (n, h) in enumerate(items, 1)]}

def qa_block(pairs):
    return '<div class="qa">' + ''.join(f'<details><summary>{E(q)}<span class="pm" aria-hidden="true">+</span></summary><p>{E(a)}</p></details>' for q, a in pairs) + '</div>'

def ld_faq(pairs):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]}

DAYS = {'pon': 'Mo', 'uto': 'Tu', 'sre': 'We', 'čet': 'Th', 'pet': 'Fr', 'sub': 'Sa', 'ned': 'Su', 'ponedeljak': 'Mo', 'petak': 'Fr', 'subota': 'Sa', 'nedelja': 'Su'}
def opening_hours(text):
    """'Pon-Pet 08:00-17:00, sub 09:00-14:00' -> ['Mo-Fr 08:00-17:00', 'Sa 09:00-14:00'] (skips what it can't read)."""
    out = []
    for part in (text or '').split(','):
        part = part.strip().lower()
        m = re.match(r'([a-zčćšžđ]+)(?:\s*-\s*([a-zčćšžđ]+))?(?:\s+i\s+([a-zčćšžđ]+))?\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$', part)
        if not m:
            continue
        a, b2, c2, t1, t2 = m.groups()
        if a not in DAYS:
            continue
        d = DAYS[a] + (('-' + DAYS[b2]) if b2 in DAYS else '') + ((',' + DAYS[c2]) if c2 in DAYS else '')
        out.append(f'{d} {t1.zfill(5)}-{t2.zfill(5)}')
    return out

def ld_dealer(d, brand_names):
    city = d['city']
    zipm = re.match(r'(\d{5})\s+(.*)', d.get('zip') or '')
    addr = {'@type': 'PostalAddress', 'streetAddress': d.get('address'), 'addressLocality': zipm.group(2) if zipm else (d.get('zip') or city),
            'addressCountry': 'RS'}
    if zipm:
        addr['postalCode'] = zipm.group(1)
    o = {'@context': 'https://schema.org', '@type': 'AutoDealer', 'name': d['name'], 'address': addr,
         'brand': [{'@type': 'Brand', 'name': n} for n in brand_names]}
    if d.get('phone'):
        o['telephone'] = lst(d['phone'])[0]
    if d.get('email'):
        o['email'] = lst(d['email'])[0]
    if d.get('website'):
        o['url'] = 'https://' + d['website']
    oh = opening_hours(d.get('hours'))
    if oh:
        o['openingHours'] = oh
    return o

# ------------------------------------------------------------------ page shell
OG_DEFAULT = 'img/og-evomobil.jpg'

def short(t, n=160):
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= n:
        return t
    cut = t[:n - 1].rsplit(' ', 1)[0].rstrip(',;:')
    return cut + '…'



# ------------------------------------------------------------------ cookie consent + Google Analytics 4 (loads only after "Prihvati")
GA_ID = ''   # Google Analytics 4 measurement ID, e.g. 'G-XXXXXXXXXX'; empty = analytics never loads
CONSENT_JS = r"""
(function(){
  /* cookie consent: nothing from Google Analytics loads until the visitor clicks "Prihvati" */
  var GA='__GA__',K='evc-consent',MAX=1000*60*60*24*180;
  function read(){try{var v=JSON.parse(localStorage.getItem(K)||'null');if(v&&Date.now()-v.t<MAX)return v.c}catch(e){}return null}
  function save(c){try{localStorage.setItem(K,JSON.stringify({c:c,t:Date.now()}))}catch(e){}}
  var loaded=false;
  function loadGA(){if(loaded||!GA)return;loaded=true;
    window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};
    gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'granted'});
    gtag('js',new Date());gtag('config',GA,{cookie_expires:15552000,allow_google_signals:false,allow_ad_personalization_signals:false});
    var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s)}
  function clearGA(){document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(/^_ga/.test(n)){
    ['',location.hostname,'.'+location.hostname.replace(/^www\./,'')].forEach(function(d){document.cookie=n+'=; Max-Age=0; path=/'+(d?'; domain='+d:'')})}})}
  var box=null;
  function show(){
    if(!box){box=document.createElement('div');box.className='ck';box.setAttribute('role','dialog');box.setAttribute('aria-live','polite');box.setAttribute('aria-label','Kolačići');
      var base=/\/(modeli|brendovi)\//.test(location.pathname)?'../':'';
      box.innerHTML='<p>Koristimo kolačiće za anonimnu statistiku poseta (Google Analytics), samo uz vašu saglasnost. <a href="'+base+'politika-privatnosti.html#kolacici">Saznajte više</a></p>'
        +'<div class="ck-btns"><button type="button" class="btn btn-ghost" data-ck="denied">Odbij</button><button type="button" class="btn btn-dark" data-ck="granted">Prihvati</button></div>';
      box.addEventListener('click',function(e){var b=e.target.closest('[data-ck]');if(!b)return;var c=b.getAttribute('data-ck');save(c);box.hidden=true;
        if(c==='granted')loadGA();else{clearGA();if(loaded)location.reload()}});
      document.body.appendChild(box)}
    box.hidden=false}   /* no auto-focus: it drew a focus ring around "Prihvati" before the visitor did anything */
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-cookie-settings]');if(a){e.preventDefault();show()}});
  function init(){var c=read();if(c==='granted')loadGA();else if(c!=='denied')show()}
  if(document.readyState!=='loading')init();else document.addEventListener('DOMContentLoaded',init);
})();
""".replace('__GA__', GA_ID)
CONSENT_CSS = r'''
/* cookie consent bar */
.ck{position:fixed;left:16px;bottom:16px;z-index:80;max-width:440px;display:flex;flex-direction:column;gap:14px;padding:18px 20px;border-radius:18px;background:var(--surface);border:1px solid var(--line);box-shadow:0 16px 40px rgba(15,23,42,.18);font-size:14px;color:var(--text)}
.ck[hidden]{display:none}
.ck p{margin:0;line-height:1.5}
.ck a{color:var(--green-ink);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.ck-btns{display:flex;gap:10px}
.ck-btns .btn{flex:1;height:42px;justify-content:center}
.ck-btns .btn:focus-visible{outline-offset:2px}
@media (max-width:560px){.ck{left:12px;right:12px;bottom:12px;max-width:none}}
'''

common_js += CONSENT_JS

def page(path, title, desc, body, ld=(), og_image=None, extra_js='', extra_head=''):
    desc = short(desc)
    depth = path.count('/')
    pre = '../' * depth
    canonical = f'{DOMAIN}/' + ('' if path == 'index.html' else path)
    og = f'{DOMAIN}/{og_image or OG_DEFAULT}'
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    hdr = relink(header, pre)
    ftr = relink(footer, pre)
    return (f'<!doctype html>\n<html lang="sr-Latn">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="color-scheme" content="only light">\n'
            f'<title>{E(title)}</title>\n<meta name="description" content="{E(desc)}">\n'
            f'<link rel="canonical" href="{canonical}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="{SITE}">\n<meta property="og:locale" content="sr_RS">\n'
            f'<meta property="og:title" content="{E(title)}">\n<meta property="og:description" content="{E(desc)}">\n'
            f'<meta property="og:url" content="{canonical}">\n<meta property="og:image" content="{og}">\n' + ('<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="evomobil.rs – električni automobili u Srbiji">\n' if og.endswith(OG_DEFAULT) else '') + f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<link rel="icon" href="{pre}favicon.ico?v={FAV_V}" sizes="any">\n<link rel="icon" href="{pre}img/favicon.svg?v={FAV_V}" type="image/svg+xml">\n<link rel="icon" href="{pre}img/favicon-32.png?v={FAV_V}" type="image/png" sizes="32x32">\n<link rel="apple-touch-icon" href="{pre}img/apple-touch-icon.png?v={FAV_V}">\n'
            '<meta name="theme-color" content="#16202e">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Montserrat:wght@600;700;800&display=swap">\n'
            f'<link rel="stylesheet" href="{pre}assets/site.css?v={CSS_V}">\n' + MASK_FIX + extra_head + lds + '</head>\n<body>\n' + sprite + hdr + body + ftr
            + '<script>' + common_js + extra_js + '</script>\n</body>\n</html>\n')

SITE_CSS = ':root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}' + style + extra_css + CONSENT_CSS
CSS_V = hashlib.md5(SITE_CSS.encode()).hexdigest()[:8]
FAV_V = hashlib.md5(open(f'{ROOT}/favicon.ico', 'rb').read() + open(f'{ROOT}/img/favicon-32.png', 'rb').read()).hexdigest()[:8]
MASK_FIX = '<style>/* logo masks resolve against the page, not the stylesheet */.blogo{-webkit-mask:var(--l) center/contain no-repeat;mask:var(--l) center/contain no-repeat}</style>\n'
pages = {}   # path -> html

# ------------------------------------------------------------------ brand pages
for slug in ORDER:
    b = brands[slug]; pre = '../'
    ids = b['models']; cities = cities_of(slug)
    title = f'{b["name"]} električni automobili u Srbiji | {SITE}'
    names = join_sr([models[i]['full'] for i in ids]) if ids else ''
    ranges = [models[i]['r'] for i in ids if models[i]['r']]
    if not ids:
        answer = f'Podatke o električnim modelima brenda {b["name"]} u Srbiji dodajemo uskoro, čim ih uvoznik objavi.'
    else:
        answer = (f'{b["name"]} u Srbiji trenutno nudi {plural_models(len(ids))}: {names}. '
              + (f'Domet po WLTP normi je od {min(ranges)} do {max(ranges)} km, zavisno od modela i verzije. ' if len(ranges) > 1 else (f'Domet po WLTP normi je do {ranges[0]} km. ' if ranges else ''))
              + (f'Vozila se mogu kupiti kod {len(b["dealers"])} {"ovlašćenog distributera" if len(b["dealers"]) == 1 else "ovlašćenih distributera"} u {"gradu" if len(cities) == 1 else "gradovima"} {join_sr(cities)}.' if cities else ''))
    desc = (f'{b["name"]} električni automobili u Srbiji: modeli, domet, baterija i kontakti distributera. Podatke dodajemo čim ih uvoznik objavi.' if not ids
            else f'{b["name"]} električni automobili u Srbiji: {names}. Domet, baterija, klasa vozila i kontakti distributera u {join_sr(cities)}.' if cities
            else f'{b["name"]} električni automobili u Srbiji: {names}. Domet, baterija i klasa vozila.')[:300]
    facts = [('OSNOVAN', b.get('founded')), ('SEDIŠTE', b.get('hq')), ('UVOZNIK U SRBIJI', b.get('importer')), ('EV MODELA', str(len(ids)))]
    others = ''.join(f'<a href="{o}.html"><span class="ol">{logo_span(o, pre)}</span>{E(brands[o]["name"])}</a>' for o in ORDER if o != slug)
    crumb = [('Početna', 'index.html'), ('Brendovi', 'brendovi.html'), (b['name'], f'brendovi/{slug}.html')]
    qa = [(f'Koje električne modele {b["name"]} nudi u Srbiji?', answer.split('. Domet')[0].strip().rstrip('.') + '.')]
    if ranges:
        best = max(ids, key=lambda i: models[i]['r'] or 0)
        qa.append((f'Koji {b["name"]} električni automobil ima najveći domet?', f'Najveći domet ima {models[best]["full"]}: {range_txt(models[best])} po WLTP normi, prema podacima proizvođača ili uvoznika.'))
    if cities:
        qa.append((f'Gde mogu kupiti {b["name"]} električni automobil u Srbiji?', f'{b["name"]} električne automobile prodaju ovlašćeni distributeri u {"gradu" if len(cities) == 1 else "gradovima"} {join_sr(cities)}. Adrese, telefoni i radno vreme nalaze se u odeljku Kontaktirajte distributera.'))
    body = f'''
<main id="top">
  <section class="bhero">
    <div class="wrap">
      {crumbs(crumb, pre)}
      <div class="bhero-grid">
        <div class="bhero-logo" role="img" aria-label="{E(b["name"])} logo">{logo_span(slug, pre)}</div>
        <div>
          <h1>{E(b["name"])} električni automobili u Srbiji</h1>
          <p class="answer">{E(answer)}</p>
          <dl class="facts">{''.join(f'<div><dt>{k}</dt><dd>{E(v)}</dd></div>' for k, v in facts if v)}</dl>
          <div class="ctas">
            <a href="#modeli-brenda" class="btn btn-dark">Električni modeli <span class="arr">→</span></a>
            {'' if not b['dealers'] else '<a href="#kontakt-distributera" class="btn btn-ghost">Kontaktirajte distributera</a>'}
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="sec alt" id="o-brendu">
    <div class="wrap b-about">
      <h2>O brendu {E(b["name"])}</h2>
      <div>{''.join(f'<p>{E(p)}</p>' for p in b["about"])}</div>
    </div>
  </section>

  <section class="sec" id="modeli-brenda">
    <div class="wrap">
      <div class="head"><div><h2>Električni modeli {E(b["name"])}</h2><p>{plural_models(len(ids)) + ' dostupno u Srbiji.' if ids else 'Električne modele ovog brenda dodajemo uskoro.'}</p></div></div>
      {'<div class="models' + (' many' if len(ids) > 6 else '') + '">' + ''.join(card(i, pre) for i in ids) + '</div>' if ids else '<p class="answer">Podatke o električnim modelima, dometu i bateriji objavićemo čim ih uvoznik za Srbiju objavi.</p>'}
      {cmp_table(ids, pre, brand_col=False) if len(ids) > 1 else ''}
      <p class="price-note">Domet je po WLTP normi, prema podacima proizvođača ili uvoznika; kod modela sa više verzija naveden je raspon.</p>
    </div>
  </section>
{dealer_section(slug, f'Kontaktirajte distributera {b["name"]}')}
  <section class="sec">
    <div class="wrap">
      <h2 class="h2s">Česta pitanja o brendu {E(b["name"])}</h2>
      {qa_block(qa)}
    </div>
  </section>

  <section class="sec alt">
    <div class="wrap">
      <div class="head"><h2 style="font-size:clamp(24px,2.6vw,32px)">Ostali brendovi</h2></div>
      <div class="others">{others}</div>
    </div>
  </section>
</main>
'''
    ld = [ld_breadcrumbs(crumb), ld_faq(qa),
          {'@context': 'https://schema.org', '@type': 'ItemList', 'name': f'Električni modeli {b["name"]} u Srbiji',
           'itemListElement': [{'@type': 'ListItem', 'position': k, 'url': f'{DOMAIN}/modeli/{i}.html', 'name': models[i]['full']} for k, i in enumerate(ids, 1)]}]
    ld += [ld_dealer(d, [b['name']]) for d in b['dealers'] if d['city'] != 'Srbija']
    og = f'img/{models[ids[0]]["photo"]}' if ids and models[ids[0]]['photo'] else None
    pages[f'brendovi/{slug}.html'] = page(f'brendovi/{slug}.html', title, desc, body, ld, og)

# ------------------------------------------------------------------ model pages
for mid, m in models.items():
    b = brands[m['b']]; pre = '../'; cities = cities_of(m['b'])
    cw = CLS_WORD.get(m['cls'], 'automobil')
    rng = range_txt(m, True)
    summary = (f'{m["full"]} je potpuno električni {cw} brenda {b["name"]}. '
               + (f'Prema podacima proizvođača ili uvoznika ima domet {rng} po WLTP normi' + (f' i bateriju od {kwh_txt(m)}' if m['kwh'] else '') + '. ' if rng else (f'Ima bateriju od {kwh_txt(m)}. ' if m['kwh'] else ''))
               + (f'U Srbiji ga prodaju ovlašćeni distributeri u {"gradu" if len(cities) == 1 else "gradovima"} {join_sr(cities)}.' if cities else ''))
    title = f'{m["full"]}: domet, baterija i cena kod distributera u Srbiji | {SITE}' if False else f'{m["full"]} u Srbiji: domet, baterija i distributeri | {SITE}'
    desc = (f'{m["full"]}, potpuno električni {cw}. ' + (f'Domet {rng} (WLTP)' + (f', baterija {kwh_txt(m)}' if m['kwh'] else '') + '. ' if rng else '')
            + f'Specifikacije i kontakti distributera {b["name"]} u Srbiji.')
    inner, kind = picture(m, pre)
    hero_img = {'photo': f'<div class="mhero-img">{inner.replace(" loading=\"lazy\"", " fetchpriority=\"high\"").replace("(max-width: 620px) 48vw, (max-width: 1000px) 46vw, 400px", "(max-width: 900px) 92vw, 640px")}</div>',
                'lg': f'<div class="mhero-img lg" role="img" aria-label="{E(m["full"])}">{inner}</div>',
                'sil': f'<div class="mhero-img sil" role="img" aria-label="{E(m["full"])}">{inner}</div>',
                'ph': '<div class="mhero-img ph">FOTOGRAFIJA USKORO</div>'}[kind]
    desc_paras = m['desc'] or [f'{m["full"]} je potpuno električni {cw} brenda {b["name"]} koji je dostupan na srpskom tržištu.',
                               'Detaljne tehničke podatke i opremu dodajemo čim ih uvoznik objavi. Do tada informacije proverite kod ovlašćenog distributera.']
    specs = [('Brend', b['name']), ('Model', m['full']), ('Klasa vozila', m['cls']), ('Pogon', '100% električni'),
             ('Domet (WLTP)', rng), ('Baterija', kwh_txt(m)), ('Menjač', 'Automatski, jedan stepen prenosa')]
    dm = DIMS.get(mid, {})
    specs += [(k, v) for k, v in (('Dužina', dm.get('length_txt') or mm(dm.get('length_mm'))),
                                  ('Širina', (mm(dm.get('width_mm')) + ' (sa sklopljenim retrovizorima)') if dm.get('width_folded') and dm.get('width_mm') else mm(dm.get('width_mm'))),
                                  ('Visina', dm.get('height_txt') or mm(dm.get('height_mm'))),
                                  ('Klirens', (mm(dm.get('clearance_mm')) + ' (pod opterećenjem)') if dm.get('clearance_laden') and dm.get('clearance_mm') else mm(dm.get('clearance_mm'))),
                                  ('Broj sedišta', str(dm['seats']) if dm.get('seats') else None)) if v]
    keys = [('DOMET (WLTP)', range_txt(m) or 'Na upit'), ('BATERIJA', kwh_txt(m) or 'Na upit'), ('KLASA', m['cls'] or 'Na upit'), ('POGON', 'Električni')]
    rel = [i for i in b['models'] if i != mid]
    crumb = [('Početna', 'index.html'), ('Brendovi', 'brendovi.html'), (b['name'], f'brendovi/{m["b"]}.html'), (m['full'], f'modeli/{mid}.html')]
    qa = []
    if rng:
        qa.append((f'Koliki je domet modela {m["full"]}?', f'{m["full"]} ima domet {rng} po WLTP normi, prema podacima proizvođača ili uvoznika. Stvarni domet zavisi od načina vožnje, temperature i opterećenja.'))
    if m['kwh']:
        qa.append((f'Koliki je kapacitet baterije modela {m["full"]}?', f'{m["full"]} ima bateriju kapaciteta {kwh_txt(m)}.'))
    if cities:
        qa.append((f'Gde mogu kupiti {m["full"]} u Srbiji?', f'{m["full"]} prodaju ovlašćeni distributeri brenda {b["name"]} u {"gradu" if len(cities) == 1 else "gradovima"} {join_sr(cities)}. Kontakti su navedeni na ovoj stranici.'))
    qa.append((f'Da li je {m["full"]} hibrid?', f'Ne. {m["full"]} je potpuno električni automobil, bez motora sa unutrašnjim sagorevanjem.'))
    body = f'''
<main id="top">
  <section class="mhero">
    <div class="wrap">
      {crumbs(crumb, pre)}
      <div class="mhero-grid">
        {hero_img}
        <div>
          <a class="mbrand" href="../brendovi/{m["b"]}.html" title="Svi modeli brenda {E(b["name"])}"><span class="mbrand-logo">{logo_span(m["b"], pre, 'nosq')}</span><span class="sr-only">{E(b["name"])}</span></a>
          <h1>{E(m["full"])}</h1>
          <div class="tags"><span class="tag">100% EV</span>{f'<span class="tag gray">{E(m["cls"].upper())}</span>' if m["cls"] else ''}</div>
          <p class="answer">{E(summary)}</p>
          <dl class="facts">{''.join(f'<div><dt>{k}</dt><dd>{E(v)}</dd></div>' for k, v in keys)}</dl>
          <div class="ctas">
            {'' if not b['dealers'] else '<a href="#kontakt-distributera" class="btn btn-dark">Kontaktirajte distributera <span class="arr">→</span></a>'}
            <a href="../brendovi/{m["b"]}.html" class="btn btn-ghost">Svi modeli {E(b["name"])}</a>
            <a href="../uporedi.html?modeli={mid}" class="btn btn-ghost">Uporedi sa drugim modelom</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="sec alt" id="o-modelu">
    <div class="wrap b-about">
      <h2>O modelu {E(m["full"])}</h2>
      <div>{''.join(f'<p>{E(p)}</p>' for p in desc_paras)}</div>
    </div>
  </section>

  <section class="sec" id="specifikacije">
    <div class="wrap">
      <h2 class="h2s">{E(m["full"])}: osnovne specifikacije</h2>
      <dl class="specs-tbl">{''.join(f'<div><dt>{k}</dt><dd{"" if v else " class=na"}>{E(v or "Na upit")}</dd></div>' for k, v in specs)}</dl>
      <p class="price-note">Domet je po WLTP normi, prema podacima proizvođača ili uvoznika. Opremu i tehničke podatke proverite kod distributera.</p>
      <p class="calc-link"><a href="../kalkulator-troskova.html?model={mid}">Koliko košta vožnja ovim modelom? Uporedite trošak struje i goriva <span class="arr">→</span></a></p>
    </div>
  </section>
{dealer_section(m["b"], f'Kontaktirajte distributera za {m["full"]}')}
  <section class="sec">
    <div class="wrap">
      <h2 class="h2s">Česta pitanja: {E(m["full"])}</h2>
      {qa_block(qa)}
    </div>
  </section>

  <section class="sec alt">
    <div class="wrap">
      <div class="head"><div><h2 style="font-size:clamp(24px,2.6vw,32px)">Ostali električni modeli {E(b["name"])}</h2></div><a class="link" href="../brendovi/{m["b"]}.html">Stranica brenda →</a></div>
      <div class="models{' many' if len(rel) > 6 else ''}">{''.join(card(i, pre) for i in rel) if rel else f'<div class="models-empty"><strong>Ovo je trenutno jedini električni model brenda {E(b["name"])} u Srbiji.</strong>Pogledajte <a href="../modeli.html">sve električne modele</a>.</div>'}</div>
    </div>
  </section>
</main>
'''
    car = {'@context': 'https://schema.org', '@type': 'Car', 'name': m['full'], 'model': m['n'],
           'brand': {'@type': 'Brand', 'name': b['name']}, 'manufacturer': {'@type': 'Organization', 'name': b['name']},
           'fuelType': 'Electric', 'vehicleTransmission': 'Automatic', 'description': summary, 'url': f'{DOMAIN}/modeli/{mid}.html'}
    if m['cls']:
        car['bodyType'] = m['cls']
    if m['photo']:
        car['image'] = f'{DOMAIN}/img/{m["photo"]}'
    dm = DIMS.get(mid, {})
    if dm.get('seats'):
        car['vehicleSeatingCapacity'] = dm['seats']
    for k, f in (('length', 'length_mm'), ('width', 'width_mm'), ('height', 'height_mm')):
        if dm.get(f) and not (k == 'width' and dm.get('width_folded')):
            car[k] = {'@type': 'QuantitativeValue', 'value': dm[f], 'unitCode': 'MMT'}
    props = []
    if m['r']:
        props.append({'@type': 'PropertyValue', 'name': 'Domet (WLTP)', 'value': m['r'], 'unitText': 'km', 'description': rng})
    if m['kwh']:
        props.append({'@type': 'PropertyValue', 'name': 'Kapacitet baterije', 'value': str(m['kwh']), 'unitText': 'kWh'})
    if props:
        car['additionalProperty'] = props
    ld = [ld_breadcrumbs(crumb), car, ld_faq(qa)]
    pages[f'modeli/{mid}.html'] = page(f'modeli/{mid}.html', title, desc, body, ld, f'img/{m["photo"]}' if m['photo'] else None)

# ------------------------------------------------------------------ list pages
ALL_IDS = [i for s in ORDER for i in brands[s]['models']]
CATS = [
    ('elektricni-suv.html', 'Električni SUV i crossover modeli u Srbiji', 'Električni SUV', lambda m: 'suv' in m['tags'],
     'Električni SUV i crossover modeli koji se prodaju u Srbiji: domet, baterija i distributeri.'),
    ('elektricni-hecbek.html', 'Električni hečbek automobili u Srbiji', 'Hečbek', lambda m: 'hatch' in m['tags'],
     'Kompaktni i mali električni hečbek automobili u Srbiji, sa dometom i kapacitetom baterije.'),
    ('elektricni-sedani.html', 'Električni sedani i karavani u Srbiji', 'Sedan', lambda m: 'sedan' in m['tags'] or 'wagon' in m['tags'],
     'Električni sedani i karavani u Srbiji: domet, baterija i gde ih kupiti.'),
    ('elektricni-pikapi.html', 'Električni pikapi u Srbiji', 'Pikap', lambda m: 'pickup' in m['tags'],
     'Potpuno električni pikapi koji se prodaju u Srbiji, sa dometom, baterijom i distributerima.'),
    ('gradski-elektricni-automobili.html', 'Gradski električni automobili u Srbiji', 'Gradski', lambda m: 'city' in m['tags'],
     'Mali gradski električni automobili u Srbiji: domet, baterija i kontakti distributera.'),
]
cat_nav_items = [('modeli.html', 'Svi modeli')] + [(c[0], c[2]) for c in CATS] + [('najveci-domet.html', 'Najveći domet')]
def cat_nav(current):
    return '<nav class="cat-links" aria-label="Kategorije">' + ''.join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == current else ""}>{E(t)}</a>' for h, t in cat_nav_items) + '</nav>'

def list_page(path, h1, intro, ids, ranked=False, crumb_name=None):
    crumb = [('Početna', 'index.html'), (crumb_name or h1, path)]
    body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>{E(h1)}</h1>
      <p class="answer">{E(intro)}</p>
      {cat_nav(path)}
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap">
      {cmp_table(ids, '', rank=ranked)}
      <p class="price-note">Domet je po WLTP normi, prema podacima proizvođača ili uvoznika; kod modela sa više verzija naveden je raspon. Proverite aktuelne podatke kod distributera.</p>
      <div class="models{' many' if len(ids) > 6 else ''}" style="margin-top:40px">{''.join(card(i, '') for i in ids)}</div>
    </div>
  </section>
</main>
'''
    ld = [ld_breadcrumbs(crumb), {'@context': 'https://schema.org', '@type': 'ItemList', 'name': h1, 'itemListOrder': 'https://schema.org/ItemListOrderDescending' if ranked else 'https://schema.org/ItemListUnordered',
          'itemListElement': [{'@type': 'ListItem', 'position': k, 'url': f'{DOMAIN}/modeli/{i}.html', 'name': models[i]['full']} for k, i in enumerate(ids, 1)]}]
    return crumb, body, ld

def names_of(ids, n=4):
    return join_sr([models[i]['full'] for i in ids[:n]]) + (' i drugi' if len(ids) > n else '')

for path, h1, nav, test, desc in CATS:
    ids = sorted([i for i in ALL_IDS if test(models[i])], key=lambda i: -(models[i]['r'] or 0))
    rs = [models[i]['r'] for i in ids if models[i]['r']]
    intro = (f'U Srbiji se trenutno prodaje {plural_models(len(ids))} u ovoj kategoriji: {join_sr([models[i]["full"] for i in ids])}. '
             + (f'Domet po WLTP normi kreće se od {min(rs)} do {max(rs)} km, a najveći domet ima {models[ids[0]]["full"]}.' if len(rs) > 1 else ''))
    crumb, body, ld = list_page(path, h1, intro, ids)
    pages[path] = page(path, f'{h1} | {SITE}', desc, body, ld)

ranked = sorted([i for i in ALL_IDS if models[i]['r']], key=lambda i: -models[i]['r'])
top3 = join_sr([f'{models[i]["full"]} ({models[i]["r"]} km)' for i in ranked[:3]])
intro = (f'Električni automobili sa najvećim dometom u Srbiji su {top3}, prema WLTP podacima proizvođača i uvoznika. '
         f'Tabela prikazuje {len(ranked)} modela poređanih po najvećem navedenom dometu.')
crumb, body, ld = list_page('najveci-domet.html', 'Električni automobili sa najvećim dometom u Srbiji', intro, ranked, ranked=True, crumb_name='Najveći domet')
pages['najveci-domet.html'] = page('najveci-domet.html', f'Električni automobili sa najvećim dometom u Srbiji | {SITE}',
                                   f'Rang lista električnih automobila u Srbiji po dometu (WLTP): {top3}.', body, ld)


CAT_LABELS = [('suv', 'SUV'), ('hatch', 'Hečbek'), ('sedan', 'Sedan'), ('city', 'Gradski'), ('pickup', 'Pikap'), ('wagon', 'Karavan')]

def catalog_page(path, h1, intro, ids, crumb_name):
    """All-models catalog: checkbox filters on the left, model grid on the right (filters run in the browser)."""
    crumb = [('Početna', 'index.html'), (crumb_name, path)]
    def cnt(test):
        return sum(1 for i in ids if test(models[i]))

    def opt(kind, name, value, label, count=None, checked=False):
        return (f'<label class="fopt"><input autocomplete="off" type="{kind}" name="{name}" value="{value}"{" checked" if checked else ""}>'
                f'<span>{label}</span>' + (f'<em>{count}</em>' if count is not None else '') + '</label>')

    def group(gid, legend, items, show=4):
        rows = ''.join(it.replace('<label class="fopt">', '<label class="fopt more">', 1) if k >= show else it for k, it in enumerate(items))
        more = (f'<button type="button" class="fmore" data-more="{len(items) - show}" aria-expanded="false">Prikaži više ({len(items) - show})</button>'
                if len(items) > show else '')
        return f'<fieldset class="fgroup" id="{gid}"><legend>{legend}</legend>{rows}{more}</fieldset>'

    bslugs = [b for b in ORDER if any(models[i]['b'] == b for i in ids)]
    brand_items = [opt('checkbox', 'b', b, E(brands[b]['name']), cnt(lambda m, b=b: m['b'] == b)) for b in bslugs]
    range_items = [opt('checkbox', 'd', v, lab, cnt(lambda m, v=v: (m['r'] or 0) >= int(v)))
                   for v, lab in [('300', '300+ km'), ('400', '400+ km'), ('500', '500+ km'), ('600', '600+ km')]]
    body_items = [opt('checkbox', 'k', t, lab, cnt(lambda m, t=t: t in m['tags']))
                  for t, lab in CAT_LABELS if cnt(lambda m, t=t: t in m['tags'])]

    def tagged(i):
        m = models[i]
        return card(i, '').replace('<article class="mcard">',
            f'<article class="mcard" data-b="{m["b"]}" data-t="{" ".join(m["tags"])}" data-r="{m["r"] or 0}" data-n="{E(m["full"].lower())}">', 1)

    filters = (
        '<aside class="cat-side" id="cat-side" aria-label="Filteri">'
        '<div class="cat-side-head"><h2>Filteri</h2><button type="button" class="cat-close" id="cat-close" aria-label="Zatvori filtere">×</button></div>'
        + group('fg-brand', 'Brend', brand_items)
        + group('fg-range', 'Domet (WLTP)', range_items)
        + group('fg-body', 'Karoserija', body_items)
        + '<button type="button" class="freset" id="freset">Poništi filtere</button>'
        '<button type="button" class="btn btn-dark cat-apply" id="cat-apply">Prikaži modele</button>'
        '</aside>')
    sort = ('<div class="csel" id="cat-sort-wrap"><span class="csel-lab" id="sort-lab">Sortiraj</span>'
            '<button type="button" class="csel-btn" id="cat-sort-btn" aria-haspopup="listbox" aria-expanded="false" aria-labelledby="sort-lab cat-sort-btn">'
            '<span id="cat-sort-val">Najveći domet</span></button>'
            '<ul class="csel-menu" id="cat-sort-menu" role="listbox" aria-labelledby="sort-lab" hidden>'
            '<li role="option" data-v="r" aria-selected="true" tabindex="-1">Najveći domet</li>'
            '<li role="option" data-v="n" aria-selected="false" tabindex="-1">Naziv A-Š</li></ul>'
            '<input type="hidden" id="cat-sort" value="r"></div>')
    grid = ''.join(tagged(i) for i in ids)
    body = (
        '\n<main id="top">\n  <section class="phero">\n    <div class="wrap">\n      '
        + crumbs(crumb, '')
        + f'\n      <h1>{E(h1)}</h1>\n      <p class="answer">{E(intro)}</p>\n'
        '    </div>\n  </section>\n  <section class="sec" style="padding-top:0">\n    <div class="wrap cat-layout">\n      '
        + filters
        + '\n      <div class="cat-main">\n        <div class="cat-bar">'
        '<button type="button" class="btn btn-ghost cat-open" id="cat-open" aria-controls="cat-side">Filteri <span id="cat-n" hidden></span></button>'
        f'<p class="cat-count" id="cat-count" role="status">Prikazano {len(ids)} od {len(ids)} modela</p>'
        + sort + '</div>\n'
        f'        <div class="models many" id="cat-grid">{grid}</div>\n'
        '        <div class="cat-empty" id="cat-empty" hidden><strong>Nijedan model ne odgovara izabranim filterima.</strong>'
        '<button type="button" class="btn btn-ghost" id="cat-empty-reset">Poništi filtere</button></div>\n'
        '        <p class="price-note">Domet je po WLTP normi, prema podacima proizvođača ili uvoznika; kod modela sa više verzija naveden je raspon. Proverite aktuelne podatke kod distributera.</p>\n'
        '      </div>\n    </div>\n  </section>\n</main>\n<div class="cat-scrim" id="cat-scrim" hidden></div>\n')
    ld = [ld_breadcrumbs(crumb), {'@context': 'https://schema.org', '@type': 'ItemList', 'name': h1, 'itemListOrder': 'https://schema.org/ItemListUnordered',
          'itemListElement': [{'@type': 'ListItem', 'position': k, 'url': f'{DOMAIN}/modeli/{i}.html', 'name': models[i]['full']} for k, i in enumerate(ids, 1)]}]
    return crumb, body, ld

CATALOG_JS = r"""(function(){
var $=function(i){return document.getElementById(i)},grid=$('cat-grid');if(!grid)return;
var cards=[].slice.call(grid.children),side=$('cat-side'),scrim=$('cat-scrim'),total=cards.length;
var inputs=[].slice.call(side.querySelectorAll('input'));
function sel(name){return inputs.filter(function(i){return i.name===name&&i.checked}).map(function(i){return i.value})}
function apply(push){
  var k=sel('k'),b=sel('b'),d=+(sel('d')[0]||0),n=0;
  cards.forEach(function(c){var t=c.dataset.t.split(' ');
    var ok=(!k.length||k.some(function(x){return t.indexOf(x)>-1}))&&(!b.length||b.indexOf(c.dataset.b)>-1)&&(+c.dataset.r>=d);
    c.hidden=!ok;if(ok)n++;});
  var s=$('cat-sort').value;
  cards.slice().sort(function(a,z){return s==='n'?a.dataset.n.localeCompare(z.dataset.n,'sr'):(+z.dataset.r)-(+a.dataset.r)}).forEach(function(c){grid.appendChild(c)});
  $('cat-count').textContent='Prikazano '+n+' od '+total+' modela';
  $('cat-empty').hidden=n>0;
  var active=k.length+b.length+(d?1:0);$('cat-n').hidden=!active;$('cat-n').textContent='('+active+')';
  $('cat-apply').textContent=n?('Prikaži '+n+(n===1?' model':' modela')):'Nema rezultata';
  evcFacets(side,cards,function(c,f){var t=c.dataset.t.split(' ');return (!f.k.length||f.k.some(function(x){return t.indexOf(x)>-1}))&&(!f.b.length||f.b.indexOf(c.dataset.b)>-1)&&(+c.dataset.r>=+(f.d[0]||0))});
  if(push!==false){var q=new URLSearchParams();if(b.length)q.set('brend',b.join(','));if(d)q.set('domet',d);if(k.length)q.set('karoserija',k.join(','));if(s!=='r')q.set('sort',s);
    try{history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}catch(e){}}
}
/* "Prikaži više" per group; a group opens by itself when one of its hidden options is selected */
function setOpen(g,o){g.classList.toggle('open-all',o);var bt=g.querySelector('.fmore');if(bt){bt.setAttribute('aria-expanded',o);bt.textContent=o?'Prikaži manje':'Prikaži više ('+bt.dataset.more+')'}}
function openSelected(){[].slice.call(side.querySelectorAll('.fgroup')).forEach(function(g){if(g.querySelector('.fopt.more input:checked'))setOpen(g,true)})}
[].slice.call(side.querySelectorAll('.fmore')).forEach(function(bt){bt.addEventListener('click',function(){var g=bt.closest('.fgroup');setOpen(g,!g.classList.contains('open-all'))})});
/* sort: small custom listbox */
var sb=$('cat-sort-btn'),sm=$('cat-sort-menu'),opts=[].slice.call(sm.children);
function setSort(v,silent){$('cat-sort').value=v;opts.forEach(function(o){o.setAttribute('aria-selected',o.dataset.v===v)});$('cat-sort-val').textContent=opts.filter(function(o){return o.dataset.v===v})[0].textContent;if(!silent)apply()}
function menu(o){sm.hidden=!o;sb.setAttribute('aria-expanded',o);if(o){var cur=sm.querySelector('[aria-selected="true"]')||opts[0];cur.focus()}}
sb.addEventListener('click',function(){menu(sm.hidden)});
sb.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();menu(true)}});
opts.forEach(function(o,i){o.addEventListener('click',function(){setSort(o.dataset.v);menu(false);sb.focus()});
  o.addEventListener('keydown',function(e){if(e.key==='ArrowDown'){e.preventDefault();opts[Math.min(i+1,opts.length-1)].focus()}else if(e.key==='ArrowUp'){e.preventDefault();opts[Math.max(i-1,0)].focus()}else if(e.key==='Enter'||e.key===' '){e.preventDefault();o.click()}else if(e.key==='Escape'||e.key==='Tab'){menu(false);if(e.key==='Escape')sb.focus()}})});
document.addEventListener('click',function(e){if(!sm.hidden&&!$('cat-sort-wrap').contains(e.target))menu(false)});
function reset(){inputs.forEach(function(i){i.checked=false});apply()}
var q=new URLSearchParams(location.search);
(q.get('karoserija')||'').split(',').concat((q.get('brend')||'').split(',')).forEach(function(v){inputs.forEach(function(i){if(v&&i.type==='checkbox'&&i.value===v)i.checked=true})});
if(q.get('domet'))inputs.forEach(function(i){if(i.name==='d')i.checked=i.value===q.get('domet')});
/* range works as single choice that can be cleared: ticking one unticks the others */
side.addEventListener('change',function(e){var t=e.target;if(t.name==='d'&&t.checked)inputs.forEach(function(i){if(i.name==='d'&&i!==t)i.checked=false})},true);
if(q.get('sort')==='n')setSort('n',true);
openSelected();
side.addEventListener('change',function(){apply()});
$('freset').addEventListener('click',reset);$('cat-empty-reset').addEventListener('click',reset);
function open(o){side.classList.toggle('open',o);scrim.hidden=!o;document.body.classList.toggle('no-scroll',o);if(o)$('cat-close').focus()}
$('cat-open').addEventListener('click',function(){open(true)});[$('cat-close'),$('cat-apply'),scrim].forEach(function(x){x.addEventListener('click',function(){open(false)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side.classList.contains('open'))open(false)});
apply(false);
})();"""

all_sorted = ALL_IDS
intro = 'Na evomobil.rs trenutno pratimo električne modele automobila koji se prodaju u Srbiji. Prikazujemo samo potpuno električne automobile, bez hibrida.'
crumb, body, ld = catalog_page('modeli.html', 'Svi električni automobili u Srbiji', intro, sorted(all_sorted, key=lambda i: -(models[i]['r'] or 0)), crumb_name='Svi modeli')
pages['modeli.html'] = page('modeli.html', f'Svi električni automobili u Srbiji | {SITE}',
                            f'Spisak svih {len(ALL_IDS)} električnih automobila na evomobil.rs, sa dometom, baterijom, klasom vozila i distributerima.', body, ld, extra_js=CATALOG_JS)

# brands index
tiles = ''.join(f'<a class="btile" href="brendovi/{s}.html"><div class="mark">{logo_span(s, "")}</div><div class="meta"><h3>{E(brands[s]["name"])}</h3></div>'
                f'<span class="count">{len(brands[s]["models"])} EV {"model" if len(brands[s]["models"]) == 1 else "modela"}</span></a>' for s in ORDER)
crumb = [('Početna', 'index.html'), ('Brendovi', 'brendovi.html')]
intro = (f'Trenutno pratimo {len(ORDER)} brendova koji u Srbiji nude potpuno električne automobile: {join_sr([brands[s]["name"] for s in ORDER])}. '
         'Na stranici svakog brenda su njegovi električni modeli, domet, baterija i kontakti ovlašćenih distributera.')
body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>Brendovi električnih automobila u Srbiji</h1>
      <p class="answer">{E(intro)}</p>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap"><div class="bento brands-only">{tiles}</div></div>
  </section>
</main>
'''
pages['brendovi.html'] = page('brendovi.html', f'Brendovi električnih automobila u Srbiji | {SITE}',
                              f'{len(ORDER)} brendova sa električnim automobilima u Srbiji: {join_sr([brands[s]["name"] for s in ORDER])}.', body,
                              [ld_breadcrumbs(crumb), {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Brendovi električnih automobila u Srbiji',
                               'itemListElement': [{'@type': 'ListItem', 'position': k, 'url': f'{DOMAIN}/brendovi/{s}.html', 'name': brands[s]['name']} for k, s in enumerate(ORDER, 1)]}])

# ------------------------------------------------------------------ dealers by city
by_city = {}
for s in ORDER:
    for d in brands[s]['dealers']:
        if d['city'] == 'Srbija':
            continue
        key = (re.sub(r'[^a-z0-9]', '', d['name'].lower().replace('d.o.o', '').replace('doo', '')), re.sub(r'\D', '', lst(d.get('phone') or [''])[0])[-6:])
        entry = by_city.setdefault(d['city'], {}).setdefault(key, {'d': d, 'brands': []})
        if brands[s]['name'] not in entry['brands']:
            entry['brands'].append(brands[s]['name'])
city_order = sorted(by_city, key=lambda c: (c != 'Beograd', c != 'Novi Sad', c != 'Niš', c))
blocks, ld_d, n_dealers = '', [], 0
city_cnt, brand_cnt = {}, {}
for c in city_order:
    cards = ''
    for e in by_city[c].values():
        n_dealers += 1
        bslugs = [s for s in ORDER if brands[s]['name'] in e['brands']]
        links = ', '.join(f'<a href="brendovi/{s}.html">{E(brands[s]["name"])}</a>' for s in bslugs)
        city_cnt[c] = city_cnt.get(c, 0) + 1
        for s in bslugs:
            brand_cnt[s] = brand_cnt.get(s, 0) + 1
        cards += dealer_card(e['d'], f'<span class="brands-of">Brendovi: {links}</span>').replace(
            '<article class="dcard"', f'<article class="dcard" data-c="{slugify(c)}" data-b="{" ".join(bslugs)}"', 1)
        ld_d.append(ld_dealer(e['d'], e['brands']))
    cid = slugify(c)
    brands_here = sorted({b for e in by_city[c].values() for b in e['brands']})
    blocks += f'''
      <div class="city-block" id="{cid}">
        <div class="dealer-main">{cards}</div>
      </div>'''

def fgroup(gid, legend, items, show=4):
    """Sidebar filter group: checkbox options, first `show` visible, the rest behind 'Prikaži više'."""
    rows = ''.join(
        f'<label class="fopt{" more" if k >= show else ""}"><input autocomplete="off" type="checkbox" name="{name}" value="{v}">'
        f'<span>{lab}</span><em>{n}</em></label>' for k, (name, v, lab, n) in enumerate(items))
    more = (f'<button type="button" class="fmore" data-more="{len(items) - show}" aria-expanded="false">Prikaži više ({len(items) - show})</button>'
            if len(items) > show else '')
    return f'<fieldset class="fgroup" id="{gid}"><legend>{legend}</legend>{rows}{more}</fieldset>'

d_filters = (
    '<aside class="cat-side" id="cat-side" aria-label="Filteri">'
    '<div class="cat-side-head"><h2>Filteri</h2><button type="button" class="cat-close" id="cat-close" aria-label="Zatvori filtere">×</button></div>'
    + fgroup('fg-city', 'Grad', [('g', slugify(c), E(c), city_cnt[c]) for c in city_order])
    + fgroup('fg-brand', 'Brend', [('b', s, E(brands[s]['name']), brand_cnt[s]) for s in ORDER if s in brand_cnt])
    + '<button type="button" class="freset" id="freset">Poništi filtere</button>'
    '<button type="button" class="btn btn-dark cat-apply" id="cat-apply">Prikaži distributere</button>'
    '</aside>')
crumb = [('Početna', 'index.html'), ('Distributeri', 'distributeri.html')]
intro = (f'Spisak {n_dealers} ovlašćenih distributera električnih automobila u {len(city_order)} gradova Srbije: {join_sr(city_order)}. '
         'Za svakog distributera navedeni su brendovi, adresa, telefon, email i radno vreme.')
body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>Distributeri električnih automobila u Srbiji</h1>
      <p class="answer">{E(intro)}</p>
      <p class="updated">{NOTE}</p>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap cat-layout">
      {d_filters}
      <div class="cat-main">
        <div class="cat-bar"><button type="button" class="btn btn-ghost cat-open" id="cat-open" aria-controls="cat-side">Filteri <span id="cat-n" hidden></span></button>
          <p class="cat-count" id="cat-count" role="status">Prikazano {n_dealers} od {n_dealers} distributera</p></div>
        <div id="d-list">{blocks}
        </div>
        <div class="cat-empty" id="cat-empty" hidden><strong>Nijedan distributer ne odgovara izabranim filterima.</strong><button type="button" class="btn btn-ghost" id="cat-empty-reset">Poništi filtere</button></div>
      </div>
    </div>
  </section>
</main>
<div class="cat-scrim" id="cat-scrim" hidden></div>
'''
DEALERS_JS = r"""(function(){
var $=function(i){return document.getElementById(i)},list=$('d-list');if(!list)return;
var cards=[].slice.call(list.querySelectorAll('.dcard')),blocks=[].slice.call(list.querySelectorAll('.city-block')),side=$('cat-side'),scrim=$('cat-scrim'),total=cards.length;
var inputs=[].slice.call(side.querySelectorAll('input'));
function sel(n){return inputs.filter(function(i){return i.name===n&&i.checked}).map(function(i){return i.value})}
function apply(push){
  var g=sel('g'),b=sel('b'),n=0;
  cards.forEach(function(c){var cb=c.dataset.b.split(' ');var ok=(!g.length||g.indexOf(c.dataset.c)>-1)&&(!b.length||b.some(function(x){return cb.indexOf(x)>-1}));c.hidden=!ok;if(ok)n++});
  blocks.forEach(function(bl){bl.hidden=!bl.querySelector('.dcard:not([hidden])')});
  $('cat-count').textContent='Prikazano '+n+' od '+total+' distributera';
  $('cat-empty').hidden=n>0;
  var a=g.length+b.length;list.classList.toggle('filtered',!!b.length);$('cat-n').hidden=!a;$('cat-n').textContent='('+a+')';
  $('cat-apply').textContent=n?('Prikaži '+n+' distributera'):'Nema rezultata';
  evcFacets(side,cards,function(c,f){var cb=c.dataset.b.split(' ');return (!f.g.length||f.g.indexOf(c.dataset.c)>-1)&&(!f.b.length||f.b.some(function(x){return cb.indexOf(x)>-1}))});
  if(push!==false){var q=new URLSearchParams();if(g.length)q.set('grad',g.join(','));if(b.length)q.set('brend',b.join(','));
    try{history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}catch(e){}}
}
function setOpen(gr,o){gr.classList.toggle('open-all',o);var bt=gr.querySelector('.fmore');if(bt){bt.setAttribute('aria-expanded',o);bt.textContent=o?'Prikaži manje':'Prikaži više ('+bt.dataset.more+')'}}
[].slice.call(side.querySelectorAll('.fmore')).forEach(function(bt){bt.addEventListener('click',function(){var gr=bt.closest('.fgroup');setOpen(gr,!gr.classList.contains('open-all'))})});
function reset(){inputs.forEach(function(i){i.checked=false});apply()}
var q=new URLSearchParams(location.search),h=location.hash.slice(1);
(q.get('grad')||'').split(',').concat((q.get('brend')||'').split(',')).forEach(function(v){inputs.forEach(function(i){if(v&&i.value===v)i.checked=true})});
if(h&&!q.get('grad'))inputs.forEach(function(i){if(i.name==='g'&&i.value===h)i.checked=true});
[].slice.call(side.querySelectorAll('.fgroup')).forEach(function(gr){if(gr.querySelector('.fopt.more input:checked'))setOpen(gr,true)});
side.addEventListener('change',function(){apply()});
$('freset').addEventListener('click',reset);$('cat-empty-reset').addEventListener('click',reset);
function open(o){side.classList.toggle('open',o);scrim.hidden=!o;document.body.classList.toggle('no-scroll',o);if(o)$('cat-close').focus()}
$('cat-open').addEventListener('click',function(){open(true)});[$('cat-close'),$('cat-apply'),scrim].forEach(function(x){x.addEventListener('click',function(){open(false)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side.classList.contains('open'))open(false)});
apply(false);
})();"""
pages['distributeri.html'] = page('distributeri.html', f'Distributeri električnih automobila u Srbiji | {SITE}',
                                  f'Ovlašćeni distributeri električnih automobila u Srbiji za {sum(1 for x in ORDER if brands[x]["dealers"])} brendova, od Audija do Volva: adrese, telefoni i radno vreme u gradovima {join_sr(city_order[:6])} i drugim.'[:300],
                                  body, [ld_breadcrumbs(crumb)] + ld_d, extra_js=DEALERS_JS)

# ------------------------------------------------------------------ chargers map (data: Open Charge Map export in data/chargers-ocm.json)
CYR = dict(zip('АБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШабвгдђежзијклљмнњопрстћуфхцчџш',
               ['A','B','V','G','D','Đ','E','Ž','Z','I','J','K','L','Lj','M','N','Nj','O','P','R','S','T','Ć','U','F','H','C','Č','Dž','Š',
                'a','b','v','g','d','đ','e','ž','z','i','j','k','l','lj','m','n','nj','o','p','r','s','t','ć','u','f','h','c','č','dž','š']))
def lat(t):
    return ''.join(CYR.get(ch, ch) for ch in (t or '')).strip()

TOWN_FIX = {'Belgrade': 'Beograd', 'Cacak': 'Čačak', 'Vrcin': 'Vrčin', 'Presevo': 'Preševo',
            # Kosovo and Metohija: Serbian place names
            'Prishtina': 'Priština', 'Prishtinë': 'Priština', 'Ferizaj': 'Uroševac', 'Gjilan': 'Gnjilane', 'Lipjan': 'Lipljan',
            'Suharekë': 'Suva Reka', 'Fushë Kosovë': 'Kosovo Polje', 'Gracanica': 'Gračanica', 'Parallove': 'Paralovo',
            'Komuna e Drenasit / Opština Glogovac': 'Glogovac', 'Çagllavicë (Prishtinë)': 'Čaglavica', 'Pejë': 'Peć', 'Peja': 'Peć'}
def town(t):
    t = lat(t)
    t = re.sub(r'\s*Municipality$', '', t)
    t = re.sub(r'^Gradska opština\s+', '', t)
    return TOWN_FIX.get(t, t)

CONN = {33: 'CCS', 25: 'Tip 2', 1036: 'Tip 2', 2: 'CHAdeMO', 27: 'Tesla', 30: 'Tesla', 1: 'Tip 1'}
ACCESS = {1: 'javni', 4: 'javni', 5: 'javni', 7: 'javni', 6: 'gosti'}     # 2, 3 = private: left out
ACCESS_LAB = {'javni': 'Javni', 'gosti': 'Za goste i kupce', 'nepoznato': 'Nepoznat pristup'}

def charger_rows():
    raw = []
    for f in ('chargers-ocm.json', 'chargers-ocm-kosovo.json'):
        if os.path.exists(f'{ROOT}/data/{f}'):
            raw += json.load(open(f'{ROOT}/data/{f}', encoding='utf-8'))
    # drop entries with coordinates outside Serbia (some are entered with wrong coordinates)
    raw = [x for x in raw if 41.8 <= x['AddressInfo']['Latitude'] <= 46.3 and 18.8 <= x['AddressInfo']['Longitude'] <= 23.1]
    rows = []
    for x in raw:
        if x.get('UsageTypeID') in (2, 3):
            continue
        a = x['AddressInfo']
        conns = x.get('Connections') or []
        kws = [c.get('PowerKW') or 0 for c in conns]
        rows.append({
            'id': x['ID'], 'name': lat(a.get('Title')) or 'Punjač', 'lat': a['Latitude'], 'lng': a['Longitude'],
            'addr': lat(a.get('AddressLine1')), 'town': town(a.get('Town')),
            'kw': round(max(kws)) if kws and max(kws) else None,
            'conn': sorted({CONN[c['ConnectionTypeID']] for c in conns if c.get('ConnectionTypeID') in CONN}),
            'points': x.get('NumberOfPoints') or len(conns) or None,
            'acc': ACCESS.get(x.get('UsageTypeID'), 'nepoznato'),
            'app': x.get('UsageTypeID') == 4,
            'down': x.get('StatusTypeID') not in (50, None),
            'seen': (x.get('DateLastVerified') or x.get('DateLastStatusUpdate') or x.get('DateCreated') or '')[:10],
        })
    # OpenStreetMap export (data/chargers-osm.geojson, made with overpass-turbo.eu; see README "Punjači iz OpenStreetMap")
    of = f'{ROOT}/data/chargers-osm.geojson'
    if os.path.exists(of):
        OSM_SOCK = {'type2_combo': 'CCS', 'type2': 'Tip 2', 'type2_cable': 'Tip 2', 'chademo': 'CHAdeMO',
                    'tesla_supercharger': 'Tesla', 'tesla_supercharger_ccs': 'CCS', 'type1': 'Tip 1', 'type1_combo': 'CCS'}
        def _kw(v):
            nums = [float(n.replace(',', '.')) for n in re.findall(r'\d+(?:[.,]\d+)?', str(v or ''))]
            nums = [n / 1000 if n > 1000 else n for n in nums]
            return max(nums) if nums else 0
        for x in json.load(open(of, encoding='utf-8')).get('features', []):
            t = x.get('properties') or {}
            t = t.get('tags', t)          # overpass-turbo puts tags at the top level; some tools nest them under "tags"
            if t.get('amenity') != 'charging_station' or t.get('access') in ('private', 'no') or t.get('disused') == 'yes':
                continue
            g = x.get('geometry') or {}
            c = g.get('coordinates')
            if not c:
                continue
            if g.get('type') == 'Point':
                lng_, lat_ = c[0], c[1]
            else:                          # a way drawn as an area: use the middle of its outline
                ring = c[0] if g.get('type') == 'Polygon' else (c[0][0] if g.get('type') == 'MultiPolygon' else c)
                lng_, lat_ = sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
            if not (41.8 <= lat_ <= 46.3 and 18.8 <= lng_ <= 23.1):
                continue
            conns = sorted({lab for k, lab in OSM_SOCK.items() if t.get('socket:' + k) not in (None, '', 'no', '0')})
            kw = max([_kw(t.get(k)) for k in t if k.startswith('socket:') and k.endswith(':output')]
                     + [_kw(t.get('charging_station:output')), _kw(t.get('maxpower'))])
            name = lat(t.get('name') or t.get('name:sr-Latn') or t.get('brand') or t.get('operator') or '') or 'Punjač'
            if t.get('operator') and lat(t['operator']) not in name and name != 'Punjač':
                name = f'{name} ({lat(t["operator"])})'
            street = ' '.join(v for v in (lat(t.get('addr:street')), t.get('addr:housenumber') or '') if v)
            pts = re.findall(r'\d+', str(t.get('capacity') or ''))
            rows.append({'id': f'o{x.get("id") or len(rows)}'.replace('/', ''), 'name': name, 'lat': lat_, 'lng': lng_,
                         'addr': street, 'town': town(t.get('addr:city') or t.get('addr:place') or ''),
                         'kw': round(kw) if kw else None, 'conn': conns, 'points': int(pts[0]) if pts else None,
                         'acc': 'gosti' if t.get('access') == 'customers' else 'javni',
                         'app': 'app' in str(t.get('authentication:app') or '') or t.get('authentication:app') == 'yes',
                         'down': t.get('operational_status') in ('closed', 'broken', 'out_of_order'),
                         'seen': (t.get('check_date') or t.get('survey:date') or '2000-01-01')[:10]})
    # extra chargers added by hand (data/chargers-extra.json), e.g. motorway chargers from Putevi Srbije, NIS, Charge&GO:
    # [{"name": "...", "lat": 44.81, "lng": 20.46, "address": "...", "town": "Beograd", "kw": 50,
    #   "connectors": ["CCS", "Tip 2"], "access": "javni", "app": true, "points": 2, "source": "..."}]
    # They win over an Open Charge Map entry at the same spot (within 60 m).
    xf = f'{ROOT}/data/chargers-extra.json'
    if os.path.exists(xf):
        for k, x in enumerate(json.load(open(xf, encoding='utf-8'))):
            rows.append({'id': f'x{k + 1}', 'name': x['name'], 'lat': float(x['lat']), 'lng': float(x['lng']),
                         'addr': x.get('address') or '', 'town': x.get('town') or '', 'kw': x.get('kw'),
                         'conn': sorted(set(x.get('connectors') or [])), 'points': x.get('points'),
                         'acc': x.get('access') or 'javni', 'app': bool(x.get('app')), 'down': bool(x.get('down')),
                         'seen': '9999-12-31'})
    # the same place is often entered more than once: keep one entry per spot (within 60 m), the most recently checked
    rows.sort(key=lambda r: r['seen'], reverse=True)
    kept = []
    for r in rows:
        twin = next((k for k in kept if math.hypot((k['lat'] - r['lat']) * 111000, (k['lng'] - r['lng']) * 111000 * math.cos(math.radians(r['lat']))) < 60), None)
        if twin:
            twin['conn'] = sorted(set(twin['conn']) | set(r['conn']))
            twin['kw'] = max(twin['kw'] or 0, r['kw'] or 0) or None
            twin['town'] = twin['town'] or r['town']
            twin['addr'] = twin['addr'] or r['addr']
            continue
        kept.append(r)
    kept.sort(key=lambda r: (-(r['kw'] or 0), r['name'].lower()))
    return kept

import math
CHARGERS = charger_rows()
OSM_NOTE = (' i <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="nofollow noopener">© OpenStreetMap</a> saradnici (ODbL)'
            if os.path.exists(f'{ROOT}/data/chargers-osm.geojson') else '')
KW_STEPS = [s for s in (22, 50, 100, 150) if any((r['kw'] or 0) >= s for r in CHARGERS)]
CONN_ORDER = [c for c in ('CCS', 'Tip 2', 'CHAdeMO', 'Tesla', 'Tip 1') if any(c in r['conn'] for r in CHARGERS)]

def charger_item(r):
    where = ', '.join(x for x in (r['addr'], r['town'] if r['town'] and r['town'] not in r['addr'] else '') if x)
    tags = ''.join(f'<span class="tag gray">{E(c)}</span>' for c in r['conn'])
    kw = f'<span class="ch-kw{" fast" if (r["kw"] or 0) >= 50 else ""}">{r["kw"]} kW</span>' if r['kw'] else '<span class="ch-kw na">snaga nepoznata</span>'
    notes = []
    if r['acc'] != 'javni':
        notes.append(ACCESS_LAB[r['acc']])
    if r['app']:
        notes.append('potrebna aplikacija ili kartica')
    if r['points'] and r['points'] > 1:
        notes.append(f'{r["points"]} mesta za punjenje')
    if r['down']:
        notes.append('privremeno van funkcije')
    nav = f'https://www.google.com/maps/dir/?api=1&destination={r["lat"]:.6f},{r["lng"]:.6f}'
    return (f'<li class="ch" data-id="{r["id"]}" data-lat="{r["lat"]:.6f}" data-lng="{r["lng"]:.6f}" data-kw="{r["kw"] or 0}" '
            f'data-c="{" ".join(c.replace(" ", "") for c in r["conn"])}" data-a="{r["acc"]}">'
            f'<div class="ch-top"><h3>{E(r["name"])}</h3>{kw}</div>'
            + (f'<p class="ch-addr">{E(where)}</p>' if where else '')
            + (f'<div class="ch-tags">{tags}</div>' if tags else '')
            + (f'<p class="ch-note">{E(", ".join(notes).capitalize())}</p>' if notes else '')
            + f'<div class="ch-act"><button type="button" class="ch-show">Prikaži na mapi</button>'
              f'<a href="{nav}" target="_blank" rel="nofollow noopener">Navigacija ↗</a></div></li>')

def ch_group(gid, legend, items, show=4):
    rows = ''.join(
        f'<label class="fopt{" more" if k >= show else ""}"><input autocomplete="off" type="checkbox" name="{name}" value="{v}">'
        f'<span>{lab}</span><em>{n}</em></label>' for k, (name, v, lab, n) in enumerate(items) if n)
    return f'<fieldset class="fgroup" id="{gid}"><legend>{legend}</legend>{rows}</fieldset>'

n_ch = len(CHARGERS)
n_fast = sum(1 for r in CHARGERS if (r['kw'] or 0) >= 50)
ch_filters = (
    '<aside class="cat-side" id="cat-side" aria-label="Filteri">'
    '<div class="cat-side-head"><h2>Filteri</h2><button type="button" class="cat-close" id="cat-close" aria-label="Zatvori filtere">×</button></div>'
    + ch_group('fg-kw', 'Snaga punjenja', [('p', s, f'{s}+ kW', sum(1 for r in CHARGERS if (r['kw'] or 0) >= s)) for s in KW_STEPS])
    + ch_group('fg-conn', 'Konektor', [('k', c.replace(' ', ''), c, sum(1 for r in CHARGERS if c in r['conn'])) for c in CONN_ORDER])
    + ch_group('fg-acc', 'Pristup', [('a', a, ACCESS_LAB[a], sum(1 for r in CHARGERS if r['acc'] == a)) for a in ('javni', 'gosti', 'nepoznato')])
    + '<button type="button" class="freset" id="freset">Poništi filtere</button>'
    '<button type="button" class="btn btn-dark cat-apply" id="cat-apply">Prikaži punjače</button>'
    '</aside>')
_srb = json.load(open(f'{ROOT}/vendor/srb-outline.geo.json', encoding='utf-8'))['features'][0]['geometry']['coordinates']
_kos = json.load(open(f'{ROOT}/vendor/kos-outline.geo.json', encoding='utf-8'))['features'][0]['geometry']['coordinates']
outline = {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'MultiPolygon', 'coordinates': [_srb, _kos]}}
def _zone(line, km=14):
    # thin polygon around the Serbia-Kosovo line, used to hide that line on the street map
    left, right = [], []
    for k, (x, y) in enumerate(line):
        a = line[max(k - 1, 0)]; b = line[min(k + 1, len(line) - 1)]
        dx, dy = (b[0] - a[0]) * math.cos(math.radians(y)), b[1] - a[1]; n = math.hypot(dx, dy) or 1
        ox, oy = -dy / n * km / 111 / math.cos(math.radians(y)), dx / n * km / 111
        left.append([x + ox, y + oy]); right.append([x - ox, y - oy])
    ring = left + right[::-1] + [left[0]]
    return {'type': 'Polygon', 'coordinates': [ring]}
border_zone = _zone(_kos[0][6:19])
crumb = [('Početna', 'index.html'), ('Punjači', 'punjaci.html')]
intro = ('Mapa punjača za električne automobile u Srbiji: lokacije, snaga punjenja i tipovi konektora. '
         'Izaberite snagu ili konektor koji odgovara vašem automobilu, a pre polaska proverite dostupnost u aplikaciji operatera.')
body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>Punjači za električne automobile u Srbiji</h1>
      <p class="answer">{E(intro)}</p>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap cat-layout">
      {ch_filters}
      <div class="cat-main">
        <div class="cat-bar"><button type="button" class="btn btn-ghost cat-open" id="cat-open" aria-controls="cat-side">Filteri <span id="cat-n" hidden></span></button>
          <p class="cat-count" id="cat-count" role="status">Prikazano {n_ch} od {n_ch} punjača</p>
          <p class="ch-legend"><i class="dot fast"></i>50+ kW <i class="dot"></i>sporije</p></div>
        <div class="ch-map" id="ch-map" role="region" aria-label="Mapa punjača"></div>
        <ul class="ch-list" id="ch-list">{''.join(charger_item(r) for r in CHARGERS)}</ul>
        <button type="button" class="btn btn-ghost ch-more" id="ch-more" hidden>Prikaži još</button>
        <div class="cat-empty" id="cat-empty" hidden><strong>Nijedan punjač ne odgovara izabranim filterima.</strong><button type="button" class="btn btn-ghost" id="cat-empty-reset">Poništi filtere</button></div>
        <p class="price-note">Izvor podataka: <a href="https://openchargemap.org" target="_blank" rel="nofollow noopener">Open Charge Map</a>{OSM_NOTE}, otvorene baze punjača koje dopunjuju korisnici. Podaci mogu biti nepotpuni ili zastareli; cenu, radno vreme i dostupnost proverite kod operatera punjača.</p>
      </div>
    </div>
  </section>
</main>
<div class="cat-scrim" id="cat-scrim" hidden></div>
'''
CHARGERS_JS = r"""document.addEventListener('DOMContentLoaded',function(){
var $=function(i){return document.getElementById(i)},list=$('ch-list');if(!list)return;
var items=[].slice.call(list.children),side=$('cat-side'),scrim=$('cat-scrim'),total=items.length,PAGE=24,shown=PAGE;
var inputs=[].slice.call(side.querySelectorAll('input'));
function sel(n){return inputs.filter(function(i){return i.name===n&&i.checked}).map(function(i){return i.value})}
/* map: OpenFreeMap street map (free, no key); Kosovo is shown as part of Serbia */
var map=null,popup=null,ready=false,FEATS={};
items.forEach(function(li){FEATS[li.dataset.id]={type:'Feature',geometry:{type:'Point',coordinates:[+li.dataset.lng,+li.dataset.lat]},properties:{id:li.dataset.id,fast:+li.dataset.kw>=50?1:0}}});
var KOS=['Kosovo','Kosova','Kosovë','Kosova / Kosovo','Kosovo / Kosova','Косово'],SRB=['Serbia','Srbija','Србија'];
function isLegacy(f){if(!Array.isArray(f))return false;if(f[0]==='all'||f[0]==='any'||f[0]==='none')return f.slice(1).some(isLegacy);return typeof f[1]==='string'}
function guardBoundary(f){
  var leg=['none',['==','disputed',1],['all',['in','adm0_l'].concat(KOS),['in','adm0_r'].concat(SRB)],['all',['in','adm0_l'].concat(SRB),['in','adm0_r'].concat(KOS)]];
  var g=function(k){return ['coalesce',['get',k],'']};
  var ex=['!',['any',['==',['to-number',['coalesce',['get','disputed'],0]],1],
      ['all',['in',g('adm0_l'),['literal',KOS]],['in',g('adm0_r'),['literal',SRB]]],
      ['all',['in',g('adm0_l'),['literal',SRB]],['in',g('adm0_r'),['literal',KOS]]],
      ['within',BORDER_ZONE]]];
  if(!f)return ex;return isLegacy(f)?['all',f,leg]:['all',f,ex];
}
function guardLabel(f){
  var leg=['any',['!=','class','country'],['all',['!in','name'].concat(KOS),['!in','name:en'].concat(KOS),['!in','name_en'].concat(KOS),['!in','name:latin'].concat(KOS)]];
  var ex=['any',['!=',['coalesce',['get','class'],''],'country'],['!',['any',
      ['in',['coalesce',['get','name'],''],['literal',KOS]],['in',['coalesce',['get','name:en'],''],['literal',KOS]],
      ['in',['coalesce',['get','name_en'],''],['literal',KOS]],['in',['coalesce',['get','name:latin'],''],['literal',KOS]]]]];
  if(!f)return ex;return isLegacy(f)?['all',f,leg]:['all',f,ex];
}
function tidyStyle(){
  (map.getStyle().layers||[]).forEach(function(l){
    try{if(l['source-layer']==='boundary')map.setFilter(l.id,guardBoundary(l.filter));
        else if(l['source-layer']==='place')map.setFilter(l.id,guardLabel(l.filter));}catch(e){}});
}
function addChargers(){
  if(!map.getSource('rs-outline'))map.addSource('rs-outline',{type:'geojson',data:OUTLINE});
  var first=(map.getStyle().layers||[]).filter(function(l){return l.type==='symbol'})[0];
  if(!map.getLayer('rs-fill'))map.addLayer({id:'rs-fill',type:'fill',source:'rs-outline',paint:{'fill-color':'#16a34a','fill-opacity':.04}},first&&first.id);
  if(!map.getSource('ch'))map.addSource('ch',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
  if(!map.getLayer('ch-dots'))map.addLayer({id:'ch-dots',type:'circle',source:'ch',paint:{
    'circle-radius':['interpolate',['linear'],['zoom'],6,['case',['==',['get','fast'],1],6,4.5],12,['case',['==',['get','fast'],1],10,8]],
    'circle-color':['case',['==',['get','fast'],1],'#16a34a','#16202e'],'circle-stroke-color':'#ffffff','circle-stroke-width':2}});
  ready=true;apply(false,FIT);
}
var FALLBACK={version:8,sources:{},layers:[{id:'bg',type:'background',paint:{'background-color':'#eef2f1'}}]};
if(window.maplibregl){
  map=new maplibregl.Map({container:'ch-map',style:'https://tiles.openfreemap.org/styles/positron',center:[20.9,43.9],zoom:6.2,
    cooperativeGestures:true,attributionControl:{compact:false},locale:{'CooperativeGesturesHandler.WindowsHelpText':'Držite Ctrl i skrolujte za zumiranje mape','CooperativeGesturesHandler.MacHelpText':'Držite ⌘ i skrolujte za zumiranje mape','CooperativeGesturesHandler.MobileHelpText':'Pomerajte mapu sa dva prsta'}});
  map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
  var styled=false;
  map.on('style.load',function(){if(map.getStyle().sources&&Object.keys(map.getStyle().sources).length&&!map.getSource('rs-outline'))styled=true;tidyStyle();addChargers()});
  /* if the street map cannot load (offline, blocked), keep the map usable with a plain background and the Serbia outline */
  var fb=function(){if(!styled&&!ready){map.setStyle(FALLBACK);map.once('style.load',function(){map.addLayer({id:'rs-line',type:'line',source:'rs-outline',paint:{'line-color':'#94a3b8','line-width':1}})})}};
  map.on('error',function(){setTimeout(fb,300)});setTimeout(fb,6000);
  map.on('click','ch-dots',function(e){openPop(e.features[0].properties.id)});
  map.on('mouseenter','ch-dots',function(){map.getCanvas().style.cursor='pointer'});map.on('mouseleave','ch-dots',function(){map.getCanvas().style.cursor=''});
}
function openPop(id){
  var li=list.querySelector('.ch[data-id="'+id+'"]');if(!li||!map)return;
  var box=document.createElement('div');box.className='ch-pop';
  box.innerHTML='<strong></strong><span class="k"></span><span class="a"></span><span class="t"></span><a target="_blank" rel="nofollow noopener">Navigacija ↗</a>';
  var ad=li.querySelector('.ch-addr');
  box.children[0].textContent=li.querySelector('h3').textContent;box.children[1].textContent=li.querySelector('.ch-kw').textContent;
  box.children[2].textContent=ad?ad.textContent:'';box.children[3].textContent=[].slice.call(li.querySelectorAll('.ch-tags .tag')).map(function(t){return t.textContent}).join(' · ');
  box.children[4].href=li.querySelector('.ch-act a').href;
  if(popup)popup.remove();popup=new maplibregl.Popup({offset:12,maxWidth:'260px',focusAfterOpen:false}).setLngLat(FEATS[id].geometry.coordinates).setDOMContent(box).addTo(map);
}
var FIT=true,FLY=0,RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function apply(push,fit){
  var p=+(sel('p')[0]||0),k=sel('k'),a=sel('a'),vis=[];
  items.forEach(function(li){var c=li.dataset.c.split(' ');
    var ok=(+li.dataset.kw>=p)&&(!k.length||k.some(function(x){return c.indexOf(x)>-1}))&&(!a.length||a.indexOf(li.dataset.a)>-1);
    li.classList.toggle('off',!ok);if(ok)vis.push(li);});
  items.forEach(function(li){li.hidden=true});vis.slice(0,shown).forEach(function(li){li.hidden=false});
  $('ch-more').hidden=vis.length<=shown;$('ch-more').textContent='Prikaži još ('+(vis.length-shown)+')';
  $('cat-count').textContent='Prikazano '+vis.length+' od '+total+' punjača';
  $('cat-empty').hidden=vis.length>0;
  var act=k.length+a.length+(p?1:0);$('cat-n').hidden=!act;$('cat-n').textContent='('+act+')';
  $('cat-apply').textContent=vis.length?('Prikaži '+vis.length+' punjača'):'Nema rezultata';
  evcFacets(side,items,function(li,f){var c=li.dataset.c.split(' ');return (+li.dataset.kw>=+(f.p[0]||0))&&(!f.k.length||f.k.some(function(x){return c.indexOf(x)>-1}))&&(!f.a.length||f.a.indexOf(li.dataset.a)>-1)});
  if(map&&ready){map.getSource('ch').setData({type:'FeatureCollection',features:vis.map(function(li){return FEATS[li.dataset.id]})});
    if(popup)popup.remove();
    if(fit&&vis.length){var b=new maplibregl.LngLatBounds();vis.forEach(function(li){b.extend([+li.dataset.lng,+li.dataset.lat])});map.stop();map.fitBounds(b,{padding:40,maxZoom:13,duration:fit===2&&!RM?1000:0})}}
  if(push!==false){var q=new URLSearchParams();if(p)q.set('snaga',p);if(k.length)q.set('konektor',k.join(','));if(a.length)q.set('pristup',a.join(','));
    try{history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}catch(e){}}
}
side.addEventListener('change',function(e){var t=e.target;if(t.name==='p'&&t.checked)inputs.forEach(function(i){if(i.name==='p'&&i!==t)i.checked=false});shown=PAGE;apply(true,2)});
$('ch-more').addEventListener('click',function(){shown+=PAGE;apply(false)});
/* the whole card shows the charger on the map (the Navigacija link keeps its own job) */
list.addEventListener('click',function(e){if(e.target.closest('a'))return;var li=e.target.closest('.ch');if(!li||!map)return;
  if(window.getSelection&&String(getSelection()).length>2&&!e.target.closest('.ch-show'))return;
  items.forEach(function(x){x.classList.toggle('sel',x===li)});
  if(popup)popup.remove();
  var el=$('ch-map'),r=el.getBoundingClientRect(),inView=r.top>=0&&r.bottom<=innerHeight;
  if(!inView)el.scrollIntoView({behavior:RM?'auto':'smooth',block:'center'});
  var go=function(){map.stop();var t=++FLY;map.once('moveend',function(){if(t===FLY)openPop(li.dataset.id)});
    map.flyTo({center:[+li.dataset.lng,+li.dataset.lat],zoom:15,curve:1.42,duration:RM?0:1600,essential:true})};
  if(inView||RM)go();else setTimeout(go,350)});
function reset(){inputs.forEach(function(i){i.checked=false});shown=PAGE;apply(true,true)}
var q=new URLSearchParams(location.search);
if(q.get('snaga'))inputs.forEach(function(i){if(i.name==='p')i.checked=i.value===q.get('snaga')});
(q.get('konektor')||'').split(',').forEach(function(v){inputs.forEach(function(i){if(v&&i.name==='k'&&i.value===v)i.checked=true})});
(q.get('pristup')||'').split(',').forEach(function(v){inputs.forEach(function(i){if(v&&i.name==='a'&&i.value===v)i.checked=true})});
$('freset').addEventListener('click',reset);$('cat-empty-reset').addEventListener('click',reset);
function open(o){side.classList.toggle('open',o);scrim.hidden=!o;document.body.classList.toggle('no-scroll',o);if(o)$('cat-close').focus()}
$('cat-open').addEventListener('click',function(){open(true)});[$('cat-close'),$('cat-apply'),scrim].forEach(function(x){x.addEventListener('click',function(){open(false);if(map)setTimeout(function(){map.resize()},50)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side.classList.contains('open'))open(false)});
apply(false,true);
});"""
pages['punjaci.html'] = page('punjaci.html', f'Punjači za električne automobile u Srbiji: mapa | {SITE}',
                             f'Mapa punjača za električne automobile u Srbiji: {n_ch} lokacija, od toga {n_fast} brzih punjača od 50 kW i više. Snaga, konektori (CCS, Tip 2, CHAdeMO) i navigacija do punjača.',
                             body, [ld_breadcrumbs(crumb)],
                             extra_js='var OUTLINE=' + json.dumps(outline, separators=(',', ':')) + ',BORDER_ZONE=' + json.dumps(border_zone, separators=(',', ':')) + ';\n' + CHARGERS_JS,
                             extra_head='<link rel="stylesheet" href="assets/maplibre-gl.css">\n<script src="assets/maplibre-gl.js" defer></script>\n')


# ------------------------------------------------------------------ side-by-side comparison (up to 3 models)
# dimensions/seats come from build/model_dims.json (official manufacturer/importer sources only; null = not published)

cmp_data = []
for mid in ALL_IDS:
    m = models[mid]; d = DIMS.get(mid, {})
    inner, kind = picture(m, '')
    cmp_data.append({'id': mid, 'b': brands[m['b']]['name'], 'n': m['n'], 'full': m['full'], 'cls': m['cls'] or '',
                     'r': m['r'] or 0, 'rt': range_txt(m) or '', 'kt': kwh_txt(m) or '', 'img': inner, 'k': kind,
                     'L': d.get('length_txt') or mm(d.get('length_mm')), 'W': (mm(d.get('width_mm')) + '*' if d.get('width_folded') and d.get('width_mm') else mm(d.get('width_mm'))),
                     'H': d.get('height_txt') or mm(d.get('height_mm')), 'C': (mm(d.get('clearance_mm')) + '**' if d.get('clearance_laden') and d.get('clearance_mm') else mm(d.get('clearance_mm'))),
                     'S': d.get('seats')})

slot = lambda k: (f'<div class="cmp-slot"><label for="cmp-s{k}">Model {k + 1}</label><select id="cmp-s{k}" data-k="{k}"><option value="">Izaberite model</option>'
                  + ''.join(f'<optgroup label="{E(brands[s]["name"])}">' + ''.join(f'<option value="{i}">{E(models[i]["full"])}</option>' for i in brands[s]['models']) + '</optgroup>'
                            for s in ORDER if brands[s]['models'])
                  + '</select></div>')
crumb = [('Početna', 'index.html'), ('Uporedi modele', 'uporedi.html')]
body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>Uporedi električne automobile</h1>
      <p class="answer">Izaberite do tri modela i uporedite domet, bateriju, dimenzije, klirens i broj sedišta jedan pored drugog.</p>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap">
      <div class="cmp-pick">{slot(0)}{slot(1)}{slot(2)}</div>
      <div class="cmp-tools"><label class="fopt cmp-diff"><input type="checkbox" id="cmp-diff" autocomplete="off"><span>Prikaži samo razlike</span></label>
        <button type="button" class="freset" id="cmp-clear">Očisti poređenje</button></div>
      <div class="cmp-wrap" id="cmp-wrap"><table class="cmp-tbl" id="cmp-tbl"></table></div>
      <p class="cmp-fn" id="cmp-fn" hidden></p>
      <div class="cat-empty" id="cmp-empty"><strong>Izaberite bar jedan model iznad.</strong><span>Modele možete dodati i dugmetom „Uporedi“ na karticama modela.</span></div>
      <p class="price-note">Domet je po WLTP normi. Dimenzije i broj sedišta preuzeti su sa zvaničnih sajtova proizvođača i uvoznika; kod modela sa više verzija navedena je osnovna verzija. Polje sa crticom znači da proizvođač podatak nije objavio.</p>
    </div>
  </section>
</main>
'''
COMPARE_JS = r"""(function(){
var $=function(i){return document.getElementById(i)},tbl=$('cmp-tbl');if(!tbl)return;
var by={};CMP.forEach(function(m){by[m.id]=m});
var sel=[0,1,2].map(function(k){return $('cmp-s'+k)});
var fmt=function(v,u){return v?String(v).replace(/\B(?=(\d{3})+(?!\d))/g,'.')+(u||''):''};
var ROWS=[['Brend',function(m){return m.b}],['Klasa',function(m){return m.cls}],
  ['Domet (WLTP)',function(m){return m.rt}],['Baterija',function(m){return m.kt}],
  ['Dužina',function(m){return m.L||''}],['Širina',function(m){return m.W||''}],['Visina',function(m){return m.H||''}],
  ['Klirens',function(m){return m.C||''}],['Broj sedišta',function(m){return m.S?String(m.S):''}]];
function ids(){return sel.map(function(s){return s.value}).filter(function(v,i,a){return v&&a.indexOf(v)===i})}
function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}
function render(){
  if(typeof pickers!=='undefined')pickers.forEach(function(p){p.sync()});
  var list=ids().map(function(i){return by[i]}).filter(Boolean),diff=$('cmp-diff').checked;
  try{sessionStorage.setItem('evc-cmp',JSON.stringify(list.map(function(m){return m.id})))}catch(e){}
  if(window.evcCmpSync)window.evcCmpSync();
  $('cmp-empty').hidden=!!list.length;$('cmp-wrap').hidden=!list.length;
  var q=list.length?'?modeli='+list.map(function(m){return m.id}).join(','):'';try{history.replaceState(null,'',location.pathname+q)}catch(e){}
  if(!list.length){tbl.innerHTML='';return}
  var h='<thead><tr><th scope="col"><span class="sr">Podatak</span></th>'+list.map(function(m){
    return '<th scope="col"><div class="cmp-imgw"><a class="cmp-img'+(m.k==='photo'?' photo':'')+'" href="modeli/'+m.id+'.html">'+m.img+'</a>'
      +'<button type="button" class="cmp-x" data-id="'+m.id+'" aria-label="Ukloni '+esc(m.full)+' iz poređenja">×</button></div><span class="mk">'+esc(m.b.toUpperCase())+'</span><a class="cmp-name" href="modeli/'+m.id+'.html">'+esc(m.n)+'</a>'
      +'</th>'}).join('')+'</tr></thead><tbody>';
  ROWS.forEach(function(r){
    var vals=list.map(r[1]),same=vals.every(function(v){return v===vals[0]});
    if(diff&&list.length>1&&same)return;
    var best=null;if(r[3]&&list.length>1){var nums=list.map(r[2]);var mx=Math.max.apply(null,nums);if(mx>0&&nums.filter(function(n){return n===mx}).length<list.length)best=mx}
    h+='<tr><th scope="row">'+r[0]+'</th>'+list.map(function(m,k){var v=vals[k],b=best!==null&&r[2](m)===best;
      return '<td'+(b?' class="best"':'')+'>'+(v?esc(v):'<span class="na">–</span>')+'</td>'}).join('')+'</tr>'});
  tbl.innerHTML=h+'</tbody>';tbl.setAttribute('data-n',list.length);
  var fn=[];if(list.some(function(m){return /\*$/.test(m.W||'')}))fn.push('* Širina sa sklopljenim retrovizorima (proizvođač ne objavljuje širinu bez retrovizora).');
  if(list.some(function(m){return /\*\*$/.test(m.C||'')}))fn.push('** Klirens pod opterećenjem, kako ga navodi proizvođač.');
  $('cmp-fn').textContent=fn.join(' ');$('cmp-fn').hidden=!fn.length;
}
sel.forEach(function(s){s.addEventListener('change',render)});
/* custom model picker on top of each (visually hidden) select: search + list grouped by brand */
var norm=function(t){return (t||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'dj')};
var pickers=sel.map(function(s,k){
  var w=document.createElement('div');w.className='cpick';
  var btn=document.createElement('button');btn.type='button';btn.className='cpick-btn';btn.setAttribute('aria-haspopup','listbox');btn.setAttribute('aria-expanded','false');
  btn.innerHTML='<span class="cpick-val"></span>';
  var pop=document.createElement('div');pop.className='cpick-pop';pop.hidden=true;
  pop.innerHTML='<input type="search" class="cpick-q" placeholder="Pretražite model ili brend" autocomplete="off" aria-label="Pretraga modela"><ul class="cpick-list" role="listbox"></ul><p class="cpick-none" hidden>Nema modela za ovu pretragu.</p>';
  var list=pop.querySelector('ul'),q=pop.querySelector('input'),none=pop.querySelector('.cpick-none');
  [].slice.call(s.querySelectorAll('optgroup')).forEach(function(g){
    var h=document.createElement('li');h.className='cpick-g';h.textContent=g.label;h.setAttribute('role','presentation');list.appendChild(h);
    [].slice.call(g.children).forEach(function(o){var li=document.createElement('li');li.className='cpick-o';li.setAttribute('role','option');li.dataset.v=o.value;
      li.dataset.s=norm(g.label+' '+o.textContent);li.textContent=o.textContent;li.tabIndex=-1;list.appendChild(li)})});
  s.parentNode.appendChild(w);w.appendChild(btn);w.appendChild(pop);s.classList.add('cpick-native');s.tabIndex=-1;s.setAttribute('aria-hidden','true');
  btn.id='cmp-b'+k;var lab=s.parentNode.querySelector('label');if(lab){lab.setAttribute('for','cmp-b'+k)}
  function items(){return [].slice.call(list.querySelectorAll('.cpick-o')).filter(function(li){return !li.hidden&&!li.classList.contains('off')})}
  function filter(){var t=norm(q.value.trim()),n=0;var last=null,shown=false;
    [].slice.call(list.children).forEach(function(li){if(li.classList.contains('cpick-g')){if(last)last.hidden=!shown;last=li;shown=false;return}
      var ok=!t||li.dataset.s.indexOf(t)>-1;li.hidden=!ok;if(ok){shown=true;n++}});if(last)last.hidden=!shown;none.hidden=n>0}
  function open(o){pickers.forEach(function(p){if(p!==api)p.close()});pop.hidden=!o;btn.setAttribute('aria-expanded',o);w.classList.toggle('open',o);
    if(o){var taken=sel.filter(function(x){return x!==s}).map(function(x){return x.value});
      [].slice.call(list.querySelectorAll('.cpick-o')).forEach(function(li){li.classList.toggle('off',taken.indexOf(li.dataset.v)>-1);li.setAttribute('aria-selected',li.dataset.v===s.value)});
      q.value='';filter();q.focus({preventScroll:true});var cur=list.querySelector('[aria-selected="true"]');if(cur)cur.scrollIntoView({block:'nearest'})}}
  function choose(v){s.value=v;s.dispatchEvent(new Event('change'));open(false);btn.focus({preventScroll:true})}
  btn.addEventListener('click',function(){open(pop.hidden)});
  q.addEventListener('input',filter);
  q.addEventListener('keydown',function(e){var it=items();if(e.key==='ArrowDown'){e.preventDefault();if(it[0])it[0].focus()}else if(e.key==='Enter'){e.preventDefault();if(it[0])choose(it[0].dataset.v)}else if(e.key==='Escape'){open(false);btn.focus()}});
  list.addEventListener('click',function(e){var li=e.target.closest('.cpick-o');if(li&&!li.classList.contains('off'))choose(li.dataset.v)});
  list.addEventListener('keydown',function(e){var it=items(),i=it.indexOf(document.activeElement);
    if(e.key==='ArrowDown'){e.preventDefault();if(it[i+1])it[i+1].focus()}else if(e.key==='ArrowUp'){e.preventDefault();if(i>0)it[i-1].focus();else q.focus()}
    else if(e.key==='Enter'||e.key===' '){e.preventDefault();if(document.activeElement.dataset.v)choose(document.activeElement.dataset.v)}else if(e.key==='Escape'){open(false);btn.focus()}});
  var api={close:function(){if(!pop.hidden)open(false)},sync:function(){var o=s.options[s.selectedIndex];var has=!!s.value;
    btn.querySelector('.cpick-val').textContent=has?o.textContent:'Izaberite model';btn.classList.toggle('empty',!has)}};
  return api});
document.addEventListener('click',function(e){if(!e.target.closest('.cpick'))pickers.forEach(function(p){p.close()})});
document.addEventListener('keydown',function(e){if(e.key==='Escape')pickers.forEach(function(p){p.close()})});
$('cmp-diff').addEventListener('change',render);
$('cmp-clear').addEventListener('click',function(){sel.forEach(function(s){s.value=''});render()});
tbl.addEventListener('click',function(e){var b=e.target.closest('.cmp-x');if(!b)return;var keep=ids().filter(function(i){return i!==b.dataset.id});sel.forEach(function(s,k){s.value=keep[k]||''});render()});
var start=(new URLSearchParams(location.search).get('modeli')||'').split(',').filter(function(i){return by[i]});
if(!start.length){try{start=(JSON.parse(sessionStorage.getItem('evc-cmp')||'[]')||[]).filter(function(i){return by[i]})}catch(e){}}
start.slice(0,3).forEach(function(i,k){sel[k].value=i});
render();
})();"""
pages['uporedi.html'] = page('uporedi.html', f'Uporedi električne automobile: domet, baterija i dimenzije | {SITE}',
                             'Uporedite do tri električna automobila koja se prodaju u Srbiji: domet po WLTP normi, baterija, dužina, širina, visina, klirens i broj sedišta.',
                             body, [ld_breadcrumbs(crumb)],
                             extra_js='var CMP=' + json.dumps(cmp_data, ensure_ascii=False, separators=(',', ':')) + ';\n' + COMPARE_JS)

# ------------------------------------------------------------------ about, contact, privacy, 404
def info_page(path, crumb_name, h1, answer, prose, title, desc, ld_extra=(), extra_head=''):
    crumb = [('Početna', 'index.html'), (crumb_name, path)]
    body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>{E(h1)}</h1>
      <p class="answer">{answer}</p>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap prose">
{prose}
    </div>
  </section>
</main>
'''
    pages[path] = page(path, title, desc, body, [ld_breadcrumbs(crumb)] + list(ld_extra), extra_head=extra_head)

N_MODELS, N_BRANDS = len(ALL_IDS), sum(1 for s in ORDER if brands[s]['models'])
N_DEALERS = n_dealers
ORG = {'@type': 'Organization', 'name': SITE, 'url': DOMAIN + '/', 'email': 'office@evomobil.rs'}

info_page('o-nama.html', 'O nama', 'O sajtu evomobil.rs',
    f'evomobil.rs je nezavisan informativni sajt o potpuno električnim automobilima koji se zvanično prodaju u Srbiji. '
    f'Na jednom mestu prikazujemo {N_MODELS} modela {N_BRANDS} brendova, njihov domet po WLTP normi, kapacitet baterije, dimenzije i kontakte ovlašćenih distributera.',
    f'''      <h2>Šta je evomobil.rs</h2>
      <p>evomobil.rs pomaže kupcima u Srbiji da brzo uporede električne automobile koji se ovde zaista mogu kupiti. Prikazujemo samo potpuno električna vozila (BEV), bez hibrida i plug-in hibrida, i samo modele koje uvoznik ili distributer nudi na srpskom tržištu.</p>
      <h2>Šta možete da pronađete</h2>
      <ul>
        <li><a href="modeli.html">Svi električni modeli</a> sa filterima po brendu, dometu i karoseriji.</li>
        <li><a href="uporedi.html">Poređenje do tri modela</a>: domet, baterija, dužina, širina, visina, klirens i broj sedišta.</li>
        <li><a href="brendovi.html">Stranice brendova</a> sa svim modelima i ovlašćenim distributerima.</li>
        <li><a href="distributeri.html">{N_DEALERS} distributera po gradovima</a> sa adresama i telefonima.</li>
        <li><a href="punjaci.html">Mapa punjača</a> za električne automobile u Srbiji.</li>
        <li><a href="subvencije-elektricni-automobili-2026.html">Vodič kroz subvencije</a> za kupovinu električnog automobila.</li>
      </ul>
      <h2>Odakle su podaci</h2>
      <p>Podatke o modelima, dometu, bateriji i dimenzijama preuzimamo sa zvaničnih sajtova proizvođača i uvoznika, iz njihovih cenovnika, tehničkih listova i saopštenja za medije. Kontakte distributera preuzimamo sa zvaničnih sajtova uvoznika i distributera. Podatke o punjačima preuzimamo iz otvorene baze Open Charge Map.</p>
      <p>Domet je naveden po WLTP normi, za verziju sa najvećim dometom. Ako proizvođač neki podatak ne objavljuje, polje ostavljamo prazno i ne procenjujemo vrednost. Cene ne prikazujemo, jer se često menjaju; aktuelnu cenu proverite kod distributera.</p>
      <h2>Nezavisnost</h2>
      <p>evomobil.rs nije zvanični sajt nijednog proizvođača, uvoznika ili distributera. Nazivi, fotografije i logotipi brendova vlasništvo su njihovih nosilaca. Oglasi na sajtu su jasno odvojeni od podataka o modelima i ne utiču na redosled ni na sadržaj podataka.</p>
      <h2>Ispravke i sugestije</h2>
      <p>Ako primetite netačan podatak, novi model ili promenu kod distributera, pišite nam na <a href="mailto:office@evomobil.rs">office@evomobil.rs</a>. Za oglašavanje se javite na <a href="mailto:oglasi@evomobil.rs">oglasi@evomobil.rs</a>.</p>''',
    f'O nama | {SITE}',
    f'evomobil.rs je nezavisan sajt o električnim automobilima u Srbiji: {N_MODELS} modela, domet, baterija, dimenzije, distributeri i punjači. Podaci sa zvaničnih sajtova proizvođača.',
    [{'@context': 'https://schema.org', '@type': 'AboutPage', 'name': 'O sajtu evomobil.rs', 'url': f'{DOMAIN}/o-nama.html', 'inLanguage': 'sr-Latn', 'about': ORG}])

info_page('kontakt.html', 'Kontakt', 'Kontakt',
    'Za pitanja, ispravke podataka i sugestije pišite na <a href="mailto:office@evomobil.rs">office@evomobil.rs</a>. Za oglašavanje pišite na <a href="mailto:oglasi@evomobil.rs">oglasi@evomobil.rs</a>.',
    '''      <div class="contact-cards">
        <a class="ccard" href="mailto:office@evomobil.rs"><span class="ccard-k">OPŠTA PITANJA I ISPRAVKE</span><strong>office@evomobil.rs</strong><span>Netačan podatak, novi model, promena kod distributera ili sugestija za sajt.</span></a>
        <a class="ccard" href="mailto:oglasi@evomobil.rs"><span class="ccard-k">OGLAŠAVANJE</span><strong>oglasi@evomobil.rs</strong><span>Zakup reklamnih mesta za uvoznike, distributere i partnere. <span class="ccard-more">Pogledajte <u>reklamna mesta</u>.</span></span></a>
      </div>
      <h2>Za kupce</h2>
      <p>evomobil.rs ne prodaje vozila i ne zakazuje test vožnje. Za ponudu, cenu, dostupnost i test vožnju obratite se ovlašćenom distributeru. Kontakte svih distributera po gradovima pronaći ćete na stranici <a href="distributeri.html">Distributeri</a>, a kontakte za određeni brend na stranici tog brenda.</p>
      <h2>Za uvoznike i distributere</h2>
      <p>Ako želite da ispravite ili dopunite podatke o vašim modelima ili prodajnim mestima, pošaljite nam link ka zvaničnom izvoru (cenovnik, tehnički list ili stranica na vašem sajtu). Podatke objavljujemo samo iz zvaničnih izvora. Uslovi za reklamna mesta nalaze se na stranici <a href="oglasavanje.html">Oglašavanje</a>.</p>''',
    f'Kontakt | {SITE}',
    'Kontakt evomobil.rs: office@evomobil.rs za pitanja i ispravke podataka, oglasi@evomobil.rs za oglašavanje. Za test vožnju se obratite distributeru.',
    [{'@context': 'https://schema.org', '@type': 'ContactPage', 'name': 'Kontakt', 'url': f'{DOMAIN}/kontakt.html', 'inLanguage': 'sr-Latn',
      'about': dict(ORG, contactPoint=[{'@type': 'ContactPoint', 'contactType': 'customer support', 'email': 'office@evomobil.rs', 'availableLanguage': 'sr'},
                                       {'@type': 'ContactPoint', 'contactType': 'sales', 'email': 'oglasi@evomobil.rs', 'availableLanguage': 'sr'}])}])
pages['kontakt.html'] = pages['kontakt.html'].replace('<u>reklamna mesta</u>', 'reklamna mesta')

info_page('politika-privatnosti.html', 'Politika privatnosti', 'Politika privatnosti',
    'evomobil.rs ne traži registraciju. Kolačiće za statistiku poseta (Google Analytics) koristimo samo ako na to pristanete, a podatke koje nam pošaljete e-poštom koristimo samo da bismo odgovorili. U nastavku je objašnjeno šta se dešava sa podacima kada koristite sajt.',
    '''      <h2>Ko je rukovalac podacima</h2>
      <p>Rukovalac podacima je vlasnik sajta evomobil.rs. Za sva pitanja o privatnosti pišite na <a href="mailto:office@evomobil.rs">office@evomobil.rs</a>.</p>
      <h2>Podaci koje prikupljamo</h2>
      <ul>
        <li><strong>Statistika poseta (Google Analytics).</strong> Samo ako kliknete „Prihvati“ u obaveštenju o kolačićima. Detalji su u odeljku Kolačići i Google Analytics.</li>
        <li><strong>Podešavanja u pregledaču.</strong> Izbor svetle ili tamne teme i lista modela za poređenje čuvaju se samo u vašem pregledaču (sessionStorage) i brišu se kada zatvorite karticu. Vaš izbor u vezi sa kolačićima čuva se u pregledaču (localStorage) do 6 meseci, da vas ne bismo pitali pri svakoj poseti. Ovi podaci se ne šalju nama.</li>
        <li><strong>E-pošta.</strong> Kada nam pišete, vaše podatke koristimo isključivo za odgovaranje na vaš upit i dalju komunikaciju. Podatke ne delimo sa trećim licima i čuvamo ih samo onoliko koliko je neophodno za ostvarivanje te svrhe. Odgovore šaljemo preko servisa Resend (detalji u odeljku Slanje e-pošte).</li>
        <li><strong>Server.</strong> Kao i svaki sajt, server na kojem se sajt nalazi može da beleži tehničke podatke o zahtevima (IP adresa, vreme, tip pregledača) radi bezbednosti i ispravnog rada.</li>
      </ul>
      <h2 id="kolacici">Kolačići i Google Analytics</h2>
      <p>Za statistiku poseta koristimo Google Analytics 4 (Google Ireland Limited i Google LLC). Na osnovu toga vidimo koliko ljudi posećuje sajt, koje stranice su najčitanije i sa kojih uređaja se pristupa, kako bismo poboljšali sadržaj i oglašivačima pokazali posećenost. Ne prodajemo podatke i ne koristimo ih za personalizovane oglase.</p>
      <ul>
        <li><strong>Pravni osnov:</strong> vaša saglasnost. Google Analytics se ne učitava dok ne kliknete „Prihvati“. Ako kliknete „Odbij“, ne postavlja se nijedan kolačić za statistiku.</li>
        <li><strong>Kolačići:</strong> _ga i _ga_&lt;ID&gt; razlikuju posetioce i posete. Traju do 6 meseci.</li>
        <li><strong>Podaci:</strong> stranice koje posećujete, vreme posete, približna lokacija (grad ili zemlja), vrsta uređaja i pregledača. Google Analytics 4 ne čuva vašu IP adresu.</li>
        <li><strong>Čuvanje:</strong> podaci o posetama se u Google Analytics čuvaju 2 meseca, a zatim se automatski brišu.</li>
        <li><strong>Prenos podataka:</strong> Google može da obrađuje podatke i van Srbije, uključujući Sjedinjene Američke Države, uz mere zaštite koje predviđa Google.</li>
        <li><strong>Povlačenje saglasnosti:</strong> u svakom trenutku, preko linka <a href="#" data-cookie-settings>Podešavanja kolačića</a> (nalazi se i u podnožju svake stranice). Možete i da obrišete kolačiće u pregledaču ili da instalirate Googleov <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">dodatak za isključivanje Google Analytics</a>.</li>
      </ul>
      <h2 id="e-posta">Slanje e-pošte (Resend)</h2>
      <p>Odgovore na vaše poruke šaljemo preko servisa Resend (Resend, Inc., Sjedinjene Američke Države), koji za nas obavlja tehničko slanje e-pošte.</p>
      <ul>
        <li><strong>Podaci:</strong> vaša adresa e-pošte, sadržaj našeg odgovora i tehnički podaci o isporuci (vreme slanja, da li je poruka isporučena).</li>
        <li><strong>Svrha i pravni osnov:</strong> odgovor na poruku koju ste nam poslali, odnosno vaš zahtev.</li>
        <li><strong>Prenos podataka:</strong> Resend može da obrađuje podatke i van Srbije, uključujući Sjedinjene Američke Države, uz mere zaštite koje predviđa Resend.</li>
        <li>Resend podatke koristi samo za slanje poruka u naše ime, ne za sopstvene svrhe.</li>
      </ul>
      <h2>Spoljni servisi</h2>
      <p>Neki delovi sajta učitavaju se sa spoljnih servisa, koji pri tome vide vašu IP adresu:</p>
      <ul>
        <li><strong>Google Fonts</strong> (Google): fontovi kojima je sajt napisan.</li>
        <li><strong>OpenFreeMap</strong>: mapa na stranici <a href="punjaci.html">Punjači</a>.</li>
        <li><strong>Google Analytics</strong>: samo uz vašu saglasnost, kao što je opisano iznad.</li>
      </ul>
      <p>Linkovi ka sajtovima distributera, proizvođača i ka Google mapama (dugme „Navigacija“) vode na spoljne sajtove koji imaju sopstvene politike privatnosti.</p>
      <h2>Vaša prava</h2>
      <p>U skladu sa Zakonom o zaštiti podataka o ličnosti imate pravo da zatražite pristup podacima koje o vama imamo, njihovu ispravku ili brisanje, kao i da uložite prigovor. Zahtev pošaljite na <a href="mailto:office@evomobil.rs">office@evomobil.rs</a>. Imate i pravo da podnesete pritužbu Povereniku za informacije od javnog značaja i zaštitu podataka o ličnosti (<a href="https://www.poverenik.rs" target="_blank" rel="noopener">poverenik.rs</a>).</p>
      <h2>Izmene</h2>
      <p>Ako uvedemo nove servise, ažuriraćemo ovu stranicu pre nego što ih uključimo.</p>''',
    f'Politika privatnosti | {SITE}',
    'Politika privatnosti sajta evomobil.rs: Google Analytics samo uz saglasnost, kolačići, spoljni servisi i kako ostvariti prava iz Zakona o zaštiti podataka o ličnosti.',
    [{'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Politika privatnosti', 'url': f'{DOMAIN}/politika-privatnosti.html', 'inLanguage': 'sr-Latn', 'publisher': ORG}])

# 404: served for any missing address, so links resolve from the site root
body404 = f'''
<main id="top">
  <section class="phero nf">
    <div class="wrap">
      <p class="nf-code">404</p>
      <h1>Stranica nije pronađena</h1>
      <p class="answer">Stranica koju tražite ne postoji ili je premeštena. Možda vam pomogne nešto od ovoga:</p>
      <div class="ctas">
        <a href="modeli.html" class="btn btn-dark">Svi električni modeli <span class="arr">→</span></a>
        <a href="index.html#pretraga" class="btn btn-ghost">Pretraga</a>
        <a href="index.html" class="btn btn-ghost">Početna</a>
      </div>
      <ul class="nf-links">
        <li><a href="brendovi.html">Brendovi</a></li><li><a href="uporedi.html">Uporedi modele</a></li><li><a href="distributeri.html">Distributeri</a></li>
        <li><a href="punjaci.html">Punjači</a></li><li><a href="subvencije-elektricni-automobili-2026.html">Subvencije 2026</a></li><li><a href="kontakt.html">Kontakt</a></li>
      </ul>
    </div>
  </section>
</main>
'''
pages['404.html'] = page('404.html', f'Stranica nije pronađena | {SITE}', 'Tražena stranica ne postoji na evomobil.rs.', body404,
                         extra_head='<meta name="robots" content="noindex">\n')
pages['404.html'] = re.sub(r'<link rel="canonical"[^>]*>\n', '', pages['404.html'])
pages['404.html'] = re.sub(r'(href|src)="(?!https?:|#|/|mailto:|tel:|data:)', r'\1="/', pages['404.html'])

# ------------------------------------------------------------------ subsidy guide (facts checked on 16 Oct 2026)
crumb = [('Početna', 'index.html'), ('Subvencije 2026', 'subvencije-elektricni-automobili-2026.html')]
sub_qa = [
    ('Koliko iznosi subvencija za električni automobil u Srbiji 2026?', 'Za nov potpuno električni putnički automobil subvencija iznosi 5.000 evra (u dinarskoj protivvrednosti).'),
    ('Ko može da dobije subvenciju?', 'Pravo imaju fizička lica, preduzetnici i pravna lica koja kupuju novo električno vozilo.'),
    ('Kako se podnosi zahtev?', 'Zahtev se podnosi elektronski, preko portala eUprava.'),
    ('Do kada traje konkurs?', 'Rok za prijave produžen je sa 30. septembra na 1. decembar 2026. Konkurs se ranije zatvara ako se potroši novac iz budžeta.'),
    ('Da li subvencija važi za hibride?', 'Ne. Subvencija u iznosu od 5.000 evra odnosi se na vozila sa električnim pogonom. Tačne uslove za svaku kategoriju vozila proverite u uredbi i javnom pozivu ministarstva.'),
]
body = f'''
<main id="top">
  <section class="phero">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>Subvencije za električne automobile u Srbiji 2026.</h1>
      <p class="answer">Država i u 2026. godini subvencioniše kupovinu novih električnih vozila. Za nov potpuno električni putnički automobil subvencija iznosi 5.000 evra. Zahtev se podnosi preko portala eUprava, a novac se dodeljuje po redosledu prijava, najkasnije do 1. decembra 2026. ili dok se ne potroše sredstva.</p>
      <div class="keybox"><dl>
        <div><dt>IZNOS ZA ELEKTRIČNI AUTOMOBIL</dt><dd>5.000 €</dd></div>
        <div><dt>PRIJAVA</dt><dd>Portal eUprava</dd></div>
        <div><dt>ROK</dt><dd>1. decembar 2026.</dd></div>
        <div><dt>BUDŽET ZA 2026.</dt><dd>170 miliona dinara</dd></div>
      </dl></div>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap prose">
      <h2>Ko daje subvenciju</h2>
      <p>Program vodi Ministarstvo zaštite životne sredine. Vlada Srbije usvojila je uredbu o subvencionisanju kupovine novih vozila na električni pogon za 2026. godinu 6. februara 2026, sa budžetom od 170 miliona dinara.</p>
      <h2>Koliko iznosi</h2>
      <p>Iznos zavisi od vrste vozila i kreće se od 250 do 5.000 evra. Za nov potpuno električni putnički automobil ili lako teretno vozilo do 3,5 tone subvencija iznosi 5.000 evra.</p>
      <h2>Ko može da se prijavi</h2>
      <p>Fizička lica, preduzetnici i pravna lica. Vozilo mora biti novo, odnosno ne sme biti ranije korišćeno ni registrovano.</p>
      <h2>Kako se prijaviti</h2>
      <ol>
        <li>Izaberite nov električni automobil kod ovlašćenog distributera. <a href="modeli.html">Pogledajte sve električne modele u Srbiji.</a></li>
        <li>Podnesite zahtev elektronski, preko portala eUprava.</li>
        <li>Sredstva se dodeljuju po redosledu potpunih i ispravnih prijava, dok ima novca u budžetu.</li>
        <li>Subvencija može pokriti deo učešća kod finansijskog lizinga ili deo kupoprodajne cene. Kod kupovine sopstvenim sredstvima isplaćuje se kada kupac dokaže da je platio deo cene koji ne pokriva subvencija.</li>
      </ol>
      <h2>Rok</h2>
      <p>Prijave su počele 1. marta 2026. Prvobitni rok bio je 30. septembar, a produžen je do 1. decembra 2026. Ako se sredstva potroše ranije, prijem zahteva se zatvara i ministarstvo o tome obaveštava na svom sajtu.</p>
      <h2>Česta pitanja</h2>
    </div>
    <div class="wrap">{qa_block(sub_qa)}</div>
    <div class="wrap">
      <p class="sources">Izvori: <a href="https://www.paragraf.rs/dnevne-vesti/071026/071026-vest10.html" rel="noopener" target="_blank">Paragraf, 7. oktobar 2026</a>; <a href="https://biznis.rs/vesti/srbija/usvojena-uredba-o-subvencionisanju-elektricnih-vozila-za-2026-godinu/" rel="noopener" target="_blank">Biznis.rs, 6. februar 2026</a>. evomobil.rs nije zvanični izvor; pre kupovine proverite aktuelne uslove u uredbi i javnom pozivu Ministarstva zaštite životne sredine.</p>
    </div>
  </section>
</main>
'''
pages['subvencije-elektricni-automobili-2026.html'] = page('subvencije-elektricni-automobili-2026.html',
    f'Subvencije za električne automobile 2026: 5.000 € | {SITE}',
    'Subvencija za nov električni automobil u Srbiji 2026. iznosi 5.000 evra. Ko može da se prijavi, kako preko eUprave i do kada traje konkurs.',
    body, [ld_breadcrumbs(crumb), ld_faq(sub_qa),
           {'@context': 'https://schema.org', '@type': 'Article', 'headline': 'Subvencije za električne automobile u Srbiji 2026.',
            'dateModified': UPDATED, 'inLanguage': 'sr-Latn', 'publisher': {'@type': 'Organization', 'name': SITE, 'url': DOMAIN + '/'}}])

# ------------------------------------------------------------------ running cost calculator (electricity vs fuel)
# Markup, CSS and JS live in build/kalkulator.html; fuel prices in data/gorivo.json (updated every Friday).
_kc = open(f'{ROOT}/build/kalkulator.html', encoding='utf-8').read()
_kc_css = _kc.split('<!--CSS-->')[1].split('<!--BODY-->')[0]
_kc_body = _kc.split('<!--BODY-->')[1].split('<!--JS-->')[0]
_kc_js = _kc.split('<!--JS-->')[1]
FUEL = json.load(open(f'{ROOT}/data/gorivo.json', encoding='utf-8'))
def _nums(t):
    return [float(x.replace(',', '.')) for x in re.findall(r'\d+(?:,\d+)?', t or '')]
kc_models = []
for i in ALL_IDS:
    m = models[i]
    bat = _nums(kwh_txt(m)); rng = _nums(range_txt(m, True)) or ([m['r']] if m['r'] else [])
    if not bat or not rng:
        continue
    if len(bat) != len(rng):
        bat = [max(bat)] if len(rng) == 1 else bat[:len(rng)]
        rng = rng[:len(bat)]
    vs = [[b_, int(r_), round(b_ / r_ * 100, 1)] for b_, r_ in zip(bat, rng)]
    # battery / WLTP range outside 11-26 kWh/100 km means the published figures don't fit together (city-only WLTP, kW instead of kWh)
    kc_models.append({'id': i, 'b': brands[m['b']]['name'], 'n': m['full'], 'v': vs, 'ok': all(11 <= v[2] <= 26 for v in vs)})
crumb = [('Početna', 'index.html'), ('Kalkulator troškova', 'kalkulator-troskova.html')]
kc_qa = [
    ('Koliko košta punjenje električnog automobila na 100 km?', 'Zavisi od potrošnje modela i cene struje. Automobil koji troši 15 kWh na 100 km, uz 10% gubitaka pri punjenju i cenu od 12 dinara po kWh, potroši struje za oko 200 dinara na 100 km. Na javnim brzim punjačima trošak je veći.'),
    ('Kako se računa potrošnja električnog automobila?', 'Kapacitet baterije podelite sa dometom po WLTP normi i pomnožite sa 100. Dobijate potrošnju u kWh na 100 km. Stvarna potrošnja je obično veća, naročito zimi i na autoputu.'),
    ('Odakle su cene goriva u kalkulatoru?', 'Koristimo najviše maloprodajne cene za BMB 95 i Evrodizel koje Ministarstvo unutrašnje i spoljne trgovine objavljuje svakog petka.'),
]
body = f"""
<main id="top">
  <section class="phero" style="padding-bottom:32px">
    <div class="wrap">
      {crumbs(crumb, '')}
      <h1>Kalkulator troškova: struja ili gorivo</h1>
      <p class="answer">Izaberite električni model, unesite koliko vozite i po kojoj ceni punite. Kalkulator poredi trošak energije sa automobilom na benzin ili dizel, na 100 km, mesečno, godišnje i za pet godina.</p>
    </div>
  </section>
  <section class="sec" style="padding-top:0">
    <div class="wrap">{_kc_body}</div>
  </section>
  <section class="sec alt">
    <div class="wrap">
      <h2 class="h2s">Česta pitanja o troškovima</h2>
      {qa_block(kc_qa)}
    </div>
  </section>
</main>
"""
_kc_js = _kc_js.replace('__MODELS__', json.dumps(kc_models, ensure_ascii=False, separators=(',', ':'))).replace('__FUEL__', json.dumps({k: FUEL.get(k) or FUEL['datum'] for k in ('datum', 'provereno', 'benzin', 'dizel')}))
pages['kalkulator-troskova.html'] = page('kalkulator-troskova.html', f'Kalkulator troškova: struja ili gorivo | {SITE}',
    'Koliko košta vožnja električnim automobilom u odnosu na benzin ili dizel? Izaberite model, kilometražu i cenu struje i uporedite trošak na 100 km, mesečno i godišnje.',
    body, [ld_breadcrumbs(crumb), ld_faq(kc_qa),
           {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'Kalkulator troškova: struja ili gorivo', 'applicationCategory': 'UtilityApplication',
            'operatingSystem': 'Any', 'inLanguage': 'sr-Latn', 'url': f'{DOMAIN}/kalkulator-troskova.html', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'RSD'}}],
    extra_head=_kc_css, extra_js=_kc_js)

# ------------------------------------------------------------------ advertising page (moved off the homepage)
crumb = [('Početna', 'index.html'), ('Oglašavanje', 'oglasavanje.html')]
ads = unembed(ads_section, '')
ads = ads.replace('<section class="sec" id="oglasavanje">', '<section class="sec" id="oglasavanje" style="padding-top:0">')
ads = re.sub(r'<h2([^>]*)>(.*?)</h2>', r'<h1\1>\2</h1>', ads, count=1, flags=re.S)
body = f'''
<main id="top">
  <section class="phero" style="padding-bottom:32px">
    <div class="wrap">{crumbs(crumb, '')}</div>
  </section>
  {ads}
</main>
'''
pages['oglasavanje.html'] = page('oglasavanje.html', f'Oglašavanje: reklamna mesta i formati | {SITE}',
                                 'Reklamna mesta na evomobil.rs za uvoznike, distributere i partnere: hero karusel, leaderboard, brend meseca, ponude partnera. Formati i zakup.',
                                 body, [ld_breadcrumbs(crumb)], extra_js='(function(){var $=function(i){return document.getElementById(i)};\n' + copy_js + '})();')

# ------------------------------------------------------------------ homepage
# featured models on the homepage (edit this list to change them; filters read the data-* attributes)
FEATURED_HOME = ['hyundai-ioniq-5', 'renault-5-e-tech', 'bmw-i4', 'byd-sealion-7', 'dacia-spring', 'foton-etunland']
_cards = []
for _mid in [i for i in FEATURED_HOME if i in models]:
    _m = models[_mid]
    _c = card(_mid, '')
    _c = _c.replace('<article class="mcard">', f'<article class="mcard" data-tags="{" ".join(_m["tags"])}" data-name="{E(_m["n"])}" data-range="{_m["r"] or 0}" data-brand="{E(brands[_m["b"]]["name"])}">', 1)
    _cards.append(_c)
src, _k = re.subn(r'(<div class="models" id="models">)(.*?)(\n\s*<div class="empty" id="empty" hidden>)',
                  lambda mm: mm.group(1) + '\n' + '\n'.join(_cards) + mm.group(3), src, count=1, flags=re.S)
assert _k == 1
open(f'{ROOT}/build/homepage-template.html', 'w', encoding='utf-8').write(src)
home = unembed(src, '')
faq_pairs = re.findall(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', home, re.S)
faq_pairs = [(re.sub(r'\s*\+\s*$', '', re.sub(r'<[^>]+>', '', q)).strip(), html.unescape(re.sub(r'<[^>]+>', '', a)).strip()) for q, a in faq_pairs]
faq_pairs = [(html.unescape(q), a) for q, a in faq_pairs]
head_meta = (f'<link rel="canonical" href="{DOMAIN}/">\n<meta property="og:type" content="website">\n<meta property="og:site_name" content="{SITE}">\n'
             f'<meta property="og:locale" content="sr_RS">\n<meta property="og:title" content="Električni automobili u Srbiji | {SITE}">\n'
             '<meta property="og:description" content="Električni automobili u Srbiji na jednom mestu: modeli, domet, baterija i distributeri.">\n'
             f'<meta property="og:url" content="{DOMAIN}/">\n<meta property="og:image" content="{DOMAIN}/{OG_DEFAULT}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="evomobil.rs – električni automobili u Srbiji">\n<meta name="twitter:card" content="summary_large_image">\n'
             f'<link rel="icon" href="favicon.ico?v={FAV_V}" sizes="any">\n<link rel="icon" href="img/favicon.svg?v={FAV_V}" type="image/svg+xml">\n<link rel="icon" href="img/favicon-32.png?v={FAV_V}" type="image/png" sizes="32x32">\n<link rel="apple-touch-icon" href="img/apple-touch-icon.png?v={FAV_V}">\n<meta name="theme-color" content="#16202e">\n')
home_ld = [
    {'@context': 'https://schema.org', '@type': 'WebSite', 'name': SITE, 'url': DOMAIN + '/', 'inLanguage': 'sr-Latn',
     'description': 'Električni automobili u Srbiji: modeli, domet i distributeri.'},
    {'@context': 'https://schema.org', '@type': 'Organization', 'name': SITE, 'url': DOMAIN + '/', 'logo': DOMAIN + '/img/icon-512.png',
     'email': 'office@evomobil.rs', 'areaServed': {'@type': 'Country', 'name': 'Srbija'},
     'contactPoint': [{'@type': 'ContactPoint', 'contactType': 'customer support', 'email': 'office@evomobil.rs', 'availableLanguage': 'sr'},
                      {'@type': 'ContactPoint', 'contactType': 'sales', 'email': 'oglasi@evomobil.rs', 'availableLanguage': 'sr'}]},
    ld_faq(faq_pairs),
]
home_ld_html = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in home_ld)
title_m = re.search(r'<title>.*?</title>\n', home)
home_head_frag = home[:title_m.end()] + head_meta + home_ld_html + home[title_m.end():]
# full document for real hosting
style_end = home_head_frag.index('</style>') + len('</style>')
head_part, body_part = home_head_frag[:style_end], home_head_frag[style_end:]
# move the JSON-LD and meta (already before <style>) and split head/body at the first element that belongs to the body
body_start = body_part.find('<svg width="0" height="0"')
head_part = re.sub(r'<style>.*?</style>', lambda mm: f'<link rel="stylesheet" href="assets/site.css?v={CSS_V}">' + MASK_FIX, head_part, count=1, flags=re.S)
_bi = common_js.index('/* "Uporedi": pick up to 3 models')
CMP_BAR_JS = '(function(){\n  ' + common_js[_bi:common_js.index('})();', _bi) + 5]
body_part = body_part.replace('</body>', '<script>' + CMP_BAR_JS + CONSENT_JS + '</script>\n</body>') if '</body>' in body_part else body_part + '<script>' + CMP_BAR_JS + CONSENT_JS + '</script>\n'
pages['index.html'] = ('<!doctype html>\n<html lang="sr-Latn">\n<head>\n<meta charset="utf-8">\n'
                       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="color-scheme" content="only light">\n'
                       + head_part + body_part[:body_start] + '\n</head>\n<body>\n' + body_part[body_start:] + '\n</body>\n</html>\n')
# preview copy for the Claude artifact (the artifact host adds the document wrapper itself)
preview = home_head_frag

# ------------------------------------------------------------------ write output
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for folder in ('img', 'logos'):
    shutil.copytree(f'{ROOT}/{folder}', f'{OUT}/{folder}')
os.makedirs(f'{OUT}/assets', exist_ok=True)
open(f'{OUT}/assets/site.css', 'w', encoding='utf-8').write(SITE_CSS)
for f in ('maplibre-gl.js', 'maplibre-gl.css'):
    shutil.copy(f'{ROOT}/vendor/maplibre/{f}', f'{OUT}/assets/{f}')
for path, h in pages.items():
    os.makedirs(os.path.dirname(f'{OUT}/{path}') or OUT, exist_ok=True)
    open(f'{OUT}/{path}', 'w', encoding='utf-8').write(h)
open(f'{ROOT}/build/_preview_index.html', 'w', encoding='utf-8').write(preview)
# README stays with the project, not in the published site
shutil.copy(f'{ROOT}/build/README-site.txt', f'{ROOT}/README.txt')
if os.path.exists(f'{OUT}/README.txt'):
    os.remove(f'{OUT}/README.txt')
# ------------------------------------------------------------------ SWITCHES (see README.txt)
# NOINDEX = True  -> every page gets <meta name="robots" content="noindex, nofollow"> and an X-Robots-Tag header
#                    (private preview, e.g. password-protected on Cloudflare). False = search engines may index.
# ADS_ENABLED = False -> Oglašavanje page, demo page, oglasi@ address, "Zakupi" buttons, ad codes and links to
#                    Oglašavanje are left out of the site; the ad spots stay as neutral "Slobodna pozicija" placeholders.
#                    True = everything for selling ads is back.
NOINDEX = True
ADS_ENABLED = False
# CLEAN_URLS = True -> addresses without .html (evomobil.rs/modeli). Files stay modeli.html on disk; Cloudflare
#                     serves /modeli from modeli.html (wrangler.jsonc: html_handling auto-trailing-slash).
#                     Links then work only on Cloudflare, not when opening the files from disk. False = .html addresses.
CLEAN_URLS = True
# PH_STYLE: how the demo photos sit in empty ad spots. 'multiply' = faint greyscale photo multiplied into green;
#           'fade' = colour photo on the right dissolving into the soft green on the left;
#           'photo' = regular full photo with a dark scrim, white text.
PH_STYLE = 'photo'

# Cloudflare Pages: security and cache headers (_headers is read by Cloudflare, never served as a page)
open(f'{OUT}/_headers', 'w').write('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
''' + ('  X-Robots-Tag: noindex, nofollow\n' if NOINDEX else '') + '''
/img/*
  Cache-Control: public, max-age=2592000

/logos/*
  Cache-Control: public, max-age=2592000

/assets/*
  Cache-Control: public, max-age=2592000
''')
if os.path.exists(f'{OUT}/vercel.json'):
    os.remove(f'{OUT}/vercel.json')

# ------------------------------------------------------------------ demo page for advertisers (not linked, noindex, not in sitemap)
# Homepage with every rentable spot filled with FICTIONAL advertisers. Creatives: demo/make_creatives.js -> demo/out/*.webp
DEMO_PATH = 'primer-oglasa.html'
if os.path.isdir(f'{ROOT}/demo/out'):
    os.makedirs(f'{OUT}/img/demo', exist_ok=True)
    for f in os.listdir(f'{ROOT}/demo/out'):
        shutil.copy(f'{ROOT}/demo/out/{f}', f'{OUT}/img/demo/{f}')
    d = pages['index.html']
    D = 'img/demo/demo-'
    # head: noindex, own title, no canonical to the homepage
    d = re.sub(r'<link rel="canonical"[^>]*>\n?', '', d, count=1)
    d = d.replace('<head>', '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
    d = re.sub(r'<title>[^<]*</title>', '<title>Primer reklamnih mesta | evomobil.rs</title>', d, count=1)
    # hero: 5 filled rotation positions
    i = d.index('  const slides=['); j = d.index('  ];', i)
    hero = [('AutoCentar Nova', 'Električni SUV', 'hero-1-nova'), ('VoltDom', 'Kućni punjač', 'hero-2-voltdom'),
            ('Punionica+', 'Aplikacija', 'hero-3-punionica'), ('EkoLizing', 'Lizing', 'hero-4-eko'), ('PutujEV', 'Planer puta', 'hero-5-putuj')]
    d = d[:i] + '  const slides=[\n' + ',\n'.join(
        f"    {{b:'{b}',m:'{m}',img:'{D}{f}.webp',alt:'Oglas: {b}',href:'#'}}" for b, m, f in hero) + '\n' + d[j:]
    d = d.replace('<a id="h-link" class="hero-img" href="#" hidden><img id="h-img" src="data:," alt="" width="1600" height="900"></a>',
                  f'<a id="h-link" class="hero-img" href="#"><img id="h-img" src="{D}hero-1-nova.webp" alt="Oglas: AutoCentar Nova" width="1600" height="900"></a>', 1)
    d = d.replace('<div class="free ph-bg" id="h-free" style="--ph:url(../img/evomobil-bg-auto.webp)">', '<div class="free ph-bg" id="h-free" style="--ph:url(../img/evomobil-bg-auto.webp)" hidden>', 1)
    d = d.replace('<span class="rs-chip"><span id="h-brand">SLOBODNA POZICIJA</span></span>', '<span class="rs-chip" hidden><span id="h-brand">AUTOCENTAR NOVA</span></span>', 1)
    def pic(big, small, alt, w, h):
        return (f'<a class="demo-ad" href="#" aria-label="{alt}"><picture><source media="(max-width: 640px)" srcset="{D}{small}.webp">'
                f'<img src="{D}{big}.webp" alt="{alt}" width="{w}" height="{h}" decoding="async"></picture></a>')
    def swap_house(doc, pos, html):
        k = doc.index(f'data-pos="{pos}"'); a = doc.index('<div class="house', k)
        depth, p = 0, a
        while True:
            o = doc.find('<div', p); c = doc.find('</div>', p)
            if o != -1 and o < c: depth += 1; p = o + 4
            else:
                depth -= 1; p = c + 6
                if depth == 0: break
        return doc[:a] + html + doc[p:]
    d = swap_house(d, 'AD-02', pic('lb-putuj', 'lb-putuj-m', 'Oglas: PutujEV', 2480, 360))
    d = swap_house(d, 'AD-04A', pic('of-sigurna', 'of-sigurna-m', 'Oglas: Sigurna Struja', 1220, 480))
    d = swap_house(d, 'AD-04B', pic('of-solar', 'of-solar-m', 'Oglas: SolarKuća', 1220, 480))
    # AD-03 brand of the month: fictional brand
    d = d.replace('<span class="rs-label">Brend meseca · Oglas</span>\n            <h3>Ovde može stajati vaš brend</h3>\n            <p>Prvo mesto u listi brendova, sa logom i linkom ka vašoj EV ponudi.</p>',
                  '<span class="rs-label">Brend meseca</span>\n            <h3>Voltra: novi električni SUV stiže u Srbiju</h3>\n            <p>Voltra X5 sa dometom do 560 km. Predstavljanje u salonima od 1. novembra.</p>', 1)
    d = d.replace('<div class="logo-slot">LOGO BRENDA</div>',
                  '<div class="logo-slot demo-logo"><span class="voltra">VOLTRA</span></div>', 1)
    d = d.replace('<a href="oglasavanje.html#zakup-03" class="btn btn-dark">Zakupi ovaj prostor <span class="arr">→</span></a>',
                  '<a href="#" class="btn btn-dark">Pogledaj Voltra X5 <span class="arr">→</span></a>', 1)
    # AD-05 test drive sponsor
    d = d.replace('<div class="slot">LOGO SPONZORA</div>\n          <p>Mesto za jednog distributera ili brend, uz link ka zakazivanju test vožnje.</p>',
                  '<a class="slot demo-sponsor" href="#"><span class="nova"><svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="17" fill="none" stroke="currentColor" stroke-width="4"/><path d="M13 27V13l14 14V13" fill="none" stroke="#f5b301" stroke-width="4" stroke-linejoin="round"/></svg><span>AutoCentar <b>Nova</b></span></span></a>\n'
                  '          <p>Zakažite besplatnu test vožnju bilo kog električnog modela iz naše ponude, u Beogradu i Novom Sadu.</p>', 1)
    # demo banner + styles
    demo_css = ('<style>.demo-top{position:sticky;top:0;z-index:60}.demo-top header.site{position:relative;top:0}.demo-bar{position:relative;z-index:90;display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap;padding:9px 16px;background:#16202e;color:#fff;font:500 13px var(--font);text-align:center}'
                '.demo-back{color:#fff;font-weight:700;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:3px 12px;text-decoration:none;white-space:nowrap}.demo-back:hover{background:#fff;color:#16202e}.demo-bar b{background:#f5b301;color:#16202e;border-radius:999px;padding:2px 10px;font-weight:800;letter-spacing:.08em;font-size:11px}'
                '.demo-ad{display:block;border-radius:var(--r-lg);overflow:hidden;line-height:0;box-shadow:0 1px 0 var(--line)}.demo-ad img{width:100%;height:auto}'
                '.offers .demo-ad{flex:none}'
                '.demo-logo{border-style:solid!important;background:#0b0f17!important;border-color:#0b0f17!important}'
                '.voltra{font:800 clamp(16px,1.6vw,22px)/1 var(--font-head);letter-spacing:.24em;color:#fff;padding-left:.24em;white-space:nowrap}'
                '.demo-sponsor{border-style:solid!important;border-color:rgba(255,255,255,.18)!important;text-decoration:none}'
                '.nova{display:inline-flex;align-items:center;gap:10px;color:#fff;font:500 20px var(--font);letter-spacing:-.01em}.nova b{font-weight:800}.nova svg{width:30px;height:30px}'
                '</style>\n')
    d = d.replace('</head>', demo_css + '</head>', 1)
    d = d.replace('<header class="site"', '<div class="demo-top">' + '<div class="demo-bar"><b>DEMO</b><span>Primer kako izgledaju popunjena reklamna mesta na evomobil.rs. Oglašivači i ponude su izmišljeni. Zakup: oglasi@evomobil.rs</span><a class="demo-back" href="oglasavanje.html">← Nazad na Oglašavanje</a></div>' + '\n<header class="site"', 1)
    d = re.sub(r'(</header>)', r'\1</div>', d, count=1)
    d = d.replace('href="#"', 'href="#" onclick="return false"')
    # demo is a picture of the site: nothing on it can be clicked, opened or typed into
    lock = ('<style>main a,main button,main input,main select,main label,main summary,main [role=button],.cmp-bar,.cmp-bar *,header.site a,footer a{cursor:default!important}#prev,#next,.demo-bar a,a[href^=mailto]{cursor:pointer!important}.ck{display:none!important}</style>'
            '<script>(function(){var free=function(t){return t&&t.closest&&t.closest(".demo-bar a,#prev,#next,#theme-btn,#menu-btn,a[href^=mailto]")};'
            'var stop=function(e){if(free(e.target))return;e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();return false};'
            "['click','auxclick','dblclick','submit','contextmenu'].forEach(function(t){document.addEventListener(t,stop,true)});"
            "document.addEventListener('mousedown',function(e){if(!free(e.target)&&e.target.closest('input,select,textarea,button,a,label,summary'))stop(e)},true);"
            "document.addEventListener('keydown',function(e){if((e.key==='Enter'||e.key===' ')&&!free(e.target)){if(e.target.closest('a,button,input,select,textarea,summary'))stop(e)}},true);"
            "document.addEventListener('DOMContentLoaded',function(){[].forEach.call(document.querySelectorAll('main a,main button,main input,main select,main textarea,main summary'),function(el){if(el.id!=='prev'&&el.id!=='next')el.setAttribute('tabindex','-1')})});"
            '})();</script>\n')
    d = d.replace('</head>', lock + '</head>', 1)
    open(f'{OUT}/{DEMO_PATH}', 'w', encoding='utf-8').write(d)

# favicon from the site logo symbol
logo_sym = re.search(r'<symbol id="logo"[^>]*viewBox="([^"]+)"[^>]*>(.*?)</symbol>', sprite, re.S)
vb = [float(x) for x in logo_sym.group(1).split()]
w, h = vb[2], vb[3]; side = max(w, h) * 1.12
fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0] - (side - w) / 2:.2f} {vb[1] - (side - h) / 2:.2f} {side:.2f} {side:.2f}">'
       f'<rect x="{vb[0] - (side - w) / 2:.2f}" y="{vb[1] - (side - h) / 2:.2f}" width="{side:.2f}" height="{side:.2f}" rx="{side * .22:.2f}" fill="#ffffff"/>'
       f'<g style="--logo-ink:#16202e;color:#16202e">{logo_sym.group(2)}</g></svg>')
shutil.copy(f'{ROOT}/favicon.ico', f'{OUT}/favicon.ico')
open(f'{OUT}/img/favicon.svg', 'w', encoding='utf-8').write(fav)

# sitemap, robots, llms.txt
urls = ['index.html'] + sorted(p for p in pages if p not in ('index.html', '404.html'))
pri = lambda p: '1.0' if p == 'index.html' else '0.8' if p.startswith(('brendovi/', 'modeli/')) or p in ('modeli.html', 'brendovi.html') else '0.7'
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>{DOMAIN}/{"" if p == "index.html" else p}</loc><lastmod>{UPDATED}</lastmod><priority>{pri(p)}</priority></url>\n' for p in urls) + '</urlset>\n'
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(sm)
# AI assistants and search engines are welcome: named explicitly so no crawler policy defaults block them
AI_BOTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User',
           'Google-Extended', 'Googlebot', 'Bingbot', 'Applebot', 'Applebot-Extended', 'DuckAssistBot', 'meta-externalagent', 'MistralAI-User', 'CCBot']
open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(''.join(f'User-agent: {b}\n' for b in AI_BOTS) + 'Allow: /\n\nUser-agent: *\nAllow: /\n\n'
                                                      f'Sitemap: {DOMAIN}/sitemap.xml\n')
llms = [f'# {SITE}', '', '> Nezvanični informativni sajt o potpuno električnim automobilima koji se prodaju u Srbiji: modeli, domet (WLTP), baterija i kontakti ovlašćenih distributera. Hibridi nisu uključeni.', '',
        '## Glavne stranice', f'- [Svi modeli]({DOMAIN}/modeli.html): {len(ALL_IDS)} električnih modela', f'- [Brendovi]({DOMAIN}/brendovi.html)',
        f'- [Najveći domet]({DOMAIN}/najveci-domet.html)', f'- [Distributeri po gradovima]({DOMAIN}/distributeri.html)', f'- [Punjači za električne automobile (mapa)]({DOMAIN}/punjaci.html)',
        f'- [Subvencije 2026]({DOMAIN}/subvencije-elektricni-automobili-2026.html)', f'- [Kalkulator troškova]({DOMAIN}/kalkulator-troskova.html): trošak struje u odnosu na benzin i dizel', f'- [Uporedi modele]({DOMAIN}/uporedi.html): poređenje do tri modela',
        f'- [O nama]({DOMAIN}/o-nama.html): izvori podataka i metodologija', f'- [Kontakt]({DOMAIN}/kontakt.html)', '',
        '## Kompletni podaci', f'- [llms-full.txt]({DOMAIN}/llms-full.txt): svi modeli sa dometom, baterijom, dimenzijama i gradovima distributera, na jednom mestu',
        f'- [modeli.json]({DOMAIN}/podaci/modeli.json): isti podaci u JSON formatu', '', '## Brendovi']
llms += [f'- [{brands[s]["name"]}]({DOMAIN}/brendovi/{s}.html): ' + ', '.join(models[i]['full'] for i in brands[s]['models']) for s in ORDER]
llms += ['', '## Modeli']
llms += [f'- [{models[i]["full"]}]({DOMAIN}/modeli/{i}.html): {models[i]["cls"] or "električni automobil"}' + (f', domet {range_txt(models[i], True)} (WLTP)' if models[i]['r'] else '') + (f', baterija {kwh_txt(models[i])}' if models[i]['kwh'] else '') for i in ALL_IDS]
open(f'{OUT}/llms.txt', 'w', encoding='utf-8').write('\n'.join(llms) + '\n')

# full plain-text data for AI assistants (llms-full.txt) and the same data as JSON
def _dims(i):
    d = DIMS.get(i, {})
    out = {}
    if d.get('length_txt') or d.get('length_mm'): out['duzina'] = d.get('length_txt') or mm(d['length_mm'])
    if d.get('width_mm'): out['sirina'] = mm(d['width_mm']) + (' (sa sklopljenim retrovizorima)' if d.get('width_folded') else '')
    if d.get('height_txt') or d.get('height_mm'): out['visina'] = d.get('height_txt') or mm(d['height_mm'])
    if d.get('clearance_mm'): out['klirens'] = mm(d['clearance_mm']) + (' (pod opterećenjem)' if d.get('clearance_laden') else '')
    if d.get('seats'): out['broj_sedista'] = d['seats']
    return out
full = [f'# {SITE}: kompletni podaci', '',
        '> Nezavisan informativni sajt o potpuno električnim automobilima (BEV) koji se zvanično prodaju u Srbiji. Bez hibrida. Bez cena.',
        '> Domet je po WLTP normi, za verziju sa najvećim dometom. Podaci su sa zvaničnih sajtova proizvođača i uvoznika. Prazno polje znači da proizvođač podatak ne objavljuje.',
        f'> Ukupno: {len(ALL_IDS)} modela, {sum(1 for x in ORDER if brands[x]["models"])} brendova. Poslednje ažuriranje: {UPDATED}.', '']
data = []
for s_ in ORDER:
    b = brands[s_]
    if not b['models']:
        continue
    cities = cities_of(s_)
    full += [f'## {b["name"]}', f'Stranica: {DOMAIN}/brendovi/{s_}.html',
             (f'Ovlašćeni distributeri u gradovima: {join_sr(cities)}.' if cities else 'Ovlašćeni distributeri: lista nije objavljena.'), '']
    for i in b['models']:
        m = models[i]; dd = _dims(i)
        full += [f'### {m["full"]}', f'- Stranica: {DOMAIN}/modeli/{i}.html', f'- Klasa: {m["cls"] or "električni automobil"}', '- Pogon: 100% električni']
        if m['r']: full.append(f'- Domet (WLTP): {range_txt(m, True)}')
        if m['kwh']: full.append(f'- Baterija: {kwh_txt(m)}')
        labels = {'duzina': 'Dužina', 'sirina': 'Širina', 'visina': 'Visina', 'klirens': 'Klirens', 'broj_sedista': 'Broj sedišta'}
        full += [f'- {labels[k]}: {v}' for k, v in dd.items()]
        full.append('')
        data.append(dict({'id': i, 'brend': b['name'], 'model': m['full'], 'url': f'{DOMAIN}/modeli/{i}.html', 'klasa': m['cls'],
                          'domet_wltp_km': m['r'], 'domet_tekst': range_txt(m, True) if m['r'] else None, 'baterija': kwh_txt(m) if m['kwh'] else None,
                          'gradovi_distributera': cities}, **dd))
full += ['## Ostalo', f'- Subvencije 2026: {DOMAIN}/subvencije-elektricni-automobili-2026.html',
         f'- Distributeri po gradovima: {DOMAIN}/distributeri.html', f'- Kalkulator troškova (struja i gorivo): {DOMAIN}/kalkulator-troskova.html', f'- Mapa punjača: {DOMAIN}/punjaci.html', f'- Uporedi modele: {DOMAIN}/uporedi.html',
         f'- Kontakt i ispravke podataka: office@evomobil.rs', '']
open(f'{OUT}/llms-full.txt', 'w', encoding='utf-8').write('\n'.join(full))
os.makedirs(f'{OUT}/podaci', exist_ok=True)
json.dump({'izvor': SITE, 'url': DOMAIN + '/', 'azurirano': UPDATED, 'napomena': 'Domet po WLTP normi; podaci sa zvaničnih sajtova proizvođača i uvoznika; null = nije objavljeno.',
           'modeli': data}, open(f'{OUT}/podaci/modeli.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(f'{len(pages)} pages written to {OUT}/ ({len(brands)} brands, {len(models)} models)')
for p in sorted(pages, key=lambda p: (p.count('/'), p)):
    pass
print('index.html', len(pages['index.html']) // 1024, 'KB; model page', len(pages['modeli/byd-seal.html']) // 1024, 'KB')

# ------------------------------------------------------------------ ADS_ENABLED = False: strip everything used to sell ads
if not ADS_ENABLED:
    import glob
    for f in ('oglasavanje.html', 'primer-oglasa.html'):
        if os.path.exists(f'{OUT}/{f}'):
            os.remove(f'{OUT}/{f}')
    if os.path.isdir(f'{OUT}/img/demo'):
        shutil.rmtree(f'{OUT}/img/demo')
    seen = collections.Counter()
    def strip(h, f):
        n0 = h
        # footer: Oglašavanje link and oglasi@ address (all pages)
        h = re.sub(r'<li><a href="(?:\.\./|/)?oglasavanje\.html">Oglašavanje</a></li>', '', h)
        h = h.replace('<li><a href="mailto:oglasi@evomobil.rs">oglasi@evomobil.rs</a></li>', '')
        # structured data: sales contact
        h = h.replace(', {"@type": "ContactPoint", "contactType": "sales", "email": "oglasi@evomobil.rs", "availableLanguage": "sr"}', '')
        if f == 'index.html':
            h = re.sub(r'<div class="rs-note">.*?</div>', '', h)
            h = re.sub(r'<!--[^>]*?AD-0.*?-->\s*', '', h, flags=re.S)                         # internal ad comments
            h = re.sub(r' data-pos="AD-0[^"]*"', '', h)                                   # AD-0x codes and "Detalji"
            h = re.sub(r'\s*<a href="oglasavanje\.html#zakup-0\d" class="btn btn-dark">Zakupi[^<]*<span class="arr">→</span></a>', '', h)
            h = h.replace('<p>Jedna od 5 pozicija u hero karuselu. Kreativa 1600 x 900 px (16:9), mesečni zakup.</p>', '')
            h = h.replace('<span class="media-hint" id="hero-hint">Kreativa oglašivača 1600 x 900 px</span>', '')
            h = h.replace('''<a class="tile tile-free ph-bg" href="oglasavanje.html#zakup-01" data-k="'+k+'"'+(s.bg?' style="--ph:url('+s.bg+')"':'')+'><b>POZICIJA '+(k+1)+'</b><strong>Slobodna pozicija</strong><span>Zakupi →</span></a>''',
                          '''<div class="tile tile-free ph-bg" data-k="'+k+'"'+(s.bg?' style="--ph:url('+s.bg+')"':'')+'><b>POZICIJA '+(k+1)+'</b><strong>Slobodna pozicija</strong></div>''')
        if f == 'index.html':
            # no word about ads anywhere while ads are off (labels and screen-reader names included)
            h = re.sub(r'\s*<span class="rs-label">Oglas</span>', '', h)
            h = h.replace('<span class="rs-label">Brend meseca · Oglas</span>', '<span class="rs-label">Brend meseca</span>')
            h = h.replace('aria-label="Oglas"', 'aria-label="Istaknuto"')
            h = h.replace('aria-label="Prethodni oglas"', 'aria-label="Prethodna pozicija"').replace('aria-label="Sledeći oglas"', 'aria-label="Sledeća pozicija"')
            h = h.replace('aria-label="Oglašivači u rotaciji"', 'aria-label="Pozicije"').replace('aria-label="Sponzorisani modeli"', 'aria-label="Istaknuti modeli"')
            h = h.replace('<div class="slot">LOGO SPONZORA</div>', '<div class="slot">LOGO</div>')
            h = re.sub(r'\s*<p>Mesto za jednog distributera ili brend, uz link ka zakazivanju test vožnje\.</p>', '', h)
        if f == 'politika-privatnosti.html':
            h = h.replace('kako bismo poboljšali sadržaj i oglašivačima pokazali posećenost.', 'kako bismo poboljšali sadržaj.')
            h = h.replace('Ne prodajemo podatke i ne koristimo ih za personalizovane oglase.', 'Ne prodajemo podatke i ne koristimo ih za profilisanje posetilaca.')
        if f == 'o-nama.html':
            h = h.replace(' Oglasi na sajtu su jasno odvojeni od podataka o modelima i ne utiču na redosled ni na sadržaj podataka.', '')
            h = h.replace(' Za oglašavanje se javite na <a href="mailto:oglasi@evomobil.rs">oglasi@evomobil.rs</a>.', '')
        if f == 'kontakt.html':
            h = h.replace(' Za oglašavanje pišite na <a href="mailto:oglasi@evomobil.rs">oglasi@evomobil.rs</a>.', '')
            h = re.sub(r'\s*<a class="ccard" href="mailto:oglasi@evomobil\.rs">.*?</span></span></a>', '', h, flags=re.S)
            h = h.replace(' Uslovi za reklamna mesta nalaze se na stranici <a href="oglasavanje.html">Oglašavanje</a>.', '')
            h = h.replace(', oglasi@evomobil.rs za oglašavanje', '')
        return h
    for f in glob.glob(f'{OUT}/**/*.html', recursive=True):
        rel = os.path.relpath(f, OUT)
        h = open(f, encoding='utf-8').read()
        h2 = strip(h, rel)
        if h2 != h:
            open(f, 'w', encoding='utf-8').write(h2)
    for f in ('sitemap.xml', 'llms.txt', 'llms-full.txt'):
        t = open(f'{OUT}/{f}', encoding='utf-8').read()
        t = re.sub(r'\s*<url><loc>[^<]*oglasavanje\.html</loc>.*?</url>', '', t)
        t = '\n'.join(l for l in t.split('\n') if 'oglasavanje' not in l and 'oglasi@' not in l)
        open(f'{OUT}/{f}', 'w', encoding='utf-8').write(t)
    # nothing about selling ads may be left (only words like "oglas" in the privacy policy)
    left = []
    for f in glob.glob(f'{OUT}/**/*', recursive=True):
        if os.path.isfile(f) and f.endswith(('.html', '.txt', '.xml', '.json')):
            t = open(f, encoding='utf-8').read()
            for w in ('oglasavanje.html', 'oglasi@', 'Zakupi', 'zakup-0', 'primer-oglasa', 'rs-note">', 'mesečni zakup'):
                if w in t:
                    left.append((os.path.relpath(f, OUT), w))
            body = re.sub(r'<script.*?</script>', '', t, flags=re.S) if f.endswith('.html') else t
            for m in re.finditer(r'(?i)ogla[sš]|sponzor|reklam', body):
                left.append((os.path.relpath(f, OUT), body[max(0, m.start() - 30):m.end() + 20]))
    if left:
        raise SystemExit('ADS_ENABLED=False but ad references remain: ' + repr(left[:10]))

# ------------------------------------------------------------------ PH_STYLE: placeholder photo look on the homepage
if PH_STYLE != 'multiply':
    for f in [f'{OUT}/index.html'] + ([f'{OUT}/primer-oglasa.html'] if os.path.exists(f'{OUT}/primer-oglasa.html') else []):
        h = open(f, encoding='utf-8').read()
        h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<script>document.documentElement.setAttribute("data-ph","' + PH_STYLE + '")</script>', 1)
        open(f, 'w', encoding='utf-8').write(h)

# ------------------------------------------------------------------ CLEAN_URLS: drop ".html" from every internal address
if CLEAN_URLS:
    import glob
    PAGES_ = sorted((os.path.relpath(f, OUT)[:-5] for f in glob.glob(f'{OUT}/**/*.html', recursive=True)), key=len, reverse=True)
    PAGES_ = [p_ for p_ in PAGES_ if p_ != '404']
    rx = re.compile(r'(?<![A-Za-z0-9_.-])((?:https://www\.evomobil\.rs/|\.\./|/)?)(' + '|'.join(re.escape(p_) for p_ in PAGES_) + r')\.html(?=["\'#?)\s<,\\]|$)')
    def _clean(m):
        pre, path = m.group(1), m.group(2)
        if path == 'index':
            return pre if pre else './'
        return pre + path
    for f in glob.glob(f'{OUT}/**/*', recursive=True):
        if not (os.path.isfile(f) and f.endswith(('.html', '.xml', '.txt', '.json'))):
            continue
        t = open(f, encoding='utf-8').read()
        t2 = rx.sub(_clean, t)
        d_ = os.path.dirname(os.path.relpath(f, OUT))
        if d_:                                                  # sibling links inside brendovi/ and modeli/ ("kia.html")
            sib = sorted((p_[len(d_) + 1:] for p_ in PAGES_ if p_.startswith(d_ + '/')), key=len, reverse=True)
            if sib:
                t2 = re.sub(r'(?<=["\'])(' + '|'.join(re.escape(x) for x in sib) + r')\.html(?=["\'#?])', r'\1', t2)
        t2 = t2.replace("+'.html", "+'")                     # links built in scripts: 'modeli/'+id+'.html'
        if t2 != t:
            open(f, 'w', encoding='utf-8').write(t2)

# ------------------------------------------------------------------ brand logos as images
# Logos were drawn as CSS masks filled with a background colour. Browsers with their own "dark mode for websites"
# (Samsung Internet) darken background colours, so logos turned dark on dark tiles. An <img> is left alone by them;
# CSS filters colour it dark (light theme) or white (dark theme).
import glob as _glob
_lg = re.compile(r'<span class="blogo([^"]*)" aria-hidden="true" style="--l:url\(([^)]+)\)"></span>')
_lgq = re.compile(r'<span class=\\"blogo([^"\\]*)\\" aria-hidden=\\"true\\" style=\\"--l:url\(([^)]+)\)\\"></span>')
for _f in _glob.glob(f'{OUT}/**/*.html', recursive=True):
    _h = open(_f, encoding='utf-8').read()
    _h2 = _lg.sub(lambda m: f'<span class="blogo{m.group(1)} has-img" aria-hidden="true"><img src="{m.group(2)}" alt="" decoding="async"></span>', _h)
    _h2 = _lgq.sub(lambda m: f'<span class=\\"blogo{m.group(1)} has-img\\" aria-hidden=\\"true\\"><img src=\\"{m.group(2)}\\" alt=\\"\\" decoding=\\"async\\"></span>', _h2)
    if _h2 != _h:
        open(_f, 'w', encoding='utf-8').write(_h2)

# NOINDEX = True: mark every page noindex in the HTML itself (works on any host)
if NOINDEX:
    import glob
    for f in glob.glob(f'{OUT}/**/*.html', recursive=True):
        h = open(f, encoding='utf-8').read()
        if '<meta name="robots"' not in h:
            h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
            open(f, 'w', encoding='utf-8').write(h)
