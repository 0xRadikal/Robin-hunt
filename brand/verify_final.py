#!/usr/bin/env python3
"""verify_final.py - Test the finished assets against every scenario I
can construct, before showing them to anyone.

SCENARIOS COVERED
  A platform specs        exact dimensions and byte limits
  B circle crop safety    X renders the avatar as a circle
  C size sweep            400 / 96 / 48 / 32 / 24 / 16 px
  D monochrome            pure black silhouette, and white-on-black
  E colour blindness      protanopia, deuteranopia, tritanopia
  F JPEG recompression    platforms re-encode uploads
  G banner safe zone      X pastes the avatar over the banner
  H mark gates            the same 8 gates used to select the form
  I on-white              the mark must work on a light surface too

COLOUR-BLINDNESS METHOD
  Brettel/Vienot-style LMS simulation. The transform used here is the
  widely published Machado et al. (2009) severity-1.0 matrix set, which
  operates in linear RGB. Applying it in gamma-encoded sRGB would
  overstate the effect, so the pipeline is:
      sRGB -> linear -> CVD matrix -> clamp -> sRGB
  The test is not "does it look identical" (it cannot) but "does the
  weakest boundary still clear the WCAG 1.4.11 threshold of 3:1".
"""

import io
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import coinkins_mark as CM  # noqa: E402
from palette import contrast  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'final')

BG = (18, 34, 68)
RING = (234, 241, 250)
DISC = (243, 182, 58)

SPECS = [
    ('avatar-400.png', 400, 400, 2 * 1024 * 1024, 'X avatar'),
    ('avatar-512.png', 512, 512, 2 * 1024 * 1024, 'Telegram / OpenSea'),
    ('favicon-32.png', 32, 32, 100 * 1024, 'browser tab'),
    ('favicon-16.png', 16, 16, 100 * 1024, 'browser tab small'),
    ('banner-1500x500.png', 1500, 500, 5 * 1024 * 1024, 'X header 3:1'),
    ('os-banner-1400x400.png', 1400, 400, 5 * 1024 * 1024,
     'OpenSea banner'),
    ('og-1200x630.png', 1200, 630, 5 * 1024 * 1024, 'OG preview'),
]

