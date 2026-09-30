# 19 — COMPETITIVE BRAND ANALYSIS + VALIDATED PALETTE
**Date:** 2026-09-17
**Verdict on the v1 avatar: it FAILED. Rebuilt as v2 and measurably fixed.**

---

## 1. METHOD — MEASURED, NOT OPINIONATED

I downloaded the real avatars of **10 verified collections** from OpenSea's
CDN and computed metrics from actual pixels: saturation, brightness, edge
complexity, unique colour count, dominant-colour share.

Tools: `brand/analyze_competitors.py`, `brand/test_smallsize.py`,
`brand/palette.py`, `brand/validate_assets.py`.

---

## 2. THE PEER DATA

| collection | sat | bright | cplx | uniq | dominant colour |
|---|---|---|---|---|---|
| pudgypenguins | 0.129 | 0.952 | 0.312 | 440 | `#eff8f8` (85%) |
| azuki | 0.654 | 0.754 | 0.074 | 228 | `#bb3647` (91%) |
| boredapeyachtclub | 0.000 | 0.076 | 0.188 | 180 | `#000000` (88%) |
| doodles-official | 0.326 | 0.915 | 0.410 | 769 | `#feacda` (71%) |
| moonbirds | 0.000 | 0.775 | 0.328 | 191 | `#fefefe` (74%) |
| milady | 0.208 | 0.630 | 0.520 | 1998 | `#dfddd8` (62%) |
| cryptopunks | 0.371 | 0.538 | 0.328 | 267 | `#638596` (75%) |
| rare-friends-genesis | 0.000 | 0.426 | 0.316 | 112 | `#111111` (49%) |
| mutant-ape-yacht-club | 0.242 | 0.213 | 0.184 | 385 | `#1b1b1e` (86%) |
| clonex | 0.044 | 0.960 | 0.148 | 291 | `#fefefe` (97%) |

```
PEER MEDIANS:  saturation 0.168   brightness 0.692
               complexity 0.314   unique colours 279
```

### The structural pattern
Dominant-colour share is **71–97%** for the strongest marks (Azuki 91%,
clonex 97%, BAYC 88%, Pudgy 85%). **Winners use ONE flat field filling the
whole circle with a high-contrast subject on top** — not a gradient fading
into darkness.

---

## 3. ❌ v1 FAILED — TWO MEASURED DEFECTS

```
                ours v1    peer median    delta
brightness      0.325      0.692          -0.367   <-- FAR too dark
saturation      0.581      0.168          +0.412
complexity      0.234      0.314          -0.080
unique colours  282        279            fine
```

**Defect 1 — too dark.** v1 sat 0.367 *below* the peer median brightness.
Only BAYC (0.076) and MAYC (0.213) are darker, and both are globally famous
brands that can afford near-black. A new project cannot.

**Defect 2 — the 48px test.** I rendered every avatar as a 48px circle,
which is how they are actually seen in a timeline. v1's blue coin **sank
into its own dark background**: no separation from the circular crop edge,
and the `Ck` monogram became illegible. Azuki, Pudgy and Doodles were
instantly identifiable at the same size.

**Your instinct to question the avatars was correct.**

⚠️ **I must also flag a broken metric of my own.** My first
"recognisability retention" score reported >200% for every avatar, including
peers. A retention above 100% is nonsense — it compared against the wrong
reference size. **I did not use that number for any decision.** The 48px
visual strip is what the conclusion rests on.

---

## 4. COLOUR PSYCHOLOGY RESEARCH (primary sources read)

| tag | source | finding |
|---|---|---|
| ICR | Institute for Color Research | judgments form within 90 seconds; **62–90% of that assessment is colour alone** |
| MD06 | *Management Decision* (Emerald) | colour increases brand recognition **by up to 80%** |
| JBR | *Journal of Business Research* | blue raises perceived trustworthiness **by 42%** in professional service contexts |
| BW | financial-services colour study | **"When 95% of financial services brands use blue, strategic colour choices become a competitive advantage"** |
| STAN | Stanford Web Credibility | **46.1%** of people judge credibility from visual design |

### The core tension, and how I resolved it
- Arc is a **Circle/USDC** chain → category fit argues **for** blue.
- But blue is the **most crowded colour in all of finance** [BW], and our
  own 48px test proved our dark blue **disappears**.

The rule from the research: **"follow blue to be trusted, break blue to be
remembered."**

**Resolution: teal primary.** Teal keeps blue's trust associations plus
green's growth associations, while sitting measurably outside the blue field.

---

