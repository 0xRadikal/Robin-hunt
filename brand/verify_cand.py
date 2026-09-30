"""
verify_cand.py - verify the searched refinement of variant A before adopting it.

Candidate from search_a2.py floor sweep:
    r_out = 6.00U (unchanged - defines the approved size)
    r_in  = 4.25U (was 4.00)
    r_disc= 3.00U (was 2.75)
    gap_half = 46.0 deg (was 34.0)

Checks the construction AND renders a side-by-side against the baseline and
every collision reference, so the change can be judged visually as well as
numerically.
"""

import math
import numpy as np
from PIL import Image, ImageDraw

import collide as CO
import coinkins_mark as CM

U = 16.0
R_OUT = 6.0

BASE = dict(r_in=4.00, r_disc=2.75, gap=34.0)
CAND = dict(r_in=4.25, r_disc=3.00, gap=46.0)

BG = (18, 34, 68)
RING = (234, 241, 250)
DISC = (243, 182, 58)


def geometry_checks(p, label):
    print('-' * 78)
    print('GEOMETRY: %s  r_out=%.2f r_in=%.2f r_disc=%.2f gap_half=%.1f'
          % (label, R_OUT, p['r_in'], p['r_disc'], p['gap']))
    print('-' * 78)
    ok = True

    def chk(n, c, d=''):
        nonlocal ok
        print('  [%s] %-50s %s' % ('PASS' if c else 'FAIL', n, d))
        if not c:
            ok = False

    radii = sorted({R_OUT, p['r_in'], p['r_disc']})
    chk('G1 exactly 3 distinct radii', len(radii) == 3, str(radii))
    chk('G2 all radii quarter-unit multiples',
        all(abs(r * 4 - round(r * 4)) < 1e-9 for r in radii),
        ' '.join('%.2f' % r for r in radii))
    chk('G3 radii strictly ordered',
        p['r_disc'] < p['r_in'] < R_OUT,
        '%.2f < %.2f < %.2f' % (p['r_disc'], p['r_in'], R_OUT))
    stroke = (R_OUT - p['r_in']) / U
    chk('G4 stroke within real top-brand range [0.0365,0.2083]',
        0.0365 <= stroke <= 0.2083, 'stroke=%.4f of width' % stroke)
    clear = p['r_in'] - p['r_disc']
    chk('G5 disc clears ring by >= 0.25U (no adjacent gold/light edge)',
        clear >= 0.25 - 1e-9, 'clearance=%.2fU' % clear)
    ann = math.pi * (R_OUT ** 2 - p['r_in'] ** 2) * (1 - p['gap'] / 180.0)
    disc = math.pi * p['r_disc'] ** 2
    ink = (ann + disc) / (U * U)
    chk('G6 ink fraction within measured range [0.070,0.497]',
        0.070 <= ink <= 0.497, 'ink=%.4f (median 0.2976)' % ink)
    chord16 = 2.0 * R_OUT * math.sin(math.radians(p['gap']))
    chk('G7 gap chord >= 1.5px at 16px render', chord16 >= 1.5,
        'chord=%.2fpx' % chord16)
    chk('G8 gap_half <= 60deg (still reads as a ring)', p['gap'] <= 60.0,
        '%.1f deg (total opening %.1f deg)' % (p['gap'], 2 * p['gap']))

    # rendered vs analytic ink - proves the rasteriser agrees with the maths
    m = CO.ring_disc_mask(1.0, p['r_in'] / R_OUT, p['r_disc'] / R_OUT,
                          p['gap'], 0.0, res=512)
    # mask is framed at span=1.15 => box side = 2*1.15 r_out
    rend = m.sum() / float(512 * 512) * (2 * 1.15) ** 2 * (R_OUT ** 2) / (U * U)
    chk('G9 rendered ink matches analytic within 0.005',
        abs(rend - ink) < 0.005, 'rendered=%.4f analytic=%.4f' % (rend, ink))

    # measured gap span from the raster
    n = 512
    cx = cy = n / 2.0
    rr = (n / 2.0 / 1.15) * ((R_OUT + p['r_in']) / 2.0 / R_OUT)
    inks = []
    for deg in range(0, 360):
        th = math.radians(deg)
        x = int(round(cx + rr * math.cos(th)))
        y = int(round(cy + rr * math.sin(th)))
        inks.append(m[y, x] if (0 <= x < n and 0 <= y < n) else 0)
    empty = sum(1 for v in inks if not v)
    chk('G10 measured gap span matches spec +-3deg',
        abs(empty - 2 * p['gap']) <= 3,
        'measured=%d deg specified=%.0f deg' % (empty, 2 * p['gap']))

    # symmetry about the horizontal axis (gap centred on +x)
    top = m[:n // 2, :].sum()
    bot = m[n // 2:, :].sum()
    chk('G11 mirror-symmetric about horizontal axis',
        abs(top - bot) <= max(4, 0.002 * m.sum()),
        'top=%d bottom=%d diff=%d' % (top, bot, abs(top - bot)))

    print('  => %s' % ('ALL GEOMETRY CHECKS PASS' if ok else 'GEOMETRY FAILURES'))
    return ok, dict(ink=ink, stroke=stroke, clear=clear, chord=chord16)


def draw_mark(size, p, bg=BG, ring=RING, disc=DISC):
    """Render using coinkins_mark's own primitive so the visual matches
    what build_final.py will actually produce."""
    SSx = 8
    W = size * SSx
    img = Image.new('RGB', (W, W), bg)
    d = ImageDraw.Draw(img)
    u = W / U
    cx = cy = W / 2.0
    CM._ring_with_gap(d, cx, cy, p['r_in'] and R_OUT * u, p['r_in'] * u,
                      p['gap'], ring)
    rd = p['r_disc'] * u
    d.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], fill=disc)
    return img.resize((size, size), Image.LANCZOS)


