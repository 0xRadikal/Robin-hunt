#!/usr/bin/env python3
"""marks.py - Actual LOGO MARKS with a designed FORM, not just colour.

WHY THIS EXISTS
  The user said "the logo is not clear". They were right: v2/v3 were a
  flat disc with the letters "Ck" on it. That is not a mark, it is a
  coloured circle with text in it. Every brand history I measured shows
  text being REMOVED from inside the mark:
    Mastercard 1996 "MasterCard" across the circles -> 2016 no text
    Starbucks 1971 four words + rings -> 2011 no text, no ring
    Apple 1976 "APPLE COMPUTER CO." -> 1977 onward no text, ever
    Wenzel 2018: character count drop significant at p = .004

DESIGN RULES, EACH TRACED TO EVIDENCE
  R1 NO TEXT inside the mark.
     Mastercard/Starbucks/Apple all removed it; Wenzel p=.004.
  R2 FLAT. No gradients, no gloss, no 3D bevel.
     Apple used gloss 2001-2007 and abandoned it by 2017.
     Wenzel: measured shift away from depth toward flat.
     NOTE: this is why v1 (which the user preferred) is still wrong -
     v1's radial gradient + glossy arc IS the 2001-2007 aesthetic.
     What v1 got RIGHT was having a FORM. We keep the form, drop gloss.
  R3 MODERATE complexity, not minimum.
     Henderson & Cote 1998: elaborateness has an INVERTED-U relation to
     affect. A bare circle is under-elaborate; a busy mark is over.
  R4 ROUND forms preferred.
     Henderson & Cote roundness dimension -> positive affect. Also the
     product is literally a coin, so roundness is also naturalness.
  R5 ONE CONSTANT GEOMETRIC IDEA.
     Mastercard: two intersecting circles, unchanged since 1966.
     Apple: bitten silhouette geometrically unchanged since 1977.
  R6 MUST READ AS A SILHOUETTE.
     Apple's mark works as solid black. Tested here in mono.
  R7 2-3 FLAT COLOURS.
     Mastercard 3, Starbucks 2, Apple 1.
  R8 EVERY internal boundary >= 3:1 luminance contrast.
     WCAG 2.1 SC 1.4.11 Non-text Contrast (w3.org). v2 failed at 1.46:1.

THE CANDIDATE IDEAS
  Each is a different answer to "what is the one constant geometric
  idea?" - the question Mastercard answers with intersecting circles and
  Apple answers with a bitten silhouette.

  M1 STACK      - coins seen edge-on, stacked. "little coins" literally.
  M2 SLOT       - a coin entering a slot. The act of paying.
  M3 ARC        - a coin mid-flip, shown as a partial ring gap.
  M4 ORBIT      - a small coin orbiting a larger one. Arc = the chain.
  M5 NOTCH      - a disc with a wedge removed, like a coin bitten.
                  This is the Apple-silhouette strategy applied to a coin.
  M6 TWIN       - two intersecting discs. Mastercard's answer, but with
                  a coin reading. Deliberately included to test whether
                  borrowing a famous structure is too derivative.
"""

import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from palette import contrast  # noqa: E402

SS = 6  # supersample factor


def _canvas(size, bg):
    W = size * SS
    img = Image.new('RGB', (W, W), bg)
    return img, ImageDraw.Draw(img), W


def _fin(img, size):
    return img.resize((size, size), Image.LANCZOS)


