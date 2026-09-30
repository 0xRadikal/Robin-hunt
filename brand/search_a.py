"""
search_a.py - constrained search over refinements of the APPROVED variant A.

The user approved variant A: a centred ring with a gap on the right and a
disc inside, on deep indigo. This search does NOT change that description.
It only moves the three free construction parameters:

    r_in      ring inner radius   (ring thickness = r_out - r_in)
    r_disc    disc radius         (fill ratio = r_disc / r_in)
    gap_half  half-angle of the gap

subject to HARD constraints that must all hold, then maximises the WORST
(minimum) collision distance across the references in collide.py.

HARD CONSTRAINTS (any violation = candidate rejected, no exceptions)
--------------------------------------------------------------------
 K1  every radius is a multiple of 0.25 U            (constructible, Grasser)
 K2  exactly 3 distinct radii                        (<=5, Grasser rule)
 K3  ring stroke >= 0.0365 of width   - thinnest real top-brand feature
 K4  ring stroke <= 0.2083 of width   - thickest real top-brand feature
 K5  disc does NOT touch the ring: r_disc <= r_in - 0.25U
     (proved necessary earlier: an adjacent gold/light boundary was the
      exact 1.63:1 defect that killed v2 and marks M5/M6)
 K6  ink fraction within the measured top-brand range [0.070, 0.497]
 K7  gap must read as a gap at 16 px: outer gap chord >= 1.5 px at 16 px
 K8  gap_half <= 60 deg  - beyond this it stops reading as a ring
 K9  disc radius >= 0.75U so the disc survives a 16 px raster

OBJECTIVE
---------
maximise  min(D1_bestrot over all 4 references)
tie-break on  min(D3_radial),  then on closeness of ink fraction to the
top-brand median 0.298.

Using the MINIMUM (worst case) rather than a sum is deliberate: a mark that
is far from three references but nearly identical to a fourth is not safe.
"""

import math
import itertools
import numpy as np

import collide as CO
import coinkins_mark as CM

U = 16.0            # radii are expressed in units of width/16
R_OUT = 6.0         # outer radius is FIXED - it defines the approved size
RES = 256           # search resolution (256 validated in collide.validate)

TB_INK_MIN, TB_INK_MAX = 0.070, 0.497
TB_INK_MED = 0.298
TB_THIN_MIN, TB_THIN_MAX = 0.0365, 0.2083


def constraints(r_in, r_disc, gap_half, verbose=False):
    """Return (ok, reasons). Every rejection is named."""
    bad = []
    # K1 quarter-unit
    for nm, v in (('r_in', r_in), ('r_disc', r_disc)):
        if abs(v * 4 - round(v * 4)) > 1e-9:
            bad.append('K1 %s=%.4f not a quarter-unit multiple' % (nm, v))
    # K2 three distinct radii
    radii = sorted(set([round(R_OUT, 6), round(r_in, 6), round(r_disc, 6)]))
    if len(radii) != 3:
        bad.append('K2 distinct radii = %d, need 3' % len(radii))
    # K3/K4 stroke thickness as a fraction of total width (width = 2*R_OUT/U... )
    # the mark is drawn into a box of width 16 U, so stroke/width:
    stroke_frac = (R_OUT - r_in) / U
    if stroke_frac < TB_THIN_MIN:
        bad.append('K3 stroke %.4f < %.4f' % (stroke_frac, TB_THIN_MIN))
    if stroke_frac > TB_THIN_MAX:
        bad.append('K4 stroke %.4f > %.4f' % (stroke_frac, TB_THIN_MAX))
    # K5 disc must not touch the ring
    if r_disc > r_in - 0.25:
        bad.append('K5 disc touches ring (gap %.2fU < 0.25U)' % (r_in - r_disc))
    # K9 disc must survive small raster
    if r_disc < 0.75:
        bad.append('K9 disc %.2fU < 0.75U' % r_disc)
    # K8 gap sanity
    if gap_half > 60.0:
        bad.append('K8 gap_half %.1f > 60' % gap_half)
    if gap_half < 5.0:
        bad.append('K8 gap_half %.1f < 5' % gap_half)
    # K7 gap readable at 16px: chord at outer radius, in px at 16px render
    # outer radius in px at 16px width = R_OUT/U * 16 = R_OUT
    chord_px = 2.0 * (R_OUT / U * 16.0) * math.sin(math.radians(gap_half))
    if chord_px < 1.5:
        bad.append('K7 gap chord %.2fpx < 1.5px at 16px' % chord_px)
    return (len(bad) == 0), bad


def ink_fraction(r_in, r_disc, gap_half):
    """Analytic ink fraction of the mark inside its 16U x 16U box."""
    box = U * U
    ann = math.pi * (R_OUT ** 2 - r_in ** 2) * (1.0 - gap_half / 180.0)
    disc = math.pi * r_disc ** 2
    return (ann + disc) / box


