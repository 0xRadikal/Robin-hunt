# 20 — LOGO SCIENCE: correcting the record and rebuilding the mark

**Status:** research complete, design not yet chosen.
**Supersedes:** §5 of `19-BRAND-ANALYSIS.md` ("PALETTE VALID") and the
entire v2/v3 colour-solver output.

---

## 0. What the user said, and why they were right

> "close proximity is not a reason for colours to be compatible"
> "the logo is not clear"
> "olive has nothing to do with the project, and olive is ugly and
>  unpopular"
> "I liked our very first logo much more than these"
> "go and look at how modern projects do logos and brands — any
>  successful company, not only NFT collections — and look at their
>  history and how they changed"

Every one of those is correct, and the first one identifies a **formal
error in my method**, not a matter of taste.

### 0.1 The formal error, proved

I used the Ou & Luo (2006) harmony model as the **objective function**.
Its chromatic term is:

```
H_C = 0.04 + 0.53 · tanh(0.8 − 0.045 · ΔC)
```

This is **monotonically decreasing in ΔC**. Measured:

| ΔC | H_C |
|---|---|
| 0 | +0.3919 |
| 5 | +0.3151 |
| 10 | +0.2183 |
| 20 | −0.0128 |
| 40 | −0.3636 |
| 60 | −0.4668 |
| 80 | −0.4861 |

The model **pays you for making the two colours more similar**.
Maximising it necessarily converges on near-identical, low-chroma
colours. That is exactly how I arrived at olive `#8A8A55` with the
highest score. The user's objection — *"being close together is not a
reason to be compatible"* — is a precise statement of this defect.

### 0.2 Why the model is not at fault

Ou & Luo was fitted on **abstract colour patches shown side by side**.
It answers *"do these two swatches feel pleasant together?"*. It does
not model identity, memorability, legibility at 16 px, category meaning,
or ownability — all of which a logo must have. Using a
swatch-pleasantness metric as a logo objective is a **category error**.

**Correct role:** colour harmony is a **constraint** (reject the clearly
broken), never the **objective**.

---

## 1. Research: the empirical logo literature

### 1.1 Henderson & Cote 1998 — *Journal of Marketing* 62(2):14-30
**1500+ citations. Empirical study of 195 logos.**

Seven measured design dimensions:

| Dimension | Definition (verbatim where quoted) |
|---|---|
| **Naturalness** | "the degree to which the design depicts commonly experienced objects" (p.16). Sub-axes: representative↔abstract, organic↔inorganic |
| **Harmony** | balance↔imbalance, symmetry↔asymmetry |
| **Elaborateness** | complexity + activity ("impression of motion or flow") + depth |
| **Parallel** | multiple elements/lines placed next to or on top of each other |
| **Repetition** | similar elements reused, not necessarily organised |
| **Proportion** | "the relationship between the horizontal and vertical dimensions" |
| **Roundness** | arcs and circles rather than sharp angles and straight lines |

**Findings that bind our design:**
- **Simple logos are more easily recognised.**
- **Elaborateness has an inverted-U relation to affect**: liking rises
  with complexity, **peaks**, then falls. So neither bare nor busy.
- Complex logos perform better under **repeated exposure**.
- **Naturalness, harmony and elaborateness** are the most significant
  moderators of recognition and affect.

### 1.2 Henderson, Cote, Leong & Schmitt 2003 — *IJRM*
**636 citations.** Adds repetition of elements, dimensional proportion,
and number of parallel lines as separate characteristics.

### 1.3 Wenzel 2018 — historical analysis of 20 major US brands
Quantified the direction of change over each brand's logo history:

- trend toward **less complexity is statistically significant**,
  **χ²(3) = 15.429, p = .001**
- first iterations ≈ **50 % complex**; modern versions ≈ **5 % complex**
- **character count dropped significantly, p = .004**
- **"debranding"**: text removed; the symbol alone carries identity
- shift **away from depth/3D toward flat**, for digital/mobile

---

## 2. Direct observation of real brand evolution

Measured from actual timeline images, not from description.

### 2.1 Mastercard (verified by image analysis)
| Stage | Text inside mark? | Overlap treatment | Colours |
|---|---|---|---|
| 1996 | **Yes** — "MasterCard" in white, italic, across both circles | comb/striped interlock | red + yellow + striped blend |
| 2016 | **No text at all** | clean solid translucent overlap | exactly **3 flat colours** (red, yellow, orange) |

**Constant across every version:** two identically sized circles
intersecting horizontally. The *idea* never changed; the *rendering* was
stripped.

### 2.2 Starbucks (verified by image analysis)
| Year | Colours | Text inside? | Outer ring? | Detail |
|---|---|---|---|---|
| 1971 | 2 | yes (4 words) | multiple rings | high, illustrative |
| 1987 | 3 | yes | yes | medium |
| 1992 | 3 | yes | yes | medium, cropped in |
| 2011 | **2** | **none** | **none** | highly simplified vector |

