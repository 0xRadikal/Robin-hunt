"""
show_final.py - render what the user will actually SEE.

Two sheets:
  1. X-PROFILE.png  - a faithful X/Twitter profile mock: banner with the
     avatar overlapped bottom-left exactly where X puts it, plus a
     timeline row at true 48px and a notification row at 32px.
  2. FINAL-SHEET.png - old vs new side by side at real sizes, on light
     and dark surfaces, in monochrome, and circle-cropped.

Geometry is READ from coinkins_mark (never copied), so this file can
never drift from the mark it claims to show.
"""

import os
from PIL import Image, ImageDraw, ImageFont

import coinkins_mark as CM

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, 'final')

BG = (18, 34, 68)
RING = (234, 241, 250)
DISC = (243, 182, 58)
MUTED = (150, 170, 196)

# X layout, measured in test_safezone.py: avatar zone x=[33,231] y=[401,500]
AV_X, AV_Y, AV_D = 33, 401, 198


def font(sz, bold=False):
    p = ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
         else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    try:
        return ImageFont.truetype(p, sz)
    except OSError:
        return ImageFont.load_default()


def circle(img):
    n = img.size[0]
    m = Image.new('L', (n * 4, n * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n * 4 - 1, n * 4 - 1], fill=255)
    m = m.resize((n, n), Image.LANCZOS)
    out = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    out.paste(img.convert('RGB'), (0, 0), m)
    return out


def variant(size, r_in, r_disc, gap, cap, bg=BG, ring=RING, disc=DISC):
    """Draw any parameter set through the SAME code path as production,
    by temporarily swapping the module constants. Restored in a finally
    block, and the caller asserts afterwards that nothing leaked."""
    keep = (CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, CM.CAP)
    try:
        CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, CM.CAP = \
            r_in, r_disc, gap, cap
        return CM.draw(size, bg, ring, disc)
    finally:
        CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, CM.CAP = keep


def old_mark(size, bg=BG, ring=RING, disc=DISC):
    """The ORIGINAL variant A: 4.00 / 2.75 / 34deg, flat ends."""
    return variant(size, 4.0, 2.75, 34.0, 0.0, bg, ring, disc)


def flat_mark(size, bg=BG, ring=RING, disc=DISC):
    """Current geometry but FLAT ends, to isolate the rounding alone."""
    return variant(size, CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, 0.0,
                   bg, ring, disc)


def x_profile(path='X-PROFILE.png'):
    banner = Image.open(os.path.join(FINAL, 'banner-1500x500.png')).convert('RGB')
    W = 1500
    H = 500 + 250 + 190
    sh = Image.new('RGB', (W, H), (255, 255, 255))
    sh.paste(banner, (0, 0))

    d = ImageDraw.Draw(sh)
    # profile card below the banner
    d.rectangle([0, 500, W, 750], fill=(255, 255, 255))

    av = Image.open(os.path.join(FINAL, 'avatar-400.png')).convert('RGB')
    av = av.resize((AV_D, AV_D), Image.LANCZOS)
    ring_w = 8
    plate = Image.new('RGB', (AV_D + ring_w * 2, AV_D + ring_w * 2),
                      (255, 255, 255))
    plate.paste(av, (ring_w, ring_w))
    plate = circle(plate)
    sh.paste(plate, (AV_X - ring_w, AV_Y - ring_w), plate)

    d.text((AV_X, 620), 'Coinkins', fill=(15, 20, 25), font=font(34, True))
    d.text((AV_X, 662), '@coinkins', fill=(83, 100, 113), font=font(24))
    d.text((AV_X, 700), 'Arc L1 - a coin that opens.',
           fill=(15, 20, 25), font=font(22))

    # timeline row: the avatar as X actually shows it, 48px
    y = 790
    d.text((40, y - 34), 'TIMELINE (real size, 48px avatar)',
           fill=(90, 90, 90), font=font(19, True))
    a48 = circle(CM.draw(48, BG, RING, DISC))
    sh.paste(a48, (40, y), a48)
    d.text((100, y + 2), 'Coinkins', fill=(15, 20, 25), font=font(21, True))
    d.text((198, y + 4), '@coinkins - 2m', fill=(83, 100, 113), font=font(18))
    d.text((100, y + 26), 'Every Coinkin is minted on Arc.',
           fill=(15, 20, 25), font=font(19))

    # notification row, 32px
    y = 880
    d.text((40, y - 26), 'NOTIFICATION (32px)', fill=(90, 90, 90),
           font=font(19, True))
    a32 = circle(CM.draw(32, BG, RING, DISC))
    sh.paste(a32, (40, y), a32)
    d.text((84, y + 6), 'Coinkins followed you', fill=(15, 20, 25),
           font=font(19))

    # favicon strip, 16px, on a browser-tab grey
    d.rectangle([700, 860, 1460, 920], fill=(222, 226, 230))
    a16 = Image.open(os.path.join(FINAL, 'favicon-16.png')).convert('RGB')
    sh.paste(a16, (720, 882))
    d.text((746, 880), 'coinkins.xyz  (16px favicon in a browser tab)',
           fill=(40, 45, 50), font=font(18))

    sh.save(path)
    print('wrote %s (%.1f KB)' % (path, os.path.getsize(path) / 1024))
    return path


