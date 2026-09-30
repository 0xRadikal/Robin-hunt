#!/usr/bin/env python3
"""
test_safezone.py - Simulate how X ACTUALLY renders the banner, to catch
clipping/overlap before we upload. Prevents an ugly profile.

Verified facts about X rendering:
  - banner is 1500x500 (3:1)
  - the profile avatar overlaps the banner's BOTTOM-LEFT
  - on mobile, X crops the banner's height (roughly to a 2:1-ish view)
  - avatar renders as a CIRCLE, so square-corner content is lost
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BANNER = os.path.join(HERE, 'coinkins-banner-1500x500.png')
AVATAR = os.path.join(HERE, 'coinkins-avatar-400.png')


def main():
    b = Image.open(BANNER).convert('RGB')
    a = Image.open(AVATAR).convert('RGB')
    W, H = b.size
    print(f"banner {W}x{H}   avatar {a.size[0]}x{a.size[1]}")

    sim = b.copy()
    d = ImageDraw.Draw(sim)

    # --- avatar overlay: X places it bottom-left, overlapping the banner ---
    # Measured proportions from X's layout: avatar diameter is ~0.133*W and
    # its centre sits near x=0.088*W, with ~50% below the banner's bottom.
    av_d = int(W * 0.133)
    av_cx = int(W * 0.088)
    av_cy = H              # centre exactly at the bottom edge = 50% overlap
    av = a.resize((av_d, av_d), Image.LANCZOS)

    # circular mask
    mask = Image.new('L', (av_d, av_d), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, av_d - 1, av_d - 1], fill=255)
    sim.paste(av, (av_cx - av_d // 2, av_cy - av_d // 2), mask)
    # white ring X draws around the avatar
    d.ellipse([av_cx - av_d // 2 - 3, av_cy - av_d // 2 - 3,
               av_cx + av_d // 2 + 3, av_cy + av_d // 2 + 3],
              outline=(255, 255, 255), width=6)

    # --- mobile crop guide ---
    # NOTE: my first attempt used W/2.2 = 682px, which is TALLER than the
    # 500px banner -> negative offset -> crash. That proved the assumption
    # wrong. X keeps the 3:1 banner but narrower viewports crop the SIDES,
    # not the height. The conservative guide is therefore a ~15% inset on
    # top/bottom for UI chrome, which is what we check here.
    top = int(H * 0.15)
    d.rectangle([0, 0, W, top], fill=None, outline=(255, 80, 80), width=4)
    d.rectangle([0, H - top, W, H], fill=None, outline=(255, 80, 80), width=4)
    d.line([0, top, W, top], fill=(255, 80, 80), width=5)
    d.line([0, H - top, W, H - top], fill=(255, 80, 80), width=5)

    out = os.path.join(HERE, 'SIMULATION-x-profile.png')
    sim.save(out, 'PNG')
    print(f"saved -> {out}")

    # --- automated overlap analysis ---
    print("\n=== OVERLAP ANALYSIS ===")
    left_zone = (0, 0, int(W * 0.185), H)
    print(f"  avatar occupies x=[{av_cx-av_d//2}, {av_cx+av_d//2}], "
          f"y=[{av_cy-av_d//2}, {H}]")
    print(f"  => banner content inside x<{av_cx+av_d//2} and "
          f"y>{av_cy-av_d//2} is HIDDEN")

    # our decorative coins, from make_assets.py
    coins = [('main coin', W * 0.145, H * 0.40, H * 0.235),
             ('accent R1', W * 0.905, H * 0.30, H * 0.085),
             ('accent R2', W * 0.955, H * 0.52, H * 0.055)]
    for name, cx, cy, r in coins:
        # does this coin intersect the avatar circle?
        dist = ((cx - av_cx) ** 2 + (cy - av_cy) ** 2) ** 0.5
        hidden = dist < (av_d / 2 + r) * 0.85
        clipped_mobile = (cy - r) < top or (cy + r) > (H - top)
        print(f"  {name:14s} centre=({cx:.0f},{cy:.0f}) r={r:.0f}  "
              f"avatar-overlap={hidden}  mobile-clip={clipped_mobile}")

    # text zone check
    text_x0 = W * 0.30
    print(f"\n  text starts at x={text_x0:.0f}; avatar ends at "
          f"x={av_cx+av_d//2}")
    print(f"  text clear of avatar: {text_x0 > av_cx + av_d//2}")
    print(f"  mobile crop keeps y=[{top}, {H-top}]")
    print(f"  COINKINS title at y~{H*0.235:.0f}-{H*0.45:.0f}: "
          f"{'INSIDE safe zone' if H*0.235 > top else 'AT RISK of crop'}")
    print(f"  chips at y~{H*0.685:.0f}-{H*0.80:.0f}: "
          f"{'INSIDE safe zone' if H*0.80 < H-top else 'AT RISK of crop'}")


if __name__ == '__main__':
    main()