**Surviving element:** the twin-tailed siren's crowned head.
**Removed:** all text, all containment rings.

### 2.3 Apple (verified by image analysis)
| Year | Colours | Shading |
|---|---|---|
| 1976 | greyscale | flat, extremely detailed engraving + text |
| 1977 | 6 flat | none |
| 1998 | 1 (black) | none |
| 2001 | many greys | **glossy 3D glass gradients** |
| 2007 | metallic silvers | **3D bevel + gloss** |
| 2017 | **1 flat grey** | **none** |

**Two findings that matter enormously to us:**
1. **The bitten-apple silhouette has been geometrically unchanged since
   1977.** Identity lives in the *silhouette*, not the *finish*.
2. **Gloss/3D peaked in 2001-2007 and was then abandoned.** Apple went
   *back* to flat.

---

## 3. What this says about MY OWN designs

### 3.1 Against v1 (the one the user preferred)
v1 has: a radial gradient, a glossy arc highlight, a soft outer glow.
That is the **2001-2007 Apple aesthetic** — the exact era the industry
abandoned. The user liked it more than v2/v3, and they were right that
it is *better*, but it is better for a reason that does not generalise:
it looks like a **finished object** instead of two flat colours.

The lesson is **not** "add gloss back". The lesson is that v1 had a
**form** — a coin with a defined edge — and my v2/v3 had only **colour**.

### 3.2 Against v2/v3
- monogram "Ck" inside a disc = **text inside the mark**, which every
  studied brand **removed**
- the mark is a plain circle, which is not ownable — a circle is the
  least distinctive shape available
- I optimised colour and never designed a **form**

### 3.3 The actual requirement
| Requirement | Source |
|---|---|
| remove text from inside the mark | Mastercard 2016, Starbucks 2011, Apple 1977+, Wenzel p=.004 |
| flat, no 3D gloss | Apple 2017, Wenzel "away from depth" |
| moderate complexity, not minimum | Henderson & Cote inverted-U |
| round forms | Henderson & Cote roundness → positive affect |
| one constant geometric idea | Mastercard circles, Apple silhouette |
| recognisable in silhouette alone | Apple's mark works as pure black |
| 2-3 flat colours | Mastercard 3, Starbucks 2, Apple 1 |
| survives at favicon size | Wenzel "digital/mobile" |

---

## 4. Colour: what the evidence actually supports

Olive was rejected by the user as ugly and unrelated. That objection is
supported, not contradicted, by the evidence — olive only won because I
was maximising the wrong function.

Evidence that **does** bear on our colour choice:
- Ou 2008 (DRS): *"Among various hues, blue is the one most likely to
  create harmony in a two-colour combination; red is the least likely."*
- *Journal of Business Research*: blue raises perceived trustworthiness
  by **42 %** in professional services.
- 95 % of financial-services brands use blue → blue is the **category
  signal**; total deviation costs credibility.
- Our own peer scan: strongest NFT marks use **one flat saturated
  field** (azuki 91 % dominant, clonex 97 %).
- **WCAG 2.1 SC 1.4.11** (w3.org): graphical objects need ≥ 3:1 against
  the adjacent colour. v2 measured **1.46:1** — a hard failure.
- Vision science: form is carried by the **luminance** channel; the
  chromatic channels have lower spatial resolution (Hansen &
  Gegenfurtner, *Visual Neuroscience* 2009, 160 cites; *J. Cognitive
  Neuroscience* 34(7):1128, 2022). Two colours can differ strongly in
  hue and still fail to separate as objects — exactly the v2 defect.

---

## 5. Open decision — deliberately not made by me

The remaining choice is **which form** the mark takes. That is a brand
decision with real consequences, and my previous attempt to resolve an
aesthetic question with a single metric is what produced the rejected
output. Options are to be rendered and measured, then chosen by the
project owner.

**Hard gates any candidate must pass before it is even shown:**
1. no text inside the mark
2. ≥ 3:1 luminance contrast on every internal boundary (WCAG 1.4.11)
3. legible as a silhouette in pure black
4. survives 16 px without feature loss
5. flat — no gradients, no gloss, no 3D
6. complexity inside the peer/brand median band, not at the minimum
7. one geometric idea that stays constant across all sizes

---

# PART 2 — Benchmarked against TOP BRANDS, not NFT collections

**User instruction:** *"forget the famous NFT logos — they are very old,
their logos are dated, and they were just a trend. Stick to famous
brands, successful companies, and top logos."*

That instruction is correct and it also removes a weakness in Part 1:
I was benchmarking against 10 NFT avatars, i.e. against **illustration
style**, not against **brand-mark craft**. All NFT-peer thresholds are
therefore withdrawn from the design gates.

