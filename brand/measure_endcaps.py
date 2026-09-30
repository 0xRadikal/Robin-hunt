"""
measure_endcaps.py - DO real top-brand marks have rounded stroke ends?

WHY THIS EXISTS
---------------
The user proposed rounding the ends of our ring, "like other famous
logos". coinkins_mark.py currently documents the OPPOSITE choice: the
ends are cut on the radius, deliberately, so that no fourth radius is
introduced.

Both cannot be right. Rather than argue from memory or from counting SVG
path commands (a curve command may belong to the FORM, not to an end
cap), this module MEASURES the actual terminal geometry of the 11
verified brand SVGs.

METHOD
------
For each brand mark:
  1. rasterise it with the already-validated parser in measure_topbrands
  2. extract the outline, then walk the boundary and find CORNERS -
     points where the boundary direction changes sharply
  3. a stroke terminal that is SQUARE contributes two ~90 deg corners;
     a terminal that is ROUND contributes none
  4. report the corner count and the sharpest angles

Also, independently: for every boundary pixel, fit the local curvature.
A round cap of stroke half-width h has curvature ~1/h, which is HIGH but
FINITE and smooth. A square cap has a curvature singularity (a true
corner). Distinguishing the two is exactly what corner detection does.

CALIBRATION - the whole point
-----------------------------
Before believing anything about the brands, the detector is run on two
SYNTHETIC controls whose answer is known by construction:
  * a bar with SQUARE ends  -> must report 4 corners
  * a bar with ROUND ends   -> must report 0 corners
If the controls fail, the brand numbers are meaningless and we abort.
"""

import math
import os
import numpy as np
from PIL import Image, ImageDraw

import measure_topbrands as MT

HERE = os.path.dirname(os.path.abspath(__file__))
SVGDIR = os.path.join(HERE, 'topbrands')

RES = 512
CORNER_THRESH_DEG = 55.0   # direction change above this counts as a corner
WALK = 9                   # boundary samples each side used for direction


MIN_CONTOUR_AREA = 200      # ignore rasterisation specks


def all_boundaries(mask, min_area=MIN_CONTOUR_AREA):
    """EVERY significant boundary, not just the largest component.

    The first version of this function took only max(contourArea). That
    was a REAL DEFECT, proved by measurement: Cisco's mark is 15 separate
    contours (its parallel bars plus the dot), and taking only the
    largest reported a 231-pixel boundary with 0 corners - i.e. it
    measured the round dot and concluded "Cisco has no corners", while
    never looking at the bars at all. Every contour above a speck
    threshold is now returned.
    """
    import cv2
    m = (mask > 0).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cnts:
        if cv2.contourArea(c) < min_area:
            continue
        out.append([(int(p[0][0]), int(p[0][1])) for p in c])
    return out


def boundary_points(mask):
    """Largest boundary only - kept for the synthetic single-shape controls."""
    bs = all_boundaries(mask, min_area=0)
    if not bs:
        return []
    return max(bs, key=len)


def corners(pts, thresh_deg=CORNER_THRESH_DEG, walk=WALK):
    """Angles at which the boundary direction turns sharply.

    For each point, take the chord to the sample `walk` steps back and
    `walk` steps forward, and measure the turn between them. Using a
    chord over several pixels (rather than adjacent pixels) suppresses
    rasterisation jitter, which would otherwise register every staircase
    step as a corner.
    """
    n = len(pts)
    if n < 4 * walk:
        return [], []
    turns = []
    for i in range(n):
        ax, ay = pts[(i - walk) % n]
        bx, by = pts[i]
        cx, cy = pts[(i + walk) % n]
        v1 = (bx - ax, by - ay)
        v2 = (cx - bx, cy - by)
        n1 = math.hypot(*v1)
        n2 = math.hypot(*v2)
        if n1 < 1e-9 or n2 < 1e-9:
            turns.append(0.0)
            continue
        dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
        dot = max(-1.0, min(1.0, dot))
        turns.append(math.degrees(math.acos(dot)))
    turns = np.array(turns)
    # non-maximum suppression so one corner is counted once
    found = []
    i = 0
    while i < n:
        if turns[i] >= thresh_deg:
            j = i
            best = i
            while j < i + 3 * walk and turns[j % n] >= thresh_deg * 0.6:
                if turns[j % n] > turns[best % n]:
                    best = j
                j += 1
            found.append((best % n, float(turns[best % n])))
            i = j
        else:
            i += 1
    return found, turns