def final_sheet(path='FINAL-SHEET.png'):
    sizes = [96, 48, 32, 24, 16]
    pad = 26
    big = 210
    colw = pad + big + pad + sum(s + 16 for s in sizes) + 40
    W = colw + 60
    H = pad * 2 + (big + 96) * 3 + 300
    sh = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sh)

    rows = [
        ('1  gap 46 deg  ->  white arc 268 deg',
         lambda s, **k: variant(s, 4.25, 3.0, 46.0, 1.0),
         'collision 0.5004'),
        ('2  gap 40 deg  ->  white arc 280 deg',
         lambda s, **k: variant(s, 4.25, 3.0, 40.0, 1.0),
         'collision 0.5041'),
        ('3  gap 28 deg  ->  white arc 304 deg   [FINAL - user choice]',
         lambda s, **k: CM.draw(s, BG, RING, DISC),
         'collision 0.4321   0 corners   16px gap chord 5.63px   '
         'ALL 39 CHECKS PASS'),
    ]
    for i, (lab, fn, note) in enumerate(rows):
        y = pad + i * (big + 96)
        d.text((pad, y - 18), lab, fill=(0, 0, 0), font=font(18, True))
        im = circle(fn(big))
        sh.paste(im, (pad, y), im)
        x = pad + big + pad
        for s in sizes:
            ims = circle(fn(s))
            sh.paste(ims, (x, y + (big - s) // 2), ims)
            d.text((x, y + (big + s) // 2 + 6), '%dpx' % s,
                   fill=(110, 110, 110), font=font(14))
            x += s + 16
        d.text((pad, y + big + 14), note, fill=(70, 70, 70), font=font(16))

    # bottom: robustness of the AFTER mark
    y = pad + (big + 96) * 3 + 30
    d.text((pad, y - 18), 'FINAL - other surfaces it must survive',
           fill=(0, 0, 0), font=font(18, True))
    cells = [
        ('on white', Image.open(os.path.join(FINAL, 'mark-onwhite-512.png'))),
        ('silhouette', Image.open(os.path.join(FINAL, 'mark-silhouette-512.png'))),
        ('mono light', Image.open(os.path.join(FINAL, 'mark-mono-light-512.png'))),
    ]
    x = pad
    for lab, im in cells:
        im = im.convert('RGB').resize((190, 190), Image.LANCZOS)
        sh.paste(im, (x, y))
        d.rectangle([x, y, x + 189, y + 189], outline=(210, 210, 210))
        d.text((x, y + 196), lab, fill=(70, 70, 70), font=font(15))
        x += 206

    sh.save(path)
    print('wrote %s (%.1f KB)' % (path, os.path.getsize(path) / 1024))
    return path


if __name__ == '__main__':
    EXPECT = (4.25, 3.0, 28.0, 1.0)
    got = (CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, CM.CAP)
    assert got == EXPECT, 'unexpected constants: %s' % (got,)
    x_profile()
    final_sheet()
    # prove the constant-swap helper restored state
    got = (CM.R_INNER_U, CM.R_DISC_U, CM.GAP_HALF_DEG, CM.CAP)
    assert got == EXPECT, 'variant() leaked temporary constants: %s' % (got,)
    print('constants intact after render: %s' % (got,))
