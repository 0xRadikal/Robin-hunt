# Coinkins — Brand Guideline

**Status:** FINAL for launch. Reversible; see §9.
**Single source of truth:** `brand/coinkins_mark.py`. Every number below
was read out of those constants or measured from a render — none was
typed in by hand.

---

## 1. The mark

An open ring with a gold coin suspended at its centre. The opening sits
on the **right**, giving the mark a reading direction so it is not merely
rotationally symmetric. A fully closed ring around a dot is a loading
spinner; the opening is what makes it ours.

### 1.1 Construction

Every dimension is a multiple of one base unit **U = W / 16**, where W is
the width of the mark's square box. There are no arbitrary numbers: the
whole mark can be rebuilt from a single value.

| element | in U | as a fraction of W |
|---|---|---|
| outer radius `R_outer` | 6.00 U | 0.375000 |
| inner radius `R_inner` | 4.25 U | 0.265625 |
| coin radius `R_disc` | 3.00 U | 0.187500 |
| ring stroke | 1.75 U | 0.109375 |
| terminal cap radius | 0.875 U | 0.054688 |
| void between coin and ring | 1.25 U | 0.078125 |
| mark diameter | 12.00 U | 0.750000 |

**Opening:** half-angle **28°**, centred on 0° (screen right).
**White arc = 304°.**

**Distinct radii: 3.** Martin Grasser, who drew the Twitter bird, gave the
working rule: *"If the answer is more than five, some of them are doing
the same job."* The terminal cap radius is **derived** — exactly half the
stroke width, the unique value tangent to both the outer and the inner
edge — so it adds no independent number to the construction.

### 1.2 Terminals

Both ends of the ring are **fully rounded** (semicircular). Tested, not
assumed:

- A corner detector was calibrated on synthetic square-ended and
  round-ended controls (5 and 0 corners respectively) **before** being
  pointed at anything real.
- Measured across 11 real top-brand marks, **8 of 11 have more than four
  sharp corners**. Rounded terminals are *not* the industry norm; this is
  a deliberate style choice, not a claim about convention.
- A sweep proved **partial** rounding is worse than either extreme — it
  raises the corner count from 4 to **8**. Only full rounding removes
  them. So the cap fraction is 1.0 or nothing.

### 1.3 What the mark deliberately does not have

- **No gradient, gloss, bevel or shadow.** Apple used glossy 3D from 2001
  to 2007 and had abandoned it by 2017. Wenzel (2018) measured the
  industry-wide shift from depth toward flat across 20 major US brands,
  significant at χ²(3) = 15.429, p = .001.
- **No text inside the mark.** Mastercard removed its wordmark in 2019,
  Starbucks in 2011, Apple in 1977; Wenzel measured the character-count
  drop at p = .004.
- **But the profile must still carry the name.** Mastercard only dropped
  its wordmark after measuring *"more than 80 percent of people
  spontaneously recognizing the Mastercard Symbol"* — equity built over
  **53 years**. Coinkins has none of that, so the name lives in the
  banner, the handle and the lockup, never inside the mark.

---

## 2. Colour

Scheme **S3 "deep indigo"**, selected by `brand/choose_colours.py`
against seven gates.

| role | hex | RGB | use |
|---|---|---|---|
| field | `#122244` | 18, 34, 68 | the mark's background |
| ring | `#EAF1FA` | 234, 241, 250 | the open ring |
| coin | `#F3B63A` | 243, 182, 58 | the disc |
| page background | `#0C172E` | 12, 23, 46 | one shade below the field |
| muted text | `#96AAC4` | 150, 170, 196 | secondary copy |
| hairline | `#1E3358` | 30, 51, 88 | borders, dividers |

### 2.1 Measured contrast

| boundary | ratio | requirement |
|---|---|---|
| ring vs field | **13.80 : 1** | WCAG 1.4.11 needs 3.0 |
| coin vs field | **8.64 : 1** | WCAG 1.4.11 needs 3.0 |
| weakest boundary in the mark | **8.64 : 1** | — |

The coin and the ring **never touch**: a 1.25 U void separates them. This
is structural, not decorative. An earlier version placed gold directly
against light ink and measured **1.63 : 1** — effectively invisible. The
adjacency is now detected from the actual render, never assumed.

