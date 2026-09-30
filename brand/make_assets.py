#!/usr/bin/env python3
"""
make_assets.py - Generate Coinkins brand assets as exact-size PNGs.

Deterministic, vector-drawn, zero external dependencies beyond Pillow.
No AI generation needed, no credits, and pixel dimensions are exact by
construction rather than by luck.

PLATFORM SPECS (verified from help.x.com and corroborated by 4 sources):
  X avatar : 400x400, max 2MB, displayed as a CIRCLE
  X banner : 1500x500, 3:1 ratio
  Telegram : square, >=512x512 recommended
  OpenSea  : square avatar; banner 1400x400

DESIGN RATIONALE (doc 06 naming science):
  "Coinkins" = coin + -kin (diminutive). So: a small, friendly coin.
  Arc's gas token IS USDC, so the coin reads as a stablecoin disc.
  Palette anchors on Circle/USDC blue for category fit, kept dark so it
  reads as infrastructure rather than a cartoon PFP.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))

BG_DEEP = (11, 13, 23)
BG_PANEL = (20, 24, 41)
BLUE = (77, 163, 255)
BLUE_DK = (43, 111, 212)
CREAM = (232, 235, 245)
MUT = (139, 147, 176)
GOLD = (245, 200, 92)


def font(size, bold=True):
    """Find a usable TTF; fall back to default rather than crashing."""
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
        else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold
        else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_coin(d, cx, cy, r, ring=True):
    """
    The mark: a coin disc with a subtle rim and a 'Ck' monogram.
    Drawn with supersampling by the caller for clean edges.
    """
    # outer rim
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE_DK)
    # inner face
    ir = int(r * 0.88)
    d.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=BLUE)
    # highlight arc (gives the disc volume)
    hr = int(r * 0.72)
    d.arc([cx - hr, cy - hr, cx + hr, cy + hr], start=200, end=340,
          fill=(150, 200, 255), width=max(2, int(r * 0.06)))
    if ring:
        # tiny notches around the edge = coin milling
        n = 24
        for i in range(n):
            a = 2 * math.pi * i / n
            x1 = cx + math.cos(a) * r * 0.93
            y1 = cy + math.sin(a) * r * 0.93
            x2 = cx + math.cos(a) * r * 0.99
            y2 = cy + math.sin(a) * r * 0.99
            d.line([x1, y1, x2, y2], fill=BLUE_DK,
                   width=max(1, int(r * 0.035)))


def centered_text(d, cx, cy, text, f, fill):
    l, t, rr, b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (rr - l) / 2 - l, cy - (b - t) / 2 - t), text,
           font=f, fill=fill)


def make_avatar(size=400, name='coinkins-avatar-400.png'):
    """Square avatar. X displays it as a circle, so keep the mark centred
    and leave margin so nothing important is clipped."""
    ss = 4                      # supersample factor for smooth edges
    W = size * ss
    img = Image.new('RGB', (W, W), BG_DEEP)
    d = ImageDraw.Draw(img)

    # soft radial-ish backdrop using concentric rings
    for i in range(18, 0, -1):
        rr = int(W * (0.30 + i * 0.030))
        shade = (
            int(BG_DEEP[0] + (BG_PANEL[0] - BG_DEEP[0]) * (i / 18) * 0.8),
            int(BG_DEEP[1] + (BG_PANEL[1] - BG_DEEP[1]) * (i / 18) * 0.8),
            int(BG_DEEP[2] + (BG_PANEL[2] - BG_DEEP[2]) * (i / 18) * 0.8),
        )
        d.ellipse([W / 2 - rr, W / 2 - rr, W / 2 + rr, W / 2 + rr],
                  fill=shade)

    r = int(W * 0.30)
    draw_coin(d, W // 2, W // 2, r)
    centered_text(d, W // 2, W // 2 - int(W * 0.005), 'Ck',
                  font(int(W * 0.235)), (8, 16, 31))

    img = img.resize((size, size), Image.LANCZOS)
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size


def make_banner(w=1500, h=500, name='coinkins-banner-1500x500.png'):
    """
    X banner. CRITICAL: the avatar overlaps the bottom-left on X, and
    mobile crops the top/bottom. Keep all text in the right 60% and
    vertically centred.
    """
    ss = 2
    W, H = w * ss, h * ss
    img = Image.new('RGB', (W, H), BG_DEEP)
    d = ImageDraw.Draw(img)

    # subtle grid = infrastructure feel
    step = int(W * 0.035)
    for x in range(0, W, step):
        d.line([x, 0, x, H], fill=(18, 22, 38), width=ss)
    for y in range(0, H, step):
        d.line([0, y, W, y], fill=(18, 22, 38), width=ss)

    # glow band
    for i in range(40):
        a = i / 40
        y = int(H * 0.5 + (a - 0.5) * H * 0.9)
        d.line([0, y, W, y],
               fill=(int(11 + 14 * (1 - abs(a - 0.5) * 2)),
                     int(13 + 20 * (1 - abs(a - 0.5) * 2)),
                     int(23 + 46 * (1 - abs(a - 0.5) * 2))),
               width=int(H * 0.03))

    # Decorative coins.
    # LESSON FROM test_safezone.py: my first layout put three coins in the
    # bottom-left, which is exactly where X pastes the circular avatar. The
    # simulation showed visual collision and clutter. Two coins also fell
    # inside the top/bottom crop-risk band.
    # FIX: keep x < 0.26*W completely clear of large art, place a single
    # coin high-left (clear of the avatar at y>401), and add small accent
    # coins on the FAR RIGHT where nothing overlaps.
    draw_coin(d, int(W * 0.145), int(H * 0.40), int(H * 0.235))
    draw_coin(d, int(W * 0.905), int(H * 0.30), int(H * 0.085))
    draw_coin(d, int(W * 0.955), int(H * 0.52), int(H * 0.055))

    # text block on the right - safe from avatar overlap and mobile crop
    x0 = int(W * 0.30)
    f1 = font(int(H * 0.215))
    f2 = font(int(H * 0.088), bold=False)
    f3 = font(int(H * 0.072))

    d.text((x0, int(H * 0.235)), 'COINKINS', font=f1, fill=CREAM)
    d.text((x0, int(H * 0.485)), 'little coins on a chain where gas is money',
           font=f2, fill=MUT)

    # chips
    cy = int(H * 0.685)
    chips = ['ARC  5042', 'GAS = USDC', 'SEADROP']
    cx = x0
    for c in chips:
        l, t, rr, b = d.textbbox((0, 0), c, font=f3)
        tw, th = rr - l, b - t
        pad = int(H * 0.042)
        d.rounded_rectangle([cx, cy, cx + tw + pad * 2, cy + th + pad * 1.7],
                            radius=int(H * 0.055),
                            fill=BG_PANEL, outline=(36, 42, 68), width=ss * 2)
        d.text((cx + pad - l, cy + pad * 0.85 - t), c, font=f3, fill=BLUE)
        cx += tw + pad * 2 + int(W * 0.013)

    img = img.resize((w, h), Image.LANCZOS)
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size


def make_og(w=1200, h=630, name='coinkins-og-1200x630.png'):
    """Open Graph card for link previews on X/Telegram."""
    ss = 2
    W, H = w * ss, h * ss
    img = Image.new('RGB', (W, H), BG_DEEP)
    d = ImageDraw.Draw(img)
    step = int(W * 0.04)
    for x in range(0, W, step):
        d.line([x, 0, x, H], fill=(18, 22, 38), width=ss)
    for y in range(0, H, step):
        d.line([0, y, W, y], fill=(18, 22, 38), width=ss)

    draw_coin(d, int(W * 0.5), int(H * 0.335), int(H * 0.20))
    centered_text(d, int(W * 0.5), int(H * 0.332), 'Ck',
                  font(int(H * 0.155)), (8, 16, 31))
    centered_text(d, int(W * 0.5), int(H * 0.60), 'COINKINS',
                  font(int(H * 0.115)), CREAM)
    centered_text(d, int(W * 0.5), int(H * 0.715),
                  'building on Arc, in public', font(int(H * 0.048), False),
                  MUT)
    centered_text(d, int(W * 0.5), int(H * 0.815),
                  'every claim verifiable on-chain',
                  font(int(H * 0.040), False), BLUE)

    img = img.resize((w, h), Image.LANCZOS)
    p = os.path.join(OUT, name)
    img.save(p, 'PNG', optimize=True)
    return p, img.size


if __name__ == '__main__':
    print("generating brand assets...")
    for fn, args in ((make_avatar, {}),
                     (make_avatar, {'size': 512,
                                    'name': 'coinkins-avatar-512.png'}),
                     (make_banner, {}),
                     (make_banner, {'w': 1400, 'h': 400,
                                    'name': 'coinkins-os-banner-1400x400.png'}),
                     (make_og, {})):
        p, sz = fn(**args)
        kb = os.path.getsize(p) / 1024
        print(f"  {os.path.basename(p):38s} {sz[0]}x{sz[1]}  {kb:.1f} KB")
