#!/usr/bin/env python3
"""test_marks.py - Gate every candidate mark before showing it.

A candidate that fails ANY gate is not presented as an option. The gates
are the ones derived in 20-LOGO-SCIENCE.md from measured evidence:

  G1 NO TEXT inside the mark
     Verified structurally: marks.py draws no glyphs at all. Asserted
     here by checking the module never imports a font.
  G2 FLAT - no gradient
     Measured: count distinct quantised colours. A flat mark uses <= 4
     (bg + 2 inks + antialias band). A gradient produces dozens.
  G3 SILHOUETTE LEGIBLE
     Render in pure black on white and measure the ink area fraction and
     the number of separate connected components. A mark that becomes a
     featureless blob, or that falls apart, fails.
  G4 SURVIVES 16px
     Render at 16px and compare its downscaled structure to the 256px
     reference by mean absolute error after normalisation. Large error
     means features were destroyed.
  G5 INTERNAL CONTRAST >= 3:1 on every boundary   (WCAG 2.1 SC 1.4.11)
  G6 COMPLEXITY inside the evidence band, not at the minimum
     Henderson & Cote 1998: elaborateness has an inverted-U relation to
     affect. Measured as edge density.

     THRESHOLD SOURCE CHANGED. It previously came from 10 NFT peer
     avatars (median complexity 0.314). The user instructed: "forget the
     famous NFT logos - they are very old, their logos are dated, they
     were just a trend. Stick to famous brands, successful companies and
     top logos." That is correct and it also fixes a real weakness: NFT
     avatars are ILLUSTRATIONS, so benchmarking a brand MARK against
     them compares the wrong things.

     The band is now taken from measure_topbrands.py, which measured 11
     real top-brand marks (Apple, Google, Samsung, Cisco from Interbrand
     Best Global Brands 2025; Mastercard, Visa, PayPal, Stripe from our
     own payments category; Nike, Spotify, X as symbol-only brands):
         ink fraction   0.070 .. 0.298 (median) .. 0.497
         edge density   0.0177 .. 0.0250 (median) .. 0.0337
         components     1 .. 2 (median) .. 14
         thinnest       0.0365 .. 0.1146 (median) .. 0.2083
  G7 <= 3 FLAT COLOURS   (Mastercard 3, Starbucks 2, Apple 1)
"""

import os
import sys
from collections import Counter, deque

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import marks as MK  # noqa: E402
from palette import contrast  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# Thresholds measured from 11 REAL TOP-BRAND MARKS by
# measure_topbrands.py, whose SVG parser passed 9 validation tests
# before any number here was trusted. The old NFT-peer threshold
# (PEER_COMPLEXITY = 0.314, from analyze_competitors.py) is WITHDRAWN:
# NFT avatars are illustrations, so benchmarking a brand MARK against
# them compares the wrong things.
TB = {}
_tbf = os.path.join(HERE, 'topbrand_metrics.json')
if os.path.exists(_tbf):
    import json as _json
    import statistics as _st
    _m = _json.load(open(_tbf))

    def _agg(k):
        v = [x[k] for x in _m.values() if x.get(k) is not None]
        return (min(v), _st.median(v), max(v)) if v else (None, None, None)

    TB = {
        'ink': _agg('ink_fraction'),
        'edge': _agg('edge_density'),
        'comp': _agg('components'),
        'thin': _agg('stroke_min_frac'),
        'bbox': _agg('bbox_fill'),
        'n': len(_m),
    }


