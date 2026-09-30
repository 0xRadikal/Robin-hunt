"""
search_a2.py - CORRECTED search over refinements of approved variant A.

WHY THIS FILE EXISTS (a recorded methodological error)
------------------------------------------------------
search_a.py maximised the worst-case collision distance. It converged on
r_in=5.25U, r_disc=0.75U, gap=10deg -> a HAIRLINE ring with a tiny dot,
ink fraction 0.1047, min_D1 0.9574 (+112% over baseline).

That is a degenerate win. The shape scores well only because it barely
resembles ANY compact mark, including a good one. It is exactly the same
category error as maximising Ou & Luo colour harmony, which converged on
olive #8A8A55 because harmony is monotonically increasing in colour
SIMILARITY. In both cases I optimised a quantity that should have been a
CONSTRAINT.

CORRECTED FORMULATION
---------------------
  CONSTRAINT : min_D1 >= FLOOR  (collision distance must merely be enough)
  OBJECTIVE  : logo QUALITY, measured against the 11 real top brands

Quality Q is a weighted distance-to-target, all targets MEASURED, not
invented (from topbrand_metrics.json medians):

  Q1  ink fraction        target 0.298   (measured median)
  Q2  stroke thickness    target 0.1146  (measured median thinnest feature)
  Q3  bbox fill           target 0.596   (measured median)
  Q4  small-size survival minimise 16px structural error
  Q5  gap legibility      gap chord at 16px, want >= 2.0px comfortably

Lower Q = closer to how real top-brand marks are actually proportioned.

The FLOOR is set from the data, not picked to flatter a favourite: it is
the value that the baseline must be beaten by a stated margin.
"""

import json
import math
import os
import itertools
import numpy as np
from PIL import Image

import collide as CO
import coinkins_mark as CM

U = 16.0
R_OUT = 6.0
RES = 256

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'search_a2_cache.json')

# ---- measured top-brand targets (loaded, never hardcoded blind) ----
_tbf = os.path.join(HERE, 'topbrand_metrics.json')
if not os.path.exists(_tbf):
    raise SystemExit('topbrand_metrics.json missing - run measure_topbrands.py')
with open(_tbf) as fh:
    TB = json.load(fh)


def _med(key):
    """Median of `key` across the 11 measured top brands.

    NO FALLBACK ON PURPOSE. An earlier version of this function took a
    `fallback` argument and I queried the thickness median under the wrong
    key name ('thinnest' instead of the actual 'stroke_min_frac'). The
    fallback silently absorbed the mistake and happened to equal the true
    median (0.1146), so the number came out RIGHT BY LUCK while the code
    was reading nothing at all. A wrong-but-plausible number is worse than
    a crash, so this now raises instead.
    """
    if not isinstance(TB, dict) or not TB:
        raise SystemExit('topbrand_metrics.json is not a brand->metrics map')
    vals = []
    for brand, m in TB.items():
        if not isinstance(m, dict) or key not in m:
            raise SystemExit('brand %r has no metric %r - keys: %s'
                             % (brand, key,
                                sorted(m.keys()) if isinstance(m, dict) else m))
        vals.append(float(m[key]))
    if len(vals) < 11:
        raise SystemExit('expected >=11 brands for %r, got %d' % (key, len(vals)))
    return float(np.median(vals))


T_INK = _med('ink_fraction')
T_THIN = _med('stroke_min_frac')     # correct key, verified against the file
T_BBOX = _med('bbox_fill')
N_BRANDS = len(TB)
TB_INK_MIN, TB_INK_MAX = 0.070, 0.497
TB_THIN_MIN, TB_THIN_MAX = 0.0365, 0.2083


def constraints(r_in, r_disc, gap_half):
    bad = []
    for nm, v in (('r_in', r_in), ('r_disc', r_disc)):
        if abs(v * 4 - round(v * 4)) > 1e-9:
            bad.append('K1')
    if len(set([round(R_OUT, 6), round(r_in, 6), round(r_disc, 6)])) != 3:
        bad.append('K2')
    stroke = (R_OUT - r_in) / U
    if stroke < TB_THIN_MIN:
        bad.append('K3')
    if stroke > TB_THIN_MAX:
        bad.append('K4')
    if r_disc > r_in - 0.25:
        bad.append('K5')
    if r_disc < 0.75:
        bad.append('K9')
    if gap_half > 60.0 or gap_half < 5.0:
        bad.append('K8')
    chord_px = 2.0 * R_OUT * math.sin(math.radians(gap_half))
    if chord_px < 1.5:
        bad.append('K7')
    return (len(bad) == 0), bad


