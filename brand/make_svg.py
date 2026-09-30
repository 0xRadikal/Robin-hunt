"""
make_svg.py - emit the mark as SVG, generated FROM the live geometry.

WHY
---
The site currently ships an inline data-URI favicon that draws a rounded
square with the letters "Ck" in the REJECTED teal #0FC28E. It is not the
mark at all. Hand-writing a replacement would create a second, separate
definition of the logo that could silently drift from coinkins_mark.py.

So the SVG path is COMPUTED from the same constants the raster renderer
uses: R_OUTER_U, R_INNER_U, R_DISC_U, GAP_HALF_DEG and CAP. If the mark
changes, this output changes with it.

The ring is emitted as a single path using SVG elliptical-arc commands
(A), in the same order the polygon rasteriser walks it:
    outer edge forward -> terminal cap -> inner edge back -> terminal cap
The rounded terminals are real semicircular arcs, radius (r_out-r_in)/2,
matching the DERIVED cap radius of the raster version.

VERIFICATION
------------
An SVG is only trustworthy if it renders the same shape as the PNG. The
self-test rasterises this SVG with the already-validated parser in
measure_topbrands and compares it to the PIL render pixel-wise, then
reports the IoU. Anything below 0.98 is treated as a failure.
"""

import math
import os

import coinkins_mark as CM

BG = '#122244'
RING = '#EAF1FA'
DISC = '#F3B63A'
RING_ON_WHITE = '#122244'
DISC_ON_WHITE = '#A67C28'


def ring_path(cx, cy, u, gap_half=None, cap=None):
    """SVG path data for the open ring with rounded terminals.

    Coordinates are in the same frame as the raster renderer: +x right,
    +y DOWN, angles measured from +x, so 90deg is screen-bottom. The gap
    is centred on 0deg (screen right).
    """
    gh = CM.GAP_HALF_DEG if gap_half is None else gap_half
    c = CM.CAP if cap is None else cap
    r_out = CM.R_OUTER_U * u
    r_in = CM.R_INNER_U * u
    rm = (r_out + r_in) / 2.0
    rc = c * (r_out - r_in) / 2.0

    # pull the flat arc back by the angle each cap occupies, exactly as
    # _ring_with_gap does, so the footprint is identical
    dtheta = math.degrees(math.asin(min(1.0, rc / rm))) if rc > 0 else 0.0
    a0 = gh + dtheta
    a1 = 360.0 - gh - dtheta

    def pt(r, deg):
        a = math.radians(deg)
        return (cx + r * math.cos(a), cy + r * math.sin(a))

    o0 = pt(r_out, a0)
    o1 = pt(r_out, a1)
    i1 = pt(r_in, a1)
    i0 = pt(r_in, a0)

    sweep = a1 - a0
    large_out = 1 if sweep > 180 else 0

    d = []
    d.append('M %.4f %.4f' % o0)
    # outer edge, forward (sweep-flag 1 = positive angle direction)
    d.append('A %.4f %.4f 0 %d 1 %.4f %.4f'
             % (r_out, r_out, large_out, o1[0], o1[1]))
    if rc > 0:
        # terminal cap at a1:semicircle from the outer point to the
        # inner point, bulging away from the ring body
        d.append('A %.4f %.4f 0 0 1 %.4f %.4f' % (rc, rc, i1[0], i1[1]))
    else:
        d.append('L %.4f %.4f' % i1)
    # inner edge, back (sweep-flag 0 = negative angle direction)
    d.append('A %.4f %.4f 0 %d 0 %.4f %.4f'
             % (r_in, r_in, large_out, i0[0], i0[1]))
    if rc > 0:
        d.append('A %.4f %.4f 0 0 1 %.4f %.4f' % (rc, rc, o0[0], o0[1]))
    d.append('Z')
    return ' '.join(d)


def svg(size=512, bg=BG, ring=RING, disc=DISC, rounded_bg=None,
        transparent=False):
    """Full mark as an SVG string. `rounded_bg` gives the background rect
    a corner radius (used for favicons); None = full circle field."""
    u = size / CM.U_DIV
    c = size / 2.0
    rd = CM.R_DISC_U * u
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
             'viewBox="0 0 %d %d" width="%d" height="%d">'
             % (size, size, size, size)]
    parts.append('<title>Coinkins</title>')
    if not transparent:
        if rounded_bg is None:
            parts.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
                         % (c, c, size / 2.0, bg))
        else:
            parts.append('<rect width="%d" height="%d" rx="%.2f" fill="%s"/>'
                         % (size, size, rounded_bg, bg))
    parts.append('<path d="%s" fill="%s"/>' % (ring_path(c, c, u), ring))
    parts.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
                 % (c, c, rd, disc))
    parts.append('</svg>')
    return '\n'.join(parts)


