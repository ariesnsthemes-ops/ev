#!/usr/bin/env python3
"""Monthly price check for the model pages (evomobil.rs).

Reads the "from" price of every electric model from the importer's site AND from every dealer site listed for the
brand in src/data/brand_content.json, cross-checks them and writes src/data/prices.json.
Cross-check (decide()): importer + at least one dealer agree -> ok; importer alone (no dealer price) -> ok;
importer and dealers disagree -> review, not applied; no importer price but 2+ dealers agree -> ok;
one dealer only -> review, not applied. "Agree" = within 100 EUR or 0.5 %.
Report: scripts/prices-report.md (pull request), .html and .pdf (printable table, workflow artifact).
The model page shows the price only in a small footnote with the check date (see src/pages/modeli/[id].astro).
Run by .github/workflows/cene-automobila.yml on the first Wednesday of the month; the run opens a pull request
with a report, so every change can be checked before it goes live.

Per model, in src/data/prices.json -> models:
  url        the importer page to read: model page, price-list page or PDF. Empty = the script looks for the model
             on the brand's site (_brand_sites), saves the page it found and marks the model "review".
  dealer_urls {dealer host: page} found the same way on the dealer sites; fix or delete by hand if wrong.
  match      the model name as the importer writes it (used to find the right price on pages with several models)
  lock       optional: {"price_eur": 26890, "since": "2026-11-27", "note": "..."} = price set by hand. The script still
             reads the sources and reports what they say, but never changes the price; a difference is "review".
             Delete "lock" to let the script take over again.
  pdf_label  optional: url is a page with many identical price-list buttons; take the one under the card titled
             exactly this (e.g. "NOVI Ë-C3 AIRCROSS"; "novi" is ignored). Citroën: alati/preuzmite-cenovnik.html
  pdf_match  optional: like pdf_label, but by words in the PDF address / button text / card heading (e.g. "308",
             "Astra", "EV2"); the link must be a price list (cenovnik). Peugeot, Opel, Kia.
  multi      optional: true = url is a list of many models (VW, Audi, Cupra, Volvo, Porsche finder): the first price
             after each place the model name (match) appears, the lowest of those
  link_word  optional: which links to follow with pdf_label / pdf_match (default: cenovnik|cene|price);
             e.g. "konfigurator" (Mazda), "katalozi" (Ford: list -> model page -> PDF price list, followed automatically)
  extra_sources optional: [{"label": "volvocentar.rs", "url": "...", "match": "EX30"}] more pages to compare with
  source_override optional: "dileri" when url is a dealer's page, not the importer's (footnote names it that way)
  skip       optional: true or a reason, e.g. "nema saglasnosti" = not checked, no price shown
  row_anchor optional: read only the price-list rows that start with this text (e.g. "ELEKTRIČNI MOTOR"), so prices of
             the petrol / hybrid tables in the same PDF are never taken. With column: the Nth price in that row.
  column     optional: in a price list with several price columns, which price in the model's row to take
             (Renault: 2 = "cena sa PDV-om"; the 1st is without VAT)
  price_eur  lowest "from" price in EUR
  checked    day of the last successful check (shown on the site as "Cena proverena")
  changed    day the price last changed (used as lastmod in the sitemap)
  source     where the shown price came from: uvoznik | dileri (the footnote names it); a locked price names none
  status     ok | review | not-found | blocked | no-url | new
             review = a model page found by the script (price applied, url saved: check it in the pull request)
                      or a change above MAX_CHANGE (NOT applied, old price stays)

Rules that keep a wrong number off the site:
  - a price outside MIN_EUR..MAX_EUR is ignored (it is a fee, a discount or a parsing error, not a car price)
  - a change larger than MAX_CHANGE (share of the old price) is NOT applied: status "review", old price stays
  - nothing found: old price and old check date stay; the site hides the footnote once the date is 120 days old
  - prices in RSD only are reported, never converted

Usage:
  python3 scripts/update_prices.py                      check every model
  python3 scripts/update_prices.py --only byd-seal,mg-mgs5-ev
  python3 scripts/update_prices.py --brand byd
  python3 scripts/update_prices.py --file page.html --id byd-seal   parse a saved page (testing), writes nothing
  python3 scripts/update_prices.py --dry-run            check, print the report, write nothing
  python3 scripts/update_prices.py --no-dealers         importer sites only

Needs: pip install playwright pypdf && python3 -m playwright install chromium
(without Playwright the script falls back to plain HTTP, which some sites block).
"""
import argparse, datetime as dt, html as htmllib, io, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request, urllib.robotparser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'src', 'data', 'prices.json')
REPORT = os.path.join(ROOT, 'scripts', 'prices-report.md')
UA = 'Mozilla/5.0 (compatible; evomobil-cene/1.0; +https://www.evomobil.rs; office@evomobil.rs)'
MIN_EUR, MAX_EUR = 8000, 400000
MAX_CHANGE = 0.15          # 15 %
WINDOW = 600               # characters after a model name in which its price is looked for
DELAY = 2.0                # seconds between requests to the same site
TODAY = dt.date.today().isoformat()
SECTION_STOP = re.compile(r'(?<![a-z])(plug in|hybrid|hibrid[a-z]*|benzin[a-z]*|dizel|diesel|phev|mhev)(?![a-z])')   # on flat() text
CARD_END = re.compile(r'saznajte vi[sš]e|vi[sš]e informacija|konfigur|prika[zž]i detalje|zatra[zž]i|[zž]elim ponudu|test vo[zž]nj|sve varijante', re.I)
OTHERS = []                # names of the other models of the brand being checked (set per model in main)

# ---------------------------------------------------------------- fetching

