"""
solve_option_c.py - find the best "option C" compromise, by measurement.

THE REQUEST
-----------
The user supplied a reference logo and asked for LONGER white edges.
measure_ref.py measured that reference rather than guessing:

    reference white arc  302 deg   (gap half-angle 29.0 deg)
    ours                 268 deg   (gap half-angle 46.0 deg)
    reference stroke     0.3550 of r_outer
    ours                 0.2917 of r_outer

So the reference has BOTH a longer arc AND a thicker band.

THE COST, ALREADY MEASURED AND REPORTED TO THE USER
---------------------------------------------------
Colorado's statutory gap half-angle is 22.02 deg. Moving from 46 to 29
cuts the distance to Colorado from 23.98 to 6.98 deg, and the measured
worst-case collision falls 0.5004 -> 0.4351, i.e. -13%, wiping out the
+14.3% that was gained earlier.

The user chose OPTION C: go as long as possible while KEEPING the
collision gain. This module finds that point instead of picking a
round number.

FORMULATION
-----------
    OBJECTIVE   maximise the white arc (= minimise gap_half)
                because that is literally what the user asked for

    CONSTRAINT  worst-case collision distance must not fall below the
                value we already banked (0.5004 at the current geometry)

    CONSTRAINT  every hard construction rule from search_a2 still holds
                (quarter-unit radii, 3 distinct radii, stroke inside the
                measured top-brand range, 0.25U disc clearance, ink
                inside the measured range, gap readable at 16px)

    TIE-BREAK   prefer the candidate whose STROKE is closer to the
                reference's 0.3550, since a thicker band is the other
                half of what the user pointed at, and prefer lower Q.

Both r_in and gap_half are swept: a thicker band changes the collision
geometry, so restricting the search to gap alone would miss the real
optimum. This is a 2-D search, not a 1-D one.
"""

import json
import math
import os
import itertools
import numpy as np

import collide as CO
import coinkins_mark as CM
import search_a2 as S2

U = 16.0
R_OUT = 6.0
RES = 256

# what we must not lose: the collision distance of the CURRENT geometry
BASELINE_GEOM = dict(r_in=4.25, r_disc=3.00, gap=46.0)

# what the reference actually measured (from measure_ref.py)
REF = dict(arc=302.0, gap_half=29.0, stroke_frac_of_router=0.3550,
           r_in_over_router=0.6450, fill=0.6714)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'option_c_cache.json')


def worst_collision(r_in, r_disc, gap, res=RES):
    A = CO.ring_disc_mask(1.0, r_in / R_OUT, r_disc / R_OUT, gap, 0.0,
                          res=res)
    ds = []
    for name, M, pb in CO.references(res=res):
        _, dr, _ = CO.d1_iou(A, M, res=res, rotations=range(0, 360, 10))
        ds.append(dr)
    return min(ds), ds


def build():
    """Score every feasible (r_in, r_disc, gap) with the SAME hard
    constraints search_a2 used, so nothing is quietly relaxed."""
    r_in_vals = [x / 4.0 for x in range(int(3.0 * 4), int(5.25 * 4) + 1)]
    r_disc_vals = [x / 4.0 for x in range(int(0.75 * 4), int(4.75 * 4) + 1)]
    gap_vals = [float(g) for g in range(10, 61, 2)]

    feas = []
    for r_in, r_disc, gap in itertools.product(r_in_vals, r_disc_vals,
                                               gap_vals):
        ok, _bad = S2.constraints(r_in, r_disc, gap)
        if not ok:
            continue
        ink = S2.ink_fraction(r_in, r_disc, gap)
        if not (S2.TB_INK_MIN <= ink <= S2.TB_INK_MAX):
            continue
        feas.append((r_in, r_disc, gap))
    print('feasible under the SAME hard constraints: %d' % len(feas),
          flush=True)

    rows = []
    for i, (r_in, r_disc, gap) in enumerate(feas):
        w, ds = worst_collision(r_in, r_disc, gap)
        Q, det = S2.quality(r_in, r_disc, gap)
        rows.append(dict(r_in=r_in, r_disc=r_disc, gap=gap,
                         arc=360.0 - 2 * gap,
                         stroke_router=(R_OUT - r_in) / R_OUT,
                         fill=r_disc / r_in,
                         worst=w, d1s=ds, Q=Q, ink=det['ink'],
                         err16=det['err16']))
        if (i + 1) % 50 == 0:
            print('  %d/%d' % (i + 1, len(feas)), flush=True)
    with open(CACHE, 'w') as fh:
        json.dump(rows, fh)
    return rows