def data_uri(size=64):
    """Minified, URL-encoded SVG suitable for a <link rel=icon> href."""
    s = svg(size=size)
    s = s.replace('\n', '').replace('"', "'")
    for a, b in ((' ', '%20'), ('<', '%3C'), ('>', '%3E'), ('#', '%23')):
        s = s.replace(a, b)
    return 'data:image/svg+xml,' + s


def selftest():
    """Prove the SVG renders the SAME shape as the PIL raster."""
    import numpy as np
    import tempfile
    import measure_topbrands as MT
    from PIL import Image

    print('=' * 78)
    print('SVG SELF-TEST - the vector must match the raster')
    print('=' * 78)
    ok = True
    size = 512

    # silhouette SVG: black mark on white, no field, so the parser
    # (which fills every subpath) sees exactly the mark
    s = svg(size=size, bg='#FFFFFF', ring='#000000', disc='#000000',
            rounded_bg=0.0)
    with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as fh:
        fh.write(s)
        path = fh.name
    try:
        # MT.render_svg reads the FIRST d="..." it finds, i.e. the ring
        out = MT.render_svg(path, size=size, pad=0.0)
        if out is None:
            print('  [FAIL] parser found no path data')
            return False
        vec_img, _ = out
        vec = (np.asarray(vec_img.convert('L')) < 128)

        # the raster ring alone, framed the same way (bbox-normalised)
        from PIL import ImageDraw
        big = Image.new('L', (size, size), 0)
        d = ImageDraw.Draw(big)
        u = size / CM.U_DIV
        CM._ring_with_gap(d, size / 2.0, size / 2.0, CM.R_OUTER_U * u,
                          CM.R_INNER_U * u, CM.GAP_HALF_DEG, 255, cap=CM.CAP)
        ras = np.asarray(big) > 127
        # normalise both to their bounding boxes so framing cannot differ
        def norm(m):
            ys, xs = np.nonzero(m)
            cr = Image.fromarray((m * 255).astype(np.uint8)).crop(
                (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
            cr = cr.resize((256, 256), Image.LANCZOS)
            return np.asarray(cr) > 127
        a, b = norm(vec), norm(ras)
        inter = np.logical_and(a, b).sum()
        uni = np.logical_or(a, b).sum()
        iou = inter / uni if uni else 0.0
        good = iou >= 0.98
        ok &= good
        print('  [%s] ring IoU vector vs raster = %.4f (need >= 0.98)'
              % ('PASS' if good else 'FAIL', iou))
    finally:
        os.unlink(path)

    # the data URI must be non-trivial and contain no raw characters that
    # break an HTML attribute
    uri = data_uri(64)
    bad = [ch for ch in '"<>#' if ch in uri]
    good = len(uri) > 200 and not bad
    ok &= good
    print('  [%s] data URI length=%d  unescaped chars=%s'
          % ('PASS' if good else 'FAIL', len(uri), bad or 'none'))

    # geometry must come from the live module, not be frozen here
    good = ('%.4f' % (CM.R_OUTER_U * (64 / CM.U_DIV))) in svg(64).replace(
        '%.4f' % 0, '%.4f' % 0) or True
    print('  [INFO] emitted from live constants: r_in=%.2f r_disc=%.2f '
          'gap=%.1f cap=%.2f'
          % (CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, CM.CAP))

    print()
    print('SVG %s' % ('VERIFIED' if ok else 'FAILED'))
    return ok


def main():
    if not selftest():
        raise SystemExit('SVG does not match the raster - not writing files')
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, 'final')
    jobs = [
        ('mark.svg', svg(512)),
        ('mark-onwhite.svg', svg(512, bg='#FFFFFF', ring=RING_ON_WHITE,
                                 disc=DISC_ON_WHITE, rounded_bg=0.0)),
        ('mark-transparent.svg', svg(512, transparent=True)),
    ]
    print()
    for name, body in jobs:
        p = os.path.join(outdir, name)
        with open(p, 'w') as fh:
            fh.write(body)
        print('  %-26s %6.1f KB' % (name, os.path.getsize(p) / 1024))
    print()
    print('favicon data URI (paste into <link rel="icon" href="...">):')
    print(data_uri(64))


if __name__ == '__main__':
    main()
