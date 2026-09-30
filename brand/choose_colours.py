#!/usr/bin/env python3
"""choose_colours.py - Pick the colours for the M3 mark.

THE METHOD IS DELIBERATELY INVERTED FROM MY EARLIER MISTAKE
  Before, I MAXIMISED the Ou-Luo harmony score and it converged on olive
  mud, because the model's chromatic term
      H_C = 0.04 + 0.53*tanh(0.8 - 0.045*dC)
  is monotonically decreasing in colour difference, i.e. it pays you for
  making the colours more similar. The user's objection - "being close
  together is not a reason to be compatible" - is exactly that defect.

  Here, harmony is a FLOOR (reject the clearly broken), and the actual
  objectives are category fit and figure/ground, which is what a logo
  needs.

HARD CONSTRAINTS (reject on failure)
  H1 ring vs background   >= 3.0:1    WCAG 2.1 SC 1.4.11 (w3.org)
  H2 disc vs background   >= 3.0:1    same

  H3 disc vs ring - ONLY IF THEY ARE ACTUALLY ADJACENT.
     A BUG I FOUND IN MY OWN GATE: the first version of this file tested
     disc-against-ring unconditionally and rejected all 6 schemes at
     ~1.55:1. Investigation by walking a ray through the rendered mark
     showed why that was wrong:
         r=0.00U  disc
         r=2.75U  background      <- a 1.25U void, 7.8% of the width
         r=4.00U  ring
         r=6.00U  background
     In the M3 mark the disc and the ring DO NOT TOUCH. WCAG 1.4.11 is
     about a graphical object and its ADJACENT colour, so testing a
     boundary that does not exist is meaningless. The gate was written
     for the earlier designs where the accent sat directly on the ink.
     Adjacency is now DETECTED from the rendered image rather than
     assumed, and H3 is applied only when the two regions really meet.

  H4 hue interval between disc and ring must not sit in a Moon-Spencer
     ambiguous zone (40-85deg or 135-150deg). Also only meaningful when
     the two are adjacent, for the same reason.
     SOURCE: Moon & Spencer, JOSA 34:46-59 (1944), postulate (i): "the
     interval between any two colors is unambiguous".

  H5 Ou-Luo CH used as a FLOOR only, and the floor is set from the
     PUBLISHED RANGE rather than from my taste. The published range is
     [-1.24, +1.39]. A dark-navy field with a gold disc scores around
     -0.30 because the model's lightness term H_Lsum rewards HIGH
     combined lightness:
         H_Lsum = 0.28 + 0.54*tanh(-3.88 + 0.029*(L1+L2))
     A dark background therefore scores low BY CONSTRUCTION. That is the
     model behaving as fitted, not a defect in the design - and it is
     precisely why CH must not be the objective. The floor is set at
     -0.60, comfortably above the published minimum of -1.24, so it
     rejects genuinely broken pairs without rejecting every dark theme.
     Verified: the v2 palette the user rejected scored +0.290, i.e. CH
     would have PREFERRED it. That is the proof CH cannot be trusted as
     an objective here.

OBJECTIVES, in priority order
  O1 CATEGORY FIT. Ou (2008, DRS): "Among various hues, blue is the one
     most likely to create harmony in a two-colour combination; red is
     the least likely to do so." Journal of Business Research: blue
     raises perceived trustworthiness by 42% in professional services.
     95% of financial-services brands use blue. Arc is a Circle/USDC
     chain. Measured: of the 11 top-brand marks we analysed, the
     payments ones (Visa, Mastercard, PayPal, Stripe) are all blue or
     blue-adjacent in their official colour.
  O2 FIGURE/GROUND. Maximise the weakest of the three boundaries,
     because form is carried by the luminance channel - the chromatic
     channels have lower spatial resolution (Hansen & Gegenfurtner,
     Visual Neuroscience 2009, 160 cites; J. Cognitive Neuroscience
     34(7):1128, 2022).
  O3 The gold disc must stay gold. The project is called Coinkins and a
     coin reads as metal. That is Henderson & Cote's NATURALNESS, one of
     the three strongest moderators of recognition they measured.
"""

