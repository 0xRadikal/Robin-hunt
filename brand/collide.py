"""
collide.py - NUMERICAL COLLISION MEASUREMENT for the Coinkins mark.

PURPOSE
-------
Independent visual review said variant A "heavily resembles" the Colorado
state flag, and flagged the copyright symbol / bullseye. Those are opinions.
This module turns them into NUMBERS so that any claimed reduction is
PROVABLE rather than asserted.

WHAT IS MEASURED
----------------
Four independent distance metrics between variant A and each reference:

  D1  IoU-based shape distance       1 - IoU of scale/centroid-aligned masks
  D2  Hu-moment log distance         translation/scale/rotation invariant
  D3  Radial-signature distance      mean |r_A(theta) - r_B(theta)| of the
                                     outer boundary, scale-normalised
  D4  Parameter-space distance       only for the ring+disc family; compares
                                     the 3 construction parameters directly

D1 is reported twice:
  D1_asdrawn  - masks in their natural orientation
  D1_bestrot  - minimised over rotation (the CONSERVATIVE / worst case)
D1_bestrot is the honest number: it asks "even at the most flattering
alignment, how different are they?"

REFERENCES - PROVENANCE OF EVERY ONE
------------------------------------
R1 colorado   C.R.S. 24-80-904, quoted verbatim in the docstring of
              colorado_params(). Geometry DERIVED from the statute, not
              eyeballed; the derivation is re-verified at import time.
R2 copyright  the real U+00A9 glyph from DejaVuSans.ttf. Not a redrawing.
R3 bullseye   three concentric circles, the mark held INVALID in
              T-347/24 Target Brands v EUIPO (Gen. Court, 9 July 2025).
R4 power      IEC 60417-5009 "standby": ring with a gap at top + a bar
              through the gap.
R5 self       variant A against itself - MUST give distance 0. This is the
              calibration control that proves the metrics are not garbage.

HONESTY NOTES
-------------
* No metric here is a legal test. Trademark similarity is a question of
  consumer perception decided by tribunals, not of pixel overlap. These
  numbers measure GEOMETRIC distance only, and are used solely to compare
  candidate refinements of our own mark against each other.
* Higher distance = less resemblance. There is no published threshold for
  "far enough"; the numbers are used COMPARATIVELY (before vs after).
"""

import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import coinkins_mark as CM

RES = 512          # working raster size
SS = 4             # supersample for reference construction

# ----------------------------------------------------------------------------
# REFERENCE 1: Colorado state flag "C" + golden disc
# ----------------------------------------------------------------------------

def colorado_params():
    """Derive the Colorado C geometry from the STATUTE.

    C.R.S. Title 24, Article 80, Part 9 (verbatim, relevant portion):

        "At a distance from the staff end of the flag of one-fifth of the
         total length of the flag there shall be a circular red C ...
         The diameter of the letter shall be two-thirds of the width of
         the flag. The inner line of the opening of the letter C shall be
         three-fourths of the width of its body or bar, and the outer line
         of the opening shall be double the length of the inner line
         thereof. Completely filling the open space inside the letter C
         shall be a golden disk"

    Let the outer radius be R = 1 and the inner radius be a, so the body
    (bar) width is (1 - a). The ends of the C are cut on the radius, so the
    opening subtends the same angle t at both radii. Then:

        inner line  = 2*a*sin(t/2) = 0.75*(1-a)        (1)
        outer line  = 2*1*sin(t/2) = 1.50*(1-a)        (2)

    Dividing (1) by (2) gives a = 0.75/1.50 = 0.5 EXACTLY - the statute
    determines the inner radius uniquely. Substituting back into (1):

        sin(t/2) = 0.75*(1-0.5)/(2*0.5) = 0.375
        t        = 2*asin(0.375) = 44.0486 deg

    The 1964 amendment set the gold disc diameter equal to the centre
    stripe width. The flag is 3 stripes wide and the letter diameter is
    2/3 of the flag width, i.e. 2 units for a 3-unit-wide flag, so R = 1
    and one stripe = 1 unit => disc radius 0.5 = a. The disc therefore
    COMPLETELY fills the opening: fill ratio = 1.0000.

    Returns (r_outer, r_inner, r_disc, gap_half_deg), normalised to r_outer=1.
    """
    a = 0.75 / 1.50                       # = 0.5, forced by (1)/(2)
    body = 1.0 - a
    s = 0.75 * body / (2.0 * a)           # sin(t/2) from eq (1)
    t = 2.0 * math.degrees(math.asin(s))
    disc = 0.5                            # 1964 amendment
    # re-verify BOTH statutory equations every import - never trust the algebra
    e1 = abs(2 * a * math.sin(math.radians(t / 2)) - 0.75 * body)
    e2 = abs(2 * 1 * math.sin(math.radians(t / 2)) - 1.50 * body)
    assert e1 < 1e-12, 'Colorado eq(1) violated: %g' % e1
    assert e2 < 1e-12, 'Colorado eq(2) violated: %g' % e2
    assert abs(disc - a) < 1e-12, 'Colorado disc must exactly fill the opening'
    return (1.0, a, disc, t / 2.0)


