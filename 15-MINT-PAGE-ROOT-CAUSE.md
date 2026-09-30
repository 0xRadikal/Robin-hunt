# 15 — WHY THERE WAS NO MINT/OVERVIEW PAGE — ROOT CAUSE
**Date:** 2026-09-16
**Your question:** why did the collection have no overview/mint page where a
user can see the stages and mint? It is one of the most important parts.
**Answer: you are right, and I found the real cause. It was my omission.**

---

## 1. WHAT I DID WRONG

In doc 13 I set `baseURI = "https://arweave.net/apft-placeholder/"` and
called it a "placeholder". I never verified it resolved. Tested now:

```
https://arweave.net/apft-placeholder/1   ->  HTTP 404
```

**It was a fabricated URL that never existed.** That is exactly the kind of
unverified assumption I am supposed to avoid. The contract worked perfectly —
it faithfully served a URL that points to nothing.

Also `contractURI()` returned `''` (empty). That is the field OpenSea reads
for the **collection-level** name, description, and image.

Result on OpenSea:
```
name             'Arc Pathfinder Test'
description      ''          <- empty
image_url        None        <- nothing to render
banner_image_url None
```
**A collection page with no image and no description looks broken/blank.**

---

## 2. PROOF BY COMPARISON — HOW A WORKING ARC-ERA COLLECTION DOES IT

I compared against `rare-friends-genesis`, which **is** verified and **does**
render. Its `tokenURI(1)`:

```
data:application/json;base64,eyJuYW1lIjoiR2VuZXNpcyAjMSIs...
```
Decoded:
```json
{
  "name": "Genesis #1",
  "description": "Original on-chain 8x8 Genesis artwork.",
  "image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0i...",
  "attributes": [
    {"trait_type":"Lineage","value":"Layered"},
    {"trait_type":"Stature","value":"Tall"},
    {"trait_type":"Crown","value":"Flat"},
    ... 9 traits total
  ]
}
```
**Fully on-chain metadata — no external server, nothing to 404.**
And OpenSea shows its images from `i2c.seadn.io` (their CDN), proving they
fetched and cached it successfully.

| | ours (before) | rare-friends |
|---|---|---|
| `tokenURI` | `arweave.net/...` → **404** | `data:application/json;base64,…` ✅ |
| `contractURI` | `''` | populated |
| OpenSea `image_url` | `None` | `i2c.seadn.io/...` |
| OpenSea `safelist_status` | not_requested | **verified** |

---

## 3. ✅ FIXED ON THE LIVE CONTRACT (2 txs, $0.1045)

```
setContractURI   status 0x1   gasUsed 690,907   $0.056391
setBaseURI       status 0x1   gasUsed 568,504   $0.048117
```

Read back from chain, decoded, verified valid JSON:
```
tokenURI(1) -> data:application/json;base64,...
   name        'Pathfinder'
   description 'On-chain proof that SeaDrop minting works on Arc.'
   image       data:image/svg+xml;base64,...
   attributes  3 traits

contractURI() -> data:application/json;base64,...
   name        'Arc Pathfinder Test'
   description 'Technical proving harness for the Coinkins project...'
   image       data:image/svg+xml;base64,...
```
**Metadata is now fully on-chain and self-contained. Cannot 404.**

---

## 4. ⚠️ A SECOND MISTAKE I MADE DURING THE FIX — AND THE LESSON

First attempt **reverted and still cost $0.0126**:
```
setContractURI  status 0x0  gasUsed 220,000 (all consumed)  $0.012622
```
I had **hardcoded** `gas_limit = 220_000`. I then measured properly:

```
payload   4 chars ->  48,889 gas
payload 400 chars -> 350,280 gas
payload 893 chars -> 697,558 gas    <- ours needed this
```
**Out of gas.** Storing long strings on-chain is expensive and scales with
length — 220k was nowhere near enough.

Note how I isolated it instead of guessing: `cast call` (simulation)
**succeeded** at all lengths, which ruled out permissions and length limits,
leaving gas as the only explanation. Then `cast estimate` confirmed it.

**Fix applied to the code:** `send()` now calls `cast estimate` and adds 25%
headroom. **No hardcoded gas limits anywhere.** This is the same discipline
I already applied to gas *price* — I should have applied it to gas *limit*.

⚠️ Honest cost of my two mistakes: **$0.0126 wasted** on the reverted tx.

---

## 5. ⬜ WHAT IS STILL NOT PROVEN — I WILL NOT CLAIM SUCCESS

After the fix, OpenSea **still** reports:
```
description  ''
image_url    None
```
Because:
- `POST /nfts/1/refresh` returns **HTTP 401** (needs an API key)
- Their indexer refreshes on its own schedule

**So I cannot yet claim the OpenSea page renders correctly.** The on-chain
side is proven; the OpenSea-render side is **pending and unverified**.

### And the bigger, separate question
A **mint/overview page with visible stages** is part of OpenSea's **Drops
program**, which is not the same thing as a collection being indexed.
Evidence gathered:

- Our page title is `Arc Pathfinder Test - Collection | OpenSea` — **"Collection"**, not "Drop"
- `rare-friends-genesis` — verified, 656 ETH volume — **also titles as "Collection"**
- OpenSea docs say SeaDrop provides *"all the functionality needed to integrate
  with OpenSea's **Drops program**"* — i.e. the contract is a **prerequisite**,
  not the whole thing
- Their docs route drop creation through **OpenSea Studio**
- `GET /api/v2/chains` confirms `arc` **is** supported: `{"chain":"arc","name":"Arc Chain","symbol":"USDC"}`

⚠️ **I do not yet know** whether Arc is enabled inside OpenSea Studio for
drop creation, or whether a self-deployed SeaDrop token can be attached to a
Studio drop page. **That is the next thing to test, and it needs the Studio
UI with a connected wallet — which requires you, not me.**

---

## 6. WHAT THIS MEANS FOR THE REAL LAUNCH

Three requirements I had not made explicit before. All are now mandatory:

1. **Metadata must exist before launch.** Either fully on-chain (like
   rare-friends) or on real, resolving IPFS/Arweave URLs that I **verify with
   an HTTP check** before use. Never a made-up URL again.
2. **`contractURI` must be set** — it drives the collection's name,
   description, image, banner, and royalty display.
3. **The drop/mint page likely requires OpenSea Studio**, not just a deployed
   contract. **Must be confirmed before announcing any mint date.**

### Cost implication for on-chain metadata
```
~890 chars of metadata = ~700,000 gas = ~$0.056 per write
```
For a 1,000-item collection with per-token on-chain metadata this would be
prohibitive **if written one by one**. Real collections use either a
generative on-chain renderer (like rare-friends' SVG builder) or a single
IPFS base URI. **This must be designed, not improvised.**

---

## 7. NEXT ACTIONS
- ⬜ **YOU:** open OpenSea Studio with the wallet, check whether Arc appears
  as a deployable/attachable chain for a Drop
- ⬜ Re-check OpenSea render in a few hours (indexer lag)
- ⬜ Design the real metadata strategy before the Coinkins launch
- ⬜ Community building before launch (your chosen direction) — separate doc