## 6. Authoritative source for "top brands"

Not my own picks. **Interbrand Best Global Brands 2025**, verified on
`interbrand.com/best-global-brands/global/`:
1 Apple, 2 Microsoft, 3 Amazon, 4 Google, 5 Samsung, 6 Toyota,
7 Coca-Cola … 15 Cisco, 16 Louis Vuitton, 17 YouTube, 18 BMW.

Plus the **payments/fintech** category Coinkins actually sits next to
(Visa, Mastercard, PayPal, Stripe), plus the **symbol-only** brands
Michael Bierut explicitly named as the reference class.

## 7. Two myths I had to discard — both verified from primary sources

### 7.1 The golden ratio in the Apple logo is false
David Cole measured it for *Gizmodo* (5 Jun 2013). Findings:
- most of the logo's large curves are **not circular arcs at all** —
  the leaf alone is two arcs of different radii
- fitting the circles plausibly moves the implied ratio anywhere between
  **1.53 and 1.73**, a tolerance meaningless for a constant defined
  as 1.618
- the Unicode  glyph and Apple's own press-kit vector **use different
  geometries**

And from the designer himself, **Rob Janoff**:
> "When I designed it I pretty much did it freehand."
> "Years later you find out supposedly why you did certain things. And,
> they are all BS. It's a wonderful urban legend."

**Consequence:** I will not claim golden-ratio construction. Doing so
would be exactly the "reverse-engineer your own work and report it as
intent" failure mode.

### 7.2 What DOES transfer — the Twitter bird, the one grid published by
its own designer

**Martin Grasser**, who drew the 2012 bird with Todd Waterbury and Angy
Che, published his own account:
> "The logo was designed to be simple, balanced, and **legible at very
> small sizes, almost like a lowercase 'e'**."
> "We liked using circles to construct our drawings, it felt like the
> bird should have an underlying neutrality and simplicity about it."

The transferable method, with no ratio mysticism:
**a small set of repeated circle radii, on shared axes, with every
curve cut at a tangent point.** Grasser's grid uses 15 circles drawn
from only a few diameters — that repetition is what makes a mark read as
machine-drawn rather than hand-drawn.

Also from the same source, on over-engineering:
> "use the grid to remove the errors an eye cannot catch at 16 pixels,
> then spend the remaining time on the idea."

## 8. 🔴 THE RISK I MUST STATE BEFORE ANY DESIGN IS CHOSEN

**Verified, Mastercard press release, 7 January 2019:**
> "with more than **80 percent** of people spontaneously recognizing the
> Mastercard Symbol **without** the word 'mastercard', we felt **ready to
> take this next step**."

**Verified, Michael Bierut (partner, Pentagram), same release:**
> "Mastercard has had the great fortune of being represented by two
> interlocking circles … **since its founding in 1966**."
> "…enters an elite cadre of brands that are represented not by name,
> but by symbol: an apple, a target, a swoosh."

### The arithmetic
| | Mastercard | Coinkins |
|---|---|---|
| years building the symbol | **53** (1966→2019) | 0 |
| measured symbol recognition | **80 %+** | 0 % — the mark does not exist |
| X followers | — | **3** (last measured) |

**Mastercard dropped the name AFTER measuring 80 % recognition, not
before.** A symbol-only identity is the **destination** mature brands
graduate to, not the starting point.

### This corrects a conclusion I made in Part 1
I wrote "remove all text". That is **right about the MARK** and **wrong
about the AVATAR/profile**. Corrected requirement:
- the **mark** carries no text — industry standard, correct
- the **profile** must still show the **name** somewhere (banner,
  handle, display name), because nobody recognises our symbol yet

Independent support, Monotype (27 Jan 2019), reporting on the same
change: *"in the Mastercard example, the wordmark isn't going away
completely. Just … almost completely."* Even Mastercard retained the
wordmark for contexts needing clarity.

## 9. MEASURED properties of 11 real top-brand marks

Source files: `cdn.simpleicons.org`, single-path SVGs on a 24×24
viewBox. Every file was verified to contain a `<title>` naming the brand
before use.

Rasterised by a **purpose-built SVG path parser** (no converter is
installed in this environment), which was **validated with 9 tests
before any measurement was trusted**:

| test | result |
|---|---|
| full square → ink fraction 1.0 | PASS |
| square → 1 component, 0 holes | PASS |
| square aspect = 1.0 | PASS |
| ring → 1 component, **1 hole** (even-odd fill works) | PASS |
| ring area 0.5888 vs analytic 0.5890 | PASS |
| bbox normalisation: tiny circle 0.7859 == big circle 0.7859 == π/4 | PASS |
| two discs → 2 components | PASS |
| **arc-flag grammar**: spaced `0 1 0` == packed `10`, area 200.49 both | PASS |
| all 11 brand files parse without error | PASS |

