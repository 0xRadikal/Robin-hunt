#!/usr/bin/env python3
"""render_vs_topbrands.py - Put our candidate marks directly beside the
real top-brand marks, at the sizes that matter.

WHY THIS REPLACES THE NFT COMPARISON
  The old strip compared our marks to 10 NFT avatars. The user
  instructed to stop doing that - NFT avatars are dated illustrations,
  not brand-mark craft. This compares against the marks of Apple,
  Google, Samsung, Cisco (Interbrand Best Global Brands 2025),
  Mastercard, Visa, PayPal, Stripe (our payments category), and Nike,
  Spotify, X (the symbol-only brands Michael Bierut named as the
  reference class).

WHAT IS SHOWN
  1. MARKS-VS-TOPBRANDS.png - our 6 forms and the 11 real marks, all as
     pure black silhouettes at equal visual size. Silhouette is the
     honest comparison: it removes colour entirely, which is how Apple's
     mark has worked since 1977 and how Nike's has always worked.
  2. MARKS-SIZES.png - our forms at 400 / 96 / 48 / 32 / 24 / 16 px.
     Grasser's stated goal for the Twitter bird was that it be "legible
     at very small sizes, almost like a lowercase e". 16px is the
     favicon; 48px is the X timeline.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import marks as MK  # noqa: E402
import measure_topbrands as MT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'topbrands')

SCHEME = ((16, 42, 74), (238, 245, 252), (245, 186, 63))


def font(size, bold=True):
    p = ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
         else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(p, size) if os.path.exists(p) \
        else ImageFont.load_default()


def circle(img):
    out = Image.new('RGB', img.size, (255, 255, 255))
    m = Image.new('L', (img.size[0] * 4, img.size[1] * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, m.size[0] - 1, m.size[1] - 1],
                              fill=255)
    out.paste(img, (0, 0), m.resize(img.size, Image.LANCZOS))
    return out


def sheet_vs():
    """Silhouette comparison: ours vs the real thing, colour removed."""
    ours = list(MK.MARKS)
    brands = sorted(f[:-4] for f in os.listdir(SRC) if f.endswith('.svg'))
    cell, pad = 96, 16
    cols = max(len(ours), len(brands))
    W = pad + cols * (cell + pad)
    H = 150 + 2 * (cell + 46)
    im = Image.new('RGB', (W, H), (252, 252, 252))
    d = ImageDraw.Draw(im)
    d.text((pad, 18), 'SILHOUETTE COMPARISON - colour removed, equal '
                      'visual size', font=font(19), fill=(16, 16, 16))
    d.text((pad, 44), 'Apple has worked as a pure silhouette since 1977; '
                      'Nike always has. If a mark fails here, colour '
                      'cannot save it.',
           font=font(13, False), fill=(95, 95, 95))

    y = 88
    d.text((pad, y), 'OURS', font=font(15), fill=(16, 90, 170))
    y += 22
    for i, n in enumerate(ours):
        x = pad + i * (cell + pad)
        im.paste(MK.silhouette(MK.MARKS[n], cell), (x, y))
        d.text((x, y + cell + 6), n, font=font(12), fill=(40, 40, 40))

    y += cell + 46
    d.text((pad, y), 'REAL TOP-BRAND MARKS', font=font(15),
           fill=(150, 30, 30))
    y += 22
    for i, b in enumerate(brands):
        x = pad + i * (cell + pad)
        out = MT.render_svg(os.path.join(SRC, b + '.svg'), cell)
        if out:
            im.paste(out[0], (x, y))
        d.text((x, y + cell + 6), b, font=font(12), fill=(40, 40, 40))

    p = os.path.join(HERE, 'MARKS-VS-TOPBRANDS.png')
    im.save(p, 'PNG', optimize=True)
    return p


def sheet_sizes():
    """Our forms down to the favicon."""
    bg, ink, acc = SCHEME
    sizes = [400, 96, 48, 32, 24, 16]
    ours = list(MK.MARKS)
    lab = 130
    W = lab + sum(s + 26 for s in sizes)
    rowh = 420 + 30
    H = 96 + len(ours) * 0 + rowh
    # one row per mark is too tall; instead columns = sizes, rows = marks
    rowh = 108
    H = 104 + len(ours) * rowh
    im = Image.new('RGB', (W, H), (252, 252, 252))
    d = ImageDraw.Draw(im)
    d.text((16, 18), 'EVERY CANDIDATE AT EVERY REAL SIZE', font=font(19),
           fill=(16, 16, 16))
    d.text((16, 44), 'Grasser designed the Twitter bird to be "legible at '
                     'very small sizes, almost like a lowercase e". '
                     '16px = favicon, 48px = X timeline.',
           font=font(13, False), fill=(95, 95, 95))
    x = lab
    for s in sizes:
        d.text((x, 78), f'{s}px', font=font(13), fill=(60, 60, 60))
        x += min(s, 96) + 26
    for r, n in enumerate(ours):
        y = 104 + r * rowh
        d.text((16, y + 34), n, font=font(14), fill=(20, 20, 20))
        x = lab
        for s in sizes:
            img = circle(MK.MARKS[n](s, bg, ink, acc))
            if s > 96:
                img = img.resize((96, 96), Image.LANCZOS)
            im.paste(img, (x, y + (96 - img.size[1]) // 2))
            x += min(s, 96) + 26
    p = os.path.join(HERE, 'MARKS-SIZES.png')
    im.save(p, 'PNG', optimize=True)
    return p


if __name__ == '__main__':
    for f in (sheet_vs(), sheet_sizes()):
        print(f"  wrote {os.path.basename(f)} "
              f"({os.path.getsize(f)/1024:.1f} KB)")
