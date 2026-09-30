# 18 — PROFILE SETUP PACK (do this BEFORE any post)
**Date:** 2026-09-17
**You are right:** posting with an empty profile burns the one first impression.

---

## 1. AUDIT — WHAT WAS ACTUALLY MISSING (measured, not assumed)

I parsed the live pages rather than guessing.

### X `@coinkins` — profile is genuinely EMPTY, confirmed
```
og:image        https://abs.twimg.com/sticky/default_profile_images/
                default_profile_200x200.png     <- X's DEFAULT egg avatar
default avatar markers present   True
profile_images found             0              <- no avatar uploaded
profile_banners found            0              <- no banner uploaded
og:description  '3 followers · 18 following. Joined Sep 2026...'
bio is EMPTY (og:desc is only stats)   True
```
✅ Your assessment was exactly correct. Also note: **followers grew 1 → 3.**

### Telegram `t.me/coinkins`
```
og:title        'coinkins'
og:description  'Telegram: t.me/coinkins'   <- generic placeholder
og:image        data:image/svg+xml...       <- auto letter-avatar "C",
                                               NOT a real uploaded photo
subscribers     1 subscriber
```
**Needs: real photo + a description.**

### OpenSea `/coinkins`
```
title           'Coinkins - Profile | OpenSea'
og:image        opensea.io/Coinkins/opengraph-image   (auto-generated)
og:description  generic boilerplate
```
**Needs: avatar, banner, bio.**

### Domain `coinkins.xyz` — DNS is now live
```
DNS   resolves -> 34.42.100.71      (was NXDOMAIN; propagation completed)
HTTPS 200 but HTTP 418, body size 0  <- serving NOTHING
```
⚠️ **The domain resolves but serves an empty page.** HTTP 418 with a
zero-byte body means DNS points somewhere that has no content deployed.

---

## 2. ✅ ASSETS GENERATED (exact dimensions, verified)

Built with `brand/make_assets.py` — deterministic vector drawing, no AI
generation, **no credits spent**, and sizes exact by construction.

| file | size | bytes | use |
|---|---|---|---|
| `coinkins-avatar-400.png` | **400×400** | 28.4 KB | X avatar |
| `coinkins-avatar-512.png` | **512×512** | 36.3 KB | Telegram / OpenSea |
| `coinkins-banner-1500x500.png` | **1500×500** | 90.6 KB | X header |
| `coinkins-os-banner-1400x400.png` | **1400×400** | 71.9 KB | OpenSea banner |
| `coinkins-og-1200x630.png` | **1200×630** | 63.7 KB | link previews |

### Specs verified from the official source
`help.x.com` states: avatar **400×400**, **max 2MB**; header **1500×500**
(3:1). Corroborated by 4 independent sources. Our largest file is 90.6 KB —
**22× under the limit.**

### Design rationale (tied to doc 06 naming science)
"Coinkins" = *coin* + *-kin* (English diminutive) → a **small, friendly
coin**. Arc's gas token **is** USDC, so the mark is a stablecoin disc in
Circle-adjacent blue, kept on a dark infrastructure palette so it reads as
serious tooling rather than a cartoon PFP.

---

## 3. 🐞 A REAL LAYOUT BUG CAUGHT BY SIMULATION

I wrote `brand/test_safezone.py` to simulate how X actually renders the
profile — because "it looks fine in the file" is not the same as "it looks
fine on X."

**First layout FAILED:**
```
three coins at x=0.052-0.192 W, y=0.50-0.755 H
X pastes the circular avatar at x=[33,231], y=[401,500]
-> visual collision with the avatar
-> 2 of 3 coins fell inside the top/bottom crop-risk band
```
The rendered simulation showed obvious clutter behind the avatar.