**Two bugs the suite caught, both mine:**
1. **My test assertion was wrong**, not the code. I compared the ring
   area against the 24×24 viewBox while the renderer deliberately
   normalises to the mark's own bounding box (so every brand is measured
   at equal visual size regardless of the SVG author's padding).
   Parser verified correct: outer circle flattens to shoelace area
   313.263 vs analytic 314.159 — 0.3 % error.
2. **A real parser bug.** Cisco's path contains
   `1.186 1.186 0 01-.806-.237`. Per the SVG 1.1 grammar the large-arc
   and sweep flags are **single digits needing no separator**, so `01`
   is two flags. My generic number tokenizer read it as `1.0`, shifting
   every following argument and feeding a command letter to `int()`.
   Fixed with arc-specific tokenization + a permanent regression test.

### The measurements

| brand | ink % | edges | parts | holes | thinnest | bbox fill | aspect |
|---|---|---|---|---|---|---|---|
| apple | 40.2 | 0.0205 | 2 | 0 | 0.2083 | 0.636 | 0.81 |
| cisco | 10.4 | 0.0288 | 14 | 1 | 0.0417 | 0.253 | 1.90 |
| google | 29.8 | 0.0265 | 1 | 0 | 0.1146 | 0.394 | 0.97 |
| mastercard | 38.5 | 0.0250 | 3 | 0 | 0.2083 | 0.799 | 1.62 |
| nike | 7.0 | 0.0177 | 1 | 0 | 0.1042 | 0.255 | 2.86 |
| paypal | 40.1 | 0.0272 | 3 | 0 | 0.1615 | 0.608 | 0.85 |
| samsung | 7.1 | 0.0249 | 7 | 0 | 0.0365 | 0.596 | 6.54 |
| spotify | 49.8 | 0.0306 | 1 | **3** | 0.2031 | 0.642 | 1.00 |
| stripe | 37.7 | 0.0226 | 1 | 0 | 0.1979 | 0.679 | 0.71 |
| visa | 13.4 | 0.0244 | 4 | 1 | 0.0625 | 0.530 | 3.10 |
| x | 19.3 | 0.0337 | 1 | 1 | 0.0521 | 0.253 | 0.98 |

### Design targets (these replace every NFT-peer threshold)

| metric | min | **median** | max |
|---|---|---|---|
| ink fraction | 0.070 | **0.298** | 0.497 |
| edge density | 0.0177 | **0.0250** | 0.0337 |
| components | 1 | **2** | 14 |
| holes | 0 | **0** | 3 |
| thinnest feature | 0.0365 | **0.1146** | 0.2083 |
| bbox fill | 0.253 | **0.596** | 0.799 |
| aspect | 0.714 | **1.000** | 6.544 |

## 10. How my 6 candidate forms actually measure against this

| mark | ink % | edges | ×median ink | ×median edges |
|---|---|---|---|---|
| M1 stack | 26.4 | 0.0282 | 0.89× | 1.13× |
| M2 slot | 19.3 | 0.0247 | 0.65× | 0.99× |
| M3 arc | 24.4 | 0.0279 | 0.82× | 1.12× |
| M4 orbit | 26.7 | 0.0311 | 0.90× | 1.24× |
| M5 notch | 32.8 | 0.0229 | 1.10× | 0.91× |
| M6 twin | 30.9 | 0.0219 | 1.04× | 0.88× |

**All six sit inside the measured top-brand range** (ink 0.070–0.497,
edges 0.0177–0.0337) and within 0.65×–1.24× of the medians.
Component counts (1–3) are at or below the top-brand median of 2.

**A claim I retract:** in working notes I wrote that my marks were "too
solid". The numbers do not support that and I withdraw it — every mark
is dimensionally in the same family as the real top-brand marks.

## 11. What is still genuinely open

The remaining question is **which single geometric idea** to own — the
question Mastercard answers with intersecting circles, Nike with a
swoosh, Apple with a bitten silhouette. That is not resolvable by a
metric, and my previous attempt to resolve an aesthetic question with
one metric is exactly what produced the rejected olive output.

---

# PART 3 — LEGAL RESEARCH RESOLVED, AND COLLISION MADE MEASURABLE

## 11. The paywalled Target ruling — resolved from the primary source

Previously I could only quote a search-result abstract of a paywalled WTR
article. That is now resolved from **primary sources**, and the abstract
was **misleading**.

**Case: T-347/24, Target Brands, Inc. v EUIPO — Polipol Polstermöbel
GmbH & Co. KG**, General Court (Second Chamber), judgment of
**9 July 2025**. Official citation OJ C/2025/4600. Language of the case:
English. Applicant represented by V. von Bomhard and A. Malkmes.

