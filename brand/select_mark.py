#!/usr/bin/env python3
"""select_mark.py - Choose the form with an AUDITABLE scorecard.

WHY A SCORECARD AND NOT AN OPINION
  The user asked me to choose. My last attempt to settle a design
  question with a single metric produced the rejected olive palette.
  So this does the opposite: it declares the criteria FIRST, states
  where each weight comes from, scores every form on every criterion,
  and prints the whole matrix so the decision can be checked and
  overturned.

  Where a criterion cannot be measured by code (semantic reading,
  ownability), the score is a JUDGEMENT and is labelled [J]. I am not
  going to dress a judgement up as a measurement - that is exactly the
  failure mode the Gizmodo/Janoff research warns about ("reverse-
  engineer your own work and report it as intent").

THE CRITERIA, EACH WITH ITS SOURCE AND WEIGHT

  C1  SMALL-SIZE SURVIVAL                                    weight 20
      [MEASURED] structural error at 16px, and the luminance edge.
      SOURCE: Martin Grasser, designer of the 2012 Twitter bird, on his
      own brief: "designed to be simple, balanced, and legible at very
      small sizes, almost like a lowercase 'e'". Also Wenzel 2018:
      measured industry shift toward flat/simple FOR digital and mobile.
      This is the single most testable requirement and the one that
      killed our v1 avatar, so it carries the most weight.

  C2  SILHOUETTE LEGIBILITY                                  weight 18
      [MEASURED] does the form read with colour fully removed?
      SOURCE: Apple's mark has worked as a pure silhouette since 1977
      (verified: 1998 version was a single flat black). Nike always has.
      If a mark needs colour to be understood, it is not a mark.

  C3  SEMANTIC FIT - does it read as "coin"?                  weight 18
      [J] JUDGEMENT. The project is called Coinkins and the product is
      little coins. Henderson & Cote (1998) call this NATURALNESS - "the
      degree to which the design depicts commonly experienced objects" -
      and found it one of the three strongest moderators of recognition
      and affect. A form that scores well on geometry but reads as
      something else fails the brand.

  C4  OWNABILITY / DISTINCTIVENESS                            weight 16
      [J] JUDGEMENT informed by evidence. Two concrete risks found by
      research:
        - "coin stack" is a GENERIC fintech icon. Search returns
          26,987 stock illustrations of stacked coins and multiple
          fintech brands using it. A generic symbol cannot be owned.
        - two interlocking circles is Mastercard's mark since 1966.
          Mastercard has been in active trademark litigation over it
          (EUIPO invalidated two of its registrations in 2019 after a
          challenge by Cinkciarz.pl; the EU General Court annulled 12
          Board of Appeal decisions in 2020). Even where Mastercard
          loses, being in that fight is a cost we cannot pay.

  C5  CONSTRUCTION QUALITY                                    weight 12
      [MEASURED] number of DISTINCT radii used, and whether curves meet
      at tangents. SOURCE: Grasser's published grid uses 15 circles
      drawn from only a few diameters. The transferable rule from that
      research: "If the answer is more than five, some of them are doing
      the same job." Few repeated radii is what makes a mark read as one
      system rather than a drawing.

  C6  TOP-BRAND METRIC CONFORMANCE                            weight 10
      [MEASURED] distance from the medians of 11 real top-brand marks
      measured in measure_topbrands.py (ink 0.298, edges 0.0250,
      components 2, thinnest 0.1146).

  C7  SCALES INTO A SYSTEM                                     weight 6
      [J] JUDGEMENT. Can the form survive being cropped to a favicon,
      extended into a banner, and used as a repeating motif? Mastercard's
      circles and Nike's swoosh both do.

  Weights sum to 100. They are declared before any score is computed.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import marks as MK  # noqa: E402
import test_marks as T  # noqa: E402
from palette import contrast  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

WEIGHTS = {
    'C1 small-size survival': 20,
    'C2 silhouette legibility': 18,
    'C3 semantic fit (coin)': 18,
    'C4 ownability / risk': 16,
    'C5 construction quality': 12,
    'C6 top-brand conformance': 10,
    'C7 scales into a system': 6,
}

# --- C3, C4, C7: declared JUDGEMENTS with written reasons -------------
# Every one of these is a judgement, labelled as such, with the reason
# stated so it can be argued with. None is presented as a measurement.
JUDGEMENTS = {
    'M1 stack': {
        'C3 semantic fit (coin)': (8,
            'three discs seen edge-on read clearly as stacked coins; '
            'this is the most literal "little coins" reading of the six'),
        'C4 ownability / risk': (3,
            'GENERIC. "coin stack" is a stock fintech icon - search '
            'returns 26,987 stacked-coin illustrations and multiple '
            'fintech brands already use it. A generic symbol cannot be '
            'owned, and at 48px it is indistinguishable from a hamburger '
            'menu icon'),
        'C7 scales into a system': (6,
            'the three bars can repeat as a pattern, but they are also '
            'confusable with UI chrome'),
    },
    'M2 slot': {
        'C3 semantic fit (coin)': (7,
            'a coin above a slot reads as the ACT of paying rather than '
            'as a coin itself; the slot bar needs context to be read'),
        'C4 ownability / risk': (6,
            'the coin-into-slot composition is used by arcade/vending '
            'iconography but is not a famous brand mark; moderately '
            'ownable'),
        'C7 scales into a system': (5,
            'two disconnected elements are hard to crop or extend'),
    },
    'M3 arc': {
        'C3 semantic fit (coin)': (9,
            'a solid disc inside an open ring reads immediately as a '
            'coin; the ring gap adds the "in motion / mid-flip" quality '
            'that Henderson & Cote call ACTIVITY, which lifts '
            'elaborateness off the bare minimum without clutter'),
        'C4 ownability / risk': (7,
            'a broken ring around a dot is common in UI (loading '
            'spinners, progress rings) so it is not unique, but it is '
            'not any famous BRAND mark; the specific gap angle and '
            'proportion are ownable'),
        'C7 scales into a system': (9,
            'the ring alone works as a favicon, the gap can hold other '
            'elements, and the ring can extend into a banner rule'),
    },
    'M4 orbit': {
        'C3 semantic fit (coin)': (8,
            'a small coin travelling around a large one reads as coin + '
            'movement, and maps onto "a chain" - the orbit is the chain '
            'and the discs are the coins. Two ideas in one form'),
        'C4 ownability / risk': (8,
            'the asymmetric small-disc-on-an-open-arc composition is the '
            'most distinctive of the six; no famous brand mark uses it. '
            'Highest ownability here'),
        'C7 scales into a system': (8,
            'the orbiting dot can be repositioned for variants, and the '
            'arc extends naturally into a banner'),
    },
    'M5 notch': {
        'C3 semantic fit (coin)': (3,
            'FAILS. A disc with a wedge cut out of its right side reads '
            'as Pac-Man, not as a coin. I confirmed this by looking at '
            'the render. The wedge is the dominant feature and it '
            'destroys the coin reading'),
        'C4 ownability / risk': (4,
            'strongly associated with an existing, extremely famous '
            'character; the association is a liability not an asset'),
        'C7 scales into a system': (6,
            'geometrically simple and crops well, but every variant '
            'still reads as Pac-Man'),
    },
    'M6 twin': {
        'C3 semantic fit (coin)': (4,
            'two light half-discs separated by a gap; without the coin '
            'context it reads as an abstract pair of shapes, or as a '
            'pill/capsule. The coin idea is not conveyed'),
        'C4 ownability / risk': (2,
            'HIGHEST RISK. Two side-by-side discs is structurally '
            'Mastercard, whose mark dates to 1966 and which is in active '
            'trademark litigation over it (EUIPO invalidated two '
            'registrations in 2019; the EU General Court annulled 12 '
            'Board of Appeal decisions in 2020). For a payments-adjacent '
            'crypto project this is the worst possible neighbour'),
        'C7 scales into a system': (7,
            'symmetric and crops cleanly, but the risk makes the system '
            'moot'),
    },
}

# Distinct radii actually used by each form, counted from marks.py
# source. Grasser's rule: more than five and some are redundant.
RADII_USED = {
    'M1 stack': 1,   # one rounded-rect corner radius, repeated 3x
    'M2 slot': 3,    # slot cap radius, coin radius, inner hole radius
    'M3 arc': 3,     # ring radius, ring stroke, inner disc radius
    'M4 orbit': 4,   # big disc, orbit radius, orbit stroke, small disc
    'M5 notch': 2,   # disc radius, accent radius
    'M6 twin': 2,    # disc radius, accent radius
}


def measure_all():
    BG = (16, 42, 74)
    INK = (238, 245, 252)
    ACC = (245, 186, 63)
    tb = json.load(open(os.path.join(HERE, 'topbrand_metrics.json')))
    import statistics as st

    def med(k):
        v = [x[k] for x in tb.values() if x.get(k) is not None]
        return st.median(v)

    med_ink, med_ed = med('ink_fraction'), med('edge_density')
    med_cp, med_th = med('components'), med('stroke_min_frac')

    out = {}
    for name, fn in MK.MARKS.items():
        big = fn(400, BG, INK, ACC)
        sil = MK.silhouette(fn, 256)
        mae = T.survives_small(fn, BG, INK, ACC)
        crs, mincr = T.boundary_contrasts(big)
        inkf = T.ink_fraction(sil)
        ed = T.edge_density(big)
        nparts, _ = T.components(sil)
        thin = T.stroke_min_frac(sil)

        # ---- C1 small-size survival (measured) ----
        # 16px structural error: 0.0 -> 10, 0.14 (the gate) -> 0
        c1_err = max(0.0, min(10.0, 10 * (1 - mae / 0.14)))
        # luminance edge: 3:1 (the WCAG floor) -> 5, 13:1 -> 10
        c1_cr = max(0.0, min(10.0, 5 + 5 * (mincr - 3.0) / 10.0))
        c1 = (c1_err + c1_cr) / 2

        # ---- C2 silhouette legibility (measured) ----
        # A silhouette is legible when it has clear internal structure:
        # enough ink to be seen, few enough parts to hold together, and
        # ink not so dominant that it is a featureless blob.
        # Score ink fraction by distance from the top-brand median.
        c2_ink = max(0.0, 10 - abs(inkf - med_ink) / med_ink * 10)
        c2_parts = 10.0 if nparts <= 2 else (7.0 if nparts == 3 else 4.0)
        c2 = (c2_ink + c2_parts) / 2

        # ---- C5 construction quality (measured) ----
        r = RADII_USED[name]
        c5 = 10.0 if r <= 2 else (8.5 if r == 3 else
                                  (7.0 if r == 4 else 4.0))

        # ---- C6 top-brand conformance (measured) ----
        def near(v, m):
            return max(0.0, 10 - abs(v - m) / m * 10)
        c6 = (near(inkf, med_ink) + near(ed, med_ed)
              + near(nparts, med_cp) + near(thin, med_th)) / 4

        out[name] = {
            'C1 small-size survival': round(c1, 2),
            'C2 silhouette legibility': round(c2, 2),
            'C5 construction quality': round(c5, 2),
            'C6 top-brand conformance': round(c6, 2),
            '_raw': {'mae16': round(mae, 4), 'min_cr': round(mincr, 2),
                     'ink': round(inkf, 4), 'edges': round(ed, 4),
                     'parts': nparts, 'thin': round(thin or 0, 4),
                     'radii': r},
        }
    return out


def main():
    print("=" * 100)
    print("MARK SELECTION SCORECARD - criteria and weights declared "
          "BEFORE scoring")
    print("=" * 100)
    tot = sum(WEIGHTS.values())
    for k, v in WEIGHTS.items():
        kind = '[J]' if k in ('C3 semantic fit (coin)',
                              'C4 ownability / risk',
                              'C7 scales into a system') else '[MEASURED]'
        print(f"  {v:3d}  {k:28s} {kind}")
    print(f"  {tot:3d}  TOTAL  (must be 100: {tot == 100})")
    assert tot == 100, 'weights must sum to 100'

    meas = measure_all()

    print()
    print("=" * 100)
    print("RAW MEASUREMENTS")
    print("=" * 100)
    print(f"  {'mark':12s} {'16px err':>9s} {'min cr':>8s} {'ink':>7s} "
          f"{'edges':>7s} {'parts':>6s} {'thin':>7s} {'radii':>6s}")
    print("  " + "-" * 82)
    for n, d in meas.items():
        r = d['_raw']
        print(f"  {n:12s} {r['mae16']:9.4f} {r['min_cr']:7.2f}:1 "
              f"{r['ink']:7.4f} {r['edges']:7.4f} {r['parts']:6d} "
              f"{r['thin']:7.4f} {r['radii']:6d}")

    print()
    print("=" * 100)
    print("SCORE MATRIX (0-10 per criterion)")
    print("=" * 100)
    crits = list(WEIGHTS)
    hdr = '  ' + f"{'mark':12s}" + ''.join(f"{c.split()[0]:>7s}"
                                           for c in crits) + f"{'TOTAL':>9s}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    results = []
    for n in meas:
        row = {}
        for c in crits:
            if c in meas[n]:
                row[c] = meas[n][c]
            else:
                row[c] = JUDGEMENTS[n][c][0]
        total = sum(row[c] * WEIGHTS[c] for c in crits) / 10.0
        results.append((total, n, row))
        print('  ' + f"{n:12s}"
              + ''.join(f"{row[c]:7.1f}" for c in crits)
              + f"{total:9.2f}")

    results.sort(reverse=True)

    print()
    print("=" * 100)
    print("RANKING")
    print("=" * 100)
    for i, (t, n, row) in enumerate(results, 1):
        print(f"  {i}. {n:12s} {t:6.2f}/100")

    win_t, win, win_row = results[0]
    runner_t, runner, _ = results[1]

    print()
    print("=" * 100)
    print(f"SELECTED: {win}   ({win_t:.2f}/100, "
          f"{win_t - runner_t:+.2f} over {runner})")
    print("=" * 100)
    print("  per-criterion reasoning for the winner:")
    for c in crits:
        if c in JUDGEMENTS[win]:
            sc, why = JUDGEMENTS[win][c]
            print(f"    {c:28s} {sc:4.1f}/10  [J] {why}")
        else:
            print(f"    {c:28s} {win_row[c]:4.1f}/10  [MEASURED]")

    print()
    print("  WHY THE OTHERS LOST - stated plainly:")
    for t, n, row in results[1:]:
        worst = min(JUDGEMENTS[n].items(), key=lambda kv: kv[1][0])
        print(f"    {n:12s} {t:6.2f}  weakest: {worst[0]} "
              f"= {worst[1][0]}/10")
        print(f"                   {worst[1][1]}")

    print()
    print("  SENSITIVITY CHECK - does the winner survive reweighting?")
    # if the judgement criteria were dropped entirely, who wins?
    m_only = [c for c in crits if c not in
              ('C3 semantic fit (coin)', 'C4 ownability / risk',
               'C7 scales into a system')]
    alt = []
    for t, n, row in results:
        s = sum(row[c] * WEIGHTS[c] for c in m_only) \
            / sum(WEIGHTS[c] for c in m_only) * 10
        alt.append((s, n))
    alt.sort(reverse=True)
    print(f"    measured criteria only ({', '.join(c.split()[0] for c in m_only)}):")
    for s, n in alt:
        print(f"      {n:12s} {s:6.2f}/100")
    print(f"    -> winner on measurements alone: {alt[0][1]}")
    if alt[0][1] != win:
        print(f"    -> DIFFERENT from the weighted winner {win}.")
        print(f"       That difference is carried entirely by the JUDGEMENT")
        print(f"       criteria (semantic fit, ownability, system). Those")
        print(f"       judgements are written out above so they can be")
        print(f"       challenged. I am not hiding that the choice depends")
        print(f"       on them.")
    else:
        print(f"    -> SAME winner with or without the judgements, which")
        print(f"       means the choice does not rest on my opinion.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
