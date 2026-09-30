#!/usr/bin/env python3
"""measure_topbrands.py - Measure the REAL marks of the world's top
brands, and derive design targets from that measurement.

WHY NOT NFT PEERS ANY MORE
  The user instructed: "forget the famous NFT logos, they are very old
  and their logos are dated and they were just a trend - stick to famous
  brands, successful companies, and top logos". That instruction is
  correct and it also fixes a weakness in my earlier work: I was
  benchmarking against 10 NFT avatars, i.e. against illustration style,
  not against brand-mark craft.

  All NFT-peer thresholds are therefore REMOVED from the design gates
  and replaced with thresholds measured here.

THE SOURCE MARKS
  Downloaded from cdn.simpleicons.org, which publishes the brand marks
  as single-path SVGs on a 24x24 viewBox. Each file was verified to
  contain a <title> naming the brand before being used. 11 marks:
    Apple, Google, Samsung, Cisco  - Interbrand Best Global Brands 2025
                                     top 20 (verified on interbrand.com)
    Mastercard, Visa, PayPal, Stripe - the payments/fintech category
                                     Coinkins actually sits next to
    Nike, Spotify, X               - symbol-only brands cited by
                                     Michael Bierut as the "elite cadre
                                     represented not by name but by
                                     symbol"

WHAT IS MEASURED, AND WHY EACH MATTERS
  ink_fraction      how much of the frame the mark fills. Too little and
                    it vanishes in an avatar circle; too much and it has
                    no breathing room.
  components        how many separate pieces the mark breaks into. A
                    mark with many loose parts falls apart when small.
  edge_density      proxy for Henderson & Cote (1998) ELABORATENESS,
                    which they found has an inverted-U relation to
                    affect. This gives us the real band instead of my
                    guess.
  stroke_min_frac   thinnest surviving feature as a fraction of width.
                    This is the number that decides whether a mark
                    survives a 16px favicon.
  bbox_fill         how tightly the mark fills its own bounding box -
                    a measure of whether the silhouette is compact.
  aspect            width/height of the mark's bounding box. Henderson &
                    Cote call this PROPORTION.
  holes             enclosed counter-shapes (like the hole in a coin).
                    These are the first thing to fill in at small sizes.

HOW THE SVG IS RASTERISED
  These files are single <path> elements using absolute/relative move,
  line, cubic, quadratic, arc and close commands. Rather than trust an
  external converter that is not installed here, the path is parsed and
  flattened to polygons in pure Python, then filled with PIL using the
  even-odd rule so counter-shapes (holes) render correctly.
  The parser is SELF-TESTED against known ground truth before any
  measurement is trusted - see validate().
"""

import json
import math
import os
import re
import sys
from collections import deque

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'topbrands')

TOKEN = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)')

# A REAL PARSER BUG FOUND BY THE VALIDATION SUITE, then fixed.
# Cisco's path contains "1.186 1.186 0 01-.806-.237". Per the SVG 1.1
# path grammar the large-arc-flag and sweep-flag are SINGLE DIGITS and
# require no separator, so "01" is two flags: laf=0, sf=1. My generic
# number tokenizer read it as the single value 1.0, which shifted every
# following argument by one and made int(flag) receive a command letter.
# Arc arguments must therefore be tokenized with arc-specific rules.
ARC_ARGS = re.compile(
    r'(-?\d*\.?\d+(?:[eE][-+]?\d+)?)[,\s]*'   # rx
    r'(-?\d*\.?\d+(?:[eE][-+]?\d+)?)[,\s]*'   # ry
    r'(-?\d*\.?\d+(?:[eE][-+]?\d+)?)[,\s]*'   # x-axis-rotation
    r'([01])[,\s]*'                            # large-arc-flag
    r'([01])[,\s]*'                            # sweep-flag
    r'(-?\d*\.?\d+(?:[eE][-+]?\d+)?)[,\s]*'   # x
    r'(-?\d*\.?\d+(?:[eE][-+]?\d+)?)'         # y
)