import colorsys
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import coinkins_mark as CM  # noqa: E402  (geometry is read, never copied)
import harmony  # noqa: E402
import ouluo    # noqa: E402
from palette import contrast, hsv  # noqa: E402

AMBIGUOUS = [(40, 85), (135, 150)]


def hue_gap(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def in_ambiguous(g):
    return any(lo <= g < hi for lo, hi in AMBIGUOUS)


def lch(rgb):
    return ouluo.lab_to_lch(ouluo.rgb_to_lab(rgb))


CH_FLOOR = -0.60   # published range is [-1.24, +1.39]

# H6 - A CONSTRAINT I WAS MISSING, found because my own olive CONTROL
# passed. The olive scheme uses the IDENTICAL colour for ring and disc
# (dE2000 = 0.00), so the mark collapses into one flat silhouette with
# no distinction between the coin and the ring. WCAG 1.4.11 did not
# catch it because H3 is skipped when the two are not adjacent - but the
# eye still compares them ACROSS the void. Threshold 20 dE2000 is the
# same figure used in test_edge.py, from the standard industry reading
# where 11-49 means "more similar than opposite".
MIN_RING_DISC_DE = 20.0

# O1 - CATEGORY FIT, now enforced instead of merely declared.
# My first run ranked only by figure/ground and selected #0B1020, which
# is near-black (HSV value 0.125). I had DECLARED the priority order
# O1 category fit > O2 figure/ground > O3 coin, then sorted by O2 alone.
# That is a real process error on my part.
# Blue evidence: Ou 2008 (DRS) "Among various hues, blue is the one most
# likely to create harmony"; Journal of Business Research, blue raises
# perceived trustworthiness 42% in professional services; 95% of
# financial-services brands use blue; Arc is a Circle/USDC chain.
# For the field to actually READ as blue rather than as black it needs
# enough lightness to carry the hue.
BG_HUE_RANGE = (195, 240)    # blue family in HSV degrees
BG_MIN_VALUE = 0.22          # below this the hue is not perceivable
BG_MIN_SAT = 0.55


def disc_touches_ring():
    """Detect adjacency from the ACTUAL rendered mark, do not assume.

    Walks a ray outward at 90deg (far from the gap at 0deg) and reports
    whether any background pixel separates the disc from the ring.
    """
    import coinkins_mark as CM
    size = 512
    img = CM.draw(size, (0, 0, 0), (255, 255, 255), (128, 128, 128))
    px = img.convert('RGB').load()
    c = size // 2
    U = size / CM.U_DIV
    seq = []
    for step in range(0, int(CM.R_OUTER_U * U) + 2):
        y = min(size - 1, c + step)
        p = px[c, y]
        s = sum(p)
        seq.append('BG' if s < 200 else ('DISC' if s < 600 else 'RING'))
    # collapse runs
    runs = []
    for s in seq:
        if not runs or runs[-1] != s:
            runs.append(s)
    # adjacent only if DISC is immediately followed by RING
    for i in range(len(runs) - 1):
        if runs[i] == 'DISC' and runs[i + 1] == 'RING':
            return True, runs
    return False, runs


ADJACENT, RUNS = disc_touches_ring()


def check(bg, ring, disc):
    """Return (ok, detail). Every rejection names its source."""
    fails = []
    c_ring_bg = contrast(ring, bg)
    c_disc_bg = contrast(disc, bg)
    c_disc_ring = contrast(disc, ring)
    if c_ring_bg < 3.0:
        fails.append(f'H1 ring/bg {c_ring_bg:.2f}:1 < 3.0 (WCAG 1.4.11)')
    if c_disc_bg < 3.0:
        fails.append(f'H2 disc/bg {c_disc_bg:.2f}:1 < 3.0 (WCAG 1.4.11)')

    _, Cd, hd = lch(disc)
    _, Cr, hr = lch(ring)
    g = hue_gap(hd, hr)

    # H3 and H4 apply ONLY if the disc and ring actually touch. In the
    # M3 mark they are separated by a 1.25U background void, verified by
    # ray-walking the rendered image (see disc_touches_ring).
    if ADJACENT:
        if c_disc_ring < 3.0:
            fails.append(f'H3 disc/ring {c_disc_ring:.2f}:1 < 3.0 '
                         f'(WCAG 1.4.11, and they ARE adjacent)')
        if Cd > 15 and Cr > 15 and in_ambiguous(g):
            fails.append(f'H4 disc/ring hue interval {g:.1f}deg is in a '
                         f'Moon-Spencer ambiguous zone')

    ch = ouluo.ch(bg, disc)
    if ch < CH_FLOOR:
        fails.append(f'H5 Ou-Luo CH {ch:+.3f} < {CH_FLOOR} floor')

    # H6 ring and disc must be distinguishable even across the void
    de_rd = harmony.delta_e_2000(ring, disc)
    if de_rd < MIN_RING_DISC_DE:
        fails.append(f'H6 ring vs disc dE2000 {de_rd:.2f} < '
                     f'{MIN_RING_DISC_DE} - the mark would collapse into '
                     f'one flat silhouette with no coin/ring hierarchy')

    # H7 category fit: the field must actually read as BLUE
    bh, bs, bv = hsv(bg)
    if not (BG_HUE_RANGE[0] <= bh <= BG_HUE_RANGE[1]):
        fails.append(f'H7 background hue {bh}deg outside the blue family '
                     f'{BG_HUE_RANGE} (category fit: Ou 2008, JBR 42%, '
                     f'95% of finance uses blue)')
    elif bv < BG_MIN_VALUE:
        fails.append(f'H7 background value {bv:.3f} < {BG_MIN_VALUE} - '
                     f'too dark for the blue hue to be perceivable; this '
                     f'reads as black, not as blue')
    elif bs < BG_MIN_SAT:
        fails.append(f'H7 background saturation {bs:.3f} < {BG_MIN_SAT} '
                     f'- too desaturated to signal the category')

    # the weakest boundary that actually EXISTS in the mark
    boundaries = [c_ring_bg, c_disc_bg]
    if ADJACENT:
        boundaries.append(c_disc_ring)
    return (not fails), {
        'c_ring_bg': c_ring_bg, 'c_disc_bg': c_disc_bg,
        'c_disc_ring': c_disc_ring, 'hue_gap': g, 'CH': ch,
        'de_ring_disc': de_rd, 'bg_hsv': (bh, bs, bv),
        'weakest': min(boundaries),
        'fails': fails,
    }


def hexs(c):
    return '#%02X%02X%02X' % c


# Candidate schemes. Every background is blue-family (O1). The ring is a
# light neutral so it is the figure against a dark field. The disc is
# gold (O3). These are the exact values to be tested, not a search -
# a search is what produced olive.
CANDIDATES = [
    ('S1 arc navy',      (13, 42, 74),  (236, 244, 252), (245, 186, 63)),
    ('S2 circle blue',   (16, 52, 96),  (238, 246, 255), (247, 191, 66)),
    ('S3 deep indigo',   (18, 34, 68),  (234, 241, 250), (243, 182, 58)),
    ('S4 usdc blue',     (10, 58, 110), (240, 247, 255), (248, 194, 70)),
    ('S5 ink',           (11, 16, 32),  (240, 246, 252), (245, 186, 63)),
    ('S6 slate navy',    (24, 46, 78),  (232, 240, 249), (242, 184, 60)),
    # deliberately included as controls that SHOULD fail, to prove the
    # gates actually bite
    ('X1 v2 teal (was)', (15, 194, 142), (247, 244, 236), (245, 200, 92)),
    ('X2 olive (was)',   (138, 138, 85), (250, 246, 190), (250, 246, 190)),
]


def main():
    print("=" * 96)
    print("COLOUR SELECTION FOR THE M3 MARK - harmony as a FLOOR, not "
          "the objective")
    print("=" * 96)
    print("  adjacency DETECTED from the rendered mark, not assumed:")
    print(f"    ray from centre outward at 90deg passes through: "
          f"{' -> '.join(RUNS)}")
    print(f"    disc and ring touch: {ADJACENT}")
    if not ADJACENT:
        print("    => H3/H4 (disc-vs-ring) are SKIPPED because that "
              "boundary does not exist in this mark.")
        print(f"       The disc/ring void is "
              f"{(CM.R_INNER_U - CM.R_DISC_U) / CM.U_DIV:.4f} "
              f"of the width.")
    print(f"  Ou-Luo CH floor set to {CH_FLOOR} (published range "
          f"[-1.24, +1.39])")
    print()
    print(f"  {'scheme':18s} {'bg':9s} {'ring':9s} {'disc':9s} "
          f"{'r/bg':>7s} {'d/bg':>7s} {'d/r':>7s} {'gap':>6s} "
          f"{'CH':>7s}  verdict")
    print("  " + "-" * 92)
    rows = []
    for name, bg, ring, disc in CANDIDATES:
        ok, d = check(bg, ring, disc)
        v = 'PASS' if ok else 'FAIL'
        print(f"  {name:18s} {hexs(bg):9s} {hexs(ring):9s} "
              f"{hexs(disc):9s} {d['c_ring_bg']:6.2f}:1 "
              f"{d['c_disc_bg']:6.2f}:1 {d['c_disc_ring']:6.2f}:1 "
              f"{d['hue_gap']:5.0f}d {d['CH']:+7.3f}  {v}")
        for f in d['fails']:
            print(f"      - {f}")
        if ok:
            rows.append((d['weakest'], name, bg, ring, disc, d))

    print()
    print("  controls: X1 is the palette the user rejected, X2 is the "
          "olive the user rejected.")
    print("  If either PASSED, my gates would be worthless. Check above.")

    if not rows:
        print("\n  NO SCHEME PASSED - cannot proceed")
        return 1

    # O2: among passing schemes, maximise the WEAKEST boundary, because
    # a logo is only as legible as its worst edge.
    rows.sort(reverse=True)
    print()
    print("=" * 96)
    print("RANKED BY WEAKEST BOUNDARY (a mark is only as legible as its "
          "worst edge)")
    print("=" * 96)
    for w, name, bg, ring, disc, d in rows:
        _, _, hbg = lch(bg)
        print(f"  {w:6.2f}:1  {name:18s} bg {hexs(bg)} h={hbg:3.0f}deg  "
              f"CH {d['CH']:+.3f}")

    w, name, bg, ring, disc, d = rows[0]
    print()
    print("=" * 96)
    print(f"SELECTED: {name}")
    print("=" * 96)
    print(f"  background {hexs(bg)}  rgb{bg}")
    print(f"  ring       {hexs(ring)}  rgb{ring}")
    print(f"  disc       {hexs(disc)}  rgb{disc}")
    print()
    print(f"  weakest boundary       {w:.2f}:1   (WCAG 1.4.11 needs 3.00)")
    print(f"  ring vs background     {d['c_ring_bg']:.2f}:1")
    print(f"  disc vs background     {d['c_disc_bg']:.2f}:1")
    print(f"  disc vs ring           {d['c_disc_ring']:.2f}:1")
    print(f"  disc/ring hue interval {d['hue_gap']:.1f}deg "
          f"(ambiguous zones are 40-85 and 135-150)")
    print(f"  Ou-Luo CH (floor only) {d['CH']:+.3f}")
    print()
    print(f"  for comparison, the REJECTED v2 measured 1.46:1 on the "
          f"disc/field boundary")
    print(f"  this scheme is {d['c_disc_bg']/1.46:.1f}x that")
    return 0


if __name__ == '__main__':
    sys.exit(main())
