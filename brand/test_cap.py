"""
test_cap.py - prove the rounded terminal is geometrically CORRECT before
any aesthetic claim is made about it.

A round cap is easy to fake and easy to get subtly wrong. The specific
failure modes this file rules out:

  F1 the mark GROWS - the cap bulges past r_out, so the logo no longer
     fits its own box and every size/safe-zone number becomes wrong
  F2 the cap is not tangent - it pokes past the outer edge or falls
     short of the inner edge, leaving a visible notch or bump
  F3 a SEAM - the cap is a separate shape whose outline does not match
     the ring's, visible as a hairline at small sizes
  F4 corners remain - the "rounding" did not actually remove the sharp
     vertices, so the whole change is cosmetic noise
  F5 the gap closes - the rounding eats the opening until the ring reads
     as a closed circle (which would destroy the only asymmetry we have)
  F6 asymmetry - the two ends are not mirror images
"""

import math
import numpy as np
from PIL import Image, ImageDraw

import coinkins_mark as CM
import measure_endcaps as ME

RES = 1024


def render(cap, res=RES):
    img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(img)
    U = res / CM.U_DIV
    c = res / 2.0
    CM._ring_with_gap(d, c, c, CM.R_OUTER_U * U, CM.R_INNER_U * U,
                      CM.GAP_HALF_DEG, 255, cap=cap)
    return np.asarray(img)


def main():
    ok = True

    def chk(name, cond, detail=''):
        nonlocal ok
        print('  [%s] %-56s %s' % ('PASS' if cond else 'FAIL', name, detail))
        if not cond:
            ok = False

    print('=' * 84)
    print('ROUNDED TERMINAL - GEOMETRIC CORRECTNESS')
    print('=' * 84)
    U = RES / CM.U_DIV
    c = RES / 2.0

    flat = render(0.0)
    rnd = render(CM.CAP)

    # F1 the mark must not grow
    def extent(m):
        ys, xs = np.nonzero(m > 127)
        dx = np.maximum(np.abs(xs - c), 0)
        dy = np.maximum(np.abs(ys - c), 0)
        return float(np.sqrt(dx * dx + dy * dy).max()) / U

    # The comparison must be against the FLAT render, not against the
    # ideal r_out: a rasterised circle always overshoots its analytic
    # radius by up to a pixel diagonal, and the flat version measures
    # 6.0208U for a 6.00U spec. Comparing the rounded version to the
    # ideal would therefore fail for a reason that has nothing to do
    # with the cap. What matters is that rounding does not make the mark
    # BIGGER than it already was.
    ef, er = extent(flat), extent(rnd)
    chk('F1 rounding does not enlarge the mark',
        er <= ef + 0.005,
        'flat max r=%.4fU  round max r=%.4fU  (spec %.2fU, raster '
        'overshoot is expected and identical for both)'
        % (ef, er, CM.R_OUTER_U))

    # F2 tangency: at the angle of the cap centre, ink must span the FULL
    # stroke, from r_in to r_out (the cap touches both edges)
    rm = (CM.R_OUTER_U + CM.R_INNER_U) / 2.0
    half = (CM.R_OUTER_U - CM.R_INNER_U) / 2.0
    rc = CM.CAP * half
    dtheta = math.degrees(math.asin(rc / rm))
    a_cap = CM.GAP_HALF_DEG + dtheta        # angle of the cap's centre

    def ink_at(ru, ang):
        a = math.radians(ang)
        x = int(round(c + ru * U * math.cos(a)))
        y = int(round(c + ru * U * math.sin(a)))
        if not (0 <= x < RES and 0 <= y < RES):
            return False
        return rnd[y, x] > 127

    chk('F2a cap touches the OUTER edge',
        ink_at(CM.R_OUTER_U - 0.06, a_cap),
        'probe r=%.2fU a=%.2fdeg' % (CM.R_OUTER_U - 0.06, a_cap))
    chk('F2b cap touches the INNER edge',
        ink_at(CM.R_INNER_U + 0.06, a_cap),
        'probe r=%.2fU a=%.2fdeg' % (CM.R_INNER_U + 0.06, a_cap))
    chk('F2c nothing outside r_out at the cap',
        not ink_at(CM.R_OUTER_U + 0.10, a_cap))
    chk('F2d nothing inside r_in at the cap',
        not ink_at(CM.R_INNER_U - 0.10, a_cap))

    # F3 single connected component, no seam -> one contour, no holes
    import cv2
    m = (rnd > 127).astype(np.uint8)
    # connectedComponentsWithStats returns (num_labels, labels, stats,
    # centroids); num_labels counts the background as label 0, so the
    # number of real components is num_labels - 1.
    cnt = cv2.connectedComponentsWithStats(m, connectivity=8)[0] - 1
    chk('F3 exactly one connected component (no seam, no stray cap)',
        cnt == 1, 'components=%d' % cnt)

    # F4 corners must be GONE
    nflat, sflat = ME.analyse(flat, 'flat ends', verbose=False)
    nrnd, srnd = ME.analyse(rnd, 'rounded ends', verbose=False)
    chk('F4 rounding removes the sharp terminals',
        nrnd == 0 and nflat >= 2,
        'flat corners=%d (sharpest %s)  rounded corners=%d'
        % (nflat, ' '.join('%.0f' % s for s in sflat[:2]) or '-', nrnd))

    # F5 the gap must still read as a gap
    mid = (CM.R_OUTER_U + CM.R_INNER_U) / 2.0
    empty = sum(1 for a in range(360) if not ink_at(mid, a))
    chk('F5 opening still present and substantial',
        empty >= 40, 'measured opening %d deg (flat spec %d deg)'
        % (empty, int(2 * CM.GAP_HALF_DEG)))

    # F6 mirror symmetry about the horizontal axis
    top = int(m[:RES // 2, :].sum())
    bot = int(m[RES // 2:, :].sum())
    chk('F6 the two ends are mirror images',
        abs(top - bot) <= max(4, int(0.002 * m.sum())),
        'top=%d bottom=%d diff=%d' % (top, bot, abs(top - bot)))

    # extra: how much ink does rounding remove?
    fi = float((flat > 127).sum())
    ri = float((rnd > 127).sum())
    print()
    print('  ink flat=%.5f  rounded=%.5f  change=%+.2f%%'
          % (fi / RES ** 2, ri / RES ** 2, 100 * (ri - fi) / fi))
    print('  cap radius = %.4fU = %.4f of width (derived, = CAP*stroke/2)'
          % (rc, rc / CM.U_DIV))

    print()
    print('=' * 84)
    print('CAP GEOMETRY %s' % ('VERIFIED' if ok else 'FAILED'))
    print('=' * 84)
    return ok


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
