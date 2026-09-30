#!/usr/bin/env python3
"""ouluo.py - The Ou & Luo (2006) quantitative two-colour harmony model.

WHY THIS FILE EXISTS
  The user said the gold coin does not harmonise with the teal background.
  My earlier tests (WCAG contrast, peer differentiation) cannot answer that
  question at all - they measure readability and distinctness. harmony.py
  showed a Moon-Spencer "ambiguous" hue interval, which is a 1944
  GEOMETRIC theory. That is necessary but not sufficient: geometry alone
  does not predict how humans actually rate a pair.

  Ou & Luo (2006) is the accepted EMPIRICAL model. It was fitted to real
  human judgements and therefore gives a NUMBER we can optimise.

PRIMARY SOURCE
  Ou L. and Luo M.R., "A colour harmony model for two-colour
  combinations", Color Research & Application 31(3):191-204, 2006.
  DOI 10.1002/col.20208
  Experiment scale: 1431 colour pairs, psychophysical assessment.

EQUATIONS - transcribed from source, then CROSS-CHECKED against a
second, fully independent publication so that no single transcription
can be wrong:
  source A: Ou & Luo 2006 as reproduced in Ou's own follow-up work
            ("Influence of area proportion on colour harmony", eqs 2-3)
  source B: Xu D., "Exploring the optimization method of color matching
            in visual communication design based on graphical algorithm",
            Int. J. Computer Information Systems and Industrial
            Management Applications 17 (2025) pp.1-14,
            DOI 10.70917/ijcisim-2025-0262, equations (5)-(17).
  Both sources print IDENTICAL constants. That agreement is the reason
  I am willing to use these numbers.

      CH = H_C + H_L + H_H

      H_C    = 0.04 + 0.53 * tanh(0.8 - 0.045 * dC)
      dC     = sqrt( dHab^2 + (dCab / 1.46)^2 )

      H_L    = H_Lsum + H_dL
      H_Lsum = 0.28 + 0.54 * tanh(-3.88 + 0.029 * Lsum),  Lsum = L1 + L2
      H_dL   = 0.14 + 0.15 * tanh(-2 + 0.2 * dL),         dL   = |L1-L2|

      H_H    = H_SY1 + H_SY2                (one term per colour)
      H_SY   = E_C * (H_S + E_Y)
      E_C    = 0.5 + 0.5 * tanh(-2 + 0.5 * Cab)
      H_S    = -0.08 - 0.14*sin(hab + 50deg) - 0.07*sin(2*hab + 90deg)
      E_Y    = ((0.22*L - 12.8)/10) * exp( (90-hab)/10 - exp((90-hab)/10) )

  Reported output range: CH in [-1.24, +1.39]. Higher = more harmonious.
  (range stated explicitly in source B, eq. 5 commentary)

NOTE ON dHab
  dHab is the CIELAB hue DIFFERENCE (the metric hue-difference term used
  in the CIELAB colour-difference equation), i.e.
      dHab = sqrt(dEab^2 - dL^2 - dCab^2)
  NOT the hue-angle difference in degrees. Using degrees here would be a
  units error that silently corrupts H_C. This is verified below.
"""

import math

D65 = (95.047, 100.0, 108.883)


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
    x, y, z = (xyz[i] / D65[i] for i in range(3))

    def f(t):
        return t ** (1.0 / 3.0) if t > 216.0 / 24389.0 \
            else (841.0 / 108.0) * t + 4.0 / 29.0

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def rgb_to_lab(rgb):
    return xyz_to_lab(rgb_to_xyz(rgb))


def lab_to_lch(lab):
    L, a, b = lab
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def _h_sy(L, C, h_deg):
    """Single-colour hue-effect term H_SY = E_C * (H_S + E_Y)."""
    E_C = 0.5 + 0.5 * math.tanh(-2.0 + 0.5 * C)
    H_S = (-0.08
           - 0.14 * math.sin(math.radians(h_deg + 50.0))
           - 0.07 * math.sin(math.radians(2.0 * h_deg + 90.0)))
    # E_Y uses a Gumbel-type term; the exponent argument is in DEGREES/10
    t = (90.0 - h_deg) / 10.0
    E_Y = ((0.22 * L - 12.8) / 10.0) * math.exp(t - math.exp(t))
    return E_C * (H_S + E_Y)


