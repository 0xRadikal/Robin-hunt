#!/usr/bin/env python3
"""solve_palette.py - Find the coin/background pair that is actually
harmonious, by SEARCH under HARD CONSTRAINTS, not by taste.

THE PROBLEM, STATED PRECISELY
  The user said the gold coin clashes with the teal field. harmony.py
  confirmed it geometrically (Moon-Spencer ambiguous interval, colour
  vibration). This script quantifies it with the empirical Ou-Luo model
  and then searches for a replacement.

THE OBJECTIVE
  maximise  CH(field, coin)      [Ou & Luo 2006, empirical, validated]

THE HARD CONSTRAINTS (a candidate is rejected if any fails)
  C1  coin vs field contrast >= 3.0:1
      SOURCE: WCAG 2.1 SC 1.4.11 Non-text Contrast (W3C) - graphical
      objects require at least 3:1 against adjacent colour. The coin IS
      a graphical object conveying meaning, so this is mandatory, not a
      preference.
  C2  monogram (ink) on coin >= 4.5:1
      SOURCE: WCAG 2.1 SC 1.4.3 Contrast (Minimum) - 4.5:1 for text.
  C3  hue interval must NOT be in a Moon-Spencer ambiguous zone.
      SOURCE: Moon & Spencer, JOSA 34:46-59 (1944), postulate (i):
      "the interval between any two colors is unambiguous".
      The first ambiguity interval is the most critical (Chuang & Ou).
  C4  no colour vibration: the pair must not be two high-chroma colours
      at similar chroma AND similar lightness. Enforced as
      dL* >= 18 OR dC* >= 25. dL*=18 is above the Moon-Spencer tone-plane
      "Contrast" threshold region, giving a clear figure/ground.
  C5  field must stay differentiated from measured peers:
      hue gap > 40deg OR saturation gap > 0.35 from every chromatic peer
      (the rule already validated in palette.py against CryptoPunks).
  C6  avatar brightness must stay near the measured peer median 0.692
      (v1 FAILED at 0.325). Enforced: field V in [0.45, 0.95].
  C7  the coin must remain SEMANTICALLY a coin. A coin reads as metal:
      warm yellow-gold, or cool silver/white metal. Enforced by hue
      windows, see COIN_HUE_WINDOWS. Without this the solver would
      happily return a purple disc with a great CH score and destroy the
      product meaning.

WHAT I AM *NOT* DOING
  I am not asserting the winner is beautiful. I am asserting it is
  measurably more harmonious than the current pair under a model fitted
  to human judgements, while satisfying every accessibility and brand
  constraint we already proved necessary.
"""

import colorsys
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harmony  # noqa: E402  Moon-Spencer + CIEDE2000
import ouluo    # noqa: E402  empirical harmony model
from palette import PALETTE, contrast, hsv  # noqa: E402

INK = PALETTE['ink']['rgb']

# Measured peers (from analyze_competitors.py -> competitor_metrics.json)
PEERS = {
    'pudgypenguins': (239, 248, 248), 'azuki': (187, 54, 71),
    'boredapeyachtclub': (0, 0, 0), 'doodles-official': (254, 172, 218),
    'moonbirds': (254, 254, 254), 'milady': (223, 221, 216),
    'cryptopunks': (99, 133, 150), 'rare-friends-genesis': (17, 17, 17),
    'mutant-ape-yacht-club': (27, 27, 30), 'clonex': (254, 254, 254),
}

# A coin is metal. Metal in CIELAB hue-angle terms:
#   warm gold / brass  : h ~ 60-100 deg  (yellow family)
#   copper / bronze    : h ~ 40-60  deg
#   silver / steel     : achromatic to slightly blue, C* < 15
COIN_HUE_WINDOWS = [(40, 105)]
COIN_MAX_CHROMA_FOR_METAL_GREY = 15

AMBIGUOUS_ZONES = [(40, 85), (135, 150)]