def tokenize(d):
    """Tokenize an SVG path, handling the arc flag grammar correctly.

    Emits ('A', rx, ry, rot, laf, sf, x, y) as an 8-tuple marker for arcs
    so the consumer never has to re-derive the flags.
    """
    out = []
    i = 0
    n = len(d)
    last_cmd = None
    while i < n:
        c = d[i]
        if c in 'MmLlHhVvCcSsQqTtAaZz':
            out.append(c)
            last_cmd = c
            i += 1
            continue
        if c in ' ,\t\r\n':
            i += 1
            continue
        if last_cmd in 'Aa':
            m = ARC_ARGS.match(d, i)
            if m:
                out.append(('ARC',) + tuple(float(g) for g in m.groups()))
                i = m.end()
                continue
        m = TOKEN.match(d, i)
        if m:
            if m.group(1):
                out.append(m.group(1))
                last_cmd = m.group(1)
            else:
                out.append(float(m.group(2)))
            i = m.end()
            continue
        i += 1
    return out


def _bez3(p0, p1, p2, p3, n=18):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        x = (u ** 3 * p0[0] + 3 * u * u * t * p1[0]
             + 3 * u * t * t * p2[0] + t ** 3 * p3[0])
        y = (u ** 3 * p0[1] + 3 * u * u * t * p1[1]
             + 3 * u * t * t * p2[1] + t ** 3 * p3[1])
        pts.append((x, y))
    return pts