# Machado, Oliveira & Fernandes (2009), IEEE TVCG - severity 1.0
CVD = {
    'protanopia': ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    'deuteranopia': ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    'tritanopia': ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _srgb(v):
    v = max(0.0, min(1.0, v))
    v = v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return int(round(max(0.0, min(1.0, v)) * 255))


def simulate_cvd(rgb, kind):
    m = CVD[kind]
    r, g, b = (_lin(x) for x in rgb)
    return tuple(_srgb(m[i][0] * r + m[i][1] * g + m[i][2] * b)
                 for i in range(3))


def ok(flag):
    return 'PASS' if flag else 'FAIL'


def main():
    allok = True

    # ---------------- A platform specs ----------------
    print("=" * 80)
    print("A  PLATFORM SPECS")
    print("=" * 80)
    for fn, w, h, maxb, why in SPECS:
        p = os.path.join(FIN, fn)
        if not os.path.exists(p):
            print(f"  FAIL  {fn} MISSING")
            allok = False
            continue
        im = Image.open(p)
        b = os.path.getsize(p)
        good = im.size == (w, h) and b <= maxb and im.mode in ('RGB',
                                                               'RGBA', 'P')
        allok &= good
        print(f"  {ok(good)}  {fn:26s} {im.size[0]}x{im.size[1]} "
              f"(want {w}x{h})  {b/1024:7.1f} KB  mode {im.mode}  {why}")

    # ---------------- B circle crop ----------------
    print()
    print("=" * 80)
    print("B  CIRCLE-CROP SAFETY (X renders the avatar as a circle)")
    print("=" * 80)
    av = Image.open(os.path.join(FIN, 'avatar-400.png')).convert('RGB')
    W, H = av.size
    cx, cy, r = W / 2, H / 2, W / 2
    px = av.load()
    from collections import Counter
    outside = []
    for x in range(0, W, 2):
        for y in range(0, H, 2):
            if math.hypot(x - cx, y - cy) > r * 0.995:
                outside.append(px[x, y])
    dom = Counter(outside).most_common(1)[0]
    share = dom[1] / len(outside)
    good = share >= 0.95
    allok &= good
    print(f"  pixels outside the inscribed circle: {len(outside)}")
    print(f"  dominant colour there: {dom[0]}  share {share*100:.1f}%")
    print(f"  {ok(good)}  corners are uniform background, nothing is "
          f"clipped")
    # and the mark must not reach the circle edge
    mark_r = CM.R_OUTER_U / CM.U_DIV
    good = mark_r < 0.5
    allok &= good
    print(f"  {ok(good)}  mark outer radius {mark_r:.4f} of width < 0.5, "
          f"so it never touches the crop edge")

    # ---------------- C size sweep ----------------
    print()
    print("=" * 80)
    print("C  SIZE SWEEP - structural fidelity and edge survival")
    print("=" * 80)
    ref = CM.silhouette(256).convert('L').resize((64, 64), Image.LANCZOS)

    def norm(p):
        lo, hi = min(p), max(p)
        return [(v - lo) / (hi - lo) if hi > lo else 0.5 for v in p]
    rn = norm(list(ref.getdata()))
    for s in (400, 96, 48, 32, 24, 16):
        img = CM.draw(s, BG, RING, DISC)
        sl = CM.silhouette(s).convert('L').resize((64, 64), Image.LANCZOS)
        mae = sum(abs(a - b) for a, b in
                  zip(rn, norm(list(sl.getdata())))) / 4096
        # does the disc still separate from the ring at this size?
        pxs = img.convert('RGB').load()
        c = s // 2
        centre = pxs[c, c]
        cr = contrast(centre, BG)
        good = mae <= 0.10 and cr >= 3.0
        allok &= good
        print(f"  {ok(good)}  {s:3d}px  structural err {mae:.4f}  "
              f"centre {centre} vs bg {cr:5.2f}:1")

    # ---------------- D monochrome ----------------
    print()
    print("=" * 80)
    print("D  MONOCHROME - the mark must work with colour fully removed")
    print("=" * 80)
    for name, img in (('black on white', CM.silhouette(256)),
                      ('white on black', CM.mono_light(256))):
        g = img.convert('L')
        vals = list(g.getdata())
        inkf = sum(1 for v in vals if v < 128) / len(vals) \
            if name.startswith('black') else \
            sum(1 for v in vals if v > 128) / len(vals)
        # the gap must still be visible: sample across it
        pxm = img.convert('RGB').load()
        S = 256
        cc = S // 2
        Um = S / CM.U_DIV
        gap_px = pxm[int(cc + 5 * Um), cc]        # in the gap, +x axis
        ring_px = pxm[int(cc - 5 * Um), cc]       # ring, -x axis
        cr = contrast(gap_px, ring_px)
        good = cr >= 3.0 and 0.05 <= inkf <= 0.60
        allok &= good
        print(f"  {ok(good)}  {name:16s} ink {inkf*100:5.1f}%  "
              f"gap {gap_px} vs ring {ring_px} = {cr:6.2f}:1")

    # ---------------- E colour blindness ----------------
    print()
    print("=" * 80)
    print("E  COLOUR-VISION DEFICIENCY (Machado et al. 2009, severity 1.0)")
    print("=" * 80)
    print(f"  {'condition':14s} {'bg':16s} {'ring':16s} {'disc':16s} "
          f"{'ring/bg':>8s} {'disc/bg':>8s}")
    print("  " + "-" * 76)
    print(f"  {'normal':14s} {str(BG):16s} {str(RING):16s} {str(DISC):16s} "
          f"{contrast(RING,BG):7.2f}:1 {contrast(DISC,BG):7.2f}:1")
    for kind in CVD:
        b2 = simulate_cvd(BG, kind)
        r2 = simulate_cvd(RING, kind)
        d2 = simulate_cvd(DISC, kind)
        c1, c2 = contrast(r2, b2), contrast(d2, b2)
        good = c1 >= 3.0 and c2 >= 3.0
        allok &= good
        print(f"  {kind:14s} {str(b2):16s} {str(r2):16s} {str(d2):16s} "
              f"{c1:7.2f}:1 {c2:7.2f}:1  {ok(good)}")
    print("  requirement: every boundary still >= 3:1 under every "
          "condition (WCAG 1.4.11)")

    # ---------------- F JPEG recompression ----------------
    print()
    print("=" * 80)
    print("F  JPEG RECOMPRESSION (platforms re-encode what you upload)")
    print("=" * 80)
    src = Image.open(os.path.join(FIN, 'avatar-400.png')).convert('RGB')
    for q in (90, 75, 60, 40):
        buf = io.BytesIO()
        src.save(buf, 'JPEG', quality=q)
        buf.seek(0)
        rt = Image.open(buf).convert('RGB')
        p2 = rt.load()
        c = 200
        centre = p2[c, c]
        Uq = 400 / CM.U_DIV
        ringpx = p2[int(c - 5 * Uq), c]
        bgpx = p2[8, 8]
        c1 = contrast(centre, bgpx)
        c2 = contrast(ringpx, bgpx)
        good = c1 >= 3.0 and c2 >= 3.0
        allok &= good
        print(f"  {ok(good)}  q{q:3d}  {len(buf.getvalue())/1024:6.1f} KB  "
              f"disc/bg {c1:6.2f}:1  ring/bg {c2:6.2f}:1")

    # ---------------- G banner safe zone ----------------
    print()
    print("=" * 80)
    print("G  BANNER SAFE ZONE (X pastes the avatar bottom-left)")
    print("=" * 80)
    bn = Image.open(os.path.join(FIN, 'banner-1500x500.png')).convert('RGB')
    # verified zone from test_safezone.py: x=[33,231], y=[401,500]
    zone = bn.crop((33, 401, 231, 500))
    zc = Counter(zone.getdata()).most_common(1)[0]
    zshare = zc[1] / (zone.size[0] * zone.size[1])
    good = zshare >= 0.90
    allok &= good
    print(f"  avatar zone x=[33,231] y=[401,500]")
    print(f"  dominant colour {zc[0]}  share {zshare*100:.1f}%")
    print(f"  {ok(good)}  zone is clear background, nothing important is "
          f"covered by the avatar")

    # ---------------- H mark gates ----------------
    print()
    print("=" * 80)
    print("H  THE 8 MARK GATES (same suite used to select the form)")
    print("=" * 80)
    import test_marks as T
    big = CM.draw(400, BG, RING, DISC)
    sil = CM.silhouette(256)
    cols = T.quantised_colours(big)
    ed = T.edge_density(big)
    inkf = T.ink_fraction(sil)
    nparts, _ = T.components(sil)
    thin = T.stroke_min_frac(sil)
    crs, mincr = T.boundary_contrasts(big)
    src_txt = open(os.path.join(HERE, 'coinkins_mark.py')).read()
    g1 = ('ImageFont' not in src_txt) and ('.text(' not in src_txt)
    checks = [
        ('G1 no text in the mark', g1, 'source has no font, no .text()'),
        ('G2 flat', len(cols) <= 5, f'{len(cols)} quantised colours'),
        ('G3 ink in top-brand range', 0.070 <= inkf <= 0.497,
         f'{inkf:.4f}'),
        ('G3 parts in range', 1 <= nparts <= 14, f'{nparts}'),
        ('G4 16px error', True, 'measured in section C'),
        ('G5 min boundary >= 3:1', mincr >= 3.0, f'{mincr:.2f}:1'),
        ('G6 edges in top-brand band', 0.0177 <= ed <= 0.0337,
         f'{ed:.4f}'),
        ('G7 <= 3 inks + bg', len(cols) <= 4, f'{len(cols)}'),
        ('G8 thinnest >= 0.0365', (thin or 0) >= 0.0365, f'{thin:.4f}'),
    ]
    for n, v, detail in checks:
        allok &= v
        print(f"  {ok(v)}  {n:30s} {detail}")

    # ---------------- I on-white ----------------
    print()
    print("=" * 80)
    print("I  ON A LIGHT SURFACE (docs, invoices, print)")
    print("=" * 80)
    lw = CM.draw(256, (255, 255, 255), (18, 34, 68), (166, 124, 40))
    p3 = lw.convert('RGB').load()
    cc = 128
    Ul = 256 / CM.U_DIV
    c_disc = contrast(p3[cc, cc], (255, 255, 255))
    c_ring = contrast(p3[int(cc - 5 * Ul), cc], (255, 255, 255))
    good = c_disc >= 3.0 and c_ring >= 3.0
    allok &= good
    print(f"  {ok(good)}  disc/white {c_disc:6.2f}:1   "
          f"ring/white {c_ring:6.2f}:1")

    print()
    print("=" * 80)
    print(f"OVERALL: {'ALL SCENARIOS PASS' if allok else 'FAILURES ABOVE'}")
    print("=" * 80)
    return 0 if allok else 1


if __name__ == '__main__':
    from collections import Counter
    sys.exit(main())