def ink_fraction(r_in, r_disc, gap_half):
    ann = math.pi * (R_OUT ** 2 - r_in ** 2) * (1.0 - gap_half / 180.0)
    disc = math.pi * r_disc ** 2
    return (ann + disc) / (U * U)


def bbox_fill(r_in, r_disc, gap_half, res=128):
    m = CO.ring_disc_mask(1.0, r_in / R_OUT, r_disc / R_OUT, gap_half, 0.0,
                          res=res)
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return 0.0
    bw = (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)
    return float(m.sum()) / float(bw)


def small_size_error(r_in, r_disc, gap_half):
    """Structural error between a 16px render and a downscaled 400px render.
    Same definition already used and verified in verify_final.py group C."""
    big = CO.ring_disc_mask(1.0, r_in / R_OUT, r_disc / R_OUT, gap_half, 0.0,
                            res=400)
    ref = np.asarray(Image.fromarray((big * 255).astype(np.uint8))
                     .resize((16, 16), Image.LANCZOS)).astype(np.float64) / 255.0
    sm = CO.ring_disc_mask(1.0, r_in / R_OUT, r_disc / R_OUT, gap_half, 0.0,
                           res=16).astype(np.float64)
    return float(np.abs(ref - sm).mean())


def quality(r_in, r_disc, gap_half):
    """Weighted distance to MEASURED top-brand proportions. Lower is better."""
    ink = ink_fraction(r_in, r_disc, gap_half)
    thin = (R_OUT - r_in) / U
    bb = bbox_fill(r_in, r_disc, gap_half)
    err = small_size_error(r_in, r_disc, gap_half)
    chord = 2.0 * R_OUT * math.sin(math.radians(gap_half))
    q1 = abs(ink - T_INK) / T_INK
    q2 = abs(thin - T_THIN) / T_THIN
    q3 = abs(bb - T_BBOX) / T_BBOX
    q4 = err / 0.10
    q5 = max(0.0, (2.0 - chord) / 2.0)
    Q = 0.28 * q1 + 0.28 * q2 + 0.16 * q3 + 0.20 * q4 + 0.08 * q5
    return Q, dict(ink=ink, thin=thin, bbox=bb, err16=err, chord=chord,
                   q1=q1, q2=q2, q3=q3, q4=q4, q5=q5)


def build_cache():
    r_in_vals = [x / 4.0 for x in range(int(3.0 * 4), int(5.25 * 4) + 1)]
    r_disc_vals = [x / 4.0 for x in range(int(0.75 * 4), int(4.75 * 4) + 1)]
    gap_vals = [float(g) for g in range(10, 61, 2)]
    feas = []
    for r_in, r_disc, gap in itertools.product(r_in_vals, r_disc_vals, gap_vals):
        ok, _ = constraints(r_in, r_disc, gap)
        if not ok:
            continue
        ink = ink_fraction(r_in, r_disc, gap)
        if not (TB_INK_MIN <= ink <= TB_INK_MAX):
            continue
        feas.append((r_in, r_disc, gap))
    print('feasible: %d - scoring collisions + quality' % len(feas), flush=True)
    out = []
    for i, (r_in, r_disc, gap) in enumerate(feas):
        A = CO.ring_disc_mask(1.0, r_in / R_OUT, r_disc / R_OUT, gap, 0.0,
                              res=RES)
        d1s = []
        for name, M, pb in CO.references(res=RES):
            _, dr, _ = CO.d1_iou(A, M, res=RES, rotations=range(0, 360, 10))
            d1s.append(dr)
        Q, det = quality(r_in, r_disc, gap)
        out.append(dict(r_in=r_in, r_disc=r_disc, gap=gap,
                        fill=r_disc / r_in, min_d1=min(d1s), d1s=d1s,
                        Q=Q, **det))
        if (i + 1) % 50 == 0:
            print('  %d/%d' % (i + 1, len(feas)), flush=True)
    with open(CACHE, 'w') as fh:
        json.dump(out, fh)
    print('cached %d rows -> %s' % (len(out), CACHE))
    return out


def load_or_build():
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            return json.load(fh)
    return build_cache()


