#!/usr/bin/env python3
"""
test_smallsize.py - The decisive test: avatars are seen at 32-48px in a
timeline, not at 400px. Measure how much each avatar SURVIVES shrinking.

Metric: "recognisability" = how much structural contrast remains at 32px
relative to the full size. A design that turns to mush at 32px is a failed
avatar no matter how nice it looks large.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(HERE, 'competitors')

NAMES = ['pudgypenguins', 'azuki', 'boredapeyachtclub', 'doodles-official',
         'moonbirds', 'milady', 'cryptopunks', 'rare-friends-genesis',
         'mutant-ape-yacht-club', 'clonex']


def circle_crop(im):
    """X shows avatars as circles - evaluate what users actually see."""
    im = im.convert('RGB')
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, w - 1, h - 1], fill=255)
    out = Image.new('RGB', (w, h), (255, 255, 255))
    out.paste(im, (0, 0), mask)
    return out


def structural_contrast(im, size):
    """
    Mean absolute difference between neighbouring pixels at a given size.
    High = the shape still reads. Low = it has become a blur.
    """
    s = im.resize((size, size), Image.LANCZOS).convert('L')
    px = list(s.getdata())
    tot, n = 0, 0
    for y in range(size):
        for x in range(size - 1):
            i = y * size + x
            tot += abs(px[i] - px[i + 1])
            n += 1
    for y in range(size - 1):
        for x in range(size):
            i = y * size + x
            tot += abs(px[i] - px[i + size])
            n += 1
    return tot / n


def main():
    items = []
    for n in NAMES:
        p = os.path.join(COMP, f'{n}.png')
        if os.path.exists(p):
            items.append((n, Image.open(p)))
    items.append(('>> OURS', Image.open(
        os.path.join(HERE, 'coinkins-avatar-400.png'))))

    print("=" * 76)
    print("SMALL-SIZE SURVIVAL (avatars are seen at 32-48px in timelines)")
    print("=" * 76)
    print(f"  {'name':24s} {'@400':>7} {'@48':>7} {'@32':>7} "
          f"{'retain%':>9}  verdict")
    print("  " + "-" * 72)

    results = {}
    for name, im in items:
        c = circle_crop(im)
        v400 = structural_contrast(c, 128)   # reference detail level
        v48 = structural_contrast(c, 48)
        v32 = structural_contrast(c, 32)
        retain = 100 * v32 / v400 if v400 else 0
        verdict = ('STRONG' if retain >= 90 else
                   'OK' if retain >= 70 else 'WEAK at small size')
        results[name] = retain
        print(f"  {name:24s} {v400:>7.2f} {v48:>7.2f} {v32:>7.2f} "
              f"{retain:>8.1f}%  {verdict}")

    # build a visual strip at real timeline size
    S = 48
    strip = Image.new('RGB', (len(items) * (S + 8) + 8, S + 16),
                      (255, 255, 255))
    for i, (name, im) in enumerate(items):
        strip.paste(circle_crop(im).resize((S, S), Image.LANCZOS),
                    (8 + i * (S + 8), 8))
    strip = strip.resize((strip.width * 3, strip.height * 3), Image.NEAREST)
    out = os.path.join(HERE, 'TEST-timeline-48px.png')
    strip.save(out)
    print(f"\n  saved -> {out} (48px circles, 3x zoom for inspection)")

    comp = {k: v for k, v in results.items() if not k.startswith('>>')}
    import statistics as st
    print(f"\n  peer retain median: {st.median(comp.values()):.1f}%")
    print(f"  ours:               {results['>> OURS']:.1f}%")


if __name__ == '__main__':
    main()
