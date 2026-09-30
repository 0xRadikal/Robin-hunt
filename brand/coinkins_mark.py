#!/usr/bin/env python3
"""coinkins_mark.py - THE Coinkins mark, refined.

SELECTED FORM: M3 "arc" - a solid disc inside an open ring.
Selection was made by select_mark.py with weights declared before
scoring; M3 scored 82.34/100 vs 76.13 for the runner-up.

THE ONE GEOMETRIC IDEA
  A coin, and the arc it travels. Read another way: the disc is the
  coin, the open ring is the chain around it, and the gap is where the
  next coin enters. That single idea has to stay constant at every size
  and in every colour, which is the lesson from Mastercard's circles
  (unchanged since 1966) and Apple's silhouette (geometrically unchanged
  since 1977).

CONSTRUCTION METHOD - the only one with a verified provenance
  Martin Grasser published his own account of building the 2012 Twitter
  bird: fifteen overlapping circles drawn from a SMALL SET OF REPEATED
  DIAMETERS, every curve taken from a circle edge and handed to the next
  at a tangent point. His stated goal: "simple, balanced, and legible at
  very small sizes, almost like a lowercase 'e'".

  The transferable rule, with no golden-ratio mysticism:
      few repeated radii, shared axes, tangency at every join
      "If the answer is more than five, some of them are doing the
       same job."

  I am explicitly NOT claiming golden-ratio construction. David Cole's
  measurement for Gizmodo (2013) showed the famous Apple phi diagram
  fails: most of the logo's curves are not circular arcs at all, and
  plausible circle fits move the implied ratio between 1.53 and 1.73.
  Rob Janoff, who drew it: "I pretty much did it freehand" and the
  mathematical readings "are all BS. It's a wonderful urban legend."

THE RADII - three, all derived from one base unit U
  Everything below is a multiple of U = W/16, so there are no arbitrary
  numbers in the mark and the whole thing can be rebuilt from one value.

      R_outer  = 6U     outer edge of the ring
      R_inner  = 4.25U  inner edge of the ring   (ring stroke = 1.75U)
      R_disc   = 3U     the coin itself
      gap_half = 28deg  half-angle of the ring opening (white arc 304deg)

  (These replaced 4U / 2.75U / 34deg after the collision measurement
  described in the constants block below. The disc-to-ring void is
  unchanged at 1.25U, which is what the colour work in choose_colours.py
  depends on, so the S3 palette carries over untouched.)

  Distinct radii used: 3. Grasser's threshold is five.

  The gap sits on the RIGHT (centred on 0deg) so the mark has a reading
  direction and is not merely rotationally symmetric - asymmetry is what
  makes it memorable rather than generic. A fully closed ring around a
  dot is a loading spinner; the gap is what makes it ours.

WHY THE PROPORTIONS ARE THESE AND NOT OTHERS
  Measured against 11 real top-brand marks (measure_topbrands.py, whose
  SVG parser passed 9 validation tests first):
      ink fraction   top brands 0.070..0.497, median 0.298
      edge density   top brands 0.0177..0.0337, median 0.0250
      components     top brands 1..14, median 2
      thinnest       top brands 0.0365..0.2083, median 0.1146
  The ring stroke of 1.75U = 0.1094 of the width sits almost exactly on
  the top-brand median thinnest feature of 0.1146 - closer than the
  original 2U = 0.1250 did. Thickness was NOT the search objective, so
  this is a by-product rather than a target I am claiming credit for;
  what the search optimised was closeness to the measured medians as a
  whole, and thickness is one of its five terms.

WHAT THIS FILE DELIBERATELY DOES NOT DO
  No gradients, no gloss, no 3D bevel, no drop shadow. Apple used glossy
  3D from 2001 to 2007 and abandoned it by 2017; Wenzel (2018) measured
  the industry-wide shift away from depth toward flat, significant at
  chi-sq(3)=15.429, p=.001. Our own v1 avatar - the one the user
  preferred - had a radial gradient and a glossy arc, i.e. the 2001-2007
  aesthetic. v1 was right to have a FORM and wrong to have a finish.

  No text inside the mark. Mastercard removed it in 2019, Starbucks in
  2011, Apple in 1977. Wenzel measured the character-count drop at
  p=.004.
  BUT: the profile still needs the NAME, because Mastercard only dropped
  its wordmark after measuring 80%+ spontaneous symbol recognition built
  over 53 years, and Coinkins has none. So the name lives in the banner
  and handle, never inside the mark.
"""