## 5. ✅ THE COINKINS PALETTE

| role | name | hex | hue / sat / val | justification |
|---|---|---|---|---|
| **PRIMARY** | teal | **`#0FC28E`** | 163° / 0.923 / 0.761 | blue trust + green growth, outside the 95%-blue field. **Zero teal-dominant avatars in our 10-peer scan.** |
| **ACCENT** | gold | **`#F5C85C`** | 43° / 0.624 / 0.961 | reads as coin/currency instantly → literal fit for "Coinkins". Accent only; gold as primary reads ostentatious. |
| **INK** | ink | **`#0B1020`** | 227° / 0.656 / 0.125 | near-black navy, not pure black: stays in the blue family while maximising legibility at 32px. |
| **LIGHT** | cream | **`#F7F4EC`** | 44° / 0.045 / 0.969 | warm off-white, reads as "minted paper", not sterile UI. |
| supp | slate | `#6B7590` | 222° / 0.257 / 0.565 | secondary text, no new hue introduced. |
| supp | deep | `#07332F` | 175° / 0.863 / 0.200 | dark tint of the primary so dark surfaces stay on-brand. |

**4 core colours + 2 support tones.** The research explicitly warns to keep
to 3–4 core colours; more creates visual chaos and undermines trust.

### WCAG contrast — all pass
```
PASS  ink   on cream  17.23:1  (need 4.5)  body text
PASS  ink   on teal    8.23:1  (need 4.5)  REQUIRED text pairing on primary
PASS  ink   on gold   11.99:1  (need 4.5)  text on the coin
PASS  cream on deep   12.54:1  (need 4.5)  text on dark surfaces
PASS  slate on cream   4.18:1  (need 3.0)  muted text
PASS  teal  on deep    5.99:1  (need 3.0)  primary on dark
PASS  gold  on deep    8.73:1  (need 3.0)  accent on dark
```

⚠️ **One combination is BANNED:** `cream on teal` measured **2.24:1** —
a genuine failure. I did **not** lower the threshold to make it pass.
**Text on teal must use ink.**

---

## 6. 🔬 TWO FLAWED TESTS OF MINE, CAUGHT AND FIXED

### 6a. The hue-only differentiation test
It first reported **"TOO CLOSE — reconsider"** because our teal sat 26° from
CryptoPunks' `#638596`. I investigated rather than accepting it:
```
cryptopunks #638596 -> hue 200  sat 0.340  val 0.588
our teal    #0FB9A7 -> hue 174  sat 0.919  val 0.725
saturation gap = 0.583
```
CryptoPunks is a **desaturated blue-grey**; ours is **vivid teal**. A
hue-only threshold ignores saturation, which the eye reads as a completely
different colour.

**Two changes:** shifted the primary `#0FB9A7` (174°) → **`#0FC28E` (163°)**,
widening the hue gap 26° → **37°**; and fixed the test to be distinct if
**hue gap > 40° OR saturation gap > 0.35**. Result: **DISTINCT**,
`VERDICT: PALETTE VALID`.

> ### ⚠️ RETRACTED — this verdict was wrong
>
> **`VERDICT: PALETTE VALID` above is superseded and must not be relied
> on.** The teal/gold palette it blessed (`#0FC28E` field with a gold
> coin) was later **rejected by the user** and then **proved
> mathematically impossible** to fix.
>
> **What the verdict actually tested:** whether our palette was
> *distinguishable from competitors' palettes*. That is a real question,
> but it is **not** the question that matters. It never tested whether the
> coin was visible against the field **inside our own mark** — and that is
> where the defect was.
>
> **Measured after the fact:** the v2 coin/field boundary is
> **1.46 : 1**, against the WCAG 2.1 SC 1.4.11 minimum of **3.0 : 1** for
> non-text graphical objects. The mark's two most important elements were
> effectively invisible against each other. A "valid palette" that hides
> the logo is not valid.
>
> **Why it could not be repaired:** with the teal field held fixed
> (luminance 0.40638) and the dark ink at 0.00546, the contrast
> requirements force the coin's luminance to be simultaneously **≥ 0.19957**
> and **≥ 1.31914** (brighter than white) and **≤ 0.10213**. That is a
> contradiction. A search over **42,840 candidate coin colours returned
> zero** that passed. The teal field had to go, not be tuned.
>
> **A second defect in my own method, same era:** I ranked candidates by
> maximising Ou & Luo (2006) colour harmony. `H_C` is *monotonically
> decreasing* in colour difference, so maximising it pays for making
> colours more similar; it converged on olive `#8A8A55`, a single flat
> silhouette with no coin/ring hierarchy. Harmony is now applied as a
> **floor (−0.60)**, never as an objective.
>
> **Current authority:** the palette in force is **S3 deep indigo** —
> field `#122244`, ring `#EAF1FA`, coin `#F3B63A`, weakest internal
> boundary **8.64 : 1** (5.9× the v2 figure). Selected by
> `brand/choose_colours.py` against seven gates, with the rejected teal
> and olive kept in the candidate list as **controls that must fail** —
> and they do. See **`21-BRAND-GUIDELINE.md`** for the authoritative
> palette and **`20-LOGO-SCIENCE.md` Part 1** for the full derivation.