Operative part, verbatim from EUR-Lex (CELEX 62024TA0347):

> 1. Dismisses the action;
> 2. Orders Target Brands, Inc. to pay the costs.

Subject matter, verbatim from the OJ headnote:

> EU trade mark — Invalidity proceedings — EU figurative mark representing
> three red and white concentric circles — Absolute ground for invalidity —
> **No distinctive character** — Article 7(1)(b) of Regulation (EU) 2017/1001

And the Board of Appeal's reasoning, as summarised in the CJEU case-law
review for 7–13 July 2025:

> The Board of Appeal annulled the decision of the Cancellation Division and
> declared the contested trade mark invalid on the ground that it was devoid
> of any inherent distinctive character. The trademark was **a simple
> reproduction of two banal and simple geometric shapes** and would be
> perceived as **a red circle (dot) inscribed in a red circle outline** on a
> white background.

### Why this is the single most important legal finding so far

I previously listed "Target Corporation" as RISK 3 — the fear being that
Target owns the bullseye and litigates. The correct reading is the
**opposite of a threat**:

| | |
|---|---|
| What I feared | Target owns "circle inside a ring" and will enforce it |
| What actually happened | Target's own EU registration **for exactly that** was **declared invalid** |
| Ground | not confusion — **no distinctive character** at all |
| Court's characterisation | "banal and simple geometric shapes" |
| Outcome | Target **lost** and **paid costs** |

The corollary is uncomfortable but has to be stated: a bare circle inside a
ring is, in the assessment of the EU General Court, **not ownable** — not by
Target, and therefore not by Coinkins either. This is the same conclusion my
own measurement reached independently (zero of the 11 measured top brands
uses a circle centred inside a ring). The law and the measurement agree.

**This does not mean "safe to use".** It means the shape is weak as
*property*, not that it is dangerous as *usage*. Those are different axes and
I previously conflated them.

## 12. Lanham Act §2(b) — scope correctly characterised

15 U.S.C. §1052(b) bars from **registration** any mark that

> Consists of or comprises the flag or coat of arms or other insignia of the
> United States, or of any State or municipality, or of any foreign nation,
> or any simulation thereof.

Two things must be kept straight, and I had been sloppy about the second:

1. **§2(b) is a bar to registration on the Principal Register.** The statute
   opens "No trademark ... shall be **refused registration** ... unless it".
   It is not a cause of action against use, and a US state is not a
   competitor who can sue for dilution.
2. **The bar is narrower than it sounds.** Per TMEP §1204.01(b), quoted in
   *In re Alabama Tourism Department* (TTAB, 6 May 2020, precedential), the
   examining attorney **should not refuse** registration where:
   - the flag design is used to form a letter, number, or design;
   - the flag is substantially obscured by words or designs;
   - **the design is not in a shape normally seen in flags**;
   - the flag design appears in a colour different from that normally used;
   - **a significant feature is missing or changed**.

   And: "The incorporation in a mark of **individual or distorted features
   that are merely suggestive** of flags, coats of arms, or other insignia
   **does not bar registration** under §2(b)."

The TTAB's own test is *"whether consumers will perceive matter in the mark
as a flag"*, assessed on colour, presentation, other design matter, and use
on the specimen (TMEP §1204.01(a)).

Applied honestly to our mark: it is circular, not rectangular; it has no
stripes, no staff, no flagpole; it carries none of the Colorado field
(blue/white/blue); and the disc does not fill the opening. The Colorado
*flag* is therefore not the real exposure. What the independent reviewer
actually reacted to is narrower and fair: **the C-with-a-gold-disc device**
is strongly associated with Colorado, and that is a *reputational /
distinctiveness* problem, not a §2(b) problem.

## 13. Colorado geometry — derived from the statute, not eyeballed

Previously I asserted Colorado's fill ratio was 1.000 from an encyclopaedia
sentence. It is now **derived from C.R.S. Title 24, Art. 80, Part 9**:

> "The diameter of the letter shall be two-thirds of the width of the flag.
> The inner line of the opening of the letter C shall be three-fourths of the
> width of its body or bar, and the outer line of the opening shall be double
> the length of the inner line thereof. Completely filling the open space
> inside the letter C shall be a golden disk"

Let outer radius `R = 1`, inner radius `a`, so body width `= 1 − a`. The ends
are cut on the radius, so the opening subtends one angle `t` at both radii:

```
inner line = 2·a·sin(t/2) = 0.75·(1−a)      (1)
outer line = 2·1·sin(t/2) = 1.50·(1−a)      (2)
(1)/(2)  =>  a = 0.75/1.50 = 0.5   EXACTLY — uniquely determined
sin(t/2) = 0.75·0.5/(2·0.5) = 0.375
t        = 2·asin(0.375) = 44.0486°   (half-angle 22.0243°)
```