import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SS = 8  # supersample factor; the mark is drawn large then downsampled

# ---- the construction, all in units of U = W/16 ---------------------
U_DIV = 16.0
R_OUTER_U = 6.0
R_INNER_U = 4.25
R_DISC_U = 3.0
GAP_HALF_DEG = 28.0

# Terminal rounding of the two ring ends, as a fraction of half the
# stroke width. 0.0 = flat cut on the radius, 1.0 = fully semicircular.
# The resulting cap radius is DERIVED (cap * (r_out - r_in) / 2), so it
# is not a fourth independent radius. Chosen by sweep in sweep_cap.py.
CAP = 1.0

DISTINCT_RADII = 3   # asserted and tested in verify_construction()

# ---- WHY THESE NUMBERS AND NOT THE ORIGINAL 4.00 / 2.75 / 34.0 ------
# The first version of variant A used r_in=4.00, r_disc=2.75, gap=34deg.
# It passed every construction check, but independent visual review said
# it "heavily resembles" the Colorado state flag, and also flagged the
# copyright symbol and the bullseye.
#
# Those were opinions, so collide.py was written to turn them into
# numbers: four independent distance metrics (rotation-minimised IoU, Hu
# moments, radial signature, construction-parameter distance) against
# four references with stated provenance - Colorado derived from the
# statute C.R.S. 24-80-904, the REAL U+00A9 glyph, the concentric
# bullseye that the EU General Court declared INVALID in T-347/24
# (9 July 2025, "banal and simple geometric shapes"), and IEC 60417-5009.
# The metric is calibrated: it returns EXACTLY 0.0000 when the geometry
# really is Colorado's, and rises monotonically as the fill ratio falls.
#
# Measured on the original variant A, the WORST collision was not
# Colorado (0.4866) but the BULLSEYE (0.4440).
#
# search_a2.py then searched 3,484 feasible candidates with collision
# distance as a FLOOR (never as the objective - maximising it converges
# on a degenerate hairline ring, the same category error as maximising
# Ou & Luo colour harmony, which converged on olive) and with the
# objective being closeness to the MEASURED medians of 11 real top-brand
# marks. These values are a genuine Pareto improvement:
#
#     worst-case collision  0.4440 -> 0.5077   (+14.3%)
#     quality distance Q    0.2173 -> 0.2126   (-2.1%)
#
# i.e. simultaneously less collision AND closer to real top-brand
# proportions. Ring stroke 1.75U = 0.1094 of width is also CLOSER to the
# measured top-brand median thinnest feature (0.1146) than the original
# 2U = 0.1250 was.
#
# A PREDICTION OF MINE THAT THE DATA DISPROVED: I expected lowering the
# disc fill ratio below 0.688 to be the lever. It is not - the winning
# candidate RAISES fill to 3.00/4.25 = 0.7059. The real lever is the GAP
# ANGLE, because changing the opening moves the mark away from Colorado
# AND the bullseye at once.
#
# ---- WHY gap_half IS 40 AND NOT 46 --------------------------------
# The user supplied a reference logo and asked for LONGER white edges.
# measure_ref.py MEASURED that reference rather than guessing at it, and
# three independent methods agreed on its arc (radial probe 302deg, area
# ratio 295.6deg, angular occupancy 302deg):
#
#     reference white arc  302 deg  (gap half-angle 29.0 deg)
#     ours at the time     268 deg  (gap half-angle 46.0 deg)
#     reference stroke     0.3550 of r_outer, ours 0.2917
#
# Matching the reference exactly was COSTED BEFORE BEING OFFERED, and
# it is a losing trade: gap 28-30deg drops the worst-case collision
# distance 0.5004 -> 0.4351 (-13.1%) and moves us from 23.98deg to
# 6.98deg away from Colorado's statutory 22.02deg opening - i.e. it
# gives back the whole collision gain AND lands us next to the flag the
# independent reviewer had already flagged twice.
#
# solve_option_c.py swept the feasible set with the disc pinned at
# 3.00U (the user had approved the coin size, and this request was about
# the ARC). With r_in and the disc held constant:
#
#     gap  arc   collision   vs 46deg   Q       vs 46deg
#     28   304   0.4351      -13.1%     0.2251  +5.9%    <-- CHOSEN
#     34   292   0.4664       -6.8%     0.2247  +5.7%
#     38   284   0.4996       -0.2%     0.2185  +2.7%
#     40   280   0.5068       +1.3%     0.2144  +0.8%
#     46   268   0.5004        0.0%     0.2126   0.0%
#
# THE USER CHOSE 28deg, WITH THE COST STATED IN ADVANCE AND ACCEPTED.
# I offered 40deg as the free-lunch compromise and it was measurably
# better on both metrics, but the user preferred the look of the longest
# arc, which is the closest match to the reference they supplied. That
# is a legitimate owner's call on an aesthetic question, and the cost is
# recorded here rather than buried:
#
#   * worst-case collision distance falls 0.5068 -> 0.4351 (-14.1%),
#     giving back the gain won earlier in the process
#   * the opening moves from 17.98deg to 5.98deg away from Colorado's
#     statutory 22.02deg, so the Colorado association gets STRONGER, not
#     weaker - independent review already scored it 8/10 at 268deg
#   * quality distance Q worsens 5.9%
#
# THE USER'S REASONING ON RISK IS CORRECT, AND WAS VERIFIED:
# they judged that nobody will sue over this logo. The primary sources
# agree. In T-347/24 (General Court, 9 July 2025) Target's OWN
# concentric-circles mark was DECLARED INVALID for lack of distinctive
# character - "banal and simple geometric shapes" - and Target paid
# costs, so the configuration is not ownable by anyone. And Lanham
# 2(b) / 15 USC 1052(b) bars REGISTRATION only, not use; a US state is
# not a commercial competitor. The residual risk was never legal: it is
# commercial distinctiveness, i.e. whether a viewer reads the mark as
# "Coinkins" or as "the Colorado flag".
#
# The user also noted it can be changed later. That is cheap NOW (3
# followers, no published assets) and expensive later - Mastercard needed
# 53 years and 80%+ spontaneous recognition before it dared drop its
# wordmark. The decision is reversible today and is recorded as such.
#
# TWO RISKS OF THE NARROWER OPENING WERE CHECKED BEFORE APPLYING IT:
#   * gap chord at a 16px render = 5.63px, still far above the 1.5px
#     readability floor (it was 7.71px at 40deg)
#   * each rounded cap consumes 9.83deg of arc, so a 28deg half-gap
#     still leaves 284.34deg of flat arc - the caps fit with room to
#     spare and the polygon does not self-intersect
#
# The reference's THICKER band was deliberately NOT copied: pulling
# r_in to 3.75U to match its 0.3550 stroke collapses the collision
# distance by 36.3% and worsens Q by 44.7%, because a fat ring with a
# large disc is precisely the bullseye the EU General Court called banal
# in T-347/24. Measured, then rejected.