def load():
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            return json.load(fh)
    return build()


def main():
    rows = load()

    def find(r_in, r_disc, gap):
        for r in rows:
            if (abs(r['r_in'] - r_in) < 1e-9 and
                    abs(r['r_disc'] - r_disc) < 1e-9 and
                    abs(r['gap'] - gap) < 1e-9):
                return r
        return None

    base = find(**{'r_in': BASELINE_GEOM['r_in'],
                   'r_disc': BASELINE_GEOM['r_disc'],
                   'gap': BASELINE_GEOM['gap']})
    if base is None:
        raise SystemExit('baseline geometry not in the feasible set')

    FLOOR = base['worst']

    print('=' * 100)
    print('OPTION C - longest white arc that KEEPS the collision gain')
    print('=' * 100)
    print('  CURRENT  r_in=%.2f r_disc=%.2f gap=%.1f -> arc %.0f deg  '
          'worst=%.4f  Q=%.4f  stroke=%.4f'
          % (base['r_in'], base['r_disc'], base['gap'], base['arc'],
             base['worst'], base['Q'], base['stroke_router']))
    print('  REFERENCE (measured)                     arc %.0f deg  '
          'stroke=%.4f  fill=%.4f'
          % (REF['arc'], REF['stroke_frac_of_router'], REF['fill']))
    print('  COLLISION FLOOR set to the current value: %.4f' % FLOOR)
    print()

    # what the pure reference match would cost (gap 28 or 30, nearest grid)
    print('  For reference, matching the user image exactly:')
    for g in (28.0, 30.0):
        r = find(4.25, 3.00, g)
        if r:
            print('    gap=%.0f -> arc %.0f deg  worst=%.4f (%+.1f%%)  Q=%.4f'
                  % (g, r['arc'], r['worst'],
                     100 * (r['worst'] - FLOOR) / FLOOR, r['Q']))
    print()

    # OPTION C: keep collision >= FLOOR, maximise the arc.
    #
    # A QUALITY FLOOR IS ALSO REQUIRED, and leaving it out was a real
    # defect in the first version of this search. With only the collision
    # constraint, the winner was gap=10 deg (arc 340) achieved by
    # SHRINKING THE DISC from 3.00U to 1.50U: the collision distance was
    # preserved by wrecking the coin instead of by the arc, and Q jumped
    # 0.2126 -> 0.3147, i.e. 48% worse. That is the same degenerate
    # behaviour as maximising collision distance outright, which produced
    # a hairline ring, and as maximising Ou-Luo harmony, which produced
    # olive. Third occurrence of one class of mistake, so it is now
    # constrained explicitly:
    #
    #   Q must not get worse than the current geometry's Q
    #   the disc must stay at 3.00U, because the user approved the coin
    #     size and this task is about the ARC, not the coin
    Q_FLOOR = base['Q']
    cand = [r for r in rows
            if r['worst'] >= FLOOR
            and r['Q'] <= Q_FLOOR
            and abs(r['r_disc'] - BASELINE_GEOM['r_disc']) < 1e-9]
    print('  collision floor %.4f, quality floor %.4f, disc fixed at %.2fU'
          % (FLOOR, Q_FLOOR, BASELINE_GEOM['r_disc']))
    print('  candidates meeting ALL THREE: %d' % len(cand))
    if not cand:
        print()
        print('  none. Relaxing the quality floor to the reference midpoint')
        print('  would be a judgement call, so it is reported, not taken.')
        # show how close we can get while keeping collision + disc only
        alt = [r for r in rows
               if r['worst'] >= FLOOR
               and abs(r['r_disc'] - BASELINE_GEOM['r_disc']) < 1e-9]
        if alt:
            a = min(alt, key=lambda r: r['gap'])
            print('  best arc with collision+disc held: gap=%.1f arc=%.0f '
                  'Q=%.4f (%+.1f%% vs current)'
                  % (a['gap'], a['arc'], a['Q'],
                     100 * (a['Q'] - Q_FLOOR) / Q_FLOOR))
        raise SystemExit('no candidate satisfies all three constraints')

    # longest arc == smallest gap
    min_gap = min(r['gap'] for r in cand)
    longest = [r for r in cand if abs(r['gap'] - min_gap) < 1e-9]
    print('  smallest gap that still clears the floor: %.1f deg '
          '(arc %.0f deg)' % (min_gap, 360 - 2 * min_gap))
    print()
    print('  all candidates at that gap, ranked by closeness to the '
          'reference stroke then Q:')
    longest.sort(key=lambda r: (abs(r['stroke_router'] -
                                    REF['stroke_frac_of_router']), r['Q']))
    print('  %-7s %-8s %-6s %-7s %-9s %-8s %-8s %-8s'
          % ('r_in', 'r_disc', 'gap', 'fill', 'stroke', 'worst', 'Q', 'ink'))
    for r in longest[:8]:
        print('  %-7.2f %-8.2f %-6.1f %-7.4f %-9.4f %-8.4f %-8.4f %-8.4f'
              % (r['r_in'], r['r_disc'], r['gap'], r['fill'],
                 r['stroke_router'], r['worst'], r['Q'], r['ink']))

    print()
    print('=' * 100)
    print('ARC SWEEP - the cost of each extra degree of white arc')
    print('=' * 100)
    print('  %-6s %-6s %-9s %-9s %-8s %-8s %-9s %s'
          % ('gap', 'arc', 'best_worst', 'vs floor', 'r_in', 'r_disc', 'Q',
             'verdict'))
    picks = {}
    for g in sorted({r['gap'] for r in rows}):
        at = [r for r in rows if abs(r['gap'] - g) < 1e-9]
        if not at:
            continue
        b = max(at, key=lambda r: r['worst'])
        keeps = b['worst'] >= FLOOR
        picks[g] = b
        print('  %-6.0f %-6.0f %-9.4f %-+9.4f %-8.2f %-8.2f %-9.4f %s'
              % (g, 360 - 2 * g, b['worst'], b['worst'] - FLOOR,
                 b['r_in'], b['r_disc'], b['Q'],
                 'KEEPS gain' if keeps else 'loses gain'))

    print()
    print('=' * 100)
    best = longest[0]
    print('RECOMMENDED OPTION C')
    print('=' * 100)
    print('  r_in=%.2f  r_disc=%.2f  gap_half=%.1f deg' %
          (best['r_in'], best['r_disc'], best['gap']))
    print('  white arc  %.0f deg  (was %.0f, reference %.0f)'
          % (best['arc'], base['arc'], REF['arc']))
    print('  recovers %.0f%% of the way from ours to the reference'
          % (100 * (best['arc'] - base['arc']) /
             (REF['arc'] - base['arc'])))
    print('  collision %.4f -> %.4f (%+.2f%%, floor was %.4f)'
          % (base['worst'], best['worst'],
             100 * (best['worst'] - base['worst']) / base['worst'], FLOOR))
    print('  Q         %.4f -> %.4f (%+.2f%%)'
          % (base['Q'], best['Q'],
             100 * (best['Q'] - base['Q']) / base['Q']))
    print('  stroke    %.4f -> %.4f (reference %.4f)'
          % (base['stroke_router'], best['stroke_router'],
             REF['stroke_frac_of_router']))
    print('  ink       %.4f -> %.4f (top-brand median %.4f)'
          % (base['ink'], best['ink'], S2.T_INK))
    return base, best, picks


if __name__ == '__main__':
    main()
