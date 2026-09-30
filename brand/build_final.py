#!/usr/bin/env python3
"""build_final.py - Generate every final Coinkins asset.

FORM      M3 "arc" - selected by select_mark.py, 82.34/100
COLOURS   S3 deep indigo - selected by choose_colours.py after both
          rejected palettes failed the gates as controls
CONSTRUCTION  3 distinct radii, all multiples of U=W/16, verified by
          coinkins_mark.py (15/15 checks pass)

WHAT IS PRODUCED
  avatar 400x400      X profile picture      (help.x.com: 400x400, <=2MB)
  avatar 512x512      Telegram / OpenSea
  favicon 32 / 16     browser tab
  banner 1500x500     X header (3:1)
  os-banner 1400x400  OpenSea collection banner
  og 1200x630         link preview
  mark mono / inverted / silhouette / transparent

THE PROFILE CARRIES THE NAME, THE MARK DOES NOT
  The mark itself has no text - Mastercard removed its wordmark in 2019,
  Starbucks in 2011, Apple in 1977, and Wenzel (2018) measured the
  character-count drop at p=.004.
  BUT Mastercard only dropped its wordmark after measuring 80%+
  spontaneous recognition built over 53 years (1966-2019). Coinkins has
  3 followers and no symbol recognition at all, so the NAME must be
  visible in the banner and OG image. Monotype on the same change: the
  wordmark "isn't going away completely. Just ... almost completely."
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import coinkins_mark as CM  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'final')
os.makedirs(OUT, exist_ok=True)

# S3 deep indigo, selected by choose_colours.py
BG = (18, 34, 68)
RING = (234, 241, 250)
DISC = (243, 182, 58)
# supporting tones, derived from BG so nothing new is invented
BG_DEEP = (12, 23, 46)
MUTED = (150, 170, 196)


def font(size, bold=True):
    p = ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
         else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(p, size) if os.path.exists(p) \
        else ImageFont.load_default()


def centred(d, cx, cy, text, f, fill):
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=f,
           fill=fill)


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size, os.path.getsize(p)


# ---------------------------------------------------------------- avatar
def avatar(size):
    return CM.draw(size, BG, RING, DISC)


# --------------------------------------------------------------- banner
def banner(w, h, with_name=True):
    """X header / OpenSea banner.

    The avatar zone is protected: test_safezone.py established that X
    pastes the circular avatar at the banner's bottom-left, occupying
    x=[33,231], y=[401,500] on a 1500x500 banner. Nothing important goes
    there.
    """
    ss = 2
    W, H = w * ss, h * ss
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # a single flat vertical step, no gradient (Apple abandoned gloss by
    # 2017; Wenzel measured the shift away from depth, p=.001)
    d.rectangle([0, 0, W, int(H * 0.18)], fill=BG_DEEP)

    # the mark, placed on the right so the bottom-left avatar zone stays
    # clear
    ms = int(H * 0.62)
    mark = CM.draw(ms, BG, RING, DISC, transparent=True)
    img.paste(mark, (int(W * 0.795), int(H * 0.19)), mark)

    if with_name:
        x0 = int(W * 0.055)
        d.text((x0, int(H * 0.255)), 'COINKINS', font=font(int(H * 0.20)),
               fill=RING)
        d.text((x0, int(H * 0.49)),
               'little coins on a chain where gas is money',
               font=font(int(H * 0.082), False), fill=MUTED)
        # fact chips - every one is verifiable on-chain
        cx, cy = x0, int(H * 0.655)
        f3 = font(int(H * 0.068))
        for c in ('ARC  5042', 'GAS = USDC', 'SEADROP'):
            l, t, r, b = d.textbbox((0, 0), c, font=f3)
            tw, th = r - l, b - t
            pad = int(H * 0.040)
            d.rounded_rectangle(
                [cx, cy, cx + tw + pad * 2, cy + th + pad * 1.7],
                radius=int(H * 0.052), fill=BG_DEEP,
                outline=(34, 58, 104), width=ss * 2)
            d.text((cx + pad - l, cy + pad * 0.85 - t), c, font=f3,
                   fill=DISC)
            cx += tw + pad * 2 + int(W * 0.012)
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------- og
def og(w, h):
    ss = 2
    W, H = w * ss, h * ss
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, int(H * 0.10)], fill=BG_DEEP)
    d.rectangle([0, int(H * 0.90), W, H], fill=BG_DEEP)

    ms = int(H * 0.40)
    mark = CM.draw(ms, BG, RING, DISC, transparent=True)
    img.paste(mark, ((W - ms) // 2, int(H * 0.145)), mark)

    centred(d, W // 2, int(H * 0.655), 'COINKINS', font(int(H * 0.115)),
            RING)
    centred(d, W // 2, int(H * 0.765), 'building on Arc, in public',
            font(int(H * 0.047), False), MUTED)
    centred(d, W // 2, int(H * 0.845), 'every claim verifiable on-chain',
            font(int(H * 0.040), False), DISC)
    return img.resize((w, h), Image.LANCZOS)


if __name__ == '__main__':
    print("=" * 74)
    print("BUILDING FINAL ASSETS  -  form M3, colours S3 deep indigo")
    print("=" * 74)
    print(f"  background {'#%02X%02X%02X' % BG}")
    print(f"  ring       {'#%02X%02X%02X' % RING}")
    print(f"  disc       {'#%02X%02X%02X' % DISC}")
    print()

    jobs = [
        ('avatar-400.png', lambda: avatar(400)),
        ('avatar-512.png', lambda: avatar(512)),
        ('favicon-32.png', lambda: avatar(32)),
        ('favicon-16.png', lambda: avatar(16)),
        ('banner-1500x500.png', lambda: banner(1500, 500)),
        ('os-banner-1400x400.png', lambda: banner(1400, 400)),
        ('og-1200x630.png', lambda: og(1200, 630)),
        ('mark-silhouette-512.png', lambda: CM.silhouette(512)),
        ('mark-mono-light-512.png', lambda: CM.mono_light(512)),
        ('mark-transparent-512.png',
         lambda: CM.draw(512, BG, RING, DISC, transparent=True)),
        # LIGHT-SURFACE VARIANT - a real failure I found and fixed.
        # My first attempt used gold #C68A12, which measured 2.98:1
        # against white and FAILED WCAG 1.4.11 (needs 3.00:1) by 0.02.
        # My first fix was worse: I searched for the lightest gold
        # clearing 3.05:1 and the search walked the hue to 72deg -
        # olive-green, the exact colour the user rejected. Minimising
        # contrast toward the threshold is the wrong objective.
        # CORRECT fix: keep the hue and saturation of the dark-theme
        # disc #F3B63A (hue 40.2deg, sat 0.761) IDENTICAL and only lower
        # the value until it clears white. #A67C28 is that colour at
        # value 0.65, measuring 3.79:1 - real headroom rather than
        # sitting on the boundary. Hue 40.1deg, i.e. the same brand
        # gold, only darker. Nothing new was invented.
        # This mirrors how Apple ships a black mark for light surfaces
        # and a white one for dark.
        ('mark-onwhite-512.png',
         lambda: CM.draw(512, (255, 255, 255), (18, 34, 68),
                         (166, 124, 40))),
    ]
    total = 0
    for name, fn in jobs:
        p, sz, b = save(fn(), name)
        total += b
        print(f"  {name:28s} {sz[0]:5d}x{sz[1]:<5d} {b/1024:8.1f} KB")
    print()
    print(f"  {len(jobs)} files, {total/1024:.1f} KB total")
    print(f"  written to {OUT}")