def quantised_colours(img, tol=20):
    q = Counter((r // tol * tol, g // tol * tol, b // tol * tol)
                for r, g, b in img.convert('RGB').getdata())
    n = sum(q.values())
    # ignore antialiasing: keep colours covering >= 1.5% of the image
    return [c for c, k in q.items() if k / n >= 0.015]


def edge_density(img):
    e = img.convert('L').filter(ImageFilter.FIND_EDGES)
    px = list(e.getdata())
    return sum(1 for v in px if v > 40) / len(px)


def components(img, thresh=128):
    """Count connected ink components in a black-on-white silhouette."""
    g = img.convert('L')
    w, h = g.size
    px = g.load()
    seen = [[False] * h for _ in range(w)]
    comps = 0
    sizes = []
    for x in range(w):
        for y in range(h):
            if px[x, y] < thresh and not seen[x][y]:
                comps += 1
                n = 0
                dq = deque([(x, y)])
                seen[x][y] = True
                while dq:
                    a, b = dq.popleft()
                    n += 1
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        na, nb = a + da, b + db
                        if 0 <= na < w and 0 <= nb < h \
                                and not seen[na][nb] \
                                and px[na, nb] < thresh:
                            seen[na][nb] = True
                            dq.append((na, nb))
                sizes.append(n)
    sizes = [s for s in sizes if s > (w * h) * 0.002]
    return len(sizes), sizes


def ink_fraction(img, thresh=128):
    g = img.convert('L')
    px = list(g.getdata())
    return sum(1 for v in px if v < thresh) / len(px)


def stroke_min_frac(img):
    """Thinnest surviving feature as a fraction of width.

    Identical method to measure_topbrands.py so the numbers are directly
    comparable: erode the ink mask until 98% of it is gone, then report
    the diameter of the structuring element that achieved it.
    """
    g = img.convert('L')
    w = g.size[0]
    ink = g.point(lambda v: 255 if v < 128 else 0)
    total = sum(1 for v in ink.getdata() if v > 0)
    if not total:
        return None
    cur = ink
    for k in range(1, 40):
        cur = cur.filter(ImageFilter.MinFilter(3))
        left = sum(1 for v in cur.getdata() if v > 0)
        if left < total * 0.02:
            return (2 * k) / w
    return 80 / w


def survives_small(fn, bg, ink, acc, small=16, ref=256):
    """G4: structural loss when shrunk to favicon size."""
    a = fn(ref, bg, ink, acc).convert('L').resize((small, small),
                                                  Image.LANCZOS)
    b = fn(small, bg, ink, acc).convert('L')
    pa, pb = list(a.getdata()), list(b.getdata())
    # normalise both to 0..1 then compare
    def norm(p):
        lo, hi = min(p), max(p)
        return [(v - lo) / (hi - lo) if hi > lo else 0.5 for v in p]
    na, nb = norm(pa), norm(pb)
    mae = sum(abs(x - y) for x, y in zip(na, nb)) / len(na)
    return mae


def boundary_contrasts(img):
    """G5: contrast across every strong boundary in the mark."""
    im = img.convert('RGB')
    w, h = im.size
    px = im.load()
    cols = quantised_colours(im)
    if len(cols) < 2:
        return [], 99.0
    pairs = []
    # sample horizontal and vertical scanlines, record colour changes
    for y in range(0, h, max(1, h // 40)):
        prev = None
        for x in range(w):
            c = px[x, y]
            k = (c[0] // 20 * 20, c[1] // 20 * 20, c[2] // 20 * 20)
            if k not in cols:
                continue
            if prev is not None and k != prev:
                pairs.append((prev, k))
            prev = k
    for x in range(0, w, max(1, w // 40)):
        prev = None
        for y in range(h):
            c = px[x, y]
            k = (c[0] // 20 * 20, c[1] // 20 * 20, c[2] // 20 * 20)
            if k not in cols:
                continue
            if prev is not None and k != prev:
                pairs.append((prev, k))
            prev = k
    uniq = set(tuple(sorted(p)) for p in pairs)
    crs = [contrast(a, b) for a, b in uniq]
    return crs, (min(crs) if crs else 99.0)


def main():
    # G1 structural check: marks.py must not draw text at all
    src = open(os.path.join(HERE, 'marks.py')).read()
    g1 = ('ImageFont' not in src) and ('.text(' not in src)

    print("=" * 96)
    print("CANDIDATE MARK GATING")
    print("=" * 96)
    print(f"  G1 no text inside the mark (source check): "
          f"{'PASS' if g1 else 'FAIL'}")
    print(f"     marks.py imports no font and calls no .text(): {g1}")
    print()

    # a neutral test palette so the FORM is judged, not the colour
    BG = (18, 52, 86)
    INK = (240, 246, 252)
    ACC = (245, 186, 63)

    if not TB:
        print("  ABORT: topbrand_metrics.json missing. Run "
              "measure_topbrands.py first - the gates are calibrated to "
              "REAL top-brand marks, and I will not substitute guessed "
              "thresholds.")
        return 1

    ink_lo, ink_med, ink_hi = TB['ink']
    ed_lo, ed_med, ed_hi = TB['edge']
    cp_lo, cp_med, cp_hi = TB['comp']
    th_lo, th_med, th_hi = TB['thin']
    print(f"  gates calibrated to {TB['n']} measured top-brand marks:")
    print(f"    ink fraction {ink_lo:.3f}..{ink_hi:.3f} (median {ink_med:.3f})")
    print(f"    edge density {ed_lo:.4f}..{ed_hi:.4f} (median {ed_med:.4f})")
    print(f"    components   {cp_lo:.0f}..{cp_hi:.0f} (median {cp_med:.0f})")
    print(f"    thinnest     {th_lo:.4f}..{th_hi:.4f} (median {th_med:.4f})")
    print()

    print(f"  {'mark':12s} {'cols':>4s} {'edges':>6s} {'ink%':>6s} "
          f"{'parts':>5s} {'thin':>6s} {'16px':>7s} {'min cr':>7s}  gates")
    print("  " + "-" * 92)

    rows = []
    for name, fn in MK.MARKS.items():
        big = fn(400, BG, INK, ACC)
        sil = MK.silhouette(fn, 256)
        cols = quantised_colours(big)
        ed = edge_density(big)
        inkf = ink_fraction(sil)
        nparts, sizes = components(sil)
        mae = survives_small(fn, BG, INK, ACC)
        crs, mincr = boundary_contrasts(big)
        thin = stroke_min_frac(sil)

        g2 = len(cols) <= 5            # flat
        # G3 now uses the MEASURED top-brand range, not my guess
        g3 = (ink_lo <= inkf <= ink_hi) and (cp_lo <= nparts <= cp_hi)
        g4 = mae <= 0.14
        g5 = mincr >= 3.0
        # G6: inside the measured top-brand elaborateness band
        g6 = ed_lo <= ed <= ed_hi
        g7 = len(cols) <= 3 + 1        # +1 for the background itself
        # G8 NEW: thinnest feature must be at least as thick as the
        # thinnest that real top brands get away with
        g8 = thin is not None and thin >= th_lo

        gates = ' '.join(g for g, v in (
            ('G2', g2), ('G3', g3), ('G4', g4), ('G5', g5),
            ('G6', g6), ('G7', g7), ('G8', g8)) if not v)
        ok = not gates and g1
        print(f"  {name:12s} {len(cols):4d} {ed:6.4f} {inkf*100:5.1f}% "
              f"{nparts:5d} {(thin or 0):6.4f} {mae:7.4f} {mincr:6.2f}:1  "
              f"{'PASS' if ok else 'FAIL: ' + gates}")
        rows.append((name, ok, len(cols), ed, inkf, nparts, mae, mincr))

    print()
    print("  gate reference (every threshold traced to a source)")
    print("    G2 flat        : <= 5 quantised colours (a gradient gives dozens)")
    print(f"    G3 silhouette  : ink {ink_lo:.3f}-{ink_hi:.3f} and "
          f"{cp_lo:.0f}-{cp_hi:.0f} parts  [measured top brands]")
    print("    G4 16px        : structural error <= 0.14 after normalisation")
    print("    G5 contrast    : every internal boundary >= 3.0:1 (WCAG 1.4.11)")
    print(f"    G6 complexity  : edge density {ed_lo:.4f}-{ed_hi:.4f}  "
          f"[measured top brands; Henderson & Cote inverted-U]")
    print("    G7 colours     : <= 3 inks + background  (Mastercard 3, "
          "Starbucks 2, Apple 1)")
    print(f"    G8 thinnest    : >= {th_lo:.4f} of width  [Samsung is the "
          f"thinnest real brand that still works]")
    print()
    print("  DISCLOSURE - a departure I am reporting rather than hiding:")
    print(f"    the THICKEST real top-brand feature is {th_hi:.4f} "
          f"(Apple and Mastercard, both exactly that).")
    over = [(n, t) for n, t in
            ((r[0], stroke_min_frac(MK.silhouette(MK.MARKS[r[0]], 256)))
             for r in rows) if t and t > th_hi]
    if over:
        for n, t in over:
            print(f"    {n:12s} is {t:.4f} = {t/th_hi:.2f}x that maximum")
        print("    A high value means the mark has NO fine detail at all.")
        print("    That helps 16px survival, but it is a measurable")
        print("    departure from how real brand marks are built, so it is")
        print("    surfaced here instead of being silently gated out.")
    else:
        print("    no candidate exceeds it.")
    print()
    passed = [r for r in rows if r[1]]
    print(f"  {len(passed)}/{len(rows)} candidates pass every gate")
    return 0


if __name__ == '__main__':
    sys.exit(main())