### 2.2 On light surfaces

On white the coin becomes **`#A67C28`** (3.79 : 1) and the ring becomes
the field colour `#122244` (15.70 : 1).

The first attempt at this substitution searched for the lightest gold
clearing the threshold and walked the hue to **72° — olive**, the exact
colour already rejected. The correct fix holds hue (40.2°) and saturation
(0.761) **identical** to the dark-theme coin and lowers only the value.

### 2.3 Colour-vision deficiency

Simulated with the Machado, Oliveira & Fernandes (2009) matrices at
severity 1.0:

| condition | ring vs field | coin vs field |
|---|---|---|
| protanopia | 13.39 : 1 | 7.51 : 1 |
| deuteranopia | 14.05 : 1 | 9.33 : 1 |
| tritanopia | 13.48 : 1 | 8.06 : 1 |

Every boundary stays above 3 : 1 under every condition. This holds
because **form is carried by the luminance channel** — the chromatic
channels have lower spatial resolution, so a mark depending on hue alone
degrades.

### 2.4 Why harmony is a floor, never a target

Ou & Luo (2006) colour harmony `H_C` is **monotonically decreasing** in
colour difference:

| ΔC | H_C |
|---|---|
| 0 | +0.3919 |
| 20 | −0.0128 |
| 80 | −0.4861 |

Maximising it therefore *pays for making colours more similar*. An early
run did exactly that and converged on olive `#8A8A55` — one flat
silhouette with no coin/ring hierarchy at all. Harmony is now a
**constraint with a floor of −0.60** (published range [−1.24, +1.39]).
S3 measures **−0.368**.

---

## 3. Clear space and minimum size