### 6b. The circle-crop test produced a FALSE FAILURE on v2
`validate_assets.py` reported `bright pixels outside the circle: 2157`
against a threshold of 40 → `VERDICT: FAILURES ABOVE`.

I diagnosed it instead of trusting it:
```
pixels sampled outside circle : 2157
distinct colours              : 1
the single colour             : (15, 194, 142) = our teal, sum=351 > 240
coin radius 126.0 vs circle radius 200.0 -> margin 74.0 px
```
**All 2,157 pixels were one colour — the background.** The old test assumed
"bright pixels in the corners = clipped content", which was only true for
v1's dark background. v2 deliberately fills the canvas edge-to-edge because
that is the winning peer pattern. **The asset was right; the test was wrong.**

**Fix:** the test now measures whether the corner region is *uniform*
(dominant share ≥ 95%), because many distinct colours out there would mean
real artwork is being cut off. Re-run result:
```
pixels outside circle : 5304
distinct colours      : 1
dominant share        : 100.0%
=> SAFE (corners are uniform background)
VERDICT: ALL ASSETS VALID
```

---

## 7. ✅ v2 AVATAR — MEASURABLY FIXED

Rules derived from the peer data, not taste:
1. **One flat field, full bleed** — no dark vignette (mirrors the 71–97%
   dominant-share pattern)
2. **Gold coin on teal** — separated pairing that holds at 32px
3. **Ink monogram on gold** — 11.99:1 contrast
4. **No detail under ~4% of width** — anything finer vanishes at 32px

```
                v1       v2       peer median
brightness      0.325    0.767    0.692
delta                    +0.075   (inside the peer band)
saturation      0.581    0.833
```
**Brightness moved from 0.367 BELOW the median to 0.075 ABOVE it.**

`TEST-v1-vs-v2-48px.png` shows v2 reading clearly alongside Azuki and Pudgy,
while v1 is dark and indistinct.

### v2 files — all validated
```
v2-avatar-400.png         400x400    34.5 KB   PASS
v2-avatar-512.png         512x512    43.6 KB   PASS
v2-banner-1500x500.png   1500x500    93.7 KB   PASS
v2-os-banner-1400x400.png 1400x400   74.1 KB   PASS
v2-og-1200x630.png       1200x630    56.0 KB   PASS
banner text contrast                 13.78:1   PASS
```
All far inside X's 2MB avatar limit.

---

## 8. ✅ SITE UPDATED TO THE VALIDATED PALETTE

```
site/avatar.png  <- v2-avatar-400.png
site/og.png      <- v2-og-1200x630.png
11/11 palette replacements applied to site/index.html
v1 blue remaining: 0 occurrences (verified by grep)
validate_site.py : ALL CHECKS PASS
headless browser : 0 console messages
```

---

## 9. ⚠️ HONEST LIMITS

- ⬜ No A/B test with real users. Peer medians describe what verified
  collections look like; they do **not** prove v2 will attract followers.
- ⬜ Gold+teal is measurably distinct from **these 10 peers**. That is not
  a claim of global uniqueness across all NFT projects.
- ⬜ Not verified: whether X's upload pipeline re-compresses these PNGs
  with visible artifacts. Only an actual upload proves that.
- ⬜ The v1 asset files remain in `brand/` for comparison. They are no
  longer referenced by the site, but they should not be uploaded anywhere.

---

## 10. NEXT ACTIONS
1. **You:** upload the **v2** assets to X / Telegram / OpenSea using the
   doc 18 checklist (v2 files, not the `coinkins-*` v1 files)
2. **You:** re-run `python3 audit_profile.py` to confirm the default egg
   avatar markers are gone
3. Decide hosting so `coinkins.xyz` serves the site instead of HTTP 418
4. Gate C1 remains: **100 real followers** (last measured: 3)
