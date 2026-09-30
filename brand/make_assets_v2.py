#!/usr/bin/env python3
"""
make_assets_v2.py - Avatar v2, rebuilt from measured evidence.

WHY v1 FAILED (measured, not opinion)
  Peer scan of 10 verified avatars gave: brightness median 0.692.
  v1 measured 0.325 -> 0.367 BELOW the median, i.e. far too dark.
  The 48px timeline test then showed v1's blue coin sinking into its dark
  background: the disc had no separation from the circular crop edge and
  the "Ck" monogram became illegible.

WHAT THE WINNERS DO (from the same scan)
  Azuki   #bb3647 at 91% of pixels  - one flat saturated field
  Doodles #feacda at 71%            - one flat bright field
  Pudgy   #eff8f8 at 85%            - one flat light field
  clonex  #fefefe at 97%            - one flat field
  => The pattern is a SINGLE dominant flat field filling the whole circle,
     with a high-contrast subject on top. Not a vignette, not a gradient
     into darkness.

v2 RULES
  1. Fill 100% of the canvas with the primary teal (no dark vignette).
  2. Gold coin on top: gold-on-teal is a complementary-ish pairing that
     stays separated at 32px.
  3. Ink monogram: ink-on-gold measures 11.99:1 contrast.
  4. No thin details - anything under ~4% of width vanishes at 32px.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import PALETTE  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))

TEAL = PALETTE['teal']['rgb']
GOLD = PALETTE['gold']['rgb']
INK = PALETTE['ink']['rgb']
CREAM = PALETTE['cream']['rgb']
DEEP = PALETTE['deep']['rgb']
SLATE = PALETTE['slate']['rgb']


def font(size, bold=True):
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
        else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def centered(d, cx, cy, text, f, fill):
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=f,
           fill=fill)


def gold_coin(d, cx, cy, r):
    """A chunky gold coin. All features >=4% of the coin so they survive
    downscaling to 32px."""
    # rim
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=(int(GOLD[0] * 0.72), int(GOLD[1] * 0.68),
                    int(GOLD[2] * 0.42)))
    # face
    ir = int(r * 0.86)
    d.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=GOLD)
    # single bold highlight, not a thin arc
    hr = int(r * 0.60)
    d.arc([cx - hr, cy - hr, cx + hr, cy + hr], start=205, end=325,
          fill=(255, 235, 175), width=max(3, int(r * 0.13)))


def make_avatar(size, name):
    ss = 4
    W = size * ss
    # RULE 1: one flat field, full bleed
    img = Image.new('RGB', (W, W), TEAL)
    d = ImageDraw.Draw(img)

    # subtle concentric ring for depth WITHOUT going dark
    d.ellipse([W * 0.06, W * 0.06, W * 0.94, W * 0.94],
              outline=(int(TEAL[0] * 0.80), int(TEAL[1] * 0.86),
                       int(TEAL[2] * 0.80)),
              width=int(W * 0.022))

    r = int(W * 0.315)
    gold_coin(d, W // 2, W // 2, r)
    centered(d, W // 2, W // 2 - int(W * 0.004), 'Ck',
             font(int(W * 0.255)), INK)

    img = img.resize((size, size), Image.LANCZOS)
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size


def make_banner(w, h, name):
    ss = 2
    W, H = w * ss, h * ss
    img = Image.new('RGB', (W, H), DEEP)
    d = ImageDraw.Draw(img)

    # teal band on the left third so the brand colour is present but the
    # avatar corner stays clean
    for x in range(int(W * 0.42)):
        a = 1 - (x / (W * 0.42)) ** 1.6
        d.line([x, 0, x, H],
               fill=(int(DEEP[0] + (TEAL[0] - DEEP[0]) * a * 0.55),
                     int(DEEP[1] + (TEAL[1] - DEEP[1]) * a * 0.55),
                     int(DEEP[2] + (TEAL[2] - DEEP[2]) * a * 0.55)))

    # coin cluster - kept clear of the avatar zone (verified by
    # test_safezone.py: avatar occupies x<231, y>401 on a 1500x500 banner)
    gold_coin(d, int(W * 0.145), int(H * 0.39), int(H * 0.225))
    gold_coin(d, int(W * 0.912), int(H * 0.30), int(H * 0.082))
    gold_coin(d, int(W * 0.957), int(H * 0.53), int(H * 0.052))

    x0 = int(W * 0.30)
    d.text((x0, int(H * 0.225)), 'COINKINS', font=font(int(H * 0.215)),
           fill=CREAM)
    d.text((x0, int(H * 0.485)),
           'little coins on a chain where gas is money',
           font=font(int(H * 0.088), False), fill=(168, 196, 190))

    cy = int(H * 0.685)
    cx = x0
    f3 = font(int(H * 0.072))
    for c in ('ARC  5042', 'GAS = USDC', 'SEADROP'):
        l, t, r, b = d.textbbox((0, 0), c, font=f3)
        tw, th = r - l, b - t
        pad = int(H * 0.042)
        d.rounded_rectangle([cx, cy, cx + tw + pad * 2, cy + th + pad * 1.7],
                            radius=int(H * 0.055), fill=(9, 62, 56),
                            outline=(16, 96, 86), width=ss * 2)
        d.text((cx + pad - l, cy + pad * 0.85 - t), c, font=f3, fill=TEAL)
        cx += tw + pad * 2 + int(W * 0.013)

    img = img.resize((w, h), Image.LANCZOS)
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size


def make_og(w, h, name):
    ss = 2
    W, H = w * ss, h * ss
    img = Image.new('RGB', (W, H), DEEP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        a = y / H
        d.line([0, y, W, y],
               fill=(int(DEEP[0] + 6 * a), int(DEEP[1] + 14 * a),
                     int(DEEP[2] + 12 * a)))
    gold_coin(d, W // 2, int(H * 0.335), int(H * 0.195))
    centered(d, W // 2, int(H * 0.332), 'Ck', font(int(H * 0.155)), INK)
    centered(d, W // 2, int(H * 0.60), 'COINKINS',
             font(int(H * 0.115)), CREAM)
    centered(d, W // 2, int(H * 0.715), 'building on Arc, in public',
             font(int(H * 0.048), False), (168, 196, 190))
    centered(d, W // 2, int(H * 0.815), 'every claim verifiable on-chain',
             font(int(H * 0.040), False), TEAL)
    img = img.resize((w, h), Image.LANCZOS)
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size


if __name__ == '__main__':
    print("generating v2 assets with validated palette...")
    jobs = [
        (make_avatar, (400, 'v2-avatar-400.png')),
        (make_avatar, (512, 'v2-avatar-512.png')),
        (make_banner, (1500, 500, 'v2-banner-1500x500.png')),
        (make_banner, (1400, 400, 'v2-os-banner-1400x400.png')),
        (make_og, (1200, 630, 'v2-og-1200x630.png')),
    ]
    for fn, args in jobs:
        p, sz = fn(*args)
        print(f"  {os.path.basename(p):32s} {sz[0]}x{sz[1]}  "
              f"{os.path.getsize(p)/1024:.1f} KB")