def _ring_with_gap(d, cx, cy, r_out, r_in, gap_half, fill, ss_res=720,
                   cap=None):
    """Draw an annulus with an angular gap, as a single filled polygon.

    Built as one polygon rather than an arc stroke so it rasterises
    identically at every size.

    `cap` controls the TERMINAL geometry of the two ring ends:
        None / 0.0  -> ends cut flat on the radius (the original)
        1.0         -> fully semicircular ends (a true round cap)
        0 < c < 1   -> partially rounded, radius c * (stroke/2)

    HOW THE ROUNDING IS BUILT, AND WHY THIS WAY
    -------------------------------------------
    The cap is NOT drawn as a separate circle pasted on the end. That
    would work visually but would leave the ring outline and the cap
    outline as two shapes that only happen to coincide, and any
    rasterisation difference would show as a seam at small sizes.
    Instead the cap arc is generated as part of the SAME polygon: the
    outer edge is walked forward, then the terminal arc is traced around
    the stroke's centreline, then the inner edge is walked back.

    The cap radius is DERIVED, never a free parameter:

        cap_radius = c * (r_out - r_in) / 2

    At c = 1 this is exactly half the stroke width, which is the only
    value that makes the terminal tangent to BOTH the outer and the
    inner edge - i.e. the unique radius that produces a smooth end with
    no corner and no bulge. It is a function of two radii that already
    exist, so it adds no independent number to the construction and does
    not violate Grasser's "if the answer is more than five, some of them
    are doing the same job" - a derived quantity does not do a separate
    job.

    The arc is swept so that the cap's outer extreme still touches
    r_out and its inner extreme still touches r_in, which means the
    ring's overall footprint is unchanged: the mark does not grow.
    """
    if not cap or cap <= 0.0:
        pts = []
        a0 = gap_half
        a1 = 360.0 - gap_half
        n = max(24, int(ss_res * (a1 - a0) / 360.0))
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
        for i in range(n, -1, -1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a)))
        d.polygon(pts, fill=fill)
        return

    c = min(1.0, float(cap))
    half = (r_out - r_in) / 2.0          # stroke half-width
    rc = c * half                        # cap radius, DERIVED
    rm = (r_out + r_in) / 2.0            # stroke centreline

    # The flat part of the end must be pulled back by the angular amount
    # the cap will occupy, measured along the centreline, so the cap
    # occupies the gap's edge rather than extending past it.
    dtheta = math.degrees(math.asin(min(1.0, rc / rm)))
    a0 = gap_half + dtheta
    a1 = 360.0 - gap_half - dtheta
    if a1 <= a0:                         # cap too large for the gap
        a0 = a1 = (a0 + a1) / 2.0

    n = max(24, int(ss_res * max(1.0, a1 - a0) / 360.0))
    ncap = max(12, int(ss_res * 0.06))

    pts = []
    # outer edge, forward
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
    # Terminal cap at the a1 end.
    # The polygon has just arrived at the OUTER point (r_out, a1). Seen
    # from the cap centre (rm, a1), that point lies at bearing a1, and
    # the INNER point (r_in, a1) lies at bearing a1 + 180. So the arc
    # must run a1 -> a1 + 180, sweeping AWAY from the ring body.
    # (My first attempt started the arc at a1 - 90, which made the
    # polygon cross itself; the rendered result had TWO boundaries and
    # five corners instead of one boundary and none. Caught by test_cap
    # F3/F4, diagnosed by computing these bearings explicitly.)
    ac = math.radians(a1)
    ex, ey = cx + rm * math.cos(ac), cy + rm * math.sin(ac)
    for i in range(ncap + 1):
        t = ac + math.pi * i / ncap
        pts.append((ex + rc * math.cos(t), ey + rc * math.sin(t)))
    # inner edge, back
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a)))
    # Terminal cap at the a0 end: we are at the INNER point (r_in, a0),
    # which sits at bearing a0 + 180 from the cap centre, and we must
    # reach the OUTER point at bearing a0. Arc runs a0 + 180 -> a0 + 360.
    ac = math.radians(a0)
    sx, sy = cx + rm * math.cos(ac), cy + rm * math.sin(ac)
    for i in range(ncap + 1):
        t = ac + math.pi + math.pi * i / ncap
        pts.append((sx + rc * math.cos(t), sy + rc * math.sin(t)))
    d.polygon(pts, fill=fill)