def score(r_in, r_disc, gap_half, res=RES):
    A = CO.ring_disc_mask(1.0, r_in / R_OUT, r_disc / R_OUT, gap_half,
                          0.0, res=res)
    pa = (1.0, r_in / R_OUT, r_disc / R_OUT, gap_half)
    d1s, d3s = [], []
    for name, M, pb in CO.references(res=res):
        _, dr, _ = CO.d1_iou(A, M, res=res, rotations=range(0, 360, 10))
        d1s.append(dr)
        d3s.append(CO.d3_radial(A, M))
    return min(d1s), min(d3s), d1s, d3s


def main():
    print('=' * 92)
    print('CONSTRAINED SEARCH over refinements of approved variant A')
    print('r_out FIXED at %.2fU. Searching r_in, r_disc, gap_half.' % R_OUT)
    print('=' * 92)

    r_in_vals = [x / 4.0 for x in range(int(3.0 * 4), int(5.25 * 4) + 1)]
    r_disc_vals = [x / 4.0 for x in range(int(0.75 * 4), int(4.75 * 4) + 1)]
    gap_vals = [float(g) for g in range(10, 61, 2)]

    total = len(r_in_vals) * len(r_disc_vals) * len(gap_vals)
    print('grid: r_in %d x r_disc %d x gap %d = %d combinations'
          % (len(r_in_vals), len(r_disc_vals), len(gap_vals), total))

    feasible = []
    rej = {}
    for r_in, r_disc, gap in itertools.product(r_in_vals, r_disc_vals, gap_vals):
        ok, bad = constraints(r_in, r_disc, gap)
        if not ok:
            for b in bad:
                k = b.split()[0]
                rej[k] = rej.get(k, 0) + 1
            continue
        ink = ink_fraction(r_in, r_disc, gap)
        if not (TB_INK_MIN <= ink <= TB_INK_MAX):
            rej['K6'] = rej.get('K6', 0) + 1
            continue
        feasible.append((r_in, r_disc, gap, ink))

    print('feasible after hard constraints: %d' % len(feasible))
    print('rejections by constraint: %s'
          % ', '.join('%s=%d' % kv for kv in sorted(rej.items())))
    if not feasible:
        raise SystemExit('no feasible candidate - constraints are contradictory')

    print()
    print('scoring %d feasible candidates (this is the slow part)...'
          % len(feasible))
    scored = []
    for i, (r_in, r_disc, gap, ink) in enumerate(feasible):
        mn1, mn3, d1s, d3s = score(r_in, r_disc, gap)
        scored.append({'r_in': r_in, 'r_disc': r_disc, 'gap': gap, 'ink': ink,
                       'min_d1': mn1, 'min_d3': mn3, 'd1s': d1s, 'd3s': d3s,
                       'fill': r_disc / r_in})
        if (i + 1) % 25 == 0:
            print('  %d/%d' % (i + 1, len(feasible)), flush=True)

    scored.sort(key=lambda r: (-r['min_d1'], -r['min_d3'],
                               abs(r['ink'] - TB_INK_MED)))

    # baseline for comparison
    base_mn1, base_mn3, base_d1s, base_d3s = score(
        CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG)

    print()
    print('=' * 92)
    print('BASELINE (as approved): r_in=%.2f r_disc=%.2f gap=%.1f fill=%.4f ink=%.4f'
          % (CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG,
             CM.R_DISC_U / CM.R_INNER_U,
             ink_fraction(CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG)))
    print('   min_D1 = %.4f   min_D3 = %.4f' % (base_mn1, base_mn3))
    print('   per-ref D1: %s' % ' '.join('%.4f' % v for v in base_d1s))
    print('=' * 92)
    print()
    print('TOP 15 by worst-case collision distance:')
    print('  %-6s %-7s %-6s %-7s %-7s %-8s %-8s  %s'
          % ('r_in', 'r_disc', 'gap', 'fill', 'ink', 'min_D1', 'min_D3',
             'D1 per ref (colo/copy/bull/pwr)'))
    for r in scored[:15]:
        print('  %-6.2f %-7.2f %-6.1f %-7.4f %-7.4f %-8.4f %-8.4f  %s'
              % (r['r_in'], r['r_disc'], r['gap'], r['fill'], r['ink'],
                 r['min_d1'], r['min_d3'],
                 ' '.join('%.3f' % v for v in r['d1s'])))

    print()
    print('improvement of best over baseline: min_D1 %.4f -> %.4f (%+.1f%%)'
          % (base_mn1, scored[0]['min_d1'],
             100.0 * (scored[0]['min_d1'] - base_mn1) / base_mn1))
    return scored, (base_mn1, base_mn3, base_d1s)


if __name__ == '__main__':
    main()
