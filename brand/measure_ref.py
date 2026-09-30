"""
measure_ref.py - MEASURE the user's reference image instead of guessing.

The user supplied a reference logo and said "make the white edges longer
like this one". "Longer" is not a number, so this module extracts the
ACTUAL geometry of the reference:

    r_outer, r_inner, r_disc, and the gap half-angle

Method
------
1. Isolate the light ring by colour: the reference has a dark navy field,
   a near-white ring, and a saturated gold disc. Classify every pixel
   into one of those three, using distance in RGB with a margin, and
   report how many pixels fall into none of them (so a bad segmentation
   cannot pass silently).
2. Find the mark centre as the centroid of ring+disc together.
3. For the ring: build a histogram of pixel radius. The ring occupies a
   band, so r_inner and r_outer are the 2nd and 98th percentiles of that
   radius distribution (percentiles, not min/max, because the reference
   is a soft-edged raster with a drop shadow and gradients).
4. For the gap: walk 0..359 degrees along the ring's mid-radius and
   record where there is no ring pixel. Report the span AND its centre.
5. Normalise everything by r_outer so it can be compared directly with
   our own construction, which is expressed in units of U = width/16.

Every number printed is accompanied by the raw pixel count it came from,
so the reader can judge whether it is trustworthy.
"""

import math
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'ref', 'user-ref.png')


def classify(arr, tol=70):
    """Split into ring (light), disc (gold), field (dark navy)."""
    a = arr.astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)

    # gold: bright, strongly saturated, red+green >> blue
    disc = (sat > 0.45) & (r > 150) & (g > 90) & (b < 140)
    # light ring: bright and NOT saturated
    ring = (lum > 150) & (sat <= 0.45) & (~disc)
    # dark field
    field = (lum <= 150) & (~disc)
    return ring, disc, field


def radial_stats(mask, cx, cy):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    rr = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    return rr