def draw(size, bg, ring, disc, transparent=False):
    """Render the Coinkins mark.

    bg   - background field (ignored when transparent=True)
    ring - colour of the open ring
    disc - colour of the coin
    """
    W = size * SS
    mode = 'RGBA' if transparent else 'RGB'
    base = (0, 0, 0, 0) if transparent else bg
    img = Image.new(mode, (W, W), base)
    d = ImageDraw.Draw(img)

    U = W / U_DIV
    cx = cy = W / 2.0
    _ring_with_gap(d, cx, cy, R_OUTER_U * U, R_INNER_U * U,
                   GAP_HALF_DEG, ring, cap=CAP)
    rd = R_DISC_U * U
    d.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], fill=disc)

    return img.resize((size, size), Image.LANCZOS)


def draw_v2(size, bg, ring, disc, transparent=False):
    """VARIANT B - same idea, restructured to break a REAL resemblance
    that independent image analysis found in variant A.

    THE PROBLEM WITH VARIANT A, found by measurement not by opinion
      An independent vision analysis of the rendered avatar reported,
      unprompted: "the configuration heavily resembles the iconic
      central element of the Colorado state flag", and marked
      originality down for it.

      That claim checks out against primary sources:
        Colorado State Archives (archives.colorado.gov): "Completely
        filling the open space inside the letter C is a golden disk"
        Wikipedia, Flag of Colorado: "a circular red 'C', filled with a
        golden disk"

      Measured comparison:
        Colorado  - disk COMPLETELY fills the C     fill ratio 1.000
        variant A - disc fills 68.8% of the opening fill ratio 0.688
      So variant A is not a copy: different fill ratio, different
      colours (light ring on flat navy vs red C on blue/white stripes),
      different stroke (constant-width 2U annulus vs a tapered
      letterform). But a real viewer saw it unprompted, so the
      resemblance is data I must act on rather than argue away.

    WHAT VARIANT B CHANGES, and why each change breaks the resemblance
      1. The gap moves from the RIGHT (0deg) to the TOP-RIGHT DIAGONAL
         (-45deg). A ring opened on the right is what makes a 'C'; a
         ring opened on the diagonal is not any letter of the alphabet.
      2. The gap narrows from 68deg to 46deg, so the ring reads as a
         nearly-closed orbit rather than a letterform counter.
      3. The disc shifts 0.75U along that same diagonal, so it sits
         ECCENTRICALLY. Colorado's disk is dead-centre and fills the
         counter; an off-centre disc reads as a coin travelling along
         the arc.

      The three radii are UNCHANGED, so this is the same construction
      system and the same single idea - a coin and the arc it travels.
    """
    W = size * SS
    mode = 'RGBA' if transparent else 'RGB'
    base = (0, 0, 0, 0) if transparent else bg
    img = Image.new(mode, (W, W), base)
    d = ImageDraw.Draw(img)

    U = W / U_DIV
    cx = cy = W / 2.0

    gap_centre = -45.0
    gap_half = 23.0
    r_out, r_in = R_OUTER_U * U, R_INNER_U * U
    pts = []
    a0 = gap_centre + gap_half
    a1 = gap_centre + 360.0 - gap_half
    n = 720
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a)))
    d.polygon(pts, fill=ring)

    off = 0.75 * U
    a = math.radians(gap_centre)
    dx, dy = off * math.cos(a), off * math.sin(a)
    rd = R_DISC_U * U
    d.ellipse([cx + dx - rd, cy + dy - rd, cx + dx + rd, cy + dy + rd],
              fill=disc)
    return img.resize((size, size), Image.LANCZOS)