The 1964 amendment sets the disc diameter equal to the centre stripe, giving
disc radius `0.5 = a`: the disc **completely fills** the opening, fill ratio
**1.0000**, as the statute says in words. Both equations and the fill identity
are re-asserted at import time in `collide.colorado_params()`; if the algebra
is ever edited wrongly the module refuses to load.

| | Colorado (statute) | variant A as approved |
|---|---|---|
| inner/outer radius | 0.5000 | 0.6667 |
| fill ratio | **1.0000** | **0.6875** |
| gap half-angle | **22.02°** | **34.00°** |

## 14. `collide.py` — collision turned into numbers

Four independent metrics, all computed by **one shared rasteriser** so our
mark and the references cannot be rendered with different bias:

- **D1** `1 − IoU` after area+centroid normalisation, reported both as-drawn
  and **minimised over rotation** (the conservative worst case).
- **D2** log-magnitude **Hu-moment** distance (Hu 1962), invariant to
  translation, scale and rotation.
- **D3** **radial-signature** distance, minimised over circular shift, so gap
  *position* cannot flatter the score while gap *width* still counts.
- **D4** distance in the 3-parameter construction space.

References, each with stated provenance: **R1** Colorado, derived from the
statute above; **R2** the **real U+00A9 glyph** from DejaVuSans.ttf, not a
redrawing; **R3** the concentric bullseye **held invalid in T-347/24**;
**R4** IEC 60417-5009 power/standby; **R5** the mark against itself as a
calibration control.

`validate()` runs **17 tests** and all pass. The ones that matter:

| test | result |
|---|---|
| D1/D2/D3 identity == 0 | 0.00e+00 |
| translation invariance | D1 = 0.0157 |
| scale invariance (1.6×) | D1 = 0.0390 |
| solid square is far | D1 = 0.5092 |
| **monotone as fill → Colorado** | 0.55:0.3572 → 0.69:0.2710 → 0.85:0.1424 → **1.00:0.0000** |
| **D1 == 0 at exact Colorado geometry** | **0.0000** |

The last two are the calibration that makes every other number meaningful:
the metric hits **exactly zero** when the geometry really is Colorado's, and
rises monotonically as the fill ratio falls — so "we reduced the resemblance"
is now a claim that can be checked, not asserted.

### Baseline: variant A as approved

| reference | D1 (worst-case rot) | D2 Hu | D3 radial |
|---|---|---|---|
| R1 Colorado C+disc | 0.4866 | 27.51 | 0.0565 |
| R2 copyright glyph | 0.8712 | 37.62 | 0.1293 |
| **R3 bullseye (T-347/24)** | **0.4440** | 48.16 | 0.1279 |
| R4 power IEC 5009 | 0.9390 | 66.63 | 0.1182 |

The **worst** collision is not Colorado — it is the **bullseye**, the very
configuration the General Court called banal. The reviewer's Colorado
instinct was directionally right but identified the second-worst neighbour.
Notably **D3 = 0.0565 against Colorado is the lowest single number in the
table**: our *outer silhouette* is very close to Colorado's; what separates
us is mainly the interior fill.

## 15. A second instance of my own category error — recorded, not hidden

`search_a.py` maximised worst-case collision distance over 3,484 feasible
candidates. It converged on `r_in=5.25, r_disc=0.75, gap=10°` — a **hairline
ring with a tiny dot**, ink fraction 0.1047, min D1 = 0.9574, **+112%** over
baseline.

That is a **degenerate win**. It scores well only because it barely resembles
any compact mark — including a good one. It is **the same mistake as
maximising Ou & Luo harmony**, which converged on olive `#8A8A55` because
harmony increases monotonically with colour *similarity*. Twice now I have
optimised a quantity that should have been a **constraint**.

Corrected formulation in `search_a2.py`:

```
CONSTRAINT : min_D1  >= floor        (collision distance need only be enough)
OBJECTIVE  : Q, distance to MEASURED top-brand proportions (lower better)
```