def main():
    im = Image.open(REF).convert('RGB')
    W, H = im.size
    arr = np.asarray(im)
    print('=' * 84)
    print('MEASURING THE USER REFERENCE  %s  %dx%d' % (os.path.basename(REF), W, H))
    print('=' * 84)

    ring, disc, field = classify(arr)
    tot = W * H
    unclass = tot - int(ring.sum()) - int(disc.sum()) - int(field.sum())
    print('  segmentation: ring=%d (%.2f%%)  disc=%d (%.2f%%)  '
          'field=%d (%.2f%%)  unclassified=%d'
          % (ring.sum(), 100 * ring.sum() / tot,
             disc.sum(), 100 * disc.sum() / tot,
             field.sum(), 100 * field.sum() / tot, unclass))
    if unclass != 0:
        print('  WARNING unclassified pixels exist - segmentation incomplete')

    # The reference contains a WORDMARK below the mark. It must be excluded
    # or it will drag the centroid down and corrupt every radius.
    # Strategy: the disc is unique to the mark, so use the disc centroid as
    # the mark centre, then keep only ring pixels within a generous radius.
    dys, dxs = np.nonzero(disc)
    if len(dxs) == 0:
        print('  FAIL no gold disc found - cannot proceed')
        return False
    cx, cy = dxs.mean(), dys.mean()
    r_disc_px = math.sqrt(disc.sum() / math.pi)
    print()
    print('  gold disc: centroid=(%.1f, %.1f)  area=%d px  '
          'equivalent radius=%.1f px' % (cx, cy, disc.sum(), r_disc_px))

    # verify the disc really is round (area vs bounding box)
    bw = dxs.max() - dxs.min() + 1
    bh = dys.max() - dys.min() + 1
    circ = disc.sum() / (math.pi * (bw / 2.0) * (bh / 2.0))
    print('  disc bbox=%dx%d  area/ellipse=%.4f (1.0 = perfect ellipse)'
          % (bw, bh, circ))
    if abs(circ - 1.0) > 0.15:
        print('  WARNING disc is not a clean circle; radii may be unreliable')

    # SEPARATE THE MARK FROM THE WORDMARK.
    # A simple "within 4x the disc radius" filter was NOT enough: the
    # radius histogram came out bimodal (p50=187px but p98=357px), which
    # is the signature of the word COINKINS still being included. The
    # wordmark is a horizontally elongated band well below the mark, so
    # it is separated by ROW OCCUPANCY: find the empty row gap between
    # the two clusters and cut there. Measured on this reference the mark
    # occupies y~192..704 and the wordmark y~704..832.
    ys_all = np.nonzero(ring.any(axis=1))[0]
    rows = ring.sum(axis=1)
    # walk down from the disc centre until a sustained low-density run
    cut = H
    run = 0
    thresh = max(4, int(0.02 * rows.max()))
    for y in range(int(cy), H):
        if rows[y] <= thresh:
            run += 1
            if run >= 12:              # 12 consecutive near-empty rows
                cut = y - run + 1
                break
        else:
            run = 0
    print('  wordmark cut at y=%d (rows below this are excluded)' % cut)

    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring_mark = ring & (yy < cut)
    removed = int(ring.sum() - ring_mark.sum())
    print('  ring pixels kept=%d  excluded (wordmark etc.)=%d'
          % (ring_mark.sum(), removed))
    # sanity: the kept band must be roughly annular, i.e. its radius
    # spread should be narrow relative to its outer radius
    _rr = np.sqrt((np.nonzero(ring_mark)[1] - cx) ** 2
                  + (np.nonzero(ring_mark)[0] - cy) ** 2)
    spread = (np.percentile(_rr, 98) - np.percentile(_rr, 2)) \
        / np.percentile(_rr, 98)
    print('  radius spread after cut = %.4f of r_outer '
          '(a clean annulus is < 0.45)' % spread)
    if spread >= 0.45:
        print('  WARNING band is too wide to be a single annulus')

    rr = radial_stats(ring_mark, cx, cy)
    if rr is None or len(rr) < 100:
        print('  FAIL not enough ring pixels')
        return False

    r_in_px = float(np.percentile(rr, 2))
    r_out_px = float(np.percentile(rr, 98))
    print()
    print('  ring radius distribution over %d px:' % len(rr))
    for p in (0, 1, 2, 5, 50, 95, 98, 99, 100):
        print('      p%-3d = %7.2f px' % (p, np.percentile(rr, p)))

    # GAP DETECTION.
    # Sampling a single pixel at the mid-radius is fragile: the reference
    # is a soft-edged raster, so one stray pixel flips the answer. Instead
    # each angle is considered "filled" if ANY ring pixel lies within the
    # stroke band at that bearing - a robust radial probe.
    rmid = (r_in_px + r_out_px) / 2.0
    band_lo, band_hi = r_in_px * 0.98, r_out_px * 1.02
    filled = np.zeros(360, dtype=bool)
    mys, mxs = np.nonzero(ring_mark)
    mrr = np.sqrt((mxs - cx) ** 2 + (mys - cy) ** 2)
    inband = (mrr >= band_lo) & (mrr <= band_hi)
    ang_all = (np.degrees(np.arctan2(mys - cy, mxs - cx)) + 360.0) % 360.0
    for a in ang_all[inband].astype(int):
        filled[a % 360] = True
    empty = [a for a in range(360) if not filled[a]]
    print('  angular probe: %d of 360 bearings have ring ink' % filled.sum())

    gap_span, gap_centre = 0, None
    if empty and len(empty) < 360:
        s = set(empty)
        best_len, best_start = 0, None
        for st in sorted(s):
            if (st - 1) % 360 in s:
                continue          # not the start of a run
            ln = 0
            k = st
            while k % 360 in s and ln < 360:
                ln += 1
                k += 1
            if ln > best_len:
                best_len, best_start = ln, st
        if best_start is None:
            # every empty angle has an empty predecessor => one full run
            best_start, best_len = min(s), len(s)
        gap_span = best_len
        gap_centre = (best_start + best_len / 2.0) % 360

    print()
    print('=' * 84)
    print('REFERENCE GEOMETRY, NORMALISED (outer radius = 1)')
    print('=' * 84)
    print('  r_outer      = %8.2f px   -> 1.0000' % r_out_px)
    print('  r_inner      = %8.2f px   -> %.4f' % (r_in_px, r_in_px / r_out_px))
    print('  r_disc       = %8.2f px   -> %.4f' % (r_disc_px,
                                                   r_disc_px / r_out_px))
    print('  stroke width = %8.2f px   -> %.4f of r_outer'
          % (r_out_px - r_in_px, (r_out_px - r_in_px) / r_out_px))
    print('  fill ratio   = %.4f  (r_disc / r_inner)' % (r_disc_px / r_in_px))
    if gap_centre is not None:
        print('  gap span     = %3d deg      half-angle = %.1f deg'
              % (gap_span, gap_span / 2.0))
        print('  gap centre   = %.1f deg  (0 = +x axis, 90 = screen bottom)'
              % gap_centre)
        print('  white arc    = %3d deg' % (360 - gap_span))
    else:
        print('  gap          = NONE FOUND (closed ring?)')

    # ---- compare with ours ----
    import coinkins_mark as CM
    print()
    print('=' * 84)
    print('SIDE BY SIDE WITH OUR CURRENT MARK')
    print('=' * 84)
    ours = dict(r_in=CM.R_INNER_U / CM.R_OUTER_U,
                r_disc=CM.R_DISC_U / CM.R_OUTER_U,
                stroke=(CM.R_OUTER_U - CM.R_INNER_U) / CM.R_OUTER_U,
                fill=CM.R_DISC_U / CM.R_INNER_U,
                gap=2 * CM.GAP_HALF_DEG,
                arc=360 - 2 * CM.GAP_HALF_DEG)
    refd = dict(r_in=r_in_px / r_out_px,
                r_disc=r_disc_px / r_out_px,
                stroke=(r_out_px - r_in_px) / r_out_px,
                fill=r_disc_px / r_in_px,
                gap=float(gap_span),
                arc=360.0 - gap_span)
    print('  %-22s %10s %10s %10s' % ('metric', 'ours', 'reference', 'delta'))
    for k in ('r_in', 'r_disc', 'stroke', 'fill', 'gap', 'arc'):
        print('  %-22s %10.4f %10.4f %+10.4f'
              % (k, ours[k], refd[k], refd[k] - ours[k]))

    print()
    print('  INTERPRETATION')
    if refd['gap'] < ours['gap']:
        print('    The reference gap is NARROWER by %.1f deg, i.e. its white'
              % (ours['gap'] - refd['gap']))
        print('    arc is LONGER by the same amount. That is exactly what the')
        print('    user means by "longer white edges".')
    else:
        print('    The reference gap is WIDER by %.1f deg, so its white arc is'
              % (refd['gap'] - ours['gap']))
        print('    SHORTER, not longer. The request must then refer to')
        print('    something other than the gap angle - re-examine.')
    return dict(ref=refd, ours=ours, px=dict(r_out=r_out_px, r_in=r_in_px,
                                             r_disc=r_disc_px,
                                             gap=gap_span,
                                             gap_centre=gap_centre))


if __name__ == '__main__':
    main()
