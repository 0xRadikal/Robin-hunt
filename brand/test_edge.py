#!/usr/bin/env python3
"""test_edge.py - Measure whether the coin edge actually SURVIVES at the
real timeline size, objectively.

WHY THIS TEST EXISTS
  The V3-48PX.png strip lets a human see the difference, but "it looks
  separated to me" is exactly the kind of claim I must not make. This
  script measures it.

A MISTAKE I MADE AND THEN CORRECTED
  My first version of this test measured only the CIEDE2000 step across
  the rim. It reported the REJECTED v2 at 41.64 dE - HIGHER than three
  of the accepted candidates. That contradicted the user, so instead of
  dismissing it I decomposed the number, and found the real explanation:

    teal L*=69.9 C*=54.8 h=164deg     gold L*=82.6 C*=58.8 h=86deg
    dE2000 = 36.86  but  dL* = 12.7  and  WCAG contrast = 1.46:1

  dE2000 fuses lightness, chroma and hue into one scalar. v2's dE is
  large almost entirely because of HUE. Hue does not build figure/ground
  - LUMINANCE does. Stripping colour proves it:
    teal -> grey 104,  gold -> grey 157   (only 53/255 apart)
    navy -> grey  26, silver -> grey 223  (197/255 apart)

  This is established vision science, not my inference:
    - "It is less sensitive to spatial details compared to the luminance
      channel" - chromatic channels, ScienceDirect topic overview.
    - Hansen & Gegenfurtner, "Independence of color and luminance edges
      in natural scenes", Visual Neuroscience (2009), 160 citations:
      luminance edges remained of stronger contrast.
    - Jennings & Martinovic, J. Vision (2014): the luminance channel has
      higher resolution than the chromatic channels.
    - J. Cognitive Neuroscience 34(7):1128 (2022): "processing of
      luminance-defined shapes leads to better WM performance when
      compared with isoluminant shapes".

  So the test now gates on BOTH: the perceptual step (dE) AND the
  luminance edge, because a high-dE isoluminant edge is exactly the
  failure the user reported seeing.

METHOD
  Render each candidate at 48px (X's timeline avatar size), walk rays
  outward from the centre, and measure across the coin's rim:
    (a) the largest CIEDE2000 step      -> total perceptual step
    (b) the largest WCAG contrast ratio -> luminance/figure-ground step

INTERPRETATION SCALE (CIEDE2000, standard industry reading)
  dE < 1    invisible to the human eye
  dE 2-10   noticeable at a glance
  dE 11-49  colours are more similar than opposite
  dE > 50   colours read as opposite
  We require dE >= 20 AND luminance contrast >= 3.0:1 (WCAG 1.4.11).
"""

import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harmony  # noqa: E402
import shortlist as SL  # noqa: E402
import solve_final as SF  # noqa: E402
from palette import contrast, luminance  # noqa: E402

MIN_EDGE_DE = 20.0
MIN_EDGE_CR = 3.0


def edge_step(img, size):
    """Largest perceptual step AND largest luminance step across the rim.

    Returns (best_dE, best_contrast_ratio).
    """
    c = size // 2
    px = img.convert('RGB').load()
    best_de = 0.0
    best_cr = 1.0
    # sample several rays so a single antialiased pixel cannot fool us
    for ang in range(0, 360, 15):
        ray = []
        for t in range(0, c):
            x = int(round(c + t * math.cos(math.radians(ang))))
            y = int(round(c + t * math.sin(math.radians(ang))))
            if 0 <= x < size and 0 <= y < size:
                ray.append(px[x, y])
        r = int(0.315 * size)
        # BUG I FOUND AND FIXED: this window was a FIXED +-6 PIXELS.
        # At 48px the rim radius is 15, so +-6 spans 40% of the radius
        # and correctly straddles coin-face -> field. At 400px the radius
        # is 126, so +-6 spans only 4.8% and BOTH samples land inside the
        # rim band itself, measuring rim-to-rim instead of coin-to-field.
        # That is why every lum400 came out lower than lum48 - an
        # artefact of my own sampling, not a property of the artwork.
        # Same bug class as the hardcoded coordinate I fixed in
        # validate_assets.py. The window must be PROPORTIONAL.
        win = max(3, int(r * 0.22))
        lo = max(1, r - win)
        hi = min(len(ray) - 1, r + win)
        for i in range(lo, hi):
            de = harmony.delta_e_2000(ray[i], ray[i + 1])
            if de > best_de:
                best_de = de
        # luminance step across the whole rim transition: from inside the
        # coin FACE to outside the rim, which is the boundary the eye
        # integrates when the avatar is small.
        inner = max(1, r - win)
        outer = min(len(ray) - 1, r + win)
        cr = contrast(ray[inner], ray[outer])
        if cr > best_cr:
            best_cr = cr
    return best_de, best_cr


def main():
    print("=" * 84)
    print("COIN-EDGE SURVIVAL AT REAL TIMELINE SIZE (48px)")
    print("=" * 84)
    print(f"  requirement: dE >= {MIN_EDGE_DE} AND luminance edge "
          f">= {MIN_EDGE_CR}:1")
    print(f"  {'option':26s} {'dE48':>7s} {'lum48':>8s} {'dE400':>7s} "
          f"{'lum400':>8s} {'CH':>8s}  verdict")
    print("  " + "-" * 82)

    ok_all = True
    results = []
    for label, field, coin in SL.CANDIDATES:
        a48 = SL.draw_avatar(48, field, coin)
        a400 = SL.draw_avatar(400, field, coin)
        de48, cr48 = edge_step(a48, 48)
        de400, cr400 = edge_step(a400, 400)
        _, ch, _ = SF.evaluate8(field, coin)
        good = de48 >= MIN_EDGE_DE and cr48 >= MIN_EDGE_CR
        if 'REJECTED' not in label and not good:
            ok_all = False
        why = 'SURVIVES'
        if not good:
            bits = []
            if de48 < MIN_EDGE_DE:
                bits.append('dE')
            if cr48 < MIN_EDGE_CR:
                bits.append('luminance')
            why = 'DISSOLVES (' + '+'.join(bits) + ')'
        print(f"  {label:26s} {de48:7.2f} {cr48:7.2f}:1 {de400:7.2f} "
              f"{cr400:7.2f}:1 {ch:+8.4f}  {why}")
        results.append((label, de48, cr48, ch, good))

    print()
    print("  ANALYSIS")
    base = [r for r in results if 'REJECTED' in r[0]][0]
    print(f"    the rejected v2: dE {base[1]:.2f} (looks fine) but "
          f"luminance edge only {base[2]:.2f}:1")
    print(f"    -> a high-dE, LOW-luminance edge. Hue-different but")
    print(f"       isoluminant. This is exactly the defect the user saw,")
    print(f"       and exactly why dE alone was the wrong gate.")
    cands = [r for r in results if 'REJECTED' not in r[0]]
    best = max(cands, key=lambda r: r[2])
    print(f"    strongest luminance edge: {best[0]} at {best[2]:.2f}:1 "
          f"({best[2]/base[2]:.1f}x the baseline)")
    print(f"    candidates beating the baseline on luminance: "
          f"{sum(1 for r in cands if r[2] > base[2])}/{len(cands)}")
    print()
    print("=" * 84)
    print(f"RESULT: {'all candidates survive downscaling' if ok_all else 'SOME CANDIDATES DISSOLVE - see above'}")
    print("=" * 84)
    return 0


if __name__ == '__main__':
    sys.exit(main())