# ----------------------------------------------------------------------------
# generic ring+disc rasteriser (shared so A and the references are
# rendered by IDENTICAL code - no rendering bias between them)
# ----------------------------------------------------------------------------

def ring_disc_mask(r_out, r_in, r_disc, gap_half_deg, gap_centre_deg=0.0,
                   res=RES, span=1.15):
    """Binary mask (uint8 0/1) of an annulus with an angular gap plus a
    concentric disc. `span` is the half-width of the view in units of
    r_out, so the shape is framed identically regardless of parameters."""
    n = res * SS
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    scale = (n / 2.0) / span          # pixels per unit of r_out
    cx = cy = n / 2.0

    # annulus with gap, as ONE filled polygon so the ends are cut on the
    # radius (a round cap would introduce a radius that is not in the spec)
    if r_in < r_out and gap_half_deg < 180.0:
        a0 = gap_centre_deg + gap_half_deg
        a1 = gap_centre_deg + 360.0 - gap_half_deg
        steps = 720
        pts = []
        for i in range(steps + 1):
            th = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((cx + r_out * scale * math.cos(th),
                        cy + r_out * scale * math.sin(th)))
        for i in range(steps, -1, -1):
            th = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((cx + r_in * scale * math.cos(th),
                        cy + r_in * scale * math.sin(th)))
        d.polygon(pts, fill=255)

    if r_disc > 0:
        rr = r_disc * scale
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)

    img = img.resize((res, res), Image.LANCZOS)
    return (np.asarray(img) > 127).astype(np.uint8)


def variant_a_mask(r_out=None, r_in=None, r_disc=None, gap_half=None,
                   res=RES, gap_centre_deg=0.0):
    """Variant A as a mask, via the SAME rasteriser as the references.
    Defaults read the live constants from coinkins_mark."""
    ro = CM.R_OUTER_U if r_out is None else r_out
    ri = CM.R_INNER_U if r_in is None else r_in
    rd = CM.R_DISC_U if r_disc is None else r_disc
    gh = CM.GAP_HALF_DEG if gap_half is None else gap_half
    # normalise so outer radius == 1
    return ring_disc_mask(1.0, ri / ro, rd / ro, gh, gap_centre_deg, res=res)


# ----------------------------------------------------------------------------
# REFERENCE 2: the real copyright glyph
# ----------------------------------------------------------------------------

FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
]

def glyph_mask(ch=u'\u00a9', res=RES, span=1.15):
    """Mask of a REAL font glyph, tightly fitted then framed to the same
    `span` convention as ring_disc_mask so the comparison is fair."""
    path = None
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            path = p
            break
    if path is None:
        raise RuntimeError('no font found for glyph reference')
    big = res * 2
    f = ImageFont.truetype(path, int(big * 0.8))
    tmp = Image.new('L', (big, big), 0)
    ImageDraw.Draw(tmp).text((big * 0.1, big * 0.1), ch, font=f, fill=255)
    arr = np.asarray(tmp)
    ys, xs = np.nonzero(arr > 127)
    if len(xs) == 0:
        raise RuntimeError('glyph rendered empty')
    tmp = tmp.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    # the glyph's own bounding circle maps onto diameter 2*r_out=2 units,
    # and the view is 2*span units wide -> glyph should occupy 1/span of frame
    target = int(round(res / span))
    tmp = tmp.resize((target, target), Image.LANCZOS)
    out = Image.new('L', (res, res), 0)
    off = (res - target) // 2
    out.paste(tmp, (off, off))
    return (np.asarray(out) > 127).astype(np.uint8)