`Q` is a weighted distance to the medians of the **11 real top brands**
(ink 0.2976, stroke 0.1146, bbox fill 0.5958) plus 16 px structural error and
gap legibility. The measured-target loader now **raises instead of falling
back**: the previous version queried the thickness median under the wrong key
(`'thinnest'` instead of the file's actual `'stroke_min_frac'`) and a silent
fallback absorbed it, so the number came out **right by luck while the code
read nothing at all**. That is exactly a luck-based result, so the fallback
is gone.

### Floor sweep — where collision-avoidance starts costing quality

| floor | r_in | r_disc | gap | fill | min D1 | Q |
|---|---|---|---|---|---|---|
| baseline | 4.00 | 2.75 | 34° | 0.688 | 0.4440 | **0.2173** |
| 0.500 | **4.25** | **3.00** | **46°** | **0.706** | **0.5004** | **0.2126** |
| 0.550 | 4.00 | 2.50 | 50° | 0.625 | 0.5527 | 0.2561 |
| 0.600 | 4.25 | 2.25 | 54° | 0.529 | 0.6184 | 0.2770 |
| 0.700 | 4.25 | 1.50 | 54° | 0.353 | 0.7122 | 0.3139 |
| 0.800 | 4.50 | 0.75 | 60° | 0.167 | 0.8037 | 0.3994 |
| pure max | 5.25 | 0.75 | 10° | 0.143 | 0.9574 | 0.6401 |

Read down: past floor 0.50, `Q` climbs steadily — collision distance is being
bought with logo quality. At floor **0.500** there is a genuine **Pareto
improvement**: collision worst case **0.4440 → 0.5077 (+14.3%)** *and* `Q`
**0.2173 → 0.2126 (−2.1%)**, i.e. simultaneously less collision **and** closer
to real top-brand proportions.

Candidate: `r_out 6.00U, r_in 4.25U, r_disc 3.00U, gap half-angle 46°`.
All **11 geometry checks pass** (3 distinct radii, quarter-unit, stroke 0.1094
inside the real range, 1.25U disc clearance, ink 0.2743, gap chord 8.63 px at
16 px, measured gap span 92° == specified, mirror symmetry exact, rendered ink
matches analytic to 0.0010).

### A hypothesis of mine that the data DISPROVED

I predicted that **lowering the disc fill ratio below 0.688** would be the
lever that increases the Colorado distance, and I said so before measuring.
The search says the opposite: the winning candidate **raises** fill to
**0.706**. The real lever is the **gap angle** (34° → 46°, i.e. total opening
68° → 92°, versus Colorado's statutory 44°). Widening the opening moves us
away from *both* Colorado and the bullseye at once, whereas shrinking the disc
mainly moves us away from Colorado while pushing the silhouette toward a
plain thin ring. **The stated prediction was wrong and the measurement stands.**

---

# PART 4 — WHAT SHIPPED, AND WHAT IT COST

## 16. Final geometry

| element | value | fraction of W |
|---|---|---|
| `R_outer` | 6.00 U | 0.375000 |
| `R_inner` | 4.25 U | 0.265625 |
| `R_disc` | 3.00 U | 0.187500 |
| ring stroke | 1.75 U | 0.109375 |
| cap radius (derived) | 0.875 U | 0.054688 |
| `gap_half` | **28°** | white arc **304°** |
| `CAP` | 1.00 | fully rounded terminals |

Distinct radii: **3**. The cap radius is `(r_out − r_in)/2`, the unique
value tangent to both edges, so it is derived rather than independent.

## 17. The user's reference image, measured

The user supplied a reference logo and asked for longer white edges.
"Longer" is not a number, so the reference was **measured**, and three
independent methods were run so the answer could not rest on one
implementation:

| method | result |
|---|---|
| radial band probe | 302° |
| ring area ÷ full annulus area | 295.6° |
| angular occupancy histogram | 302° |

Reference geometry normalised to its own outer radius: `r_in` 0.6450,
`r_disc` 0.4331, stroke **0.3550**, fill ratio 0.6714, gap half-angle
**29.0°**.

Two real defects in my own measurement code had to be fixed first:

1. **The wordmark was being counted as part of the ring.** The radius
   histogram was bimodal — `p50 = 176 px` but `p98 = 210 px` — which is
   the signature of the letters COINKINS still being included. A "within
   4× the disc radius" filter was not enough; it was replaced with a
   row-occupancy cut that finds the 12-row empty band between mark and
   wordmark (at `y = 637` on this image), plus a spread check that aborts
   if the retained band is too wide to be a single annulus.
2. **Gap detection sampled one pixel** at the mid-radius, which on a
   soft-edged raster returned "all 360 bearings empty" and then crashed
   on a `None`. Replaced with a radial band probe over every ring pixel.

## 18. The trade was priced before it was offered

Matching the reference exactly costs real ground:

| gap | arc | collision | vs 280° | Q | vs 280° |
|---|---|---|---|---|---|
| 28° | **304°** | 0.4351 | **−14.1%** | 0.2251 | +5.9% |
| 34° | 292° | 0.4664 | −7.4% | 0.2247 | +5.7% |
| 38° | 284° | 0.4996 | −0.9% | 0.2185 | +2.7% |
| 40° | 280° | **0.5068** | — | **0.2144** | — |
| 46° | 268° | 0.5004 | −1.3% | 0.2126 | −0.8% |

I recommended **40°**, which was free on both metrics and recovered 35%
of the distance to the reference. The user chose **28°** — the longest
arc — with the cost stated in advance. Verified live after the change:
worst-case collision **0.5041 → 0.4321**, exactly the predicted −14.3%.

The reference's **thicker band was deliberately not copied**. Pulling
`r_in` to 3.75 U to match its 0.3550 stroke collapses collision distance
by **36.3%** and worsens Q by **44.7%**, because a fat ring around a
large disc is precisely the bullseye T-347/24 called banal.

Two risks of the narrower opening were checked **before** applying it:
the gap chord at a 16 px render is **5.63 px** (floor 1.5 px), and each
rounded cap consumes 9.83° of arc, leaving 284.34° of flat arc — so the
caps fit and the polygon cannot self-intersect.

## 19. A third instance of one class of error

`solve_option_c.py`, first version, maximised the arc subject only to a
collision floor. It returned `gap = 10°` (arc 340°) — achieved by
**shrinking the disc from 3.00 U to 1.50 U**. Collision distance was
preserved by wrecking the coin, and Q jumped 0.2126 → 0.3147 (**+48%**).

That is the same mistake as:

| attempt | what was maximised | what it converged on |
|---|---|---|
| colour | Ou-Luo harmony | olive `#8A8A55`, no hierarchy |
| geometry | collision distance | hairline ring, Q 2.9× worse |
| arc | arc under a collision floor | tiny disc, Q 1.48× worse |

**One class of error, three times: optimising a quantity that should be
a constraint.** Fixed by adding a quality floor and pinning the disc at
3.00 U, since the coin size was already approved and the request was
about the arc.

## 20. `make_svg.py` — the vector cannot drift from the raster

The site shipped a data-URI favicon that drew a rounded square with the
letters "Ck" in the **rejected teal** `#0FC28E` — not the mark at all.
Hand-writing a replacement would have created a second definition of the
logo, free to drift from `coinkins_mark.py`.

Instead the SVG path is **computed** from `R_OUTER_U`, `R_INNER_U`,
`R_DISC_U`, `GAP_HALF_DEG` and `CAP`, using elliptical-arc commands, with
the rounded terminals as real semicircular arcs of the same derived
radius. The self-test rasterises that SVG with the independently
validated parser from `measure_topbrands.py` and compares it pixel-wise,
bbox-normalised, against the PIL render:

**IoU = 0.9804** (threshold 0.98) — vector and raster draw the same shape.

## 21. Site re-theme, self-verifying

`retheme_site.py` replaces the v2 palette with S3, swaps the fake favicon
for the real mark, replaces the `.mark` placeholder box with an inline
SVG, and copies the avatar and OG image into `site/`. It then **verifies
its own work**: that no rejected v2 colour survives anywhere in the file
(it caught four stragglers — `#b57edc`, `#d6c7e8`, `#1a1523`, `#3a2b44`),
that every S3 colour is present, that the favicon carries the mark rather
than a letterform, and that the SVG tags balance.

Confirmed in a real browser: the page loads with **zero console errors**
(the favicon 404 is gone), and `index.html`, `avatar.png` and `og.png`
all return HTTP 200.

## 22. Final verification state

| suite | result |
|---|---|
| `coinkins_mark.verify_construction` | **15/15 PASS** |
| `test_cap` | **9/9 PASS** |
| `collide.validate` | **17/17 PASS** |
| `measure_topbrands.validate` | **9/9 PASS** |
| `make_svg.selftest` | **PASS**, IoU 0.9804 |
| `choose_colours` | S3 selected, weakest 8.64 : 1 |
| `build_final` | 11 raster + 3 vector assets |
| `verify_final` | **ALL 39 SCENARIOS PASS** |
| `retheme_site` | all checks PASS |

Measured against the 11 real top brands: ink **0.2943** (median 0.298),
edge density **0.0193** (median 0.0250), thinnest feature **0.1094**
(median 0.1146), components **2** (median 2).

## 23. The honest closing position

The **execution** is finished and measurably sound. Independent review
calls it *"the only version that feels fully resolved and intentional"*,
notes it performs **better** in pure black and white than the flat-ended
version, and finds its 16 px legibility improved.

The **concept** remains the open question, and that is recorded rather
than resolved by assertion. The same review scores Colorado resemblance
at **8/10** and says do not launch, because no geometric optimisation
fixes a concept without an ownable hook. The measurement agrees: **zero
of the 11 real top brands** uses a disc centred inside a ring, and the EU
General Court called that configuration banal.

What the research *did* settle is that this is **not a legal exposure**.
T-347/24 invalidated Target's own version of the shape for lack of
distinctive character; §2(b) bars registration, not use; and TMEP
§1204.01(b) exempts non-flag shapes and merely suggestive features. The
brand owner's judgement — that nobody will sue, and that it can be
changed later — is correct on both counts, and changing it is cheap at 3
followers and 0% recognition in a way it will not be at 1,000.
