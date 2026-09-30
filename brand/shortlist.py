#!/usr/bin/env python3
"""shortlist.py - Turn the solver output into a small set of REAL brand
options, score them all identically, and render them so they can be
judged by eye as well as by number.

WHY A SHORTLIST RATHER THAN "THE WINNER"
  The top raw CH scores are olive/khaki fields (#8A8A55, #9E9262). They
  are genuinely the most harmonious under the empirical model, but the
  colour-PSYCHOLOGY evidence we gathered argues against olive for a
  money product:
    - Ou 2008 (DRS): "Among various hues, blue is the one most likely to
      create harmony in a two-colour combination; red is the least
      likely to do so."
    - Journal of Business Research: blue raises perceived trustworthiness
      by 42% in professional services.
    - 95% of financial-services brands use blue -> blue is the trusted
      category signal, and deviating too far costs credibility.
  Olive scores high on harmony and low on category fit. That is a real
  trade-off, not something I should silently resolve on the user's
  behalf. So I present the options with BOTH numbers visible.

  The user decides. I only guarantee that every option here passes all
  8 hard gates and that the numbers are measured, not claimed.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harmony    # noqa: E402
import ouluo      # noqa: E402
import solve_final as SF  # noqa: E402
from palette import PALETTE, contrast, hsv  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
INK = PALETTE['ink']['rgb']
GOLD = PALETTE['gold']['rgb']
TEAL = PALETTE['teal']['rgb']

# Candidates drawn from the solver's accepted sets, chosen to span the
# harmony/category-fit trade-off. Every one was produced BY the search,
# none invented here.
CANDIDATES = [
    # label                      field            coin
    ('v2 REJECTED (baseline)',   TEAL,            GOLD),
    ('A1 deep gold field',       (138, 111, 3),   GOLD),
    ('A2 teal-cyan + gold',      (18, 128, 128),  GOLD),
    ('A3 arc blue + gold',       (37, 122, 168),  GOLD),
    ('B1 olive + pale gold',     (138, 138, 85),  (250, 246, 190)),
    ('B2 bronze + light gold',   (158, 114, 47),  (250, 225, 155)),
    ('B3 azure + cream gold',    (12, 143, 199),  (250, 234, 190)),
    ('C1 steel blue + silver',   (54, 141, 178),  (230, 246, 255)),
    ('C2 deep navy + silver',    (30, 95, 138),   (230, 242, 255)),
    ('C3 deep teal + silver',    (26, 117, 117),  (230, 246, 255)),
]


def hexs(rgb):
    return '#%02X%02X%02X' % rgb


def font(size, bold=True):
    p = ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
         else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(p, size) if os.path.exists(p) \
        else ImageFont.load_default()


def centered(d, cx, cy, text, f, fill):
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=f,
           fill=fill)


def draw_avatar(size, field, coin):
    ss = 4
    W = size * ss
    img = Image.new('RGB', (W, W), field)
    d = ImageDraw.Draw(img)
    r = int(W * 0.315)
    cx = cy = W // 2
    rim = (int(coin[0] * 0.72), int(coin[1] * 0.68), int(coin[2] * 0.42))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rim)
    ir = int(r * 0.86)
    d.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=coin)
    centered(d, cx, cy - int(W * 0.004), 'Ck', font(int(W * 0.255)), INK)
    return img.resize((size, size), Image.LANCZOS)


def circle_mask(img):
    """Render as X actually shows it: a circle."""
    out = Image.new('RGB', img.size, (255, 255, 255))
    mask = Image.new('L', (img.size[0] * 4, img.size[1] * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, mask.size[0] - 1, mask.size[1] - 1],
                                 fill=255)
    out.paste(img, (0, 0), mask.resize(img.size, Image.LANCZOS))
    return out


def main():
    print("=" * 100)
    print("SHORTLIST - every option passes all 8 gates unless marked")
    print("=" * 100)
    print(f"  {'option':26s} {'field':8s} {'coin':8s} {'CH':>8s} "
          f"{'gap':>6s} {'dL*':>5s} {'cr':>6s} {'ink':>6s} "
          f"{'bright':>7s} {'sat':>5s}  verdict")
    print("  " + "-" * 96)

    rows = []
    for label, field, coin in CANDIDATES:
        ok, sc, rep = SF.evaluate8(field, coin)
        br = SF.avatar_brightness(field, coin)
        _, s, _ = hsv(field)
        verdict = 'PASS' if ok else 'FAIL: ' + '; '.join(
            f.split(' ', 1)[0] for f in rep['fails'])
        print(f"  {label:26s} {hexs(field):8s} {hexs(coin):8s} {sc:+8.4f} "
              f"{rep['gap']:5.0f}d {rep['dL']:5.0f} "
              f"{rep['cr_coin']:5.2f}:1 {rep['cr_ink']:5.2f}:1 "
              f"{br:7.3f} {s:5.2f}  {verdict}")
        rows.append((label, field, coin, sc, rep, br, ok))

    print()
    print("  gate reference: cr>=3.00 (WCAG 1.4.11)  ink>=4.50 (WCAG 1.4.3)")
    print("  gap must avoid 40-85deg and 135-150deg (Moon-Spencer ambiguous)")
    print("  peer median brightness 0.692; peer strongest marks are "
          "flat+saturated")

    # ---------------- render the comparison sheet -------------------
    cell, pad, top = 190, 22, 92
    cols = 5
    n = len(rows)
    rws = (n + cols - 1) // cols
    W = cols * (cell + pad) + pad
    H = top + rws * (cell + pad + 74) + pad
    sheet = Image.new('RGB', (W, H), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 22), 'COINKINS v3 CANDIDATES - rendered as X shows them '
                      '(circle), with measured harmony',
           font=font(21), fill=(20, 20, 20))
    d.text((pad, 54), 'CH = Ou & Luo (2006) empirical colour-harmony '
                      'score, higher is better. cr = WCAG contrast.',
           font=font(15, False), fill=(90, 90, 90))

    for i, (label, field, coin, sc, rep, br, ok) in enumerate(rows):
        cx0 = pad + (i % cols) * (cell + pad)
        cy0 = top + (i // cols) * (cell + pad + 74)
        av = circle_mask(draw_avatar(cell, field, coin))
        sheet.paste(av, (cx0, cy0))
        col = (16, 120, 40) if ok else (185, 30, 30)
        d.text((cx0, cy0 + cell + 5), label, font=font(13), fill=(20, 20, 20))
        d.text((cx0, cy0 + cell + 23), f"CH {sc:+.3f}   cr {rep['cr_coin']:.2f}:1",
               font=font(13, False), fill=col)
        d.text((cx0, cy0 + cell + 40), f"gap {rep['gap']:.0f}deg  "
                                       f"dL* {rep['dL']:.0f}",
               font=font(12, False), fill=(110, 110, 110))
        d.text((cx0, cy0 + cell + 56), 'PASS' if ok else 'REJECTED',
               font=font(13), fill=col)

    out = os.path.join(HERE, 'V3-CANDIDATES.png')
    sheet.save(out, 'PNG', optimize=True)
    print(f"\n  wrote {out} ({os.path.getsize(out)/1024:.1f} KB)")

    # ---------------- 48px timeline reality check -------------------
    strip_h = 130
    sw = pad + len(rows) * (48 + 26)
    strip = Image.new('RGB', (sw, strip_h), (255, 255, 255))
    ds = ImageDraw.Draw(strip)
    ds.text((pad, 8), 'AT REAL TIMELINE SIZE (48px) - does the coin still '
                      'separate from the field?',
            font=font(14), fill=(20, 20, 20))
    for i, (label, field, coin, sc, rep, br, ok) in enumerate(rows):
        small = circle_mask(draw_avatar(48, field, coin))
        strip.paste(small, (pad + i * (48 + 26), 44))
        ds.text((pad + i * (48 + 26), 98), label.split()[0],
                font=font(11, False), fill=(60, 60, 60))
    out2 = os.path.join(HERE, 'V3-48PX.png')
    strip.save(out2, 'PNG', optimize=True)
    print(f"  wrote {out2} ({os.path.getsize(out2)/1024:.1f} KB)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
