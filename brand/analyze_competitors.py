#!/usr/bin/env python3
"""
analyze_competitors.py - Download real competitor avatars and measure them
objectively: dominant colours, saturation, brightness, contrast, edge
complexity, and whether they survive small-size rendering.

No opinions. Every number is computed from the actual pixels.
"""
import colorsys
import io
import json
import os
import urllib.request
from collections import Counter

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'competitors')
os.makedirs(CACHE, exist_ok=True)

# Verified-collection avatars pulled from OpenSea's own CDN.
# Slugs confirmed verified in doc 16 research.
TARGETS = [
    'pudgypenguins', 'azuki', 'boredapeyachtclub', 'doodles-official',
    'moonbirds', 'milady', 'cryptopunks', 'rare-friends-genesis',
    'mutant-ape-yacht-club', 'clonex',
]


def get_json(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=25))
        except Exception:
            pass
    return None


def fetch_avatars():
    found = {}
    for slug in TARGETS:
        p = os.path.join(CACHE, f'{slug}.png')
        if os.path.exists(p):
            found[slug] = p
            continue
        d = get_json(f'https://api.opensea.io/api/v2/collections/{slug}')
        if not d or not d.get('image_url'):
            print(f"  {slug:24s} no image_url available")
            continue
        try:
            req = urllib.request.Request(
                d['image_url'], headers={'User-Agent': 'Mozilla/5.0'})
            raw = urllib.request.urlopen(req, timeout=30).read()
            Image.open(io.BytesIO(raw)).convert('RGB').save(p, 'PNG')
            found[slug] = p
            print(f"  {slug:24s} downloaded")
        except Exception as e:
            print(f"  {slug:24s} download failed: {str(e)[:40]}")
    return found


def quantize_palette(im, n=5):
    q = im.convert('RGB').resize((80, 80)).quantize(colors=n, method=2)
    pal = q.getpalette()
    counts = Counter(q.getdata())
    out = []
    total = sum(counts.values())
    for idx, cnt in counts.most_common(n):
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        out.append((rgb, cnt / total))
    return out


def metrics(path):
    im = Image.open(path).convert('RGB')
    small = im.resize((64, 64))
    px = list(small.getdata())
    n = len(px)

    # saturation + value
    sats, vals = [], []
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        sats.append(s)
        vals.append(v)
    sat = sum(sats) / n
    val = sum(vals) / n

    # edge complexity: how much detail survives shrinking
    tiny = im.resize((32, 32)).resize((16, 16))
    tp = list(tiny.getdata())
    diffs = 0
    for i in range(len(tp) - 1):
        d = sum(abs(a - b) for a, b in zip(tp[i], tp[i + 1]))
        if d > 60:
            diffs += 1
    complexity = diffs / len(tp)

    # unique colour count = visual busyness
    uniq = len(set(im.resize((48, 48)).getdata()))

    pal = quantize_palette(im)
    return {
        'size': im.size,
        'saturation': round(sat, 3),
        'brightness': round(val, 3),
        'complexity': round(complexity, 3),
        'unique_colors_48px': uniq,
        'dominant': [{'rgb': list(c), 'hex': '#%02x%02x%02x' % c,
                      'share': round(s, 3)} for c, s in pal],
    }


def main():
    print("=" * 74)
    print("DOWNLOADING COMPETITOR AVATARS")
    print("=" * 74)
    found = fetch_avatars()
    print(f"\n  usable: {len(found)}")

    # include ours for direct comparison
    ours = os.path.join(HERE, 'coinkins-avatar-400.png')
    if os.path.exists(ours):
        found['>> COINKINS (ours)'] = ours

    print()
    print("=" * 74)
    print("OBJECTIVE METRICS")
    print("=" * 74)
    print(f"  {'name':24s} {'sat':>6} {'bright':>7} {'cplx':>6} "
          f"{'uniq':>7}  top colour")
    print("  " + "-" * 70)
    rows = {}
    for name, p in found.items():
        try:
            m = metrics(p)
        except Exception as e:
            print(f"  {name:24s} ERROR {str(e)[:30]}")
            continue
        rows[name] = m
        top = m['dominant'][0]
        print(f"  {name:24s} {m['saturation']:>6.3f} {m['brightness']:>7.3f} "
              f"{m['complexity']:>6.3f} {m['unique_colors_48px']:>7} "
              f" {top['hex']} ({top['share']*100:.0f}%)")

    json.dump(rows, open(os.path.join(HERE, 'competitor_metrics.json'), 'w'),
              indent=2)

    # aggregate, excluding ours
    comp = {k: v for k, v in rows.items() if not k.startswith('>>')}
    if comp:
        import statistics as st
        print()
        print("=" * 74)
        print(f"PEER AVERAGES (n={len(comp)}, verified collections only)")
        print("=" * 74)
        for f in ('saturation', 'brightness', 'complexity'):
            vals = [v[f] for v in comp.values()]
            print(f"  {f:14s} mean {st.mean(vals):.3f}  "
                  f"median {st.median(vals):.3f}  "
                  f"min {min(vals):.3f}  max {max(vals):.3f}")
        uq = [v['unique_colors_48px'] for v in comp.values()]
        print(f"  {'unique_colors':14s} mean {st.mean(uq):.0f}  "
              f"median {st.median(uq):.0f}  min {min(uq)}  max {max(uq)}")

        if '>> COINKINS (ours)' in rows:
            o = rows['>> COINKINS (ours)']
            print()
            print("  OURS vs PEER MEDIAN:")
            for f in ('saturation', 'brightness', 'complexity'):
                med = st.median([v[f] for v in comp.values()])
                delta = o[f] - med
                print(f"    {f:12s} ours {o[f]:.3f} vs {med:.3f}  "
                      f"({delta:+.3f})")
            med_u = st.median(uq)
            print(f"    {'unique_cols':12s} ours {o['unique_colors_48px']} "
                  f"vs {med_u:.0f}")

    print(f"\n  saved -> competitor_metrics.json")


if __name__ == '__main__':
    main()
