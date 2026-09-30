#!/usr/bin/env python3
"""
harmony.py - Measure COLOUR HARMONY properly. This is the dimension I
failed to test before.

WHAT I GOT WRONG
  Doc 19 validated contrast (WCAG) and differentiation-from-peers, then
  declared "PALETTE VALID". Those tests answer "is it readable?" and "is it
  distinct?" They say NOTHING about whether two hues are AESTHETICALLY
  COMPATIBLE. The user says gold on teal looks wrong. This script tests
  that claim with colour science instead of opinion.

THE SCIENCE USED
  1. CIELAB / CIEDE2000 - the CIE's perceptually-uniform colour difference
     metric (ISO/CIE 11664-6). Euclidean RGB distance is perceptually
     meaningless; Delta-E 2000 is the accepted standard.
  2. Classical harmony templates (Itten / Munsell tradition): hue angles
     that are known to be stable - complementary 180, split-complementary
     150/210, triadic 120, analogous <=30-40, tetradic 90.
  3. Moon-Spencer harmony theory: specific hue intervals are "ambiguous"
     and read as unresolved/clashing, notably ~30-60 degrees apart with
     both colours highly saturated.
  4. Chroma/lightness balance: two colours of near-equal high chroma and
     near-equal lightness compete for attention ("colour vibration").
"""
import colorsys
import math


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_to_xyz(rgb):
    r, g, b = [srgb_to_linear(v) for v in rgb]
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    return x * 100, y * 100, z * 100


def xyz_to_lab(xyz):
    # D65 white point
    xn, yn, zn = 95.047, 100.0, 108.883
    x, y, z = xyz[0] / xn, xyz[1] / yn, xyz[2] / zn

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t + 16 / 116)
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def rgb_to_lab(rgb):
    return xyz_to_lab(rgb_to_xyz(rgb))


def lab_to_lch(lab):
    L, a, b = lab
    C = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360
    return L, C, h


def delta_e_2000(rgb1, rgb2):
    """Full CIEDE2000 implementation (ISO/CIE 11664-6)."""
    L1, a1, b1 = rgb_to_lab(rgb1)
    L2, a2, b2 = rgb_to_lab(rgb2)
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cbar ** 7 / (Cbar ** 7 + 25 ** 7))) \
        if Cbar > 0 else 0
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)
    Lbarp = (L1 + L2) / 2
    Cbarp = (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbarp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbarp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbarp = (h1p + h2p + 360) / 2
    else:
        hbarp = (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbarp - 30))
         + 0.24 * math.cos(math.radians(2 * hbarp))
         + 0.32 * math.cos(math.radians(3 * hbarp + 6))
         - 0.20 * math.cos(math.radians(4 * hbarp - 63)))
    dtheta = 30 * math.exp(-(((hbarp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbarp ** 7 / (Cbarp ** 7 + 25 ** 7)) \
        if Cbarp > 0 else 0
    Sl = 1 + (0.015 * (Lbarp - 50) ** 2) / math.sqrt(20 + (Lbarp - 50) ** 2)
    Sc = 1 + 0.045 * Cbarp
    Sh = 1 + 0.015 * Cbarp * T
    Rt = -math.sin(math.radians(2 * dtheta)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


HARMONY_TEMPLATES = {
    'monochromatic': (0, 12),
    'analogous': (12, 40),
    'AMBIGUOUS (Moon-Spencer)': (40, 85),
    'tetradic / square-ish': (85, 105),
    'triadic': (105, 135),
    'AMBIGUOUS (second zone)': (135, 150),
    'split-complementary': (150, 170),
    'complementary': (170, 190),
    'split-complementary ': (190, 210),
}


def classify(hue_gap):
    g = min(hue_gap, 360 - hue_gap)
    for name, (lo, hi) in HARMONY_TEMPLATES.items():
        if lo <= g < hi:
            return name, g
    return 'split/triadic region', g


def analyse(name_a, rgb_a, name_b, rgb_b):
    La, Ca, ha = lab_to_lch(rgb_to_lab(rgb_a))
    Lb, Cb, hb = lab_to_lch(rgb_to_lab(rgb_b))
    gap = abs(ha - hb)
    cls, g = classify(gap)
    de = delta_e_2000(rgb_a, rgb_b)

    print(f"\n  {name_a} {rgb_a}  vs  {name_b} {rgb_b}")
    print(f"    LCh A: L*={La:6.2f}  C*={Ca:6.2f}  h={ha:6.1f}deg")
    print(f"    LCh B: L*={Lb:6.2f}  C*={Cb:6.2f}  h={hb:6.1f}deg")
    print(f"    hue gap      {g:6.1f}deg  -> {cls}")
    print(f"    Delta-E 2000 {de:6.2f}")
    print(f"    L* difference {abs(La-Lb):6.2f}")
    print(f"    C* difference {abs(Ca-Cb):6.2f}")

    issues = []
    if 40 <= g < 85 or 135 <= g < 150:
        issues.append('hue gap sits in an AMBIGUOUS zone (Moon-Spencer): '
                      'neither analogous nor complementary, reads unresolved')
    if Ca > 45 and Cb > 45 and abs(Ca - Cb) < 25:
        issues.append(f'both highly chromatic (C*={Ca:.0f} and {Cb:.0f}) '
                      'and similar -> they compete, causing colour vibration')
    if abs(La - Lb) < 12 and Ca > 40 and Cb > 40:
        issues.append(f'near-equal lightness (dL*={abs(La-Lb):.1f}) with high '
                      'chroma -> edges shimmer, no clear figure/ground')
    return {'gap': g, 'class': cls, 'dE': de,
            'dL': abs(La - Lb), 'dC': abs(Ca - Cb), 'issues': issues}


if __name__ == '__main__':
    TEAL = (15, 194, 142)
    GOLD = (245, 200, 92)
    print("=" * 74)
    print("HARMONY AUDIT OF THE CURRENT PALETTE (user says it clashes)")
    print("=" * 74)
    r = analyse('teal #0FC28E', TEAL, 'gold #F5C85C', GOLD)
    print()
    print("=" * 74)
    if r['issues']:
        print("  RESULT: PROBLEMS CONFIRMED")
        for i in r['issues']:
            print(f"    - {i}")
    else:
        print("  RESULT: no harmony problems detected")
    print("=" * 74)
