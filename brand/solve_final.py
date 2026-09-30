#!/usr/bin/env python3
"""solve_final.py - The constrained solve, with the brand-strength
constraint that the pure-CH maximiser was missing.

THE CONFLICT I FOUND AND MUST NOT HIDE
  Ou-Luo CH rewards SMALL chroma difference (H_C = 0.04+0.53tanh(0.8-
  0.045*dC) is monotonically decreasing in dC). A pure CH maximiser
  therefore drifts toward muted, greyish fields:
      best scenario-C field was #878594, saturation 0.101
  That IS more harmonious by the empirical model, but it contradicts our
  own measured peer evidence: the strongest marks use ONE FLAT SATURATED
  field (azuki #bb3647 sat 0.711 at 91% of pixels; doodles #feacda sat
  0.323 at 71%). A grey avatar would be harmonious and forgettable.

  Optimising a single metric until it breaks something else is exactly
  the mistake I made before (I optimised contrast and broke harmony).
  So CH is the OBJECTIVE, and brand strength is a CONSTRAINT.

CONSTRAINT SET (8 hard gates; a candidate is rejected if any fails)
  C1 coin/field contrast >= 3.0:1   WCAG 2.1 SC 1.4.11 (w3.org)
  C2 ink/coin contrast   >= 4.5:1   WCAG 2.1 SC 1.4.3  (w3.org)
  C3 hue interval not in a Moon-Spencer ambiguous zone
                                    Moon & Spencer, JOSA 34:46-59 (1944)
  C4 no colour vibration: dL* >= 18 OR dC* >= 25
  C5 field differentiated from measured peers
  C6 field V in [0.45, 0.95]
  C7 coin must read as metal
  C8 NEW - field saturation >= 0.35 AND field chroma C* >= 25
     SOURCE: our own measurement of 10 verified peer avatars. The flat
     saturated field is the pattern the strongest marks share. 0.35 is
     set above doodles (0.323), the weakest saturated peer that still
     works, so we are not merely matching the floor.

OBJECTIVE
  maximise Ou-Luo CH(field, coin). Ou & Luo, Color Res Appl
  31(3):191-204 (2006), DOI 10.1002/col.20208 - empirical, fitted to
  1431 human-judged pairs, and validated in ouluo.py against CIE
  reference values, the published output range, and the published
  finding that blue is the most harmonious hue.
"""

import colorsys
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harmony   # noqa: E402
import ouluo     # noqa: E402
import solve_palette as SP  # noqa: E402
from palette import PALETTE, contrast, hsv  # noqa: E402

GOLD = PALETTE['gold']['rgb']
INK = PALETTE['ink']['rgb']
CREAM = PALETTE['cream']['rgb']
COIN_AREA = 3.141592653589793 * 0.315 ** 2

MIN_FIELD_SAT = 0.35
MIN_FIELD_CHROMA = 25.0


def hexs(rgb):
    return '#%02X%02X%02X' % rgb


def avatar_brightness(field, coin):
    _, _, vf = hsv(field)
    _, _, vc = hsv(coin)
    a = min(COIN_AREA, 1.0)
    return vf * (1 - a) + vc * a


def evaluate8(field, coin):
    """The 7 gates from solve_palette plus C8 brand strength."""
    ok, score, rep = SP.evaluate(field, coin)
    _, s, _ = hsv(field)
    _, Cf, _ = ouluo.lab_to_lch(ouluo.rgb_to_lab(field))
    if s < MIN_FIELD_SAT or Cf < MIN_FIELD_CHROMA:
        rep['fails'].append(
            f'C8 field too muted: sat {s:.3f} (need >={MIN_FIELD_SAT}), '
            f'C* {Cf:.1f} (need >={MIN_FIELD_CHROMA}) - contradicts the '
            f'measured peer pattern of one flat saturated field')
        ok = False
    rep['field_sat'] = s
    return ok, score, rep


def search(coins, step_h=3, step_s=4, step_v=4):
    out = []
    for fh in range(0, 360, step_h):
        for fs in range(30, 101, step_s):
            for fv in range(30, 101, step_v):
                r, g, b = colorsys.hsv_to_rgb(fh / 360, fs / 100, fv / 100)
                field = (round(r * 255), round(g * 255), round(b * 255))
                for coin in coins:
                    ok, sc, rep = evaluate8(field, coin)
                    if ok:
                        out.append((sc, field, coin, rep))
    out.sort(key=lambda t: -t[0])
    return out