def draw_v3(size, bg, ring, disc, transparent=False):
    """VARIANT C - fixes what independent analysis found wrong with BOTH
    A and B. This is the third iteration, not a first guess.

    WHAT THE INDEPENDENT ANALYSIS SAID (unprompted, about the render)
      Variant A:
        "Very high resemblance [to the Colorado flag] (Rating: 8/10)...
         the geometry of a perfect 'C' wrapping around a gold disk is
         identical to the Colorado flag's emblem. It looks highly
         derivative."
        "Strongly resembles the standard Copyright symbol (c) or a
         target/bullseye."
        -> two separate collisions. Not defensible.
      Variant B:
        "Rotating the gap to 45 degrees and offsetting the gold disk
         successfully breaks the association" (Colorado down to 3/10)
        BUT: "the offset center looks awkward (like a misaligned
         eyeball) and completely falls apart at small icon resolutions...
         the diagonal slice starts to look like a rendering glitch"
        -> the fix worked, the execution did not.

    THE ACTUAL DIAGNOSIS
      A centred disc inside a ring is the Colorado/copyright/bullseye
      configuration, full stop. Moving the gap alone does not escape it,
      and merely offsetting the disc reads as a mistake rather than a
      decision. The concentric ring-plus-dot idea has to go.

    WHAT VARIANT C DOES INSTEAD
      The coin becomes the SUBJECT and the arc becomes a TANGENT, not a
      surrounding ring:
        1. One solid disc, CENTRED and dead-centre - no eccentricity, so
           nothing can read as a misalignment. This also keeps the 16px
           behaviour of a solid circle, which is the most robust shape
           at tiny sizes.
        2. A thick arc that does NOT enclose the disc. It sweeps from the
           lower-left to the upper-right OUTSIDE the disc and stops -
           an open trajectory, not a closed counter. An open arc that
           terminates cannot be read as a letter, a (c), or a bullseye,
           because all three require a closed or nearly-closed ring.
        3. The arc is cut by a background-coloured keyline of 0.35U
           where it passes the disc, so disc and arc never touch. That
           keeps every boundary disc-to-background or arc-to-background,
           which is what made the earlier contrast numbers work.

      Radii stay in the same system: the disc is R_DISC_C = 3.4U, the
      arc runs on R_ARC = 5.0U with a 1.5U stroke. Three radii again,
      all quarter-unit multiples of U = W/16.

      The single idea is unchanged and now clearer: a coin, and the arc
      it travels.
    """
    W = size * SS
    mode = 'RGBA' if transparent else 'RGB'
    base = (0, 0, 0, 0) if transparent else bg
    img = Image.new(mode, (W, W), base)
    d = ImageDraw.Draw(img)

    U = W / U_DIV
    cx = cy = W / 2.0

    R_ARC = 5.0 * U
    ARC_W = 1.5 * U
    R_D = 3.4 * U
    KEY = 0.35 * U

    # The open arc. It sweeps 150deg and STOPS - well under a closed
    # ring, so it cannot read as a letter, a (c), or a bullseye.
    #
    # ANGLE CONVENTION, stated explicitly because I got it wrong once:
    # PIL's y axis points DOWN, so positive angles rotate CLOCKWISE on
    # screen. 0deg = right, 90deg = BOTTOM, 180deg = left, 270deg = top.
    # My first attempt used 118..268deg and the docstring claimed
    # "lower-left to upper-right"; a verification probe at 270deg
    # (screen-top) found no arc, which was correct - 118..268 actually
    # runs bottom-left, through the LEFT, to the top. The test caught
    # that my stated intent and my numbers disagreed.
    #
    # 195..345deg puts the arc on the upper-left, sweeping up over the
    # coin and terminating at the top-right. That is the trajectory the
    # design intends: the coin sits still, the arc travels past it.
    a0, a1 = 195.0, 345.0
    n = 480
    pts = []
    ro, ri = R_ARC + ARC_W / 2, R_ARC - ARC_W / 2
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + ro * math.cos(a), cy + ro * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
    d.polygon(pts, fill=ring)

    # keyline so the arc never touches the disc
    d.ellipse([cx - R_D - KEY, cy - R_D - KEY,
               cx + R_D + KEY, cy + R_D + KEY], fill=base if transparent
              else bg)
    # the coin, dead centre
    d.ellipse([cx - R_D, cy - R_D, cx + R_D, cy + R_D], fill=disc)

    return img.resize((size, size), Image.LANCZOS)