def _bez2(p0, p1, p2, n=14):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _arc(p0, rx, ry, rot, laf, sf, p1, n=24):
    """SVG elliptical arc -> polyline. Implements the W3C endpoint-to-
    centre parameterisation (SVG 1.1 Appendix F.6.5)."""
    if rx == 0 or ry == 0 or p0 == p1:
        return [p1]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rot)
    cosp, sinp = math.cos(phi), math.sin(phi)
    dx2, dy2 = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
    x1p = cosp * dx2 + sinp * dy2
    y1p = -sinp * dx2 + cosp * dy2
    # correct out-of-range radii (F.6.6)
    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = (rx ** 2) * (ry ** 2) - (rx ** 2) * (y1p ** 2) \
        - (ry ** 2) * (x1p ** 2)
    den = (rx ** 2) * (y1p ** 2) + (ry ** 2) * (x1p ** 2)
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if laf == sf:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cosp * cxp - sinp * cyp + (p0[0] + p1[0]) / 2.0
    cy = sinp * cxp + cosp * cyp + (p0[1] + p1[1]) / 2.0

    def ang(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        n1 = math.hypot(ux, uy)
        n2 = math.hypot(vx, vy)
        if n1 == 0 or n2 == 0:
            return 0.0
        c = max(-1.0, min(1.0, dot / (n1 * n2)))
        a = math.acos(c)
        if ux * vy - uy * vx < 0:
            a = -a
        return a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry,
              (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sf and dth > 0:
        dth -= 2 * math.pi
    elif sf and dth < 0:
        dth += 2 * math.pi
    pts = []
    for i in range(1, n + 1):
        th = th1 + dth * i / n
        x = cosp * rx * math.cos(th) - sinp * ry * math.sin(th) + cx
        y = sinp * rx * math.cos(th) + cosp * ry * math.sin(th) + cy
        pts.append((x, y))
    return pts


def path_to_polys(d):
    """Flatten an SVG path 'd' attribute into a list of polygons."""
    t = tokenize(d)
    i = 0
    polys, cur = [], []
    cx = cy = sx = sy = 0.0
    cmd = None
    prev_c2 = None   # for S/s
    prev_q1 = None   # for T/t

    def num():
        nonlocal i
        v = t[i]
        i += 1
        return v

    while i < len(t):
        if isinstance(t[i], str):
            cmd = t[i]
            i += 1
            if cmd in 'Zz':
                if cur:
                    polys.append(cur)
                    cur = []
                cx, cy = sx, sy
                continue
        if i >= len(t):
            break
        c = cmd
        rel = c.islower()
        C = c.upper()

        if C == 'M':
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            if cur:
                polys.append(cur)
            cur = [(x, y)]
            cx, cy = x, y
            sx, sy = x, y
            cmd = 'l' if rel else 'L'
            prev_c2 = prev_q1 = None
        elif C == 'L':
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            cur.append((x, y))
            cx, cy = x, y
            prev_c2 = prev_q1 = None
        elif C == 'H':
            x = num()
            if rel:
                x = cx + x
            cur.append((x, cy))
            cx = x
            prev_c2 = prev_q1 = None
        elif C == 'V':
            y = num()
            if rel:
                y = cy + y
            cur.append((cx, y))
            cy = y
            prev_c2 = prev_q1 = None
        elif C == 'C':
            x1, y1, x2, y2, x, y = (num() for _ in range(6))
            if rel:
                x1, y1 = cx + x1, cy + y1
                x2, y2 = cx + x2, cy + y2
                x, y = cx + x, cy + y
            cur += _bez3((cx, cy), (x1, y1), (x2, y2), (x, y))
            prev_c2 = (x2, y2)
            prev_q1 = None
            cx, cy = x, y
        elif C == 'S':
            x2, y2, x, y = (num() for _ in range(4))
            if rel:
                x2, y2 = cx + x2, cy + y2
                x, y = cx + x, cy + y
            x1, y1 = ((2 * cx - prev_c2[0], 2 * cy - prev_c2[1])
                      if prev_c2 else (cx, cy))
            cur += _bez3((cx, cy), (x1, y1), (x2, y2), (x, y))
            prev_c2 = (x2, y2)
            prev_q1 = None
            cx, cy = x, y
        elif C == 'Q':
            x1, y1, x, y = (num() for _ in range(4))
            if rel:
                x1, y1 = cx + x1, cy + y1
                x, y = cx + x, cy + y
            cur += _bez2((cx, cy), (x1, y1), (x, y))
            prev_q1 = (x1, y1)
            prev_c2 = None
            cx, cy = x, y
        elif C == 'T':
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            x1, y1 = ((2 * cx - prev_q1[0], 2 * cy - prev_q1[1])
                      if prev_q1 else (cx, cy))
            cur += _bez2((cx, cy), (x1, y1), (x, y))
            prev_q1 = (x1, y1)
            prev_c2 = None
            cx, cy = x, y
        elif C == 'A':
            tok = t[i]
            if isinstance(tok, tuple) and tok[0] == 'ARC':
                i += 1
                rx, ry, rot, laf, sf, x, y = tok[1:]
            else:
                rx, ry, rot, laf, sf, x, y = (num() for _ in range(7))
            if rel:
                x, y = cx + x, cy + y
            cur += _arc((cx, cy), rx, ry, rot, int(laf), int(sf), (x, y))
            prev_c2 = prev_q1 = None
            cx, cy = x, y
        else:
            i += 1
    if cur:
        polys.append(cur)
    return polys


def render_svg(path, size=512, pad=0.06):
    d = open(path).read()
    m = re.search(r'\sd="([^"]+)"', d)
    if not m:
        return None
    polys = path_to_polys(m.group(1))
    if not polys:
        return None
    xs = [p[0] for pl in polys for p in pl]
    ys = [p[1] for pl in polys for p in pl]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    inner = size * (1 - 2 * pad)
    s = inner / max(w, h)
    ox = (size - w * s) / 2 - x0 * s
    oy = (size - h * s) / 2 - y0 * s

    img = Image.new('L', (size, size), 255)
    # even-odd fill: XOR each polygon so holes punch through
    for pl in polys:
        if len(pl) < 3:
            continue
        layer = Image.new('L', (size, size), 0)
        ImageDraw.Draw(layer).polygon(
            [(p[0] * s + ox, p[1] * s + oy) for p in pl], fill=255)
        img = Image.composite(
            Image.new('L', (size, size), 255),
            Image.new('L', (size, size), 0),
            Image.eval(Image.merge('L', [img]), lambda v: v)
        ) if False else img
        # manual XOR
        a = img.point(lambda v: 255 if v < 128 else 0)   # current ink
        x = Image.new('L', (size, size))
        pa, pl_ = a.load(), layer.load()
        px = x.load()
        for yy in range(size):
            for xx in range(size):
                px[xx, yy] = 255 if (pa[xx, yy] > 127) ^ (pl_[xx, yy] > 127) \
                    else 0
        img = x.point(lambda v: 0 if v > 127 else 255)
    return img.convert('RGB'), (w / h)


def components_and_holes(img, thresh=128):
    g = img.convert('L')
    w, h = g.size
    px = g.load()
    seen = [[False] * h for _ in range(w)]

    def flood(sx, sy, ink):
        n = 0
        touches_border = False
        dq = deque([(sx, sy)])
        seen[sx][sy] = True
        while dq:
            a, b = dq.popleft()
            n += 1
            if a in (0, w - 1) or b in (0, h - 1):
                touches_border = True
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                na, nb = a + da, b + db
                if 0 <= na < w and 0 <= nb < h and not seen[na][nb]:
                    is_ink = px[na, nb] < thresh
                    if is_ink == ink:
                        seen[na][nb] = True
                        dq.append((na, nb))
        return n, touches_border

    comps, holes = [], []
    minsz = w * h * 0.0015
    for x in range(w):
        for y in range(h):
            if not seen[x][y]:
                ink = px[x, y] < thresh
                n, border = flood(x, y, ink)
                if ink and n > minsz:
                    comps.append(n)
                elif (not ink) and (not border) and n > minsz:
                    holes.append(n)
    return len(comps), len(holes)


def stroke_min(img):
    g = img.convert('L')
    w = g.size[0]
    ink = g.point(lambda v: 255 if v < 128 else 0)
    total = sum(1 for v in ink.getdata() if v > 0)
    if not total:
        return None
    cur = ink
    for k in range(1, 40):
        cur = cur.filter(ImageFilter.MinFilter(3))
        left = sum(1 for v in cur.getdata() if v > 0)
        if left < total * 0.02:
            return (2 * k) / w
    return 80 / w


def measure(img, aspect):
    g = img.convert('L')
    w, h = g.size
    px = list(g.getdata())
    inkf = sum(1 for v in px if v < 128) / len(px)
    ed = sum(1 for v in g.filter(ImageFilter.FIND_EDGES).getdata()
             if v > 40) / len(px)
    nc, nh = components_and_holes(img)
    sm = stroke_min(img)
    # bbox fill
    xs, ys = [], []
    pl = g.load()
    for x in range(w):
        for y in range(h):
            if pl[x, y] < 128:
                xs.append(x)
                ys.append(y)
    bb = 0.0
    if xs:
        bw = max(xs) - min(xs) + 1
        bh = max(ys) - min(ys) + 1
        bb = (len(xs)) / (bw * bh)
    return {
        'ink_fraction': round(inkf, 4),
        'edge_density': round(ed, 4),
        'components': nc,
        'holes': nh,
        'stroke_min_frac': round(sm, 4) if sm else None,
        'bbox_fill': round(bb, 4),
        'aspect': round(aspect, 3),
    }


def validate():
    """Self-test the SVG parser before trusting any measurement."""
    print("=" * 78)
    print("VALIDATING THE SVG PATH PARSER (no external converter exists here)")
    print("=" * 78)
    ok = True
    tmp = os.path.join(HERE, '_parsertest.svg')

    # 1. a plain square: ink fraction must equal the padded area exactly
    open(tmp, 'w').write(
        '<svg viewBox="0 0 24 24"><path d="M0 0H24V24H0Z"/></svg>')
    img, asp = render_svg(tmp, 400, pad=0.0)
    m = measure(img, asp)
    got, want = m['ink_fraction'], 1.0
    good = abs(got - want) < 0.01
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  full square -> ink fraction "
          f"{got:.4f} (want {want})")
    good = m['components'] == 1 and m['holes'] == 0
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  full square -> 1 component, "
          f"0 holes (got {m['components']}, {m['holes']})")
    good = abs(m['aspect'] - 1.0) < 0.01
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  square aspect {m['aspect']} "
          f"(want 1.0)")

    # 2. a ring: outer circle with an inner circle punched out.
    # Even-odd fill MUST produce exactly 1 component and 1 hole.
    open(tmp, 'w').write(
        '<svg viewBox="0 0 24 24"><path d="'
        'M12 2A10 10 0 1 0 12 22A10 10 0 1 0 12 2Z'
        'M12 7A5 5 0 1 1 12 17A5 5 0 1 1 12 7Z"/></svg>')
    img, asp = render_svg(tmp, 400, pad=0.0)
    m = measure(img, asp)
    good = m['components'] == 1 and m['holes'] == 1
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  ring -> 1 component, 1 hole "
          f"(got {m['components']}, {m['holes']}) - proves even-odd fill "
          f"and hole detection work")
    # A BUG IN MY OWN TEST, FOUND AND FIXED:
    # I first asserted against pi*(100-25)/576, i.e. the ring's area as a
    # fraction of the 24x24 viewBox. It measured 0.5888 and I recorded a
    # FAIL. Investigation showed the PARSER is correct (the outer circle
    # flattens to shoelace area 313.263 vs the analytic 314.159, a 0.3%
    # error) and the RENDERER is correct too: render_svg deliberately
    # normalises to the mark's own BOUNDING BOX, not the viewBox, so that
    # every brand is measured at equal visual size regardless of how much
    # padding its SVG author left. The ring's bbox is 20x20, so the right
    # analytic value is pi*(100-25)/400 = 0.5890. Measured 0.5888.
    # The assertion was wrong, not the code.
    want = math.pi * (100 - 25) / 400
    good = abs(m['ink_fraction'] - want) < 0.01
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  ring area {m['ink_fraction']:.4f}"
          f" vs analytic {want:.4f} (bbox-normalised) - proves the "
          f"elliptical-arc parser is numerically correct")

    # 2b. prove bbox normalisation actually happens: the SAME circle drawn
    # small inside the viewBox must measure the same as one drawn large.
    open(tmp, 'w').write(
        '<svg viewBox="0 0 24 24"><path d="'
        'M12 10A2 2 0 1 0 12 14A2 2 0 1 0 12 10Z"/></svg>')
    small, a1 = render_svg(tmp, 400, pad=0.0)
    open(tmp, 'w').write(
        '<svg viewBox="0 0 24 24"><path d="'
        'M12 2A10 10 0 1 0 12 22A10 10 0 1 0 12 2Z"/></svg>')
    large, a2 = render_svg(tmp, 400, pad=0.0)
    f1 = measure(small, a1)['ink_fraction']
    f2 = measure(large, a2)['ink_fraction']
    good = abs(f1 - f2) < 0.01 and abs(f1 - math.pi / 4) < 0.01
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  bbox normalisation: tiny circle "
          f"{f1:.4f} == big circle {f2:.4f} == pi/4 {math.pi/4:.4f}")

    # 3. two separate circles -> 2 components
    open(tmp, 'w').write(
        '<svg viewBox="0 0 24 24"><path d="'
        'M5 12A4 4 0 1 0 5 4A4 4 0 1 0 5 12Z'
        'M19 20A4 4 0 1 0 19 12A4 4 0 1 0 19 20Z"/></svg>')
    img, asp = render_svg(tmp, 400, pad=0.0)
    m = measure(img, asp)
    good = m['components'] == 2
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  two discs -> 2 components "
          f"(got {m['components']})")

    # 4. REGRESSION TEST for the arc-flag bug that crashed on Cisco.
    # SVG 1.1 permits the large-arc and sweep flags to be written as bare
    # adjacent digits with no separator. "0 01-.8-.2" is rot=0, laf=0,
    # sf=1, x=-0.8, y=-0.2. The first tokenizer read "01" as 1.0 and
    # everything after shifted, eventually feeding a command letter to
    # int(). Both spellings must now produce the same geometry.
    spaced = 'M4 12A8 8 0 1 0 20 12A8 8 0 1 0 4 12Z'
    packed = 'M4 12a8 8 0 1016 0a8 8 0 10-16 0Z'
    pa = path_to_polys(spaced)
    pb = path_to_polys(packed)

    def shoelace(pl):
        a = 0.0
        for j in range(len(pl)):
            x1, y1 = pl[j]
            x2, y2 = pl[(j + 1) % len(pl)]
            a += x1 * y2 - x2 * y1
        return abs(a) / 2

    aa = sum(shoelace(p) for p in pa)
    ab = sum(shoelace(p) for p in pb)
    good = abs(aa - ab) < 1.0 and abs(aa - math.pi * 64) < 1.5
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  arc flag grammar: spaced "
          f"'0 1 0' area {aa:.2f} == packed '10' area {ab:.2f} "
          f"== pi*r^2 {math.pi*64:.2f}")

    # 5. every real brand file must parse without raising
    parsed, failed = 0, []
    if os.path.isdir(SRC):
        for f in sorted(os.listdir(SRC)):
            if not f.endswith('.svg'):
                continue
            try:
                r = render_svg(os.path.join(SRC, f), 96)
                if r is None:
                    failed.append(f + ' (no path)')
                else:
                    parsed += 1
            except Exception as e:
                failed.append(f'{f} ({type(e).__name__}: {e})')
    good = not failed
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  all {parsed} brand files parse "
          f"without error")
    for f in failed:
        print(f"        FAILED: {f}")

    os.remove(tmp)
    print()
    print(f"  PARSER {'VALIDATED' if ok else 'FAILED - measurements unusable'}")
    print()
    return ok