def mk(family):
    seen, coins = set(), []
    for h, s, v in family:
        r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
        c = (round(r * 255), round(g * 255), round(b * 255))
        if c not in seen:
            seen.add(c)
            coins.append(c)
    return coins


def dedupe(cands, min_de=16.0, limit=6):
    out = []
    for sc, field, coin, rep in cands:
        if all(harmony.delta_e_2000(field, o[1]) >= min_de for o in out):
            out.append((sc, field, coin, rep))
        if len(out) >= limit:
            break
    return out


def row(sc, field, coin, rep):
    br = avatar_brightness(field, coin)
    print(f"    CH {sc:+.4f}  field {hexs(field)} sat {rep['field_sat']:.2f} "
          f"h={rep['hf']:4.0f}  +  coin {hexs(coin)}  "
          f"gap {rep['gap']:4.0f}deg  dL* {rep['dL']:4.0f}  "
          f"cr {rep['cr_coin']:4.2f}:1  bright {br:.3f}")


def main():
    print("=" * 78)
    print("FINAL SOLVE - 8 HARD CONSTRAINTS, Ou-Luo CH AS OBJECTIVE")
    print("=" * 78)

    print()
    print("BASELINE (rejected by the user, now also rejected by measurement)")
    ok, sc, rep = evaluate8(PALETTE['teal']['rgb'], GOLD)
    print(f"  v2 gold on teal: CH {sc:+.4f}  -> {'ACCEPTED' if ok else 'REJECTED'}")
    for f in rep['fails']:
        print(f"    - {f}")

    print()
    print("=" * 78)
    print("A) EXACT current gold coin #F5C85C retained")
    print("=" * 78)
    a = search([GOLD])
    print(f"  passing all 8: {len(a)}")
    for t in dedupe(a):
        row(*t)

    print()
    print("=" * 78)
    print("B) warm-metal coin (gold/brass band), coin also solved")
    print("=" * 78)
    warm = mk([(h, s, v) for h in range(44, 102, 6)
               for s in range(24, 101, 14) for v in range(62, 101, 9)])
    print(f"  coin candidates: {len(warm)}")
    b = search(warm, step_h=6, step_s=8, step_v=8)
    print(f"  passing all 8: {len(b)}")
    for t in dedupe(b):
        row(*t)

    print()
    print("=" * 78)
    print("C) white/silver metal coin, coin also solved")
    print("=" * 78)
    silver = mk([(h, s, v) for h in (0, 45, 200, 210)
                 for s in (0, 3, 6, 10) for v in range(84, 101, 4)])
    print(f"  coin candidates: {len(silver)}")
    c = search(silver, step_h=6, step_s=8, step_v=8)
    print(f"  passing all 8: {len(c)}")
    for t in dedupe(c):
        row(*t)

    print()
    print("=" * 78)
    print("HEAD-TO-HEAD: best of each scenario vs the rejected baseline")
    print("=" * 78)
    best = []
    for name, lst in [('A gold kept', a), ('B warm metal', b),
                      ('C white metal', c)]:
        if lst:
            best.append((name,) + lst[0])
    best.sort(key=lambda t: -t[1])
    print(f"  {'scenario':16s} {'CH':>8s}  {'field':8s} {'coin':8s} "
          f"{'gap':>6s} {'cr':>6s} {'bright':>7s}")
    print("  " + "-" * 66)
    print(f"  {'v2 REJECTED':16s} {sc:+8.4f}  "
          f"{hexs(PALETTE['teal']['rgb']):8s} {hexs(GOLD):8s} "
          f"{rep['gap']:5.0f}d {rep['cr_coin']:5.2f}  "
          f"{avatar_brightness(PALETTE['teal']['rgb'], GOLD):7.3f}")
    for name, s2, f2, c2, r2 in best:
        print(f"  {name:16s} {s2:+8.4f}  {hexs(f2):8s} {hexs(c2):8s} "
              f"{r2['gap']:5.0f}d {r2['cr_coin']:5.2f}  "
              f"{avatar_brightness(f2, c2):7.3f}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