**Fixed layout — re-tested, all clear:**
```
main coin   centre=(217,200) r=118   avatar-overlap=False  mobile-clip=False
accent R1   centre=(1358,150) r=42   avatar-overlap=False  mobile-clip=False
accent R2   centre=(1432,260) r=28   avatar-overlap=False  mobile-clip=False
text starts x=450, avatar ends x=231 -> text clear of avatar: True
COINKINS title  INSIDE safe zone
chips           INSIDE safe zone
```

**Also fixed a bug in my own test:** I first assumed X crops the banner
height to ~2.2:1, which computed to 682px — taller than the 500px banner,
causing a crash. That crash *proved* the assumption wrong. X keeps the 3:1
ratio; narrow viewports crop the **sides**, not the height. Replaced with a
conservative 15% top/bottom chrome inset.

---

## 4. COPY — READY TO PASTE

### X bio (160 char limit — counted)
```
Little coins on a chain where gas is money. Building an NFT project on Arc
in public — every claim verifiable on-chain. Not affiliated w/ Circle.
```
**148 characters.** Fits.

- **Location:** `Arc · chainId 5042`
- **Website:** `https://coinkins.xyz`

⚠️ The "Not affiliated w/ Circle" line is deliberate. Circle's brand
guidelines (doc 01) forbid implying endorsement, and they can revoke usage
with 3 business days' notice. This protects us.

### Telegram — channel name + description
Name: `Coinkins`
```
Little coins on a chain where gas is money.

Building an NFT project on Arc (Circle's stablecoin-native L1) in public.
Every technical claim we make is verifiable on-chain.

Research + code: github.com/0xRadikal/Coinkins
Site: coinkins.xyz

Not affiliated with Circle, Arc, or OpenSea. Not financial advice.
```

### OpenSea profile bio
```
Building on Arc in public. We deployed a full SeaDrop collection on Arc
mainnet — allowlist + paid public mint — for $0.22 in gas, and published
everything we learned.

The Coinkins collection has not launched yet.

coinkins.xyz · github.com/0xRadikal/Coinkins
```

⚠️ **Note the explicit "has not launched yet".** Without it, visitors may
assume the test contract is the real collection.

---

## 5. SETUP CHECKLIST — in this order

| # | action | asset |
|---|---|---|
| 1 | X → avatar | `coinkins-avatar-400.png` |
| 2 | X → header | `coinkins-banner-1500x500.png` |
| 3 | X → bio / location / website | copy from §4 |
| 4 | Telegram → channel photo | `coinkins-avatar-512.png` |
| 5 | Telegram → name + description | copy from §4 |
| 6 | OpenSea → avatar + banner | `-avatar-512` + `-os-banner-1400x400` |
| 7 | OpenSea → bio | copy from §4 |
| 8 | Deploy the site so `coinkins.xyz` stops serving an empty page | `site/index.html` |
| 9 | Re-run `audit_profile.py` to confirm defaults are gone | — |
| 10 | **Only then** start posting doc 17's content | — |

---

## 6. ⚠️ RISKS I MUST FLAG

- **Do not post before step 9 passes.** A profile with a default egg avatar
  reads as a bot; the first impression is unrecoverable and the follow-back
  rate collapses.
- `coinkins.xyz` currently serves a **zero-byte page**. Putting it in the X
  bio before deploying content sends visitors to a blank screen.
  **Deploy first, then add the link.**
- The banner says `GAS = USDC` — verified true (doc 12), but it is a factual
  claim on a public asset, so it must stay accurate if Arc ever changes.
- ⬜ **Not verified:** whether these specific images pass X's upload
  processing without re-compression artifacts. Only an actual upload proves
  that. Dimensions and file sizes are confirmed correct.

---

## 7. STILL OPEN
- ⬜ Deploy `site/index.html` to `coinkins.xyz` (I can do this — needs your
  hosting choice: Cloudflare Pages, or point DNS at this sandbox)
- ⬜ Gate C1: 100 real followers (currently **3**)
- ⬜ On-chain metadata renderer (deliberately blocked until C1 passes)