def synthetic_bar(round_ends, res=RES):
    """Control: a straight bar, square or round ended."""
    img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(img)
    y = res // 2
    h = res // 12          # stroke half-width
    x0, x1 = res // 5, res * 4 // 5
    if round_ends:
        d.line([(x0, y), (x1, y)], fill=255, width=2 * h)
        d.ellipse([x0 - h, y - h, x0 + h, y + h], fill=255)
        d.ellipse([x1 - h, y - h, x1 + h, y + h], fill=255)
    else:
        d.rectangle([x0, y - h, x1, y + h], fill=255)
    return np.asarray(img)


def our_ring(round_ends, res=RES):
    """Our own mark's ring, with square or round ends, for comparison."""
    import coinkins_mark as CM
    img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(img)
    U = res / CM.U_DIV
    c = res / 2.0
    CM._ring_with_gap(d, c, c, CM.R_OUTER_U * U, CM.R_INNER_U * U,
                      CM.GAP_HALF_DEG, 255)
    if round_ends:
        rc = (CM.R_OUTER_U - CM.R_INNER_U) / 2.0 * U     # cap radius
        rm = (CM.R_OUTER_U + CM.R_INNER_U) / 2.0 * U     # centreline
        for sgn in (+1, -1):
            a = math.radians(sgn * CM.GAP_HALF_DEG)
            x = c + rm * math.cos(a)
            y = c + rm * math.sin(a)
            d.ellipse([x - rc, y - rc, x + rc, y + rc], fill=255)
    return np.asarray(img)


def analyse(mask, label, verbose=True):
    """Corner count summed over ALL significant contours of the mark."""
    bs = all_boundaries(mask)
    total = 0
    sharp = []
    plen = 0
    for pts in bs:
        cs, _ = corners(pts)
        total += len(cs)
        sharp.extend(t for _, t in cs)
        plen += len(pts)
    sharp.sort(reverse=True)
    if verbose:
        print('  %-26s parts=%-3d boundary=%-5d corners=%-3d sharpest=%s'
              % (label, len(bs), plen, total,
                 ' '.join('%.0f' % s for s in sharp[:6]) or '-'))
    return total, sharp


def main():
    print('=' * 84)
    print('CALIBRATION - the detector must get the KNOWN answers right')
    print('=' * 84)
    ok = True
    nsq, _ = analyse(synthetic_bar(False), 'control: SQUARE-ended bar')
    nrd, _ = analyse(synthetic_bar(True), 'control: ROUND-ended bar')
    c1 = nsq >= 4
    c2 = nrd == 0
    print('  [%s] square bar must show >=4 corners  (got %d)'
          % ('PASS' if c1 else 'FAIL', nsq))
    print('  [%s] round bar must show 0 corners     (got %d)'
          % ('PASS' if c2 else 'FAIL', nrd))
    ok = c1 and c2
    if not ok:
        print()
        print('DETECTOR NOT TRUSTWORTHY - aborting, no brand claims will be made')
        return False

    print()
    print('=' * 84)
    print('THE 11 REAL TOP-BRAND MARKS')
    print('=' * 84)
    results = {}
    for fn in sorted(os.listdir(SVGDIR)):
        if not fn.endswith('.svg'):
            continue
        name = fn[:-4]
        path = os.path.join(SVGDIR, fn)
        out = MT.render_svg(path, size=RES)
        if out is None:
            print('  %-26s SKIPPED (no path data)' % name)
            continue
        img, _aspect = out      # render_svg returns (image, aspect ratio)
        arr = np.asarray(img.convert('L'))
        mask = (arr < 128).astype(np.uint8) * 255
        n, sharp = analyse(mask, name)
        results[name] = (n, sharp)

    print()
    print('=' * 84)
    print('OUR OWN MARK, BOTH WAYS')
    print('=' * 84)
    nsq_o, _ = analyse(our_ring(False), 'ours: SQUARE ends (current)')
    nrd_o, _ = analyse(our_ring(True), 'ours: ROUND ends (proposed)')

    print()
    print('=' * 84)
    print('WHAT THE MEASUREMENT ACTUALLY SHOWS')
    print('=' * 84)
    zero = [k for k, (n, _) in results.items() if n == 0]
    few = [k for k, (n, _) in results.items() if 1 <= n <= 4]
    many = [k for k, (n, _) in results.items() if n > 4]
    print('  0 corners (fully curved outline) : %d  %s'
          % (len(zero), ', '.join(sorted(zero))))
    print('  1-4 corners                      : %d  %s'
          % (len(few), ', '.join(sorted(few))))
    print('  >4 corners (has sharp vertices)  : %d  %s'
          % (len(many), ', '.join(sorted(many))))
    print()
    print('  ours with SQUARE ends: %d corners' % nsq_o)
    print('  ours with ROUND  ends: %d corners' % nrd_o)
    return True


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
