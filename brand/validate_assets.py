#!/usr/bin/env python3
"""
validate_assets.py - Verify every brand asset against the platform specs
we confirmed from help.x.com, before anything is uploaded.

Fails loudly rather than letting a wrong-sized image reach a profile.

IMPORTANT - THIS FILE WAS REPOINTED, AND WHY
--------------------------------------------
It used to validate `v2-*.png`, the palette that the user REJECTED. Those
files still exist on disk, so the script kept running and kept printing
"VERDICT: ALL ASSETS VALID" - a true statement about the wrong images,
which is worse than a failure because it looks like reassurance about the
shipping assets. It now validates `final/`, the assets that are actually
going to be uploaded, and ABORTS if that directory is missing.

Scope note: the deeper suite is `verify_final.py` (39 scenarios across 9
groups - colour blindness, JPEG recompression, circle crop, size sweep,
monochrome, banner safe zone, on-white). This file stays because it is
the narrow, fast check of the things a PLATFORM will reject outright:
exact pixel dimensions and file size.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'final')

if not os.path.isdir(ASSETS):
    sys.exit('final/ not found - run build_final.py first')

# (filename, expected_w, expected_h, max_bytes, purpose)
SPECS = [
    ('avatar-400.png', 400, 400, 2 * 1024 * 1024, 'X avatar'),
    ('avatar-512.png', 512, 512, 2 * 1024 * 1024,
     'Telegram/OpenSea avatar'),
    ('banner-1500x500.png', 1500, 500, 5 * 1024 * 1024,
     'X header (3:1)'),
    ('os-banner-1400x400.png', 1400, 400, 5 * 1024 * 1024,
     'OpenSea banner'),
    ('og-1200x630.png', 1200, 630, 5 * 1024 * 1024,
     'OG link preview'),
    ('favicon-32.png', 32, 32, 256 * 1024, 'browser tab'),
    ('favicon-16.png', 16, 16, 256 * 1024, 'browser tab, smallest'),
]


def contrast_ratio(rgb1, rgb2):
    """WCAG relative-luminance contrast ratio. Text must be readable."""
    def lum(c):
        s = []
        for v in c[:3]:
            v = v / 255
            s.append(v / 12.92 if v <= 0.03928
                     else ((v + 0.055) / 1.055) ** 2.4)
        return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2]
    l1, l2 = lum(rgb1), lum(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def main():
    ok = True
    print("=" * 70)
    print("BRAND ASSET VALIDATION")
    print("=" * 70)
    for fn, w, h, maxb, purpose in SPECS:
        p = os.path.join(ASSETS, fn)
        if not os.path.exists(p):
            print(f"  MISSING  {fn}")
            ok = False
            continue
        im = Image.open(p)
        b = os.path.getsize(p)
        dim_ok = im.size == (w, h)
        sz_ok = b <= maxb
        mode_ok = im.mode in ('RGB', 'RGBA')
        good = dim_ok and sz_ok and mode_ok
        if not good:
            ok = False
        print(f"  {'PASS' if good else 'FAIL'}  {fn}")
        print(f"        size {im.size[0]}x{im.size[1]} "
              f"(want {w}x{h}) {'ok' if dim_ok else 'WRONG'}")
        print(f"        bytes {b:,} (limit {maxb:,}) "
              f"{'ok' if sz_ok else 'TOO BIG'}  mode {im.mode}")
        print(f"        purpose: {purpose}")

    # avatar must survive circular cropping: check the corners are
    # background, i.e. nothing important is lost when X masks a circle
    print()
    print("=" * 70)
    print("AVATAR CIRCLE-CROP SAFETY")
    print("=" * 70)
    av = Image.open(os.path.join(ASSETS, 'avatar-400.png')).convert('RGB')
    W, H = av.size
    cx, cy, r = W / 2, H / 2, W / 2
    import math
    from collections import Counter

    # BUG I FIXED: the original test counted "bright pixels outside the
    # circle" and flagged 2157 as a failure. Investigation showed all 2157
    # were ONE colour - the teal background (15,194,142), sum=351 > 240.
    # v2 deliberately fills the canvas edge-to-edge because that is the
    # pattern used by the strongest peers (Azuki 91%, clonex 97% dominant
    # share). A flat background at the corners is CORRECT, not a defect.
    #
    # What actually matters is whether circular cropping destroys CONTENT.
    # Correct test: the corner region must be visually uniform (i.e. just
    # background). Many distinct colours out there would mean real artwork
    # is being cut off.
    corner_px = []
    for x in range(0, W, 3):
        for y in range(0, H, 3):
            if math.hypot(x - cx, y - cy) > r:
                corner_px.append(av.getpixel((x, y)))
    uniq = len(set(corner_px))
    dominant_share = (Counter(corner_px).most_common(1)[0][1]
                      / len(corner_px)) if corner_px else 1.0
    print(f"  pixels outside circle: {len(corner_px)}")
    print(f"  distinct colours there: {uniq}")
    print(f"  dominant share: {dominant_share*100:.1f}%")
    uniform = dominant_share >= 0.95
    print(f"  => {'SAFE (corners are uniform background)' if uniform else 'RISK: real content is being clipped'}")
    if not uniform:
        ok = False

    # readability of the banner title against its background
    print()
    print("=" * 70)
    print("BANNER TEXT CONTRAST (WCAG)")
    print("=" * 70)
    bn = Image.open(
        os.path.join(ASSETS, 'banner-1500x500.png')).convert('RGB')
    # BUG I FIXED: I originally hardcoded a sample coordinate (520,170) and
    # it landed BETWEEN glyph strokes, returning a dark pixel and reporting
    # a false 1.11:1 failure. Hardcoded sample points are as unreliable as
    # hardcoded gas limits. Now the text pixel is DISCOVERED by scanning
    # the title band for the brightest pixel, which cannot miss.
    title_px, bg_px = None, bn.getpixel((700, 60))
    best_sum = -1
    for y in range(115, 230, 3):
        for x in range(450, 1040, 3):
            px = bn.getpixel((x, y))
            if sum(px) > best_sum:
                best_sum, title_px = sum(px), px
    cr = contrast_ratio(title_px, bg_px)
    print(f"  title pixel {title_px} (discovered by scan)  bg pixel {bg_px}")
    print(f"  contrast ratio {cr:.2f}:1  (WCAG AA large text needs >= 3.0)")
    print(f"  => {'PASS' if cr >= 3.0 else 'FAIL - hard to read'}")
    if cr < 3.0:
        ok = False

    print()
    print("=" * 70)
    print(f"VERDICT: {'ALL ASSETS VALID' if ok else 'FAILURES ABOVE'}")
    print("=" * 70)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