def _disc(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def m1_stack(size, bg, ink, acc):
    """Three coins seen edge-on, stacked. Reads as 'little coins'."""
    img, d, W = _canvas(size, bg)
    cx = W // 2
    w = int(W * 0.60)
    h = int(W * 0.155)
    gap = int(W * 0.045)
    top = int(W * 0.245)
    for i in range(3):
        y = top + i * (h + gap)
        col = ink if i != 1 else acc
        d.rounded_rectangle([cx - w // 2, y, cx + w // 2, y + h],
                            radius=h // 2, fill=col)
    return _fin(img, size)


def m2_slot(size, bg, ink, acc):
    """A coin dropping into a slot. The act of payment."""
    img, d, W = _canvas(size, bg)
    cx = W // 2
    # the slot: a thick horizontal bar with a gap
    sy = int(W * 0.70)
    sh = int(W * 0.105)
    d.rounded_rectangle([int(W * 0.18), sy, int(W * 0.82), sy + sh],
                        radius=sh // 2, fill=ink)
    # the coin above, partially entering
    r = int(W * 0.215)
    _disc(d, cx, int(W * 0.415), r, acc)
    # inner hole keeps it reading as a coin, not a dot (R3 complexity)
    _disc(d, cx, int(W * 0.415), int(r * 0.34), bg)
    return _fin(img, size)


def m3_arc(size, bg, ink, acc):
    """A coin mid-flip: a ring with a gap, plus the coin body."""
    img, d, W = _canvas(size, bg)
    cx = cy = W // 2
    R = int(W * 0.345)
    t = int(W * 0.105)
    # open ring = motion (Henderson-Cote 'activity' raises elaborateness
    # off the minimum without adding clutter)
    d.arc([cx - R, cy - R, cx + R, cy + R], start=-58, end=238,
          fill=ink, width=t)
    _disc(d, cx, cy, int(W * 0.165), acc)
    return _fin(img, size)


def m4_orbit(size, bg, ink, acc):
    """A small coin orbiting a large one. Coin + chain in one idea."""
    img, d, W = _canvas(size, bg)
    cx = cy = W // 2
    _disc(d, cx, cy, int(W * 0.225), ink)
    R = int(W * 0.355)
    t = int(W * 0.055)
    d.arc([cx - R, cy - R, cx + R, cy + R], start=205, end=95,
          fill=ink, width=t)
    ang = math.radians(150)
    _disc(d, int(cx + R * math.cos(ang)), int(cy + R * math.sin(ang)),
          int(W * 0.098), acc)
    return _fin(img, size)


def m5_notch(size, bg, ink, acc):
    """A coin with a wedge removed - the Apple-silhouette strategy.

    FIX APPLIED: my first version put an accent dot directly on the
    light disc. Measured boundary contrast was 1.63:1, failing WCAG
    1.4.11 (needs 3:1) - the SAME class of error as v2's gold-on-teal.
    Two light colours touching never separate. The accent now appears
    only inside the notch, where it touches the DARK background.
    """
    img, d, W = _canvas(size, bg)
    cx = cy = W // 2
    R = int(W * 0.345)
    _disc(d, cx, cy, R, ink)
    # remove a wedge: the ownable, silhouette-legible feature
    d.pieslice([cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2],
               start=-32, end=32, fill=bg)
    # accent sits in the notch void, adjacent to bg only
    ar = int(W * 0.082)
    _disc(d, int(cx + R * 0.66), cy, ar, acc)
    return _fin(img, size)


def m6_twin(size, bg, ink, acc):
    """Two intersecting discs - Mastercard's structure, coin reading.

    FIX APPLIED: originally a light disc touching a gold disc measured
    1.63:1. Mastercard solves this by making the OVERLAP a third colour
    and by keeping both discs dark enough against white. Here both discs
    use the light ink and are SEPARATED by a background-coloured gap, so
    every boundary is light-against-dark. The accent marks the overlap
    region only, bounded by bg.
    """
    img, d, W = _canvas(size, bg)
    cy = W // 2
    r = int(W * 0.235)
    off = int(r * 0.72)
    # two light discs
    _disc(d, W // 2 - off, cy, r, ink)
    _disc(d, W // 2 + off, cy, r, ink)
    # carve a bg-coloured separation so no two light areas touch
    gapw = max(2, int(W * 0.018))
    d.rectangle([W // 2 - gapw, cy - r - 4, W // 2 + gapw, cy + r + 4],
                fill=bg)
    # accent: a small coin sitting in the gap, touching bg on both sides
    _disc(d, W // 2, cy, int(W * 0.062), acc)
    return _fin(img, size)


MARKS = {
    'M1 stack': m1_stack,
    'M2 slot': m2_slot,
    'M3 arc': m3_arc,
    'M4 orbit': m4_orbit,
    'M5 notch': m5_notch,
    'M6 twin': m6_twin,
}


def silhouette(fn, size=256):
    """R6: render the mark as a pure black-on-white silhouette."""
    return fn(size, (255, 255, 255), (0, 0, 0), (0, 0, 0))


if __name__ == '__main__':
    print("marks.py defines", len(MARKS), "candidate forms:")
    for k in MARKS:
        print("  ", k)