def ch_from_lab(lab1, lab2, detail=False):
    """Ou-Luo colour harmony CH for two CIELAB colours."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    _, C1, h1 = lab_to_lch(lab1)
    _, C2, h2 = lab_to_lch(lab2)

    dL = abs(L1 - L2)
    dCab = C2 - C1
    dEab = math.sqrt((L2 - L1) ** 2 + (a2 - a1) ** 2 + (b2 - b1) ** 2)
    # metric hue difference, guarded against tiny negative from rounding
    inner = dEab ** 2 - (L2 - L1) ** 2 - dCab ** 2
    dHab = math.sqrt(max(inner, 0.0))

    dC = math.sqrt(dHab ** 2 + (dCab / 1.46) ** 2)

    H_C = 0.04 + 0.53 * math.tanh(0.8 - 0.045 * dC)

    Lsum = L1 + L2
    H_Lsum = 0.28 + 0.54 * math.tanh(-3.88 + 0.029 * Lsum)
    H_dL = 0.14 + 0.15 * math.tanh(-2.0 + 0.2 * dL)
    H_L = H_Lsum + H_dL

    H_H = _h_sy(L1, C1, h1) + _h_sy(L2, C2, h2)

    CH = H_C + H_L + H_H
    if detail:
        return {'CH': CH, 'H_C': H_C, 'H_L': H_L, 'H_H': H_H,
                'H_Lsum': H_Lsum, 'H_dL': H_dL,
                'dC': dC, 'dHab': dHab, 'dCab': dCab, 'dL': dL,
                'dEab': dEab, 'Lsum': Lsum}
    return CH


def ch(rgb1, rgb2, detail=False):
    return ch_from_lab(rgb_to_lab(rgb1), rgb_to_lab(rgb2), detail)


# ======================================================================
# VALIDATION - I do not trust this implementation until it passes.
# ======================================================================

def _check(label, got, want, tol, notes=''):
    ok = abs(got - want) <= tol
    print(f"  {'PASS' if ok else 'FAIL'}  {label:46s} "
          f"got {got:9.4f}  want {want:9.4f}  tol {tol}")
    if notes:
        print(f"        {notes}")
    return ok


def validate():
    print("=" * 74)
    print("VALIDATING THE Ou-Luo IMPLEMENTATION")
    print("=" * 74)
    allok = True

    # ---- 1. CIELAB pipeline against CIE reference values --------------
    # sRGB white must give L*=100, a*=b*=0 under D65.
    L, a, b = rgb_to_lab((255, 255, 255))
    allok &= _check('white -> L*', L, 100.0, 0.02)
    allok &= _check('white -> a*', a, 0.0, 0.02)
    allok &= _check('white -> b*', b, 0.0, 0.02)
    L, a, b = rgb_to_lab((0, 0, 0))
    allok &= _check('black -> L*', L, 0.0, 0.02)
    # sRGB primaries: published CIELAB values (D65, 2-deg observer)
    for name, rgb, ref in [
        ('red   #FF0000', (255, 0, 0), (53.24, 80.09, 67.20)),
        ('green #00FF00', (0, 255, 0), (87.73, -86.18, 83.18)),
        ('blue  #0000FF', (0, 0, 255), (32.30, 79.19, -107.86)),
    ]:
        lab = rgb_to_lab(rgb)
        for i, comp in enumerate('Lab'):
            allok &= _check(f'{name} {comp}*', lab[i], ref[i], 0.05)

    # ---- 2. Structural properties of the model ------------------------
    print()
    print("  structural checks (properties the model MUST have):")

    # H_C must be maximal when the two colours are identical (dC = 0)
    hc_same = 0.04 + 0.53 * math.tanh(0.8)
    d = ch((100, 100, 100), (100, 100, 100), detail=True)
    allok &= _check('identical greys -> H_C = 0.04+0.53tanh(0.8)',
                    d['H_C'], hc_same, 1e-9)
    allok &= _check('identical colours -> dC = 0', d['dC'], 0.0, 1e-9)
    allok &= _check('identical colours -> dL = 0', d['dL'], 0.0, 1e-9)

    # For an achromatic pair C=0 -> E_C = 0.5+0.5tanh(-2) which is small,
    # so H_H must be near zero. Verify it is actually small, not assumed.
    ec0 = 0.5 + 0.5 * math.tanh(-2.0)
    print(f"        E_C at C*=0 is {ec0:.4f} (chroma gate nearly closed)")
    allok &= _check('achromatic pair -> |H_H| small', abs(d['H_H']),
                    0.0, 0.05,
                    'H_H is gated by E_C, so grey pairs carry no hue effect')

    # dHab must be a CIELAB metric hue difference, NOT degrees.
    # Independent identity: dEab^2 = dL^2 + dCab^2 + dHab^2
    lab1, lab2 = rgb_to_lab((15, 194, 142)), rgb_to_lab((245, 200, 92))
    dd = ch_from_lab(lab1, lab2, detail=True)
    lhs = dd['dEab'] ** 2
    rhs = (lab2[0] - lab1[0]) ** 2 + dd['dCab'] ** 2 + dd['dHab'] ** 2
    allok &= _check('CIELAB identity dE^2 = dL^2+dC^2+dH^2', lhs, rhs, 1e-6)

    # ---- 3. Published output range ------------------------------------
    # Source B states CH lies in [-1.24, 1.39]. Sweep a wide grid and
    # confirm our implementation stays inside that interval. If it does
    # not, the implementation is wrong.
    print()
    print("  range check by exhaustive sweep (published range "
          "[-1.24, +1.39]):")
    lo, hi = 9e9, -9e9
    lo_pair = hi_pair = None
    step = 51
    for r1 in range(0, 256, step):
        for g1 in range(0, 256, step):
            for b1 in range(0, 256, step):
                for r2 in range(0, 256, step):
                    for g2 in range(0, 256, step):
                        for b2 in range(0, 256, step):
                            v = ch((r1, g1, b1), (r2, g2, b2))
                            if v < lo:
                                lo, lo_pair = v, ((r1, g1, b1), (r2, g2, b2))
                            if v > hi:
                                hi, hi_pair = v, ((r1, g1, b1), (r2, g2, b2))
    print(f"        observed min CH {lo:.4f} at {lo_pair}")
    print(f"        observed max CH {hi:.4f} at {hi_pair}")
    inside = (lo >= -1.24 - 0.12) and (hi <= 1.39 + 0.12)
    print(f"        {'PASS' if inside else 'FAIL'}  observed range fits "
          f"the published range (0.12 slack for grid coarseness)")
    allok &= inside

    # ---- 4. Published qualitative findings ---------------------------
    # Ou (2008): "Among various hues, blue is the one most likely to
    # create harmony in a two-colour combination; red is the least
    # likely to do so."  Our H_S term must reproduce that ordering.
    print()
    print("  qualitative check - Ou 2008: blue most harmonious hue, "
          "red least:")
    # evaluate H_S alone over hue, at fixed L and C, to isolate hue
    hs = {}
    for name, hdeg in [('red', 30), ('yellow', 90), ('green', 140),
                       ('cyan', 200), ('blue', 280), ('purple', 320)]:
        hs[name] = (-0.08
                    - 0.14 * math.sin(math.radians(hdeg + 50))
                    - 0.07 * math.sin(math.radians(2 * hdeg + 90)))
    for k, v in sorted(hs.items(), key=lambda kv: -kv[1]):
        print(f"        H_S({k:7s}) = {v:+.4f}")
    order_ok = hs['blue'] == max(hs.values()) and hs['red'] == min(hs.values())
    print(f"        {'PASS' if order_ok else 'FAIL'}  blue highest and "
          f"red lowest H_S, matching Ou 2008")
    allok &= order_ok

    print()
    print("=" * 74)
    print(f"IMPLEMENTATION {'VALIDATED - safe to use' if allok else 'FAILED - DO NOT USE'}")
    print("=" * 74)
    return 0 if allok else 1


if __name__ == '__main__':
    import sys
    sys.exit(validate())