def circle_crop(img):
    n = img.size[0]
    mask = Image.new('L', (n * 4, n * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, n * 4 - 1, n * 4 - 1], fill=255)
    mask = mask.resize((n, n), Image.LANCZOS)
    out = Image.new('RGB', (n, n), (255, 255, 255))
    out.paste(img, (0, 0), mask)
    return out


def sheet(path='CAND-COMPARE.png'):
    """Baseline vs candidate, at real sizes, plus the collision references."""
    pad = 24
    big = 260
    sizes = [96, 48, 32, 24, 16]
    rowh = big + 90
    W = pad * 2 + big + pad + sum(s + 18 for s in sizes) + 120
    H = pad * 2 + rowh * 2 + 300
    sh = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sh)

    for row, (lab, p) in enumerate([('BASELINE  (as approved)', BASE),
                                    ('CANDIDATE (refined)', CAND)]):
        y = pad + row * rowh
        d.text((pad, y - 14), lab, fill=(0, 0, 0))
        d.text((pad, y + big + 8),
               'r_in=%.2f r_disc=%.2f gap=%.0f deg  fill=%.3f'
               % (p['r_in'], p['r_disc'], p['gap'], p['r_disc'] / p['r_in']),
               fill=(60, 60, 60))
        sh.paste(circle_crop(draw_mark(big, p)), (pad, y))
        x = pad + big + pad
        for s in sizes:
            im = circle_crop(draw_mark(s, p))
            sh.paste(im, (x, y + (big - s) // 2))
            d.text((x, y + (big + s) // 2 + 6), '%dpx' % s, fill=(90, 90, 90))
            x += s + 18

    # collision references
    y = pad + rowh * 2 + 20
    d.text((pad, y - 14), 'COLLISION REFERENCES (measured against)',
           fill=(0, 0, 0))
    refs = CO.references(res=200)
    x = pad
    for name, M, _ in refs:
        im = Image.fromarray(((1 - M) * 255).astype(np.uint8)).convert('RGB')
        sh.paste(im, (x, y))
        d.text((x, y + 206), name, fill=(60, 60, 60))
        x += 216
    sh.save(path)
    print('wrote %s (%.1f KB)' % (path, __import__('os').path.getsize(path) / 1024))
    return path


def main():
    okb, mb = geometry_checks(BASE, 'BASELINE')
    print()
    okc, mc = geometry_checks(CAND, 'CANDIDATE')
    print()
    print('=' * 78)
    print('COLLISION DISTANCES (higher = less resemblance)')
    print('=' * 78)
    print('BASELINE:')
    rb = CO.measure(r_in=BASE['r_in'], r_disc=BASE['r_disc'],
                    gap_half=BASE['gap'])
    print('CANDIDATE:')
    rc = CO.measure(r_in=CAND['r_in'], r_disc=CAND['r_disc'],
                    gap_half=CAND['gap'])
    print()
    print('  %-22s %10s %10s %9s' % ('reference', 'base D1', 'cand D1', 'change'))
    for a, b in zip(rb, rc):
        if a['ref'].startswith('R5'):
            continue
        ch = b['D1_bestrot'] - a['D1_bestrot']
        print('  %-22s %10.4f %10.4f %+9.4f' %
              (a['ref'], a['D1_bestrot'], b['D1_bestrot'], ch))
    wb = min(r['D1_bestrot'] for r in rb if not r['ref'].startswith('R5'))
    wc = min(r['D1_bestrot'] for r in rc if not r['ref'].startswith('R5'))
    print('  %-22s %10.4f %10.4f %+9.4f  (%+.1f%%)'
          % ('WORST CASE', wb, wc, wc - wb, 100 * (wc - wb) / wb))
    print()
    sheet()
    return okb and okc


if __name__ == '__main__':
    if not main():
        raise SystemExit('candidate failed geometry checks')