# ----------------------------------------------------------------------------
# REFERENCE 3: concentric bullseye (the mark invalidated in T-347/24)
# ----------------------------------------------------------------------------

def bullseye_mask(res=RES, span=1.15):
    """Three concentric rings: outer ring, gap, inner disc - i.e. the
    'red circle (dot) inscribed in a red circle outline' described by the
    EUIPO Board of Appeal in T-347/24. Proportions taken as the classic
    equal-band bullseye: outer 1.0, ring inner 0.667, disc 0.333."""
    return ring_disc_mask(1.0, 2.0 / 3.0, 1.0 / 3.0, 0.0, 0.0,
                          res=res, span=span)


# ----------------------------------------------------------------------------
# REFERENCE 4: IEC 60417-5009 power / standby
# ----------------------------------------------------------------------------

def power_mask(res=RES, span=1.15):
    """Ring with a gap at the top plus a vertical bar through the gap."""
    n = res * SS
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    scale = (n / 2.0) / span
    cx = cy = n / 2.0
    r_out, r_in = 1.0, 0.78
    gap_half = 22.0
    # PIL y grows downward, so -90 deg is screen TOP
    a0 = -90.0 + gap_half
    a1 = -90.0 + 360.0 - gap_half
    steps = 720
    pts = []
    for i in range(steps + 1):
        th = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r_out * scale * math.cos(th),
                    cy + r_out * scale * math.sin(th)))
    for i in range(steps, -1, -1):
        th = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r_in * scale * math.cos(th),
                    cy + r_in * scale * math.sin(th)))
    d.polygon(pts, fill=255)
    bw = (1.0 - 0.78) / 2.0 * scale
    d.rectangle([cx - bw, cy - 1.15 * scale, cx + bw, cy - 0.30 * scale],
                fill=255)
    img = img.resize((res, res), Image.LANCZOS)
    return (np.asarray(img) > 127).astype(np.uint8)


# ----------------------------------------------------------------------------
# METRICS
# ----------------------------------------------------------------------------

def _centroid(m):
    ys, xs = np.nonzero(m)
    return xs.mean(), ys.mean()


def _normalise(m, res=RES):
    """Translate to centroid and scale so the ink area is a fixed fraction.
    Area normalisation (not bbox) because bbox is dominated by the single
    outermost pixel and is therefore noisy."""
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return m.copy()
    cx, cy = xs.mean(), ys.mean()
    area = float(len(xs))
    target = 0.25 * res * res            # fixed reference area
    s = math.sqrt(target / area)
    img = Image.fromarray((m * 255).astype(np.uint8))
    nw = max(1, int(round(res * s)))
    img = img.resize((nw, nw), Image.LANCZOS)
    a = (np.asarray(img) > 127).astype(np.uint8)
    ys2, xs2 = np.nonzero(a)
    if len(xs2) == 0:
        return np.zeros((res, res), np.uint8)
    cx2, cy2 = xs2.mean(), ys2.mean()
    out = np.zeros((res, res), np.uint8)
    dx = int(round(res / 2.0 - cx2))
    dy = int(round(res / 2.0 - cy2))
    for y, x in zip(ys2, xs2):
        yy, xx = y + dy, x + dx
        if 0 <= yy < res and 0 <= xx < res:
            out[yy, xx] = 1
    return out


def iou(a, b):
    inter = np.logical_and(a, b).sum()
    uni = np.logical_or(a, b).sum()
    return float(inter) / float(uni) if uni else 0.0


