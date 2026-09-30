"""
sweep_cap.py - choose the amount of terminal rounding by MEASUREMENT.

CAP = 0.00  flat ends (what the mark had)
CAP = 1.00  fully semicircular ends

For each value this reports:
  * collision distance to the 4 references (worst case) - does rounding
    change how close we are to Colorado / the copyright glyph / the
    bullseye / the power symbol?
  * corner count - is the terminal actually round?
  * ink fraction vs the measured top-brand median
  * 16 px structural error - does rounding survive downscaling?
  * gap chord at 16 px - is the opening still readable?

NOTHING here is optimised blindly. Rounding is a STYLE decision the user
asked for; the sweep exists to pick the value that costs the least on
every metric that already has a measured target, and to prove that the
choice does not quietly break something.
"""

import math
import numpy as np
from PIL import Image, ImageDraw

import coinkins_mark as CM
import collide as CO
import measure_endcaps as ME

RES = 512
T_INK = 0.2976       # measured median of 11 real top-brand marks


def mask(cap, res=RES, span=1.15):
    """Render the mark's ring+disc into collide.py's framing convention so
    the collision numbers are directly comparable to the baseline."""
    n = res * 4
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    scale = (n / 2.0) / span / CM.R_OUTER_U    # px per U-radius unit
    c = n / 2.0
    CM._ring_with_gap(d, c, c, CM.R_OUTER_U * scale, CM.R_INNER_U * scale,
                      CM.GAP_HALF_DEG, 255, cap=cap)
    rd = CM.R_DISC_U * scale
    d.ellipse([c - rd, c - rd, c + rd, c + rd], fill=255)
    img = img.resize((res, res), Image.LANCZOS)
    return (np.asarray(img) > 127).astype(np.uint8)


def ring_only(cap, res=1024):
    img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(img)
    U = res / CM.U_DIV
    c = res / 2.0
    CM._ring_with_gap(d, c, c, CM.R_OUTER_U * U, CM.R_INNER_U * U,
                      CM.GAP_HALF_DEG, 255, cap=cap)
    return np.asarray(img)


def err16(cap):
    """Structural error between a true 16px render and a downscaled one."""
    keep = CM.CAP
    try:
        CM.CAP = cap
        big = CM.silhouette(400).convert('L').resize((16, 16), Image.LANCZOS)
        sml = CM.silhouette(16).convert('L')
        a = np.asarray(big).astype(float)
        b = np.asarray(sml).astype(float)

        def norm(x):
            lo, hi = x.min(), x.max()
            return (x - lo) / (hi - lo) if hi > lo else x * 0 + 0.5
        return float(np.abs(norm(a) - norm(b)).mean())
    finally:
        CM.CAP = keep


def main():
    caps = [0.0, 0.25, 0.5, 0.75, 1.0]
    refs = CO.references(res=RES)

    print('=' * 100)
    print('TERMINAL ROUNDING SWEEP')
    print('geometry r_out=%.2f r_in=%.2f r_disc=%.2f gap=%.1fdeg'
          % (CM.R_OUTER_U, CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG))
    print('=' * 100)
    print('  %-6s %-8s %-8s %-9s %-9s %-8s %s'
          % ('CAP', 'corners', 'ink', 'd_ink', 'worstD1', 'err16',
             'D1 per ref (colo/copy/bull/pwr)'))

    rows = []
    for cap in caps:
        A = mask(cap)
        d1s = []
        for name, M, pb in refs:
            _, dr, _ = CO.d1_iou(A, M, res=RES, rotations=range(0, 360, 10))
            d1s.append(dr)
        ncorn, _ = ME.analyse(ring_only(cap), 'cap=%.2f' % cap, verbose=False)
        ink = float(A.sum()) / (RES * RES) * (2 * 1.15) ** 2 \
            * (CM.R_OUTER_U ** 2) / (CM.U_DIV ** 2)
        e16 = err16(cap)
        rows.append(dict(cap=cap, corners=ncorn, ink=ink, worst=min(d1s),
                         d1s=d1s, err16=e16))
        print('  %-6.2f %-8d %-8.4f %-9.4f %-9.4f %-8.4f %s'
              % (cap, ncorn, ink, abs(ink - T_INK), min(d1s), e16,
                 ' '.join('%.3f' % v for v in d1s)))

    base = rows[0]
    print()
    print('=' * 100)
    print('READING THE TABLE')
    print('=' * 100)
    print('  flat (CAP=0.00) is the reference row.')
    for r in rows[1:]:
        print('  CAP=%.2f : corners %d->%d   worst collision %+.4f   '
              'ink distance %+.4f   16px error %+.4f'
              % (r['cap'], base['corners'], r['corners'],
                 r['worst'] - base['worst'],
                 abs(r['ink'] - T_INK) - abs(base['ink'] - T_INK),
                 r['err16'] - base['err16']))
    print()
    full = rows[-1]
    print('  FULL rounding (CAP=1.00):')
    print('    - removes all %d sharp terminals' % base['corners'])
    print('    - changes worst-case collision by %+.4f (%+.1f%%)'
          % (full['worst'] - base['worst'],
             100 * (full['worst'] - base['worst']) / base['worst']))
    print('    - moves ink fraction %.4f -> %.4f (target %.4f)'
          % (base['ink'], full['ink'], T_INK))
    print('    - 16px structural error %.4f -> %.4f'
          % (base['err16'], full['err16']))
    print()
    print('  NOTE: rounding is a STYLE choice, so the collision column is')
    print('  reported for honesty, not as justification. If it moves by a')
    print('  trivial amount, say so plainly rather than dressing it up.')
    return rows


if __name__ == '__main__':
    main()