- **Clear space:** at least **1 U** (W/16, i.e. 6.25% of the mark's width)
  on every side, measured from the outer radius. Nothing may enter it —
  no text, no border, no other mark.
- **Minimum size: 16 px.** Verified, not asserted: at 16 px the structural
  error against a downscaled 400 px render is **0.0677**, the gap chord is
  **5.63 px** (readability floor is 1.5 px), and the coin still occupies
  26 pixels inside a 6 × 6 box.
- In a **circular crop** (X, Telegram, Discord) the outer radius is 0.375
  of the width, well inside the 0.5 crop boundary, and all four corners
  are 100% uniform field colour.

---

## 4. Asset inventory

`brand/final/` — rebuild with `python3 brand/build_final.py`.

| file | size | use |
|---|---|---|
| `avatar-400.png` | 400×400 | X / Telegram profile |
| `avatar-512.png` | 512×512 | OpenSea, Discord |
| `favicon-32.png` | 32×32 | browser tab |
| `favicon-16.png` | 16×16 | browser tab, smallest |
| `banner-1500x500.png` | 1500×500 | X header |
| `os-banner-1400x400.png` | 1400×400 | OpenSea banner |
| `og-1200x630.png` | 1200×630 | link previews |
| `mark-silhouette-512.png` | 512×512 | black on white |
| `mark-mono-light-512.png` | 512×512 | white on black |
| `mark-transparent-512.png` | 512×512 | overlay on any field |
| `mark-onwhite-512.png` | 512×512 | documents, print |
| `mark.svg` | vector | scalable, any size |
| `mark-onwhite.svg` | vector | light surfaces |
| `mark-transparent.svg` | vector | overlays |

The SVG files are **computed from the same constants** as the PNGs by
`brand/make_svg.py`, whose self-test rasterises the vector with an
independently validated parser and compares it pixel-wise to the raster:
**IoU 0.9804**. They cannot silently drift apart.

### 4.1 Banner safe zone

X pastes the avatar over the banner at **x = [33, 231], y = [401, 500]**.
That region of `banner-1500x500.png` is **100% uniform field colour**, so
nothing important is ever covered. The mark sits at x = 0.795·W.

---

## 5. Do

- Use the supplied files. Do not redraw the mark.
- Keep the opening on the **right**.
- Keep at least 1 U of clear space.
- On dark surfaces use the ring `#EAF1FA`; on light surfaces use
  `mark-onwhite`.
- Pair the mark with the wordmark wherever recognition matters — which,
  at present, is everywhere.

## 6. Do not

- **Do not rotate.** The opening's position is the only asymmetry the mark
  has, and asymmetry is what makes it memorable rather than generic.
- Do not add a gradient, gloss, bevel, shadow or outline.
- Do not place text inside the ring.
- Do not recolour the coin outside hue 40.2°; walking the hue up lands on
  olive, which has already been rejected once.
- Do not let the coin touch the ring.
- Do not stretch. Aspect ratio is 1 : 1.
- Do not use below 16 px.

---

## 7. Provenance of every threshold

No number here was invented. The design targets are the **measured
medians of 11 real top-brand marks** (Apple, Cisco, Google, Mastercard,
Nike, PayPal, Samsung, Spotify, Stripe, Visa, X), each SVG verified by
its own `<title>` before use and parsed by a purpose-built parser that
passed 9 validation tests **before** its output was trusted.

| metric | min | median | max | ours |
|---|---|---|---|---|
| ink fraction | 0.070 | 0.298 | 0.497 | **0.2943** |
| edge density | 0.0177 | 0.0250 | 0.0337 | **0.0193** |
| thinnest feature | 0.0365 | 0.1146 | 0.2083 | **0.1094** |
| components | 1 | 2 | 14 | **2** |

---

## 8. Known weakness, stated plainly

Independent visual review rates the **execution** highly — *"the only
version that feels fully resolved and intentional"*, better in pure black
and white than the flat-ended version, and more legible at 16 px.

The same review scores the **Colorado state flag resemblance at 8/10**
and would not launch the concept. That criticism is correct and is not
hidden here:

- Colorado's emblem is a circular C with a golden disc inside. Ours is a
  circular ring with a gold disc inside.
- Measured worst-case collision distance is **0.4321**, and the opening is
  only **5.98°** away from Colorado's statutory 22.02°.
- **Zero of the 11 measured top brands** uses a disc centred inside a
  ring.
- The EU General Court called that configuration *"banal and simple
  geometric shapes"* in T-347/24 (9 July 2025).

The 304° arc was chosen by the brand owner over a measurably safer 280°
option. The trade was priced first: collision distance 0.5041 → 0.4321
(−14.3%) and quality distance Q 0.2126 → 0.2251 (+5.9%). It is an
aesthetic decision taken with the cost known.

### 8.1 Why this is not a legal problem

- **T-347/24, Target Brands v EUIPO** (General Court, 9 July 2025, OJ
  C/2025/4600): Target's **own** concentric-circles mark was **declared
  invalid** for lack of distinctive character, and Target paid costs. The
  configuration is not ownable by anyone — including us, but equally
  including everyone else.
- **Lanham Act §2(b) / 15 U.S.C. §1052(b)** bars **registration**, not
  use. A US state is not a commercial competitor and cannot sue for
  dilution.
- **TMEP §1204.01(b)** exempts designs that are not flag-shaped, that
  change a significant feature, or that are *"merely suggestive"* of a
  flag. Our mark is circular, has no stripes, no staff, no flagpole, none
  of the Colorado field, and its disc does not fill the opening.

The residual risk is **commercial distinctiveness**, not litigation:
whether a viewer reads the mark as *Coinkins* or as *the Colorado flag*.

---

## 9. Reversibility

This decision is **cheap to reverse now** and expensive later.

| | now | after traction |
|---|---|---|
| X followers | 3 | — |
| symbol recognition | 0% | — |
| published assets | none | many |
| cost to change | ≈ nothing | high |

Mastercard needed **53 years** and 80%+ spontaneous recognition before it
could rely on its symbol alone. Until Coinkins has measurable
recognition, the mark can be replaced at will, and the tooling makes it
cheap: change the constants in `coinkins_mark.py`, then re-run the
pipeline in §10.

---

## 10. Rebuild and verify

```bash
cd brand
python3 coinkins_mark.py      # 15 construction checks
python3 test_cap.py           #  9 terminal-geometry checks
python3 collide.py            # 17 metric-validation tests + collision
python3 choose_colours.py     # re-select the palette against 7 gates
python3 build_final.py        # 11 raster assets
python3 make_svg.py           #  3 vector assets + vector/raster IoU
python3 verify_final.py       # 39 scenarios across 9 groups
python3 retheme_site.py       # re-theme the site, self-verifying
python3 show_final.py         # comparison sheet + X profile mock
```

All of the above currently pass.