def d1_iou(a, b, res=RES, rotations=None):
    """1 - IoU after area+centroid normalisation.
    Returns (d_asdrawn, d_bestrot, best_angle)."""
    na = _normalise(a, res)
    nb = _normalise(b, res)
    as_drawn = 1.0 - iou(na, nb)
    if rotations is None:
        rotations = range(0, 360, 5)
    best, bang = as_drawn, 0
    imb = Image.fromarray((nb * 255).astype(np.uint8))
    for ang in rotations:
        if ang == 0:
            v = as_drawn
        else:
            rb = imb.rotate(ang, resample=Image.BILINEAR, fillcolor=0)
            rb = (np.asarray(rb) > 127).astype(np.uint8)
            v = 1.0 - iou(na, rb)
        if v < best:
            best, bang = v, ang
    return as_drawn, best, bang


def hu(m):
    mm = cv_moments(m)
    return mm


def cv_moments(m):
    """Hu moments without OpenCV dependence on contours - computed from the
    filled mask via raw image moments (Hu 1962)."""
    m = m.astype(np.float64)
    h, w = m.shape
    y, x = np.mgrid[0:h, 0:w].astype(np.float64)
    m00 = m.sum()
    if m00 == 0:
        return np.zeros(7)
    xb = (x * m).sum() / m00
    yb = (y * m).sum() / m00
    xc, yc = x - xb, y - yb

    def mu(p, q):
        return ((xc ** p) * (yc ** q) * m).sum()

    def nu(p, q):
        return mu(p, q) / (m00 ** (1.0 + (p + q) / 2.0))

    n20, n02, n11 = nu(2, 0), nu(0, 2), nu(1, 1)
    n30, n03, n21, n12 = nu(3, 0), nu(0, 3), nu(2, 1), nu(1, 2)
    h1 = n20 + n02
    h2 = (n20 - n02) ** 2 + 4 * n11 ** 2
    h3 = (n30 - 3 * n12) ** 2 + (3 * n21 - n03) ** 2
    h4 = (n30 + n12) ** 2 + (n21 + n03) ** 2
    h5 = ((n30 - 3 * n12) * (n30 + n12) *
          ((n30 + n12) ** 2 - 3 * (n21 + n03) ** 2) +
          (3 * n21 - n03) * (n21 + n03) *
          (3 * (n30 + n12) ** 2 - (n21 + n03) ** 2))
    h6 = ((n20 - n02) * ((n30 + n12) ** 2 - (n21 + n03) ** 2) +
          4 * n11 * (n30 + n12) * (n21 + n03))
    h7 = ((3 * n21 - n03) * (n30 + n12) *
          ((n30 + n12) ** 2 - 3 * (n21 + n03) ** 2) -
          (n30 - 3 * n12) * (n21 + n03) *
          (3 * (n30 + n12) ** 2 - (n21 + n03) ** 2))
    return np.array([h1, h2, h3, h4, h5, h6, h7])


def d2_hu(a, b):
    """Log-magnitude Hu distance (the standard CV_CONTOURS_MATCH_I3-style
    formulation applied to filled-mask Hu moments)."""
    ha, hb = cv_moments(a), cv_moments(b)
    tot = 0.0
    for i in range(7):
        va = math.copysign(math.log10(abs(ha[i])), ha[i]) if ha[i] != 0 else 0.0
        vb = math.copysign(math.log10(abs(hb[i])), hb[i]) if hb[i] != 0 else 0.0
        tot += abs(va - vb)
    return tot


def radial_signature(m, nbins=360):
    """Max ink radius as a function of angle, normalised by its own mean.
    Captures the OUTER silhouette including where the gap cuts it."""
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return np.zeros(nbins)
    cx, cy = xs.mean(), ys.mean()
    dx, dy = xs - cx, ys - cy
    r = np.sqrt(dx * dx + dy * dy)
    th = (np.degrees(np.arctan2(dy, dx)) + 360.0) % 360.0
    idx = (th / 360.0 * nbins).astype(int) % nbins
    sig = np.zeros(nbins)
    np.maximum.at(sig, idx, r)
    mean = sig[sig > 0].mean() if (sig > 0).any() else 1.0
    return sig / mean


def d3_radial(a, b, nbins=360):
    """Mean absolute difference of radial signatures, minimised over
    circular shift (so gap POSITION does not dominate; gap WIDTH does)."""
    sa, sb = radial_signature(a, nbins), radial_signature(b, nbins)
    best = None
    for s in range(nbins):
        v = np.abs(sa - np.roll(sb, s)).mean()
        if best is None or v < best:
            best = v
    return float(best)