class Fetcher:
    """Playwright (real Chromium, renders JavaScript) when installed, else urllib. One page at a time."""

    def __init__(self):
        self.pw = self.browser = None
        self.last = {}
        self.robots = {}
        self.cache = {}
        self.errors = {}     # address -> why it could not be read (diagnostics)
        self.trail = []      # addresses read for the model being checked (diagnostics)
        self.evidence = {}
        self.price_url = {}  # listing page -> the linked PDF the price actually came from   # url -> (ext, bytes): JPEG screenshot of an HTML page or the PDF file itself
        try:
            from playwright.sync_api import sync_playwright
            self.pw = sync_playwright().start()
            self.browser = self.pw.chromium.launch()
            self.ctx = self.browser.new_context(user_agent=UA.replace('compatible; ', ''), locale='sr-RS')
        except Exception as e:  # noqa: BLE001
            print(f'(Playwright nije dostupan: {e.__class__.__name__}; koristi se običan HTTP)')

    def close(self):
        if self.browser: self.browser.close()
        if self.pw: self.pw.stop()

    def allowed(self, url):
        """robots.txt check. The file is fetched with the browser (or our UA); a missing or refused robots.txt
        (4xx, network error) means no rules, as search engines treat it. Python's own reader would treat a
        refused robots.txt (403) as "everything forbidden", which is wrong."""
        host = urllib.parse.urlsplit(url)
        base = f'{host.scheme}://{host.netloc}'
        if base not in self.robots:
            rp = None
            try:
                if self.browser:
                    r = self.ctx.request.get(base + '/robots.txt', timeout=20000)
                    body = r.text() if r.ok else None
                else:
                    body = self.raw(base + '/robots.txt').decode('utf-8', 'replace')
                if body and 'disallow' in body.lower():
                    rp = urllib.robotparser.RobotFileParser()
                    rp.parse(body.splitlines())
            except Exception:  # noqa: BLE001
                rp = None
            self.robots[base] = rp
        rp = self.robots[base]
        return True if rp is None else rp.can_fetch('evomobil-cene', url)

    def wait(self, url):
        host = urllib.parse.urlsplit(url).netloc
        gap = time.time() - self.last.get(host, 0)
        if gap < DELAY: time.sleep(DELAY - gap)
        self.last[host] = time.time()

    def get(self, url):
        """-> (kind, text, links)  kind: 'html' | 'pdf'; links: [(href, link text)] for html. Each address is read once per run."""
        self.trail.append(url)
        if url not in self.cache:
            try:
                self.cache[url] = self._get(url)
            except Exception as ex:  # noqa: BLE001
                self.errors[url] = err(ex)
                raise
        return self.cache[url]

    def _get(self, url):
        self.wait(url)
        if url.lower().split('?')[0].endswith('.pdf'):
            if self.browser:
                body, why = None, ''
                for headers in ({}, {'Accept': 'application/pdf,*/*;q=0.8', 'Referer': '{0.scheme}://{0.netloc}/'.format(urllib.parse.urlsplit(url))}):
                    try:
                        r = self.ctx.request.get(url, timeout=60000, headers=headers)
                        if r.ok and r.body()[:5] == b'%PDF-': body = r.body(); break
                        why = f'HTTP {r.status}' if not r.ok else 'odgovor nije PDF'
                    except Exception as ex:  # noqa: BLE001
                        why = err(ex)
                if body is None:
                    try: body = self.raw(url)
                    except Exception as ex: raise RuntimeError(f'{why}; običan HTTP: {err(ex)}')  # noqa: BLE001
                self.evidence[url] = ('pdf', body)
                return 'pdf', pdf_text(body), []
            raw = self.raw(url)
            self.evidence[url] = ('pdf', raw)
            return 'pdf', pdf_text(raw), []
        if self.browser:
            page = self.ctx.new_page()
            try:
                resp = page.goto(url, wait_until='domcontentloaded', timeout=60000)
                ctype = (resp.headers.get('content-type', '') if resp else '')
                if 'pdf' in ctype:
                    body = resp.body()
                    self.evidence[url] = ('pdf', body)
                    return 'pdf', pdf_text(body), []
                # JS checks ("please wait…"), redirects and prices loaded later: wait, then read; retry if the page moves
                text = ''
                for _ in range(4):
                    try:
                        page.wait_for_load_state('networkidle', timeout=15000)
                    except Exception:  # noqa: BLE001  pages that never go idle (chat widgets, trackers)
                        pass
                    try:
                        text = page.inner_text('body')
                    except Exception:  # noqa: BLE001  "page is navigating": try again
                        page.wait_for_timeout(2500)
                        continue
                    if 'request is being verified' not in text: break
                    page.wait_for_timeout(3000)
                # [href, link text, heading of the card the link sits in] - price-list pages often have many identical
                # "Skinite cenovnike" buttons, told apart only by the model name above them
                links = page.eval_on_selector_all('a[href]', '''els => els.map(a => {
                    let n = a, head = '';
                    for (let i = 0; i < 6 && n && !head; i++) {
                        n = n.parentElement;
                        if (!n) break;
                        const h = n.querySelector('h1,h2,h3,h4,h5,h6,[class*="title"],[class*="name"]');
                        if (h && !h.contains(a)) head = (h.innerText || '').trim();
                    }
                    return [a.href, (a.innerText || a.title || '').trim(), head.slice(0, 120)];
                })''')
                try:   # evidence: the page as it looked, with the date and address stamped on top
                    page.evaluate('''([u, d]) => { const b = document.createElement('div');
                        b.textContent = 'evomobil.rs provera cena · ' + d + ' · ' + u;
                        b.style.cssText = 'position:relative;z-index:2147483647;background:#ffeb3b;color:#000;font:14px/1.4 sans-serif;padding:6px 10px';
                        document.body.prepend(b); }''', [url, dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')])
                    self.evidence[url] = ('jpg', page.screenshot(full_page=True, type='jpeg', quality=55, timeout=30000))
                except Exception:  # noqa: BLE001
                    pass
                return 'html', text, links
            finally:
                page.close()
        raw = self.raw(url)
        if raw[:5] == b'%PDF-': return 'pdf', pdf_text(raw), []
        page = raw.decode('utf-8', 'replace')
        links = [(urllib.parse.urljoin(url, h), re.sub(r'<[^>]+>', ' ', t).strip(), '')
                 for h, t in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', page, re.S)]
        return 'html', html_text(page), links

    def plain(self, url):
        """Text of a file (sitemap, robots) without rendering; None on any error."""
        try:
            if self.browser:
                r = self.ctx.request.get(url, timeout=30000)
                return r.text() if r.ok else None
            return self.raw(url).decode('utf-8', 'replace')
        except Exception:  # noqa: BLE001
            return None

    def sitemap_urls(self, site, limit=25):
        """All page addresses in the site's sitemap(s) (sitemap.xml, sitemap_index.xml, Sitemap: lines in robots.txt)."""
        base = '{0.scheme}://{0.netloc}'.format(urllib.parse.urlsplit(site))
        key = 'sitemap:' + base
        if key in self.cache: return self.cache[key]
        todo = [base + '/sitemap.xml', base + '/sitemap_index.xml']
        robots = self.plain(base + '/robots.txt') or ''
        todo += re.findall(r'(?im)^\s*sitemap:\s*(\S+)', robots)
        seen, pages = set(), []
        while todo and len(seen) < limit:
            u = todo.pop(0)
            if u in seen: continue
            seen.add(u)
            body = self.plain(u)
            if not body or '<loc' not in body: continue
            for loc in re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', body):
                loc = htmllib.unescape(loc)
                (todo if re.search(r'\.xml(\.gz)?($|\?)', loc) else pages).append(loc)
        self.cache[key] = pages
        return pages

    def raw(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'sr,en;q=0.8'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()


def html_text(page):
    page = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', page)
    page = re.sub(r'(?i)<br\s*/?>|</(p|div|li|tr|td|h\d)>', '\n', page)
    return htmllib.unescape(re.sub(r'<[^>]+>', ' ', page))


def pdf_text(raw):
    from pypdf import PdfReader
    return '\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(raw)).pages)

# ---------------------------------------------------------------- reading prices

def norm(s):
    s = s.replace('+', ' plus ')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

NUM = r'(\d{1,3}(?:[.\s  ,]\d{3})+|\d{4,6})(?:[.,]\d{1,2})?(?![\d])'
EUR_AFTER = re.compile(NUM + r'(?:\s*,\s*[-–])?\s*(?:€|eur\b|evra\b|euro\b)', re.I)   # also "29.990,- €"
EUR_BEFORE = re.compile(r'(?:€|eur\b)\s*' + NUM, re.I)
RSD = re.compile(NUM + r'\s*(?:rsd\b|din\b|dinara\b)', re.I)
HINT = re.compile(r'(?:\bod\b|cena|početn|pocetn|već od|vec od|from)\W{0,12}$', re.I)
NOT_PRICE = re.compile(r'(?:subvencij|ušted|usted|popust|bonus|garanc|rata|mesečn|mesecn|učešć|ucesc|leasing|lizing)\W{0,30}$', re.I)


def to_int(s):
    return int(re.sub(r'\D', '', s))


BARE = re.compile(r'(?<![\d.,])(\d{1,3}(?:\.\d{3})+)(?:,\d{2})?(?![\d.,]?\d)')   # "45.990" only; "97 323" is 97 KS + 323 km


def candidates(text, bare=False):
    """Prices with € / EUR. bare=True (price lists whose header says the currency once, e.g. Hyundai):
    also "45.990" without a currency sign."""
    out = []
    for rx in ((EUR_AFTER, EUR_BEFORE, BARE) if bare else (EUR_AFTER, EUR_BEFORE)):
        for m in rx.finditer(text):
            v = to_int(m.group(1))
            if not MIN_EUR <= v <= MAX_EUR: continue
            before = text[max(0, m.start() - 40):m.start()]
            if NOT_PRICE.search(before): continue
            out.append((m.start(1), v, bool(HINT.search(before))))   # position of the number: "€ 34.990 €" counts once
    seen, uniq = set(), []
    for c in sorted(out):
        if c[0] not in seen: seen.add(c[0]); uniq.append(c)
    return uniq


def find_price(text, match, multi, longer=(), column=None, anchor=None):
    """Lowest plausible EUR price.
    Page about one model: the lowest price, preferring prices after "od"/"cena".
    Page with several models (price list, PDF, brand page): for each place the model name appears, the first price
    after it (within WINDOW characters); then the lowest of those. Names of longer sibling models are skipped
    ("ë-C3" does not match "ë-C3 Aircross")."""
    if anchor:
        return find_in_rows(text, anchor, column or 1)
    cands = candidates(text)
    if not cands and multi and re.search(r'€|\beur\b|evr', text, re.I) and not RSD.search(text):
        cands = candidates(text, bare=True)   # price list with the currency only in the header
    if not cands:
        rsd = [to_int(m.group(1)) for m in RSD.finditer(text) if to_int(m.group(1)) > 500000]
        return None, ('samo RSD: ' + ', '.join(f'{v:,}'.replace(',', '.') for v in sorted(rsd)[:3])) if rsd else 'nema cene u EUR'
    spots = name_spots(text, match, longer)
    if multi or (spots and len({v for _, v, _ in cands}) > 1 and len(spots) < len(cands)):
        firsts = []
        other_spots = [o for name in OTHERS for o in name_spots(text, name)]
        for s in spots:
            after = [c for c in cands if 0 <= c[0] - s <= WINDOW]
            if after and any(s < o < after[0][0] for o in other_spots if o != s):
                continue   # another model's name sits between this name and the price (menu, filter chips)
            if after and CARD_END.search(text[s:after[0][0]]):
                continue   # the card ends (its buttons) before the price: that price belongs to the next card
            if column:   # price lists with several price columns (e.g. Renault: without VAT, with VAT, bonus…): the Nth price in the row
                eol = text.find('\n', s)
                row = [c for c in after if eol < 0 or c[0] < eol] or after
                if len(row) >= column: firsts.append(row[column - 1][1])
            elif after: firsts.append(after[0][1])
        if firsts: return min(firsts), (f'{column}. cena u redu modela' if column else 'prva cena posle naziva modela')
        if multi: return None, f'model "{match}" nije pronađen pored cene'
    hinted = [c for c in cands if c[2]]
    return min(v for _, v, _ in (hinted or cands)), ('uz "od/cena"' if hinted else 'najniža cena na strani')


def find_in_rows(text, anchor, column):
    """Price lists with one table per powertrain (Citroën: "ELEKTRIČNI MOTOR" rows): after every occurrence of the
    anchor, the column-th price before the next occurrence; the lowest of those. Hybrid / petrol rows are never read."""
    t = flat(text)
    rx = re.compile(r'\s+'.join(map(re.escape, flat(anchor).split())) + r'(?![a-z0-9])')   # "automatskiElektro" counts
    spots = [m.start() for m in rx.finditer(t)]
    if not spots: return None, f'tabela "{anchor}" nije pronađena'
    stops = [m.start() for m in SECTION_STOP.finditer(t)]
    picks = []
    for bare in (False, True):
        cands = candidates(text, bare=bare)
        for i, s0 in enumerate(spots):
            end = spots[i + 1] if i + 1 < len(spots) else s0 + WINDOW
            end = min([end] + [x for x in stops if x > s0 + len(anchor)])   # the hybrid / petrol table starts here
            row = [v for pos, v, _ in cands if s0 <= pos < min(end, s0 + WINDOW)]
            if column == 'min' and row: picks.append(min(row))
            elif column != 'min' and len(row) >= column: picks.append(row[column - 1])
        if picks: break
    if not picks: return None, f'nema cena u redovima "{anchor}"'
    which = 'najniža cena' if column == 'min' else f'{column}. cena'
    return min(picks), f'{which} u redovima "{anchor}" ({len(picks)} redova)'


def flat(s):
    """lower case, no accents, punctuation -> space except "+" (C-HR+ is not C-HR); SAME length as the input."""
    out = []
    for ch in s.lower():
        a = unicodedata.normalize('NFKD', ch).encode('ascii', 'ignore').decode()[:1] or ' '
        out.append(a if a.isalnum() or a == '+' else ' ')
    return ''.join(out)


def name_spots(text, match, longer=()):
    t = flat(text)
    rx = lambda m: re.compile(r'(?<![a-z0-9])' + r'\s+'.join(map(re.escape, flat(m).split())) + r'(?![a-z0-9+])')
    spots = [m.start() for m in rx(match).finditer(t)]
    skip = {m.start() for name in longer for m in rx(name).finditer(t)}
    return [s for s in spots if s not in skip]

# ---------------------------------------------------------------- finding a model page

def has_all(hay, key):
    return all(re.search(r'\b' + re.escape(k) + r'\b', hay) for k in key)


def score_link(href, label, key, prefer, siblings=()):
    hay = norm(href + ' ' + label)
    if not has_all(hay, key): return None
    # a page of a longer sibling model ("Atto 2 DM-i", "bZ4X Touring", "e-C4 X", "Enyaq Coupe") is not this model
    hay_url, hay_label = norm(href), norm(label)
    for sib in siblings:
        sk = norm(sib).split()
        if has_all(hay_url, sk) or (label and has_all(hay_label, sk)): return None
        compact = ''.join(sk)                       # "ec4x", "bz4xtouring" written together in a URL
        if compact in hay_url.replace(' ', ''): return None
    score = len(key)
    score += 2 if any(w in hay for w in ('model', 'modeli', 'vozila', 'new cars', 'automobili')) else 0
    score += 1 if prefer and prefer in href else 0
    score -= href.count('?') + href.count('/') * 0.1
    score -= 3 if any(w in hay for w in ('test', 'konfigur', 'servis', 'kontakt', 'vest', 'news', 'blog', 'akcij', 'oprema', 'dodatn')) else 0
    return score


def propose_url(f, site, match, siblings=()):
    """Model page on a brand/dealer site: links on the home page first, then the sitemap."""
    key = norm(match).split()
    host = urllib.parse.urlsplit(site).netloc.replace('www.', '')
    prefer = urllib.parse.urlsplit(site).path.rstrip('/')   # e.g. /rs on leapmotor.net/rs
    links = []
    try:
        _, _, links = f.get(site)
    except Exception:  # noqa: BLE001
        pass
    cands = [(score_link(h, t, key, prefer, siblings), h) for h, t, *_ in links if host in h]
    cands += [(score_link(u, '', key, prefer, siblings), u) for u in f.sitemap_urls(site) if host in u and (not prefer or prefer in u)]
    cands = [c for c in cands if c[0] is not None]
    best = max(cands)[1] if cands else None
    pricelist = next((h for h, t, *_ in links if host in h and re.search(r'cenovnik|cene|price', norm(h + ' ' + t))), None)
    return best, pricelist

# ---------------------------------------------------------------- sources: importer + dealers

def err(ex):
    return f'greška ({ex.__class__.__name__}: {(str(ex).splitlines() or [""])[0][:80]})'


def read_page(f, url, match, longer, column=None, anchor=None, pdf_label=None, pdf_match=None, link_word=None, force_multi=False):
    """-> (state, price, how)  state: ok | not-found | blocked
    An HTML page without a price is searched for linked PDF price lists that name the model (or are called
    cenovnik / pricelist), so url can point at a stable "cenovnici" page while the PDF file names change."""
    if not f.allowed(url): return 'blocked', None, 'robots.txt ne dozvoljava'
    try:
        kind, text, links = f.get(url)
    except Exception as ex:  # noqa: BLE001
        return 'not-found', None, err(ex)
    if 'request is being verified' in text or len(text.strip()) < 200:
        return 'blocked', None, 'sajt blokira automatsku proveru'
    multi = force_multi or kind == 'pdf' or bool(re.search(r'cenovnik|cenovnici|price', url, re.I))
    price, how = (None, 'cenovnik se bira po naslovu') if (pdf_label or pdf_match) and kind == 'html' else find_price(text, match, multi, longer, column, anchor)
    if price or kind != 'html':
        return ('ok' if price else 'not-found'), price, f'{kind}, {how}'
    key = norm(match).split()
    word = link_word or r'cenovnik|cenovnici|cene|price|pricelist'
    pdfs = []
    for h, t, *ctx in links:
        if h in pdfs: continue
        if pdf_match:   # e.g. "308": in the PDF address, the button text or the card heading, and it must be a price list
            hay = norm(urllib.parse.unquote(h) + ' ' + t + ' ' + (ctx[0] if ctx else ''))
            if has_all(hay, norm(pdf_match).split()) and re.search(word, hay): pdfs.append(h)
            continue
        if pdf_label:   # the card heading must be exactly this model ("NOVI Ë-C3 AIRCROSS"), not just contain it
            head = ' '.join(w for w in flat(ctx[0] if ctx else '').split() if w != 'novi')
            want = ' '.join(w for w in flat(pdf_label).split() if w != 'novi')
            if head == want and re.search(word, norm(urllib.parse.unquote(h) + ' ' + t)): pdfs.append(h)   # not "katalog"
            continue
        if '.pdf' not in h.lower(): continue
        hay = norm(h + ' ' + t)
        if has_all(hay, key) or (len(key) > 1 and has_all(hay.replace(' ', ''), [''.join(key)])):
            pdfs.append(h)
    need = norm(pdf_match).split() if pdf_match else None
    for pdf in pdfs[:5]:
        got = follow(f, url, pdf, match, longer, column, anchor, need=need)
        if got: return got
    if pdf_label and not pdfs: return 'not-found', None, f'nema dugmeta za cenovnik ispod naslova "{pdf_label}"'
    if pdf_match and not pdfs: return 'not-found', None, f'nema cenovnika sa "{pdf_match}" na stranici'
    return 'not-found', None, f'{kind}, {how}' + (f'; pregledano linkova: {len(pdfs[:5])}' if pdfs else '')


def follow(f, page_url, link, match, longer, column, anchor, depth=0, need=None):
    """Read a followed link: a PDF price list, or a page (configurator, "katalozi i cenovnici") that shows the price
    itself or links one more PDF price list (Ford: list -> model page -> "Puma Bev Cenovnik" PDF)."""
    try:
        kind, ptext, plinks = f.get(link)
    except Exception:  # noqa: BLE001
        return None
    if need and kind == 'pdf' and not has_all(norm(ptext), need):
        return None   # a price list of another model (it never names this one)
    p2, how2 = find_price(ptext, match, True, longer, column, anchor)
    if p2:
        f.price_url[page_url] = link
        name = urllib.parse.unquote(link.rstrip('/').rsplit('/', 1)[-1])[:60]
        return 'ok', p2, f'{kind} sa stranice ({name}), {how2}'
    if kind == 'html' and depth == 0:
        for h, t, *_ in plinks:
            if re.search(r'cenovnik|cenovnici|pricelist|price', norm(urllib.parse.unquote(h) + ' ' + t)) and h != link:
                got = follow(f, page_url, h, match, longer, column, anchor, 1, need)
                if got: return got
    return None


def source(f, label, url, site, match, longer, column=None, anchor=None, pdf_label=None, pdf_match=None, link_word=None, force_multi=False):
    """One source (importer or a dealer). url empty -> look for the model on site. Never raises."""
    out = {'src': label, 'url': url, 'proposed': False, 'state': 'no-url', 'price': None, 'how': ''}
    try:
        if not url:
            if not site:
                out['how'] = 'nema adrese sajta'
                return out
            page, pricelist = propose_url(f, site, match, longer)
            url = page or pricelist
            if not url:
                out['how'] = 'model nije pronađen na sajtu'
                return out
            out.update(url=url, proposed=True)
        out['state'], out['price'], out['how'] = read_page(f, url, match, longer, column, anchor, pdf_label, pdf_match, link_word, force_multi)
    except Exception as ex:  # noqa: BLE001  one bad site never stops the run
        out.update(state='not-found', how=err(ex))
    return out


def host_of(u):
    return urllib.parse.urlsplit(u if '://' in u else 'https://' + u).netloc.replace('www.', '')


def dealer_sites(importer_site):
    """Dealer websites per brand from brand_content.json, without the importer's own site."""
    content = json.load(open(os.path.join(ROOT, 'src', 'data', 'brand_content.json'), encoding='utf-8'))
    out = {}
    for slug, c in content.items():
        if slug.startswith('_'): continue
        own = host_of(importer_site.get(slug) or '')
        seen = {}
        for d in c.get('dealers', []):
            w = d.get('website')
            if not w: continue
            h = host_of(w)
            if h and h != own and h not in seen: seen[h] = w if '://' in w else 'https://' + w
        out[slug] = seen
    return out


EVIDENCE = os.path.join(ROOT, 'scripts', 'dokazi')


def save_evidence(f, mid, srcs):
    """For every source that gave a price: the screenshot / PDF copy in scripts/dokazi/<date>/, file name in the source."""
    day = os.path.join(EVIDENCE, TODAY)
    for s in srcs:
        if not s['price'] or not s['url']: continue
        url = f.price_url.get(s['url'], s['url'])
        ev = f.evidence.get(url)
        if not ev: continue
        os.makedirs(day, exist_ok=True)
        name = f'{mid}__{re.sub(r"[^a-z0-9.-]+", "-", s["src"].lower())}.{ev[0]}'
        with open(os.path.join(day, name), 'wb') as fh: fh.write(ev[1])
        s['evidence'] = f'{TODAY}/{name}'


def save_debug(f, mid, srcs):
    """No price found: keep what the script saw (page text and links) in scripts/dokazi/<date>/debug/<model>.txt,
    so the settings (url, pdf_match, row_anchor…) can be fixed from the evidence branch without guessing."""
    day = os.path.join(EVIDENCE, TODAY, 'debug')
    os.makedirs(day, exist_ok=True)
    out = [f'# {mid}  {TODAY}', '']
    for s in srcs: out.append(f'izvor {s["src"]}: {s["url"]} -> {s["state"]}: {s["how"]}')
    for u in dict.fromkeys(f.trail):
        got = f.cache.get(u)
        out += ['', '=' * 100, u]
        if not got: out.append('(nije učitano: ' + f.errors.get(u, '?') + ')'); continue
        kind, text, links = got
        out += [f'[{kind}, {len(text)} znakova]', text[:12000]]
        if links:
            out += ['', '--- linkovi (href | tekst | naslov kartice) ---']
            out += [' | '.join(str(x).replace('\n', ' ')[:120] for x in l) for l in links[:400]]
    with open(os.path.join(day, mid + '.txt'), 'w', encoding='utf-8') as fh: fh.write('\n'.join(out))


def archive(urls):
    """Ask the Internet Archive (Wayback Machine) to snapshot each page: an independent, dated copy.
    -> {url: archived copy url}. Slow on purpose (one request per ~10 s); failures are only reported."""
    out = {}
    for u in urls:
        try:
            req = urllib.request.Request('https://web.archive.org/save/' + u, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                loc = r.headers.get('Content-Location') or ''
                out[u] = ('https://web.archive.org' + loc) if loc.startswith('/web/') else r.geturl()
        except Exception as ex:  # noqa: BLE001
            out[u] = 'nije arhivirano: ' + err(ex)
        time.sleep(10)
    return out


def same(a, b):
    return abs(a - b) <= max(100, 0.005 * max(a, b))


def decide(srcs, old):
    """Cross-check the sources. -> (price, status, apply, agreement text)
    importer + at least one dealer agree        -> ok
    importer only (no dealer price to compare)  -> ok
    importer and all dealers disagree           -> review, not applied
    no importer, >= 2 dealers agree             -> ok
    no importer, one dealer                     -> review, not applied"""
    imp = next((s['price'] for s in srcs if s['src'] == 'uvoznik' and s['price']), None)
    dl = [s['price'] for s in srcs if s['src'] != 'uvoznik' and s['price']]
    if imp:
        if not dl: return imp, 'ok', True, 'samo uvoznik'
        agree = [d for d in dl if same(d, imp)]
        if agree: return imp, 'ok', True, f'uvoznik + {len(agree)}/{len(dl)} dilera se slažu'
        return imp, 'review', False, f'uvoznik i dileri se NE slažu ({len(dl)} dilera)'
    if not dl: return None, None, False, ''
    best = max(([d2 for d2 in dl if same(d, d2)] for d in dl), key=len)
    if len(best) >= 2:
        return min(best), 'ok', True, f'{len(best)}/{len(dl)} dilera se slažu (uvoznik bez cene)'
    return min(dl), 'review', False, 'samo jedan diler, nema potvrde'


def all_names():
    """Every model name per brand (also hybrids and vans), so that "Seal" is never read from a "Seal U DM-i" line."""
    brands = {b['slug']: b for b in json.load(open(os.path.join(ROOT, 'src', 'data', 'brands.json'), encoding='utf-8'))['brands']}
    content = json.load(open(os.path.join(ROOT, 'src', 'data', 'brand_content.json'), encoding='utf-8'))
    out = {}
    for slug, c in content.items():
        if slug.startswith('_'): continue
        bn = c['name'].lower()
        out[slug] = [m['name'][len(bn) + 1:] if m['name'].lower().startswith(bn + ' ') else m['name'] for m in brands[c['data_slug']]['models']]
    return out

# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only'); ap.add_argument('--brand'); ap.add_argument('--file'); ap.add_argument('--id')
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--multi', action='store_true')
    ap.add_argument('--no-dealers', action='store_true', help='only the importer sites')
    a = ap.parse_args()
    data = json.load(open(DATA, encoding='utf-8'))
    models, sites = data['models'], data['_brand_sites']
    names = all_names()
    dealers = dealer_sites(sites)

    if a.file:  # test mode: parse a saved page or PDF
        raw = open(a.file, 'rb').read()
        text = pdf_text(raw) if raw[:5] == b'%PDF-' else html_text(raw.decode('utf-8', 'replace'))
        e = models[a.id]
        print(e['name'], '->', find_price(text, e['match'], multi=raw[:5] == b'%PDF-' or a.multi))
        return

    ids = [i for i in models if (not a.only or i in a.only.split(',')) and (not a.brand or i.startswith(a.brand + '-'))]
    f = Fetcher()
    rows = []
    try:
        for mid in ids:
            e = models[mid]
            old = e.get('price_eur')
            brand = next(b for b in sorted(sites, key=len, reverse=True) if mid.startswith(b + '-'))
            longer = [n for n in names.get(brand, ()) if flat(n).startswith(flat(e['match']) + ' ')
                      and brand + '-' + '-'.join(flat(n).split()) != mid]   # not this model's own full name

            f.trail = []
            OTHERS[:] = [n for n in names.get(brand, ()) if flat(n) != flat(e['match']) and not flat(n).startswith(flat(e['match']) + ' ')
                         and not flat(e['match']).startswith(flat(n) + ' ')]
            if e.get('skip'):   # brand/model left out on purpose (no consent yet, no public price)
                e['status'] = 'skip'
                rows.append({'id': mid, 'name': e['name'], 'old': e.get('price_eur'), 'new': None, 'status': 'skip', 'applied': False,
                             'agreement': '', 'notes': e.get('skip') if isinstance(e.get('skip'), str) else 'preskočeno', 'sources': []})
                continue
            srcs = [source(f, 'uvoznik', e.get('url'), sites.get(brand), e['match'], longer, e.get('column'), e.get('row_anchor'),
                           e.get('pdf_label'), e.get('pdf_match'), e.get('link_word'), e.get('multi', False))]
            for x in e.get('extra_sources', []):   # more pages to compare with (e.g. a dealer's stock list)
                srcs.append(source(f, x['label'], x['url'], None, x.get('match', e['match']), longer, x.get('column'),
                                   x.get('row_anchor'), x.get('pdf_label'), x.get('pdf_match'), x.get('link_word'), x.get('multi', True)))
            if not a.no_dealers:
                known = e.setdefault('dealer_urls', {})
                for host, site in dealers.get(brand, {}).items():
                    srcs.append(source(f, host, known.get(host), site, e['match'], longer))
            for s in srcs:   # remember the pages found, so next month reads them directly (fix by hand if wrong)
                if s['proposed'] and s['price']:
                    if s['src'] == 'uvoznik': e['url'] = s['url']
                    else: e['dealer_urls'][s['src']] = s['url']

            save_evidence(f, mid, srcs)
            price, status, apply, agreement = decide(srcs, old)
            if price is None or e.get('lock'):
                try: save_debug(f, mid, srcs)
                except Exception as ex: print('debug nije snimljen:', err(ex))  # noqa: BLE001
            notes = []
            lock = e.get('lock')
            if lock:   # price set by hand: report what the sources say, never change it
                lp = lock['price_eur']
                found = price
                notes.append(f'RUČNO ZAKLJUČANO {eur(lp)} (od {lock.get("since", "?")})'
                             + (f'; izvori kažu {eur(found)}' if found and not same(found, lp) else '; izvori se slažu' if found else ''))
                status = 'review' if found and not same(found, lp) else 'ok'
                e.update(price_eur=lp, checked=TODAY)
                e['note'] = '; '.join(n for n in [agreement] + notes if n)
                e['status'] = status
                rows.append({'id': mid, 'name': e['name'], 'old': old, 'new': lp, 'status': status, 'applied': False,
                             'agreement': agreement, 'notes': '; '.join(notes), 'sources': srcs})
                print(f'{mid:32} {status:10} {old or "-":>8} -> {lp:>8}  {e["note"]}')
                continue
            if price is None:
                imp = srcs[0]
                status = {'blocked': 'blocked', 'no-url': 'no-url'}.get(imp['state'], 'not-found')
                notes.append(imp['how'])
            else:
                if any(s['proposed'] and s['price'] for s in srcs) and status == 'ok':
                    status = 'review'; notes.append('stranica pronađena automatski, proveri link (cena primenjena)')
                if apply and old and abs(price - old) / old > MAX_CHANGE:
                    status, apply = 'review', False
                    notes.append(f'promena {100 * (price - old) / old:+.0f} % (više od {MAX_CHANGE:.0%}), NIJE primenjeno')
            if apply:
                if price != old: e['changed'] = TODAY
                imp = next((x['price'] for x in srcs if x['src'] == 'uvoznik' and x['price']), None)
                e.update(price_eur=price, checked=TODAY,
                         source=e.get('source_override') or ('uvoznik' if imp and same(imp, price) else 'dileri'))
            elif status == 'review' and price is not None:
                notes.append('nije primenjeno, ostaje stara cena' if 'NIJE' not in ' '.join(notes) else '')
            e['status'] = status
            e['note'] = '; '.join(n for n in [agreement] + notes if n)
            rows.append({'id': mid, 'name': e['name'], 'old': old, 'new': price, 'status': status, 'applied': apply,
                         'agreement': agreement, 'notes': '; '.join(n for n in notes if n), 'sources': srcs})
            print(f'{mid:32} {status:10} {old or "-":>8} -> {price or "-":>8}  {e["note"]}')
        if os.environ.get('ARCHIVE', '1') != '0' and not a.dry_run:
            urls = sorted({f.price_url.get(s['url'], s['url']) for r in rows for s in r['sources'] if s['price'] and s['url']})
            print(f'Arhiviranje {len(urls)} stranica u Internet Archive…')
            arch = archive(urls)
            for r in rows:
                for s in r['sources']:
                    if s['price'] and s['url']: s['archive'] = arch.get(f.price_url.get(s['url'], s['url']))
        report(rows, f)
    finally:
        f.close()

    if not a.dry_run:
        with open(DATA, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2); fh.write('\n')

# ---------------------------------------------------------------- report: markdown (pull request), HTML and PDF

STATUS_TXT = {'ok': 'OK', 'review': 'Za proveru', 'not-found': 'Nije pronađeno', 'blocked': 'Blokirano', 'no-url': 'Bez adrese', 'skip': 'Preskočeno'}


def eur(v):
    return f'{v:,} €'.replace(',', '.') if v else '–'


def groups(rows):
    changed = [r for r in rows if r['status'] == 'ok' and r['applied'] and r['new'] != r['old']]
    return [
        ('Promenjene cene (idu na sajt posle odobrenja)', changed),
        ('Za ručnu proveru', [r for r in rows if r['status'] == 'review']),
        ('Nije pronađeno, blokirano ili bez adrese', [r for r in rows if r['status'] in ('not-found', 'blocked', 'no-url')]),
        ('Bez promene', [r for r in rows if r['status'] == 'ok' and r['new'] == r['old']]),
        ('Preskočeno namerno', [r for r in rows if r['status'] == 'skip']),
    ], changed


def report(rows, f=None):
    gs, changed = groups(rows)
    cnt = {k: sum(1 for r in rows if r['status'] == k) for k in STATUS_TXT}
    summary = (f'{cnt["ok"]} OK ({len(changed)} promenjeno) · {cnt["review"]} za proveru · {cnt["not-found"]} nije pronađeno · '
               f'{cnt["blocked"]} blokirano · {cnt["no-url"]} bez adrese')
    run = ''
    if os.environ.get('GITHUB_RUN_ID'):
        run = f'{os.environ["GITHUB_SERVER_URL"]}/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{os.environ["GITHUB_RUN_ID"]}'

    # markdown (pull request body and the Actions summary)
    def proof_md(s):
        bits = []
        if s.get('evidence') and run: bits.append(f'dokaz: `{s["evidence"]}`')
        a = s.get('archive') or ''
        if a.startswith('http'): bits.append(f'[arhiva]({a})')
        return (' (' + ', '.join(bits) + ')') if bits else ''
    src_md = lambda r: '<br>'.join(f'{s["src"]}: ' + (f'[{eur(s["price"])}]({s["url"]}){proof_md(s)}' if s['price'] else
                                   (s['how'] or s['state']) + (f' ([stranica]({s["url"]}))' if s['url'] else '')) for s in r['sources'])
    md = [f'## Provera cena {TODAY}', '', f'**{summary}**', '']
    if run: md += [f'Tabela za štampu (PDF i HTML) i dokazi (screenshotovi, kopije PDF cenovnika): {run} → Artifacts → **izvestaj-cene**. '
                   f'Dokazi se trajno čuvaju i na grani `dokazi-cena`, u folderu `{TODAY}`. „arhiva“ = nezavisna kopija u Internet Archive.', '']
    for title, part in gs:
        if not part: continue
        md += [f'### {title}', '', '| Model | Staro | Novo | Izvori | Slaganje / napomena |', '|---|---:|---:|---|---|']
        md += [f'| {r["name"]} | {eur(r["old"])} | {eur(r["new"])} | {src_md(r)} | {"; ".join(x for x in (r["agreement"], r["notes"]) if x)} |' for r in part]
        md.append('')
    with open(REPORT, 'w', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')

    # HTML table (and PDF from it)
    E = htmllib.escape
    def src_html(r):
        return ''.join(f'<div><b>{E(s["src"])}</b>: ' + (f'<a href="{E(s["url"])}">{eur(s["price"])}</a>'
                                                         + (f' <span class="m">dokaz: {E(s["evidence"])}</span>' if s.get('evidence') else '')
                                                         + (f' <a class="m" href="{E(s["archive"])}">arhiva</a>' if (s.get('archive') or '').startswith('http') else '')
                                                         if s['price'] else f'<span class="m">{E(s["how"] or s["state"])}</span>'
                                                         + (f' <a class="m" href="{E(s["url"])}">stranica</a>' if s['url'] else '')) + '</div>'
                       for s in r['sources'])
    body = []
    for title, part in gs:
        if not part: continue
        body.append(f'<h2>{E(title)} <span class="m">({len(part)})</span></h2><table><thead><tr><th>Model</th><th class="n">Staro</th>'
                    '<th class="n">Novo</th><th>Status</th><th>Izvori (uvoznik, dileri)</th><th>Slaganje / napomena</th><th>OK?</th></tr></thead><tbody>')
        for r in part:
            diff = r['new'] and r['old'] and r['new'] != r['old']
            body.append(f'<tr class="{r["status"]}"><td><b>{E(r["name"])}</b></td><td class="n">{eur(r["old"])}</td>'
                        f'<td class="n{" ch" if diff else ""}">{eur(r["new"])}</td><td>{STATUS_TXT.get(r["status"], r["status"])}</td>'
                        f'<td class="s">{src_html(r)}</td><td>{E("; ".join(x for x in (r["agreement"], r["notes"]) if x))}</td><td class="box">☐</td></tr>')
        body.append('</tbody></table>')
    page = f"""<!DOCTYPE html><html lang="sr"><head><meta charset="utf-8"><title>Provera cena {TODAY}</title><style>
@page{{size:A4 landscape;margin:12mm}}
body{{font:12px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#16202e;margin:24px}}
h1{{font-size:20px;margin:0 0 4px}}h2{{font-size:15px;margin:22px 0 6px}}.m{{color:#5b6b80;font-weight:400}}
table{{border-collapse:collapse;width:100%;page-break-inside:auto}}tr{{page-break-inside:avoid}}
th,td{{border-bottom:1px solid #e0e7e3;padding:5px 6px;text-align:left;vertical-align:top}}th{{background:#edf2ef;font-size:11px}}
.n{{text-align:right;white-space:nowrap}}.ch{{font-weight:700;color:#0a7d4f}}.s div{{white-space:nowrap}}.s a{{color:#16202e}}
tr.review td:first-child{{border-left:3px solid #e0a000}}tr.not-found td:first-child,tr.blocked td:first-child,tr.no-url td:first-child{{border-left:3px solid #c0392b}}
.box{{font-size:16px;text-align:center}}
</style></head><body><h1>Provera cena električnih automobila · {TODAY}</h1><p class="m">{E(summary)}. Ništa ne ide na sajt dok se pull request ne odobri.
Izvori: uvoznik = zvanični sajt brenda, ostalo = sajtovi dilera iz podataka sajta. Cene se smatraju potvrđenim kad se uvoznik i bar jedan diler slažu (razlika do 100 € ili 0,5 %).</p>
{''.join(body)}</body></html>"""
    html_path = REPORT.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as fh: fh.write(page)
    if f and f.browser:
        try:
            pg = f.ctx.new_page(); pg.set_content(page); pg.pdf(path=REPORT.replace('.md', '.pdf'), format='A4', landscape=True, print_background=True); pg.close()
        except Exception as ex:  # noqa: BLE001
            print('PDF nije napravljen:', err(ex))


if __name__ == '__main__':
    sys.exit(main())