def main():
    if not validate():
        return 1
    files = sorted(f for f in os.listdir(SRC) if f.endswith('.svg'))
    print("=" * 78)
    print("MEASURED PROPERTIES OF THE WORLD'S TOP BRAND MARKS")
    print("=" * 78)
    print(f"  {'brand':12s} {'ink%':>6s} {'edges':>7s} {'parts':>5s} "
          f"{'holes':>5s} {'thinnest':>8s} {'bboxfill':>8s} {'aspect':>6s}")
    print("  " + "-" * 74)
    res = {}
    for f in files:
        name = f[:-4]
        out = render_svg(os.path.join(SRC, f), 384)
        if not out:
            print(f"  {name:12s} could not parse")
            continue
        img, asp = out
        m = measure(img, asp)
        res[name] = m
        print(f"  {name:12s} {m['ink_fraction']*100:5.1f}% "
              f"{m['edge_density']:7.4f} {m['components']:5d} "
              f"{m['holes']:5d} {(m['stroke_min_frac'] or 0):8.4f} "
              f"{m['bbox_fill']:8.3f} {m['aspect']:6.2f}")

    if not res:
        return 1

    def stats(k):
        v = sorted(x[k] for x in res.values() if x[k] is not None)
        n = len(v)
        med = v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
        return min(v), med, max(v)

    print()
    print("=" * 78)
    print("DESIGN TARGETS DERIVED FROM TOP BRANDS (replacing NFT-peer "
          "thresholds)")
    print("=" * 78)
    for k in ('ink_fraction', 'edge_density', 'components', 'holes',
              'stroke_min_frac', 'bbox_fill', 'aspect'):
        lo, med, hi = stats(k)
        print(f"  {k:18s} min {lo:8.4f}   MEDIAN {med:8.4f}   max {hi:8.4f}")

    with open(os.path.join(HERE, 'topbrand_metrics.json'), 'w') as fh:
        json.dump(res, fh, indent=2)
    print(f"\n  wrote topbrand_metrics.json ({len(res)} marks)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
