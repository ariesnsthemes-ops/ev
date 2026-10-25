"""Optimise model photos: trim margins, clean faint transparent haze, save 1280px and 640px WebP.
Usage: python3 photos.py <source_dir>   (files named evomobil-<model-id>.<ext>, or mapped below)"""
import sys, os, glob, json
from PIL import Image, ImageChops
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = sys.argv[1]
KEEP_OLD = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else set()
MAP = {'BMW i4 M50': 'bmw-i4-m50', 'BMW i4 eDrive40 Gran Coup': 'bmw-i4', 'BMW i7 60 sedan': 'bmw-i7', 'BMW iX M70': 'bmw-ix-m-model',
       'BMW iX xDrive60': 'bmw-ix', 'BMW iX1': 'bmw-ix1', 'iX5 60': 'bmw-ix3'}

def trim(im):
    im = im.convert('RGBA'); a = im.split()[3]
    if a.getextrema()[0] < 250:
        a = a.point(lambda v: 0 if v < 40 else v)          # drop faint haze left by cut-outs
        im.putalpha(a)
        box = a.point(lambda v: 255 if v > 60 else 0).getbbox()
    else:
        rgb = im.convert('RGB'); w, h = rgb.size
        cs = [rgb.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
        bg = tuple(sorted(c[i] for c in cs)[2] for i in range(3))
        box = ImageChops.difference(rgb, Image.new('RGB', rgb.size, bg)).convert('L').point(lambda v: 255 if v > 16 else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box; pw, ph = int((r - l) * .02), int((b - t) * .03)
    return im.crop((max(0, l - pw), max(0, t - ph), min(im.width, r + pw), min(im.height, b + ph)))

def save(img, path, opaque):
    if opaque: img.convert('RGB').save(path, 'WEBP', quality=84, method=6)
    else: img.save(path, 'WEBP', quality=84, method=6, alpha_quality=90)

for f in sorted(glob.glob(SRC + '/*')):
    n = os.path.splitext(os.path.basename(f))[0]
    mid = n[len('evomobil-'):] if n.startswith('evomobil-') else next((v for k, v in MAP.items() if k in n), None)
    if not mid or mid in KEEP_OLD:
        print('skip', os.path.basename(f)); continue
    im = trim(Image.open(f)); opaque = im.split()[3].getextrema()[0] >= 250
    for w, p in ((1280, f'{ROOT}/img/evomobil-{mid}.webp'), (640, f'{ROOT}/img/evomobil-{mid}-640.webp')):
        save(im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS), p, opaque)
    print('ok', mid, im.size)