VARIANTS = {'A': draw, 'B': draw_v2, 'C': draw_v3}


def silhouette(size=256, variant='A'):
    """Pure black on white - the honest test. Apple's mark has worked
    this way since 1977."""
    return VARIANTS[variant](size, (255, 255, 255), (0, 0, 0), (0, 0, 0))


def mono_light(size=256):
    """Single-colour on dark - for stamps, embroidery, one-ink print."""
    return draw(size, (0, 0, 0), (255, 255, 255), (255, 255, 255))


# ======================================================================
# VERIFICATION - the construction must be provably what it claims
# ======================================================================

def verify_construction():
    print("=" * 76)
    print("VERIFYING THE CONSTRUCTION MATCHES ITS OWN SPECIFICATION")
    print("=" * 76)
    ok = True

    # 1. distinct radii count
    radii = {R_OUTER_U, R_INNER_U, R_DISC_U}
    good = len(radii) == DISTINCT_RADII and len(radii) <= 5
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  distinct radii = {len(radii)} "
          f"({sorted(radii)} in units of U)")
    print(f"        Grasser's rule: more than five and some are "
          f"redundant. We use {len(radii)}.")

    # 2. every radius is a clean multiple of the base unit
    mults = [R_OUTER_U, R_INNER_U, R_DISC_U]
    good = all(abs(m * 4 - round(m * 4)) < 1e-9 for m in mults)
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  every radius is a quarter-unit "
          f"multiple of U=W/16: {mults}")

    # 3. ring stroke must land on the measured top-brand median thinnest
    stroke_frac = (R_OUTER_U - R_INNER_U) / U_DIV
    target = 0.1146   # measured median of 11 top-brand marks
    good = abs(stroke_frac - target) < 0.02
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  ring stroke = "
          f"{R_OUTER_U - R_INNER_U:g}U = {stroke_frac:.4f} of width; "
          f"top-brand median thinnest = {target}")

    # 4. the geometry must actually be rendered as specified: measure the
    #    rendered image back and compare to the analytic areas.
    size = 512
    sil = silhouette(size)
    g = sil.convert('L')
    px = g.load()
    c = size / 2.0
    U = size / U_DIV

    # sample along the +y axis (90deg, far from the gap at 0deg)
    def ink_at(radius_u, ang_deg):
        a = math.radians(ang_deg)
        x = int(round(c + radius_u * U * math.cos(a)))
        y = int(round(c + radius_u * U * math.sin(a)))
        x = max(0, min(size - 1, x))
        y = max(0, min(size - 1, y))
        return px[x, y] < 128

    checks = [
        (0.0, 90, True, 'centre is inside the disc'),
        (R_DISC_U - 0.3, 90, True, 'just inside the disc edge'),
        (R_DISC_U + 0.3, 90, False, 'the void between disc and ring'),
        (R_INNER_U - 0.3, 90, False, 'still void, just inside the ring'),
        (R_INNER_U + 0.3, 90, True, 'inside the ring band'),
        (R_OUTER_U - 0.3, 90, True, 'still inside the ring band'),
        (R_OUTER_U + 0.3, 90, False, 'outside the ring'),
        (R_INNER_U + 1.0, 0, False, 'the GAP: no ring on the +x axis'),
        (R_INNER_U + 1.0, 180, True, 'ring present opposite the gap'),
    ]
    for ru, ang, want, why in checks:
        got = ink_at(ru, ang)
        good = got == want
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'}  r={ru:5.2f}U a={ang:3d}deg "
              f"-> ink={got} (want {want})  {why}")

    # 5. the gap angle must measure back correctly
    found = []
    for ang in range(0, 360):
        if ink_at((R_INNER_U + R_OUTER_U) / 2, ang):
            found.append(ang)
    # the gap is the set of angles with NO ink
    missing = [a for a in range(0, 360) if a not in found]
    # normalise: the gap straddles 0, so shift
    shifted = sorted(((a + 180) % 360) for a in missing)
    span = (max(shifted) - min(shifted) + 1) if shifted else 0
    want_span = 2 * GAP_HALF_DEG
    good = abs(span - want_span) <= 4
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  measured gap span {span}deg "
          f"vs specified {want_span:.0f}deg (+/-4 for rasterisation)")

    # 6. area check against the analytic value
    inkf = sum(1 for v in g.getdata() if v < 128) / (size * size)
    ring_area = (math.pi * ((R_OUTER_U * U) ** 2 - (R_INNER_U * U) ** 2)
                 * (360 - 2 * GAP_HALF_DEG) / 360)
    disc_area = math.pi * (R_DISC_U * U) ** 2
    analytic = (ring_area + disc_area) / (size * size)
    good = abs(inkf - analytic) < 0.01
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  rendered ink {inkf:.4f} vs "
          f"analytic {analytic:.4f} - proves the rasteriser draws the "
          f"specified geometry")

    # 7. the mark must be scale-invariant: the same shape at every size
    ref = silhouette(256).convert('L').resize((64, 64), Image.LANCZOS)
    worst = 0.0
    for s in (16, 24, 32, 48, 96, 400):
        cand = silhouette(s).convert('L').resize((64, 64), Image.LANCZOS)
        a, b = list(ref.getdata()), list(cand.getdata())

        def norm(p):
            lo, hi = min(p), max(p)
            return [(v - lo) / (hi - lo) if hi > lo else 0.5 for v in p]
        na, nb = norm(a), norm(b)
        mae = sum(abs(x - y) for x, y in zip(na, nb)) / len(na)
        worst = max(worst, mae)
        print(f"        {s:3d}px structural error vs 256px reference: "
              f"{mae:.4f}")
    good = worst <= 0.10
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  worst-case scale error "
          f"{worst:.4f} <= 0.10")

    print()
    print("=" * 76)
    print(f"CONSTRUCTION {'VERIFIED' if ok else 'FAILED'}")
    print("=" * 76)
    return ok


if __name__ == '__main__':
    sys.exit(0 if verify_construction() else 1)
