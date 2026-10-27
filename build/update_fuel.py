#!/usr/bin/env python3
"""Fuel price check for the cost calculator (evomobil.rs).

Reads the maximum retail prices for BMB 95 and Evrodizel, checks them and writes data/gorivo.json:
  provereno = the day of this check (shown on the site as "cene na dan ...")
  datum     = the Friday from which the current prices apply (changes only when a price changes)
Run by .github/workflows/cene-goriva.yml every day at 7:00 and on Fridays at 15:10 (Belgrade).

Source: nafta.hr/sr/cene-goriva-srbija (stable page, table per fuel with the price at AVIA, EKO, MOL, NIS, OMV...).
The prices there are the government's maximum retail prices, set by the Ministry of Trade every Friday at 15:00.

Exit codes: 0 = done (updated or unchanged), 1 = could not read or the numbers failed a check (nothing written).
Usage: python3 build/update_fuel.py            fetch and update
       python3 build/update_fuel.py --file x.html   parse a saved copy of the page (for testing)
"""
import collections, datetime as dt, html, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'gorivo.json')
URL = 'https://nafta.hr/sr/cene-goriva-srbija/'
SOURCE_NAME = 'nafta.hr'
MIN_RSD, MAX_RSD = 150, 320     # anything outside is a parsing error, not a price
MAX_WEEKLY_JUMP = 20            # RSD/l; a larger change in one week is treated as suspicious
MIN_STATIONS = 3                # at least this many companies must show the same (maximum) price


def fail(msg):
    print('GREŠKA: ' + msg)
    summary(f'### Cene goriva: provera nije uspela\n\n{msg}\n\nCene na sajtu nisu menjane. Izvor: {URL}\n')
    sys.exit(1)


def summary(md):
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        with open(p, 'a', encoding='utf-8') as f:
            f.write(md + '\n')


def fetch():
    req = urllib.request.Request(URL, headers={'User-Agent': 'evomobil.rs fuel price check (weekly; office@evomobil.rs)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def to_text(page):
    page = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', page)
    page = re.sub(r'(?i)<br\s*/?>|</(p|div|tr|li|h\d|table|td|th)>', '\n', page)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', page))
    return re.sub(r'[ \t\xa0]+', ' ', t)


PRICE = re.compile(r'(\d{3})(?:[.,](\d{1,2}))?\s*(?:RSD|din)', re.I)


def section_prices(text, start_rx, stop_rx):
    """Prices listed after the heading matching start_rx, up to the next fuel heading (stop_rx).
    The fuel name also appears in running text, so the first mention followed by a list of prices wins."""
    for m in re.finditer(start_rx, text, re.I):
        rest = text[m.end():]
        s = re.search(stop_rx, rest, re.I)
        block = rest[:s.start()] if s else rest[:3000]
        prices = [float(a + '.' + (b or '0')) for a, b in PRICE.findall(block)]
        if len(prices) >= MIN_STATIONS:
            return prices
    return []


def cap(prices, label):
    """The maximum retail price set by the government: the price most companies show.
    (The page can also list premium fuels such as BMB 100 or "plus" diesel at a higher price at one or two
    companies, so the most common price is used, not the highest one.)"""
    prices = [p for p in prices if MIN_RSD <= p <= MAX_RSD]
    if not prices:
        fail(f'Na stranici nije pronađena nijedna cena za {label}. Moguće je da je izvor promenio izgled stranice.')
    top, n = collections.Counter(prices).most_common(1)[0]
    if n < MIN_STATIONS:
        fail(f'{label}: nijedna cena se ne ponavlja kod bar {MIN_STATIONS} kompanije (najčešća: {top} RSD/l, {n}×). Proverite izvor ručno.')
    return int(top) if top == int(top) else top


def last_friday_15(now):
    """Date of the Friday whose 15:00 decision is in force at `now` (Belgrade time)."""
    d = now.date() - dt.timedelta(days=(now.weekday() - 4) % 7)
    if now.weekday() == 4 and now.hour < 15:
        d -= dt.timedelta(days=7)
    return d


def belgrade_now():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo('Europe/Belgrade'))
    except Exception:
        return dt.datetime.utcnow() + dt.timedelta(hours=1)


def main():
    if '--file' in sys.argv:
        page = open(sys.argv[sys.argv.index('--file') + 1], encoding='utf-8').read()
    else:
        try:
            page = fetch()
        except Exception as e:
            fail(f'Stranica sa cenama nije dostupna ({e}).')
    text = to_text(page)
    benzin = cap(section_prices(text, r'BMB\s*95', r'Evro\s*-?\s*dizel|Euro\s*-?\s*dizel|Eurodizel|Evrodizel|BMB\s*100|TNG|Autogas|LPG'), 'BMB 95')
    dizel = cap(section_prices(text, r'Evro\s*-?\s*dizel|Euro\s*-?\s*dizel|Eurodizel|Evrodizel', r'BMB\s*95|TNG|Autogas|Komentar'), 'Evrodizel')
    if dizel == benzin:
        fail(f'BMB 95 i Evrodizel imaju istu cenu ({benzin} RSD/l), što ukazuje na grešku pri čitanju stranice.')

    old = json.load(open(DATA, encoding='utf-8'))
    for name, new, prev in (('BMB 95', benzin, old['benzin']), ('Evrodizel', dizel, old['dizel'])):
        if abs(new - prev) > MAX_WEEKLY_JUMP:
            fail(f'{name}: nova cena {new} RSD/l razlikuje se od prethodne ({prev}) za više od {MAX_WEEKLY_JUMP} RSD. '
                 'Ako je promena stvarna, upišite je ručno u data/gorivo.json.')

    print(f'Pročitano: BMB 95 {benzin} RSD/l, Evrodizel {dizel} RSD/l (prethodno {old["benzin"]} / {old["dizel"]})')
    now = belgrade_now()
    today = now.date().isoformat()
    if benzin == old['benzin'] and dizel == old['dizel']:
        old['provereno'] = today
        with open(DATA, 'w', encoding='utf-8') as f:
            json.dump(old, f, ensure_ascii=False, indent=1)
            f.write('\n')
        summary(f'### Cene goriva: bez promene\n\nBMB 95 {benzin} RSD/l, Evrodizel {dizel} RSD/l (važe od {old["datum"]}, provereno {today}).\n')
        print(f'Bez promene, provereno {today}.')
        return
    prev_b, prev_d = old['benzin'], old['dizel']
    old.update({'datum': last_friday_15(now).isoformat(), 'provereno': today, 'benzin': benzin, 'dizel': dizel, 'izvor_preuzimanja': URL})
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(old, f, ensure_ascii=False, indent=1)
        f.write('\n')
    summary(f'### Cene goriva: ažurirano\n\n| Gorivo | Bilo | Sada |\n|---|---|---|\n'
            f'| BMB 95 | {prev_b} RSD/l | **{benzin} RSD/l** |\n| Evrodizel | {prev_d} RSD/l | **{dizel} RSD/l** |\n\n'
            f'Važe od {old["datum"]}. Izvor: {URL}\n')
    print(f'Upisano u data/gorivo.json (važe od {old["datum"]}).')


if __name__ == '__main__':
    main()