def main():
    rows = load_or_build()
    base = None
    for r in rows:
        if (abs(r['r_in'] - CM.R_INNER_U) < 1e-9 and
                abs(r['r_disc'] - CM.R_DISC_U) < 1e-9 and
                abs(r['gap'] - CM.GAP_HALF_DEG) < 1e-9):
            base = r
    if base is None:
        A = CO.ring_disc_mask(1.0, CM.R_INNER_U / R_OUT, CM.R_DISC_U / R_OUT,
                              CM.GAP_HALF_DEG, 0.0, res=RES)
        d1s = []
        for name, M, pb in CO.references(res=RES):
            _, dr, _ = CO.d1_iou(A, M, res=RES, rotations=range(0, 360, 10))
            d1s.append(dr)
        Q, det = quality(CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG)
        base = dict(r_in=CM.R_INNER_U, r_disc=CM.R_DISC_U,
                    gap=CM.GAP_HALF_DEG, fill=CM.R_DISC_U / CM.R_INNER_U,
                    min_d1=min(d1s), d1s=d1s, Q=Q, **det)

    print('=' * 100)
    print('MEASURED TARGETS from %d real top brands (medians, no fallbacks)'
          % N_BRANDS)
    print('  ink_fraction=%.4f  stroke_min_frac=%.4f  bbox_fill=%.4f'
          % (T_INK, T_THIN, T_BBOX))
    print('=' * 100)
    print('BASELINE as approved: r_in=%.2f r_disc=%.2f gap=%.1f fill=%.4f'
          % (base['r_in'], base['r_disc'], base['gap'], base['fill']))
    print('  min_D1=%.4f   Q=%.4f   ink=%.4f thin=%.4f bbox=%.4f err16=%.4f'
          % (base['min_d1'], base['Q'], base['ink'], base['thin'],
             base['bbox'], base['err16']))
    print('  per-ref D1 (colorado/copyright/bullseye/power): %s'
          % ' '.join('%.4f' % v for v in base['d1s']))
    print()

    print('DEGENERACY CHECK - what pure distance-maximisation picks:')
    best_d = max(rows, key=lambda r: r['min_d1'])
    print('  r_in=%.2f r_disc=%.2f gap=%.1f -> min_D1=%.4f but Q=%.4f ink=%.4f'
          % (best_d['r_in'], best_d['r_disc'], best_d['gap'],
             best_d['min_d1'], best_d['Q'], best_d['ink']))
    print('  (rejected: Q is %.1fx worse than baseline Q=%.4f)'
          % (best_d['Q'] / base['Q'], base['Q']))
    print()

    print('=' * 100)
    print('FLOOR SWEEP - best-quality candidate that clears each collision floor')
    print('=' * 100)
    print('  %-8s %-6s %-7s %-6s %-7s %-8s %-8s %-7s %-7s %s'
          % ('floor', 'r_in', 'r_disc', 'gap', 'fill', 'min_D1', 'Q',
             'ink', 'thin', 'D1 per ref'))
    picks = {}
    for floor in [base['min_d1'], 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
        cand = [r for r in rows if r['min_d1'] >= floor]
        if not cand:
            print('  %-8.3f  (none feasible)' % floor)
            continue
        b = min(cand, key=lambda r: r['Q'])
        picks[floor] = b
        print('  %-8.3f %-6.2f %-7.2f %-6.1f %-7.4f %-8.4f %-8.4f %-7.4f %-7.4f %s'
              % (floor, b['r_in'], b['r_disc'], b['gap'], b['fill'],
                 b['min_d1'], b['Q'], b['ink'], b['thin'],
                 ' '.join('%.3f' % v for v in b['d1s'])))
    print()
    print('BASELINE Q for reference: %.4f' % base['Q'])
    print()
    print('Interpretation: read DOWN the floor column. The first row where Q')
    print('starts rising sharply is where collision-avoidance begins to cost')
    print('real logo quality. Choose the highest floor that keeps Q <= baseline.')
    print()
    ok = [(f, b) for f, b in picks.items() if b['Q'] <= base['Q']]
    if ok:
        f, b = max(ok, key=lambda x: x[0])
        print('=> RECOMMENDED: floor=%.3f  r_in=%.2f r_disc=%.2f gap=%.1f' %
              (f, b['r_in'], b['r_disc'], b['gap']))
        print('   collision min_D1 %.4f -> %.4f (%+.1f%%)  AND  Q %.4f -> %.4f (%+.1f%%)'
              % (base['min_d1'], b['min_d1'],
                 100 * (b['min_d1'] - base['min_d1']) / base['min_d1'],
                 base['Q'], b['Q'], 100 * (b['Q'] - base['Q']) / base['Q']))
        print('   i.e. LESS collision AND closer to real top-brand proportions.')
    else:
        print('=> NO candidate improves collision without costing quality.')
    return rows, base, picks


if __name__ == '__main__':
    main()