def d4_params(pa, pb):
    """Euclidean distance in the 3-D construction-parameter space of the
    ring+disc family: (r_in/r_out, r_disc/r_in, gap_half/180).
    Only defined where both shapes belong to that family."""
    ao, ai, ad, ag = pa
    bo, bi, bd, bg = pb
    va = np.array([ai / ao, (ad / ai) if ai else 0.0, ag / 180.0])
    vb = np.array([bi / bo, (bd / bi) if bi else 0.0, bg / 180.0])
    return float(np.linalg.norm(va - vb))


# ----------------------------------------------------------------------------
# DRIVER
# ----------------------------------------------------------------------------

def a_params(r_out=None, r_in=None, r_disc=None, gap_half=None):
    ro = CM.R_OUTER_U if r_out is None else r_out
    ri = CM.R_INNER_U if r_in is None else r_in
    rd = CM.R_DISC_U if r_disc is None else r_disc
    gh = CM.GAP_HALF_DEG if gap_half is None else gap_half
    return (1.0, ri / ro, rd / ro, gh)


def references(res=RES):
    co = colorado_params()
    return [
        ('R1 colorado C+disc', ring_disc_mask(*co, gap_centre_deg=0.0, res=res), co),
        ('R2 copyright glyph', glyph_mask(res=res), None),
        ('R3 bullseye T-347/24', bullseye_mask(res=res), (1.0, 2 / 3, 1 / 3, 0.0)),
        ('R4 power IEC 5009', power_mask(res=res), None),
    ]


def measure(r_out=None, r_in=None, r_disc=None, gap_half=None,
            res=RES, label='variant A', verbose=True):
    A = variant_a_mask(r_out, r_in, r_disc, gap_half, res=res)
    pa = a_params(r_out, r_in, r_disc, gap_half)
    rows = []
    for name, M, pb in references(res=res):
        dd, dr, ang = d1_iou(A, M, res=res)
        row = {
            'ref': name,
            'D1_asdrawn': dd,
            'D1_bestrot': dr,
            'bestang': ang,
            'D2_hu': d2_hu(A, M),
            'D3_radial': d3_radial(A, M),
            'D4_param': d4_params(pa, pb) if pb else float('nan'),
        }
        rows.append(row)
    # R5 calibration control: A vs itself must be exactly 0
    dd, dr, ang = d1_iou(A, A, res=res)
    rows.append({'ref': 'R5 self (control)', 'D1_asdrawn': dd,
                 'D1_bestrot': dr, 'bestang': ang, 'D2_hu': d2_hu(A, A),
                 'D3_radial': d3_radial(A, A),
                 'D4_param': d4_params(pa, pa)})
    if verbose:
        print('  %-22s %10s %10s %6s %9s %9s %9s'
              % ('reference', 'D1_drawn', 'D1_bestrot', 'ang', 'D2_hu',
                 'D3_radial', 'D4_param'))
        for r in rows:
            print('  %-22s %10.4f %10.4f %6d %9.4f %9.4f %9.4f'
                  % (r['ref'], r['D1_asdrawn'], r['D1_bestrot'], r['bestang'],
                     r['D2_hu'], r['D3_radial'], r['D4_param']))
    return rows