def hue_gap(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def in_ambiguous(gap):
    return any(lo <= gap < hi for lo, hi in AMBIGUOUS_ZONES)


def lch(rgb):
    return ouluo.lab_to_lch(ouluo.rgb_to_lab(rgb))


def coin_is_metal(rgb):
    """C7: does this colour read as metal?"""
    L, C, h = lch(rgb)
    if C <= COIN_MAX_CHROMA_FOR_METAL_GREY:
        return True, 'silver/steel (near-achromatic metal)'
    for lo, hi in COIN_HUE_WINDOWS:
        if lo <= h <= hi:
            return True, 'gold/brass/copper (warm metal)'
    return False, f'h={h:.0f}deg is not a metal hue'


def field_is_differentiated(rgb):
    """C5: still measurably distinct from every chromatic peer."""
    oh, os_, _ = hsv(rgb)
    worst = None
    for name, prgb in PEERS.items():
        ph, ps, _ = hsv(prgb)
        if ps < 0.12:
            continue  # achromatic peer, no hue to clash with
        g = hue_gap(oh, ph)
        sg = abs(os_ - ps)
        if not (g > 40 or sg > 0.35):
            return False, f'too close to {name} (hue gap {g}deg, ' \
                          f'sat gap {sg:.2f})'
        if worst is None or g < worst[1]:
            worst = (name, g, sg)
    return True, f'closest chromatic peer {worst[0]} at {worst[1]}deg'


def evaluate(field, coin, verbose=False):
    """Return (ok, score, report). Score is Ou-Luo CH."""
    fails = []

    cr_coin = contrast(field, coin)
    if cr_coin < 3.0:
        fails.append(f'C1 coin/field contrast {cr_coin:.2f}:1 < 3.0 '
                     f'(WCAG 1.4.11)')

    cr_ink = contrast(INK, coin)
    if cr_ink < 4.5:
        fails.append(f'C2 ink/coin contrast {cr_ink:.2f}:1 < 4.5 '
                     f'(WCAG 1.4.3)')

    Lf, Cf, hf = lch(field)
    Lc, Cc, hc = lch(coin)
    gap = hue_gap(hf, hc)
    # a near-achromatic coin has no meaningful hue angle, so the
    # Moon-Spencer interval test does not apply to it
    hue_meaningful = Cc > COIN_MAX_CHROMA_FOR_METAL_GREY and Cf > 15
    if hue_meaningful and in_ambiguous(gap):
        fails.append(f'C3 hue interval {gap:.1f}deg is in a Moon-Spencer '
                     f'ambiguous zone')

    dL, dC = abs(Lf - Lc), abs(Cf - Cc)
    if not (dL >= 18 or dC >= 25):
        fails.append(f'C4 colour vibration risk: dL*={dL:.1f} and '
                     f'dC*={dC:.1f} both too small')

    diff_ok, diff_note = field_is_differentiated(field)
    if not diff_ok:
        fails.append(f'C5 {diff_note}')

    _, _, v = hsv(field)
    if not (0.45 <= v <= 0.95):
        fails.append(f'C6 field brightness V={v:.3f} outside [0.45,0.95] '
                     f'(peer median 0.692)')

    metal_ok, metal_note = coin_is_metal(coin)
    if not metal_ok:
        fails.append(f'C7 {metal_note}')

    score = ouluo.ch(field, coin)
    rep = {
        'CH': score, 'cr_coin': cr_coin, 'cr_ink': cr_ink,
        'gap': gap, 'dL': dL, 'dC': dC, 'dE': harmony.delta_e_2000(field, coin),
        'Lf': Lf, 'Cf': Cf, 'hf': hf, 'Lc': Lc, 'Cc': Cc, 'hc': hc,
        'fails': fails, 'metal': metal_note, 'diff': diff_note,
        'field_V': v,
    }
    return (len(fails) == 0), score, rep


def hexs(rgb):
    return '#%02X%02X%02X' % rgb


def show(label, field, coin):
    ok, score, r = evaluate(field, coin)
    print(f"\n  {label}")
    print(f"    field {hexs(field)} {field}  "
          f"L*={r['Lf']:.1f} C*={r['Cf']:.1f} h={r['hf']:.0f}deg")
    print(f"    coin  {hexs(coin)} {coin}  "
          f"L*={r['Lc']:.1f} C*={r['Cc']:.1f} h={r['hc']:.0f}deg")
    print(f"    Ou-Luo CH      {score:+.4f}   (higher is more harmonious)")
    print(f"    hue interval   {r['gap']:.1f}deg"
          f"{'  <-- AMBIGUOUS' if in_ambiguous(r['gap']) else ''}")
    print(f"    dL* {r['dL']:.1f}   dC* {r['dC']:.1f}   "
          f"dE2000 {r['dE']:.1f}")
    print(f"    contrast coin/field {r['cr_coin']:.2f}:1   "
          f"ink/coin {r['cr_ink']:.2f}:1")
    if r['fails']:
        print(f"    REJECTED:")
        for f in r['fails']:
            print(f"      - {f}")
    else:
        print(f"    ACCEPTED - all 7 hard constraints satisfied")
    return ok, score, r


def sweep_coin(field, step=6):
    """Scenario A: keep the field, search every coin colour."""
    best = []
    for h in range(0, 360, 2):
        for s in range(0, 101, step):
            for v in range(20, 101, step):
                r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
                coin = (round(r * 255), round(g * 255), round(b * 255))
                ok, score, rep = evaluate(field, coin)
                if ok:
                    best.append((score, coin, rep))
    best.sort(key=lambda t: -t[0])
    return best


def sweep_field(coin, step=6):
    """Scenario B: keep the coin, search every field colour."""
    best = []
    for h in range(0, 360, 2):
        for s in range(0, 101, step):
            for v in range(20, 101, step):
                r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
                field = (round(r * 255), round(g * 255), round(b * 255))
                ok, score, rep = evaluate(field, coin)
                if ok:
                    best.append((score, field, rep))
    best.sort(key=lambda t: -t[0])
    return best


def dedupe(cands, min_de=10.0, limit=8):
    """Keep only perceptually distinct options (dE2000 apart)."""
    out = []
    for score, rgb, rep in cands:
        if all(harmony.delta_e_2000(rgb, o[1]) >= min_de for o in out):
            out.append((score, rgb, rep))
        if len(out) >= limit:
            break
    return out


def main():
    TEAL = PALETTE['teal']['rgb']
    GOLD = PALETTE['gold']['rgb']

    print("=" * 74)
    print("STEP 1 - SCORE THE CURRENT PAIR (the one the user rejected)")
    print("=" * 74)
    show('CURRENT v2: gold coin on teal field', TEAL, GOLD)

    print()
    print("=" * 74)
    print("STEP 2 - SCENARIO A: keep the teal field, replace the coin")
    print("=" * 74)
    print("  searching 180 hues x saturation x value under 7 constraints...")
    a = sweep_coin(TEAL)
    print(f"  candidates passing ALL constraints: {len(a)}")
    if a:
        for score, coin, rep in dedupe(a):
            print(f"    CH {score:+.4f}  {hexs(coin)} {coin}  "
                  f"L*={rep['Lc']:.0f} C*={rep['Cc']:.0f} "
                  f"h={rep['hc']:.0f}deg  gap {rep['gap']:.0f}deg  "
                  f"{rep['metal']}")
    else:
        print("    NONE. The teal field cannot host a harmonious metal "
              "coin under these constraints.")

    print()
    print("=" * 74)
    print("STEP 3 - SCENARIO B: keep the gold coin, replace the field")
    print("=" * 74)
    b = sweep_field(GOLD)
    print(f"  candidates passing ALL constraints: {len(b)}")
    for score, field, rep in dedupe(b):
        print(f"    CH {score:+.4f}  {hexs(field)} {field}  "
              f"L*={rep['Lf']:.0f} C*={rep['Cf']:.0f} "
              f"h={rep['hf']:.0f}deg  gap {rep['gap']:.0f}deg  "
              f"V={rep['field_V']:.2f}")

    print()
    print("=" * 74)
    print("STEP 4 - SCENARIO C: search BOTH (coarser grid)")
    print("=" * 74)
    both = []
    for fh in range(0, 360, 6):
        for fs in range(30, 101, 12):
            for fv in range(45, 96, 10):
                r, g, bb = colorsys.hsv_to_rgb(fh / 360, fs / 100, fv / 100)
                field = (round(r * 255), round(g * 255), round(bb * 255))
                for ch_ in list(range(40, 106, 6)) + [0]:
                    for cs in ([0, 4, 8] if ch_ == 0 else range(20, 101, 16)):
                        for cv in range(50, 101, 10):
                            r2, g2, b2 = colorsys.hsv_to_rgb(
                                ch_ / 360, cs / 100, cv / 100)
                            coin = (round(r2 * 255), round(g2 * 255),
                                    round(b2 * 255))
                            ok, score, rep = evaluate(field, coin)
                            if ok:
                                both.append((score, (field, coin), rep))
    both.sort(key=lambda t: -t[0])
    print(f"  pairs passing ALL constraints: {len(both)}")
    seen = []
    for score, (field, coin), rep in both:
        if all(harmony.delta_e_2000(field, o[0]) >= 12 for o in seen):
            seen.append((field, coin))
            print(f"    CH {score:+.4f}  field {hexs(field)} + "
                  f"coin {hexs(coin)}  gap {rep['gap']:.0f}deg  "
                  f"dL* {rep['dL']:.0f}  cr {rep['cr_coin']:.1f}:1")
        if len(seen) >= 10:
            break

    return 0


if __name__ == '__main__':
    sys.exit(main())
