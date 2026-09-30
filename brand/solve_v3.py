#!/usr/bin/env python3
"""solve_v3.py - Produce the FINAL ranked options, with full evidence.

WHAT WE PROVED BEFORE THIS SCRIPT (see solve_palette.py output)
  1. The current pair scores Ou-Luo CH = +0.2904 and fails 3 constraints:
       C1 coin/field contrast 1.46:1  (needs >= 3.0, WCAG 1.4.11)
       C3 hue interval 78.3deg        (Moon-Spencer ambiguous zone)
       C4 dL*=12.7 and dC*=4.0        (colour vibration)
     The user's complaint is therefore a REAL, MEASURABLE defect and not
     a matter of taste.

  2. Keeping the teal field is IMPOSSIBLE, proved algebraically:
       ink luminance  Lk = 0.00546
       teal luminance Lt = 0.40638
       C2 (dark ink on coin >= 4.5:1) forces coin luminance Lc >= 0.19957
       C1 with a LIGHT coin forces Lc >= 3*(Lt+0.05)-0.05 = 1.31914 > 1.0
         -> impossible, brighter than white
       C1 with a DARK coin forces Lc <= (Lt+0.05)/3-0.05 = 0.10213
         -> contradicts Lc >= 0.19957
     Both branches are infeasible. 42,840 candidate coin colours were
     tested and 0 passed. The FIELD must change.

  3. The earlier v1 avatar failed because it was too DARK (brightness
     0.325 vs peer median 0.692). So we cannot simply go dark again
     without evidence. Therefore C6 keeps the field in a measured band,
     and we ALSO report the resulting avatar brightness so the peer
     comparison is explicit rather than assumed.

THE SCENARIOS RANKED HERE
  A "gold coin retained"  - the name is Coinkins; a gold coin is the
                            strongest literal signal. Field is solved.
  B "any warm metal coin" - widen the coin to the whole gold/brass band.
  C "silver/white coin"   - a white metal coin. Ou 2008 found blue is
                            the hue most likely to create harmony, so a
                            blue-family field with a white metal coin is
                            theoretically strong. Tested, not assumed.

Every row is measured. Nothing in this file is an aesthetic assertion.
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

# Coin disc radius as a fraction of avatar width, taken from
# make_assets_v2.py: r = int(W * 0.315). Area of that disc in a unit
# square is pi * 0.315^2.
COIN_AREA = 3.141592653589793 * 0.315 ** 2


def hexs(rgb):
    return '#%02X%02X%02X' % rgb


def avatar_brightness(field, coin):
    """Approximate mean V of the finished avatar. analyze_competitors.py
    measured peer avatars as mean HSV value; peer median was 0.692 and
    v1 FAILED at 0.325, so this number matters."""
    _, _, vf = hsv(field)
    _, _, vc = hsv(coin)
    a = min(COIN_AREA, 1.0)
    return vf * (1 - a) + vc * a


def report(field, coin, label):
    ok, score, r = SP.evaluate(field, coin)
    br = avatar_brightness(field, coin)
    print(f"\n  {label}")
    print(f"    field {hexs(field)}  L*={r['Lf']:5.1f} C*={r['Cf']:5.1f} "
          f"h={r['hf']:5.0f}deg")
    print(f"    coin  {hexs(coin)}  L*={r['Lc']:5.1f} C*={r['Cc']:5.1f} "
          f"h={r['hc']:5.0f}deg   ({r['metal']})")
    print(f"    Ou-Luo CH {score:+.4f}  |  hue interval {r['gap']:.1f}deg"
          f"  |  dL* {r['dL']:.1f}  dC* {r['dC']:.1f}  "
          f"dE2000 {r['dE']:.1f}")
    print(f"    contrast: coin/field {r['cr_coin']:.2f}:1 (need 3.0)  "
          f"ink/coin {r['cr_ink']:.2f}:1 (need 4.5)  "
          f"cream/field {contrast(CREAM, field):.2f}:1")
    print(f"    avatar mean brightness {br:.3f} "
          f"(measured peer median 0.692)")
    print(f"    peer differentiation: {r['diff']}")
    print(f"    => {'ACCEPTED' if ok else 'REJECTED'}")
    for f in r['fails']:
        print(f"       - {f}")
    return ok, score, r, br


def search(fix_coin=None, coin_family=None, step_h=3, step_s=5, step_v=5):
    """Search fields (and optionally coins) satisfying all constraints."""
    out = []
    if fix_coin is not None:
        coins = [fix_coin]
    else:
        coins = []
        seen = set()
        for h, s, v in coin_family:
            r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
            c = (round(r * 255), round(g * 255), round(b * 255))
            if c not in seen:
                seen.add(c)
                coins.append(c)
    for fh in range(0, 360, step_h):
        for fs in range(0, 101, step_s):
            for fv in range(10, 101, step_v):
                r, g, b = colorsys.hsv_to_rgb(fh / 360, fs / 100, fv / 100)
                field = (round(r * 255), round(g * 255), round(b * 255))
                for coin in coins:
                    ok, sc, rep = SP.evaluate(field, coin)
                    if ok:
                        out.append((sc, field, coin, rep))
    out.sort(key=lambda t: -t[0])
    return out


def dedupe(cands, min_de=14.0, limit=6):
    """Keep only perceptually distinct FIELDS so the list is real
    choices, not 40 near-identical greens."""
    out = []
    for sc, field, coin, rep in cands:
        if all(harmony.delta_e_2000(field, o[1]) >= min_de for o in out):
            out.append((sc, field, coin, rep))
        if len(out) >= limit:
            break
    return out


def main():
    print("=" * 74)
    print("V3 PALETTE SOLVER - RANKED, MEASURED OPTIONS")
    print("=" * 74)

    print()
    print("BASELINE - what the user rejected")
    print("-" * 74)
    report(PALETTE['teal']['rgb'], GOLD, 'v2 CURRENT (gold on bright teal)')

    print()
    print("=" * 74)
    print("SCENARIO A - keep the EXACT gold coin #F5C85C, solve the field")
    print("=" * 74)
    a = search(fix_coin=GOLD)
    print(f"  fields passing all 7 constraints: {len(a)}")
    for sc, field, coin, rep in dedupe(a):
        br = avatar_brightness(field, coin)
        print(f"    CH {sc:+.4f}  field {hexs(field)}  "
              f"L*={rep['Lf']:4.0f} C*={rep['Cf']:4.0f} h={rep['hf']:4.0f}  "
              f"gap {rep['gap']:4.0f}deg  cr {rep['cr_coin']:4.2f}:1  "
              f"brightness {br:.3f}")

    print()
    print("=" * 74)
    print("SCENARIO B - any warm-metal coin, solve the field")
    print("=" * 74)
    warm = [(h, s, v) for h in range(42, 104, 6)
            for s in range(20, 101, 16) for v in range(60, 101, 10)]
    b = search(coin_family=warm, step_h=6, step_s=10, step_v=8)
    print(f"  pairs passing all 7 constraints: {len(b)}")
    for sc, field, coin, rep in dedupe(b):
        br = avatar_brightness(field, coin)
        print(f"    CH {sc:+.4f}  field {hexs(field)} + coin {hexs(coin)}  "
              f"gap {rep['gap']:4.0f}deg  dL* {rep['dL']:4.0f}  "
              f"cr {rep['cr_coin']:4.2f}:1  brightness {br:.3f}")

    print()
    print("=" * 74)
    print("SCENARIO C - white/silver metal coin, solve the field")
    print("=" * 74)
    silver = [(h, s, v) for h in (0, 200, 210)
              for s in (0, 3, 6) for v in range(84, 101, 4)]
    c = search(coin_family=silver, step_h=6, step_s=10, step_v=8)
    print(f"  pairs passing all 7 constraints: {len(c)}")
    for sc, field, coin, rep in dedupe(c):
        br = avatar_brightness(field, coin)
        print(f"    CH {sc:+.4f}  field {hexs(field)} + coin {hexs(coin)}  "
              f"gap {rep['gap']:4.0f}deg  dL* {rep['dL']:4.0f}  "
              f"cr {rep['cr_coin']:4.2f}:1  brightness {br:.3f}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