def validate():
    """Prove the metrics work BEFORE trusting any number they produce."""
    print('=' * 78)
    print('METRIC VALIDATION - nothing below is trusted until these pass')
    print('=' * 78)
    ok = True
    res = 256

    def chk(name, cond, detail=''):
        nonlocal ok
        print('  [%s] %-52s %s' % ('PASS' if cond else 'FAIL', name, detail))
        if not cond:
            ok = False

    A = variant_a_mask(res=res)
    chk('T1 variant A mask is non-empty', A.sum() > 0, 'ink=%d' % A.sum())

    # T2 identity
    dd, dr, _ = d1_iou(A, A, res=res)
    chk('T2 D1(A,A) == 0', dd < 1e-9 and dr < 1e-9, 'drawn=%.2e rot=%.2e' % (dd, dr))
    chk('T3 D2(A,A) == 0', d2_hu(A, A) < 1e-9, '%.2e' % d2_hu(A, A))
    chk('T4 D3(A,A) == 0', d3_radial(A, A) < 1e-9, '%.2e' % d3_radial(A, A))

    # T5 translation invariance: shifting a mask must not change D1
    sh = np.zeros_like(A)
    sh[:, 12:] = A[:, :-12]
    dd2, _, _ = d1_iou(A, sh, res=res)
    chk('T5 D1 translation-invariant', dd2 < 0.02, 'D1=%.4f' % dd2)

    # T6 scale invariance: a 1.6x scaled copy must still match
    big = Image.fromarray((A * 255).astype(np.uint8)).resize(
        (int(res * 1.6), int(res * 1.6)), Image.LANCZOS)
    canv = Image.new('L', (res * 2, res * 2), 0)
    canv.paste(big, (30, 30))
    canv = canv.resize((res, res), Image.LANCZOS)
    bigm = (np.asarray(canv) > 127).astype(np.uint8)
    dd3, _, _ = d1_iou(A, bigm, res=res)
    chk('T6 D1 scale-invariant', dd3 < 0.06, 'D1=%.4f' % dd3)

    # T7 a clearly different shape must score far
    sq = np.zeros((res, res), np.uint8)
    sq[60:196, 60:196] = 1
    dd4, dr4, _ = d1_iou(A, sq, res=res)
    chk('T7 D1(A, solid square) is large', dr4 > 0.35, 'D1_bestrot=%.4f' % dr4)

    # T8 monotonicity: as fill ratio -> 1.0 the Colorado distance must FALL
    co = colorado_params()
    COL = ring_disc_mask(*co, gap_centre_deg=0.0, res=res)
    ds = []
    for fill in (0.55, 0.6875, 0.85, 1.00):
        m = ring_disc_mask(1.0, co[1], co[1] * fill, co[3], 0.0, res=res)
        _, dr5, _ = d1_iou(m, COL, res=res)
        ds.append((fill, dr5))
    mono = all(ds[i][1] > ds[i + 1][1] for i in range(len(ds) - 1))
    chk('T8 D1 falls monotonically as fill -> Colorado',
        mono, ' '.join('%.2f:%.4f' % x for x in ds))
    # and at fill=1.0 with matched radii it must be ~0
    chk('T9 D1 ~ 0 when geometry matches Colorado exactly',
        ds[-1][1] < 0.02, 'D1=%.4f' % ds[-1][1])

    # T10 Colorado statutory derivation re-verified
    chk('T10 Colorado params from statute', abs(co[1] - 0.5) < 1e-12 and
        abs(co[2] / co[1] - 1.0) < 1e-12 and abs(co[3] - 22.0243127) < 1e-6,
        'inner=%.4f fill=%.4f gaphalf=%.4f' % (co[1], co[2] / co[1], co[3]))

    # T11 references all render
    for name, M, _ in references(res=res):
        chk('T11 %s renders' % name, M.sum() > 0, 'ink=%d' % M.sum())

    # T12 glyph reference really is the copyright glyph, not a blank/box
    G = glyph_mask(res=res)
    frac = G.sum() / float(res * res)
    chk('T12 copyright glyph ink fraction sane', 0.05 < frac < 0.60,
        'ink=%.4f' % frac)

    # T13 D4 parameter distance is 0 for identical params, >0 otherwise
    pa = a_params()
    chk('T13 D4 identity == 0', d4_params(pa, pa) < 1e-12)
    chk('T14 D4 positive for Colorado', d4_params(pa, co) > 0.1,
        '%.4f' % d4_params(pa, co))

    print()
    print('VALIDATION: %s' % ('ALL PASS' if ok else 'FAILURES PRESENT'))
    return ok


if __name__ == '__main__':
    if not validate():
        raise SystemExit('metrics not trustworthy - aborting')
    print()
    print('=' * 78)
    print('BASELINE - variant A AS APPROVED (r_out=%.2f r_in=%.2f r_disc=%.2f gap=%.1f)'
          % (CM.R_OUTER_U, CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG))
    print('=' * 78)
    measure()
