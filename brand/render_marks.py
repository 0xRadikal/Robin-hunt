#!/usr/bin/env python3
"""render_marks.py - Show every gated mark the way it will actually be
seen: as a circle avatar, at real sizes, and as a silhouette.

Numbers alone cannot settle a logo. But a picture alone cannot either -
that is how I produced the rejected output. Both together is the point.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import marks as MK  # noqa: E402
import test_marks as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# Colour schemes that pass the harmony/contrast work already done.
# The FORM is the question here, so every form is shown in the same
# scheme, and then the winning form is shown in every scheme.
SCHEMES = {
    # name            background        ink (light)        accent
    'navy':   ((16, 42, 74),   (238, 245, 252), (245, 186, 63)),
    'ink':    ((11, 16, 32),   (240, 246, 252), (245, 186, 63)),
    'teal':   ((7, 51, 47),    (232, 248, 243), (245, 200, 92)),
    'arcblue': ((13, 71, 112), (236, 246, 255), (250, 204, 90)),
}


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


def sheet_forms():
    """All 6 forms in one scheme, big + silhouette + 48px + 16px."""
    bg, ink, acc = SCHEMES['navy']
    names = list(MK.MARKS)
    cell, pad, top = 176, 20, 96
    rowh = cell + 150
    W = pad + len(names) * (cell + pad)
    H = top + rowh + pad
    im = Image.new('RGB', (W, H), (250, 250, 250))
    d = ImageDraw.Draw(im)
    d.text((pad, 20), 'COINKINS — CANDIDATE LOGO FORMS (no text inside '
                      'the mark, flat, 3 colours)', font=font(20),
           fill=(18, 18, 18))
    d.text((pad, 48), 'row 1: 176px circle avatar   row 2: pure black '
                      'silhouette   row 3: 48px timeline   row 4: 16px '
                      'favicon', font=font(14, False), fill=(95, 95, 95))

    for i, n in enumerate(names):
        fn = MK.MARKS[n]
        x = pad + i * (cell + pad)
        im.paste(circle(fn(cell, bg, ink, acc)), (x, top))
        sil = MK.silhouette(fn, 64)
        im.paste(sil, (x, top + cell + 8))
        im.paste(circle(fn(48, bg, ink, acc)), (x + 72, top + cell + 8))
        im.paste(circle(fn(16, bg, ink, acc)), (x + 128, top + cell + 8))
        d.text((x, top + cell + 80), n, font=font(14), fill=(18, 18, 18))
        big = fn(400, bg, ink, acc)
        crs, mn = T.boundary_contrasts(big)
        d.text((x, top + cell + 100),
               f"min contrast {mn:.2f}:1", font=font(12, False),
               fill=(16, 110, 40))
        d.text((x, top + cell + 116),
               f"edges {T.edge_density(big):.3f}", font=font(12, False),
               fill=(110, 110, 110))
    p = os.path.join(HERE, 'MARKS-FORMS.png')
    im.save(p, 'PNG', optimize=True)
    return p


def sheet_schemes():
    """Every form crossed with every colour scheme."""
    names = list(MK.MARKS)
    cell, pad, top = 116, 14, 74
    W = pad + 130 + len(names) * (cell + pad)
    H = top + len(SCHEMES) * (cell + pad + 20) + pad
    im = Image.new('RGB', (W, H), (250, 250, 250))
    d = ImageDraw.Draw(im)
    d.text((pad, 18), 'FORM x COLOUR SCHEME — every cell passes all 8 '
                      'gates', font=font(18), fill=(18, 18, 18))
    d.text((pad, 44), 'colour is a constraint here, not the objective — '
                      'the FORM is what carries identity',
           font=font(13, False), fill=(95, 95, 95))
    for r, (sname, (bg, ink, acc)) in enumerate(SCHEMES.items()):
        y = top + r * (cell + pad + 20)
        d.text((pad, y + cell // 2 - 8), sname, font=font(15),
               fill=(18, 18, 18))
        d.rectangle([pad, y + cell // 2 + 14, pad + 40,
                     y + cell // 2 + 30], fill=bg)
        for c, n in enumerate(names):
            x = pad + 130 + c * (cell + pad)
            im.paste(circle(MK.MARKS[n](cell, bg, ink, acc)), (x, y))
            if r == 0:
                d.text((x, y - 20), n, font=font(13), fill=(18, 18, 18))
    p = os.path.join(HERE, 'MARKS-SCHEMES.png')
    im.save(p, 'PNG', optimize=True)
    return p


def sheet_timeline():
    """Against the real measured peers at timeline size."""
    bg, ink, acc = SCHEMES['navy']
    peers_dir = os.path.join(HERE, 'competitors')
    peers = sorted(os.listdir(peers_dir))[:6] \
        if os.path.isdir(peers_dir) else []
    names = list(MK.MARKS)
    S = 48
    W = 30 + (len(names) + len(peers)) * (S + 22)
    im = Image.new('RGB', (W, 136), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((14, 10), 'AT 48px NEXT TO REAL MEASURED PEERS — does ours '
                     'hold its own?', font=font(14), fill=(18, 18, 18))
    x = 14
    for n in names:
        im.paste(circle(MK.MARKS[n](S, bg, ink, acc)), (x, 44))
        d.text((x, 98), n.split()[0], font=font(11, False),
               fill=(40, 40, 40))
        x += S + 22
    d.line([x - 11, 40, x - 11, 110], fill=(200, 200, 200), width=2)
    for pf in peers:
        try:
            p = Image.open(os.path.join(peers_dir, pf)).convert('RGB')
            im.paste(circle(p.resize((S, S), Image.LANCZOS)), (x, 44))
            d.text((x, 98), pf[:7], font=font(10, False),
                   fill=(130, 130, 130))
            x += S + 22
        except Exception:
            pass
    p = os.path.join(HERE, 'MARKS-TIMELINE.png')
    im.save(p, 'PNG', optimize=True)
    return p


if __name__ == '__main__':
    for f in (sheet_forms(), sheet_schemes(), sheet_timeline()):
        print(f"  wrote {os.path.basename(f)} "
              f"({os.path.getsize(f)/1024:.1f} KB)")
