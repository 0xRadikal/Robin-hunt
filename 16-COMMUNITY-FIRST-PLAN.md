# 16 — COMMUNITY-FIRST PLAN (measured, not guessed)
**Date:** 2026-09-16
**Your direction:** build the community BEFORE launching.
**Confirmed by you:** Arc IS available in OpenSea Studio.

---

## 1. FIRST — AN HONEST STATUS CORRECTION

I fixed the metadata on-chain and verified it by decoding it back. But
**OpenSea has still NOT picked it up:**

```
on-chain contractURI  -> valid JSON, name 'Arc Pathfinder Test', SVG image  ✅
OpenSea rendered page -> 0 occurrences of our description text             ❌
OpenSea cached image  -> no i2c.seadn.io entry for our collection          ❌
OpenSea API           -> now returns HTTP 401 (key required; it was open earlier)
```
**I am not claiming the metadata fix worked end-to-end.** On-chain: proven.
OpenSea render: **still unverified.** Their indexer refreshes on its own
schedule and the force-refresh endpoint needs an API key.

⚠️ This matters for launch planning: **metadata must be correct BEFORE the
first mint**, because fixing it afterwards may not refresh promptly.

---

## 2. 📊 HARD DATA — WHAT VERIFIED COLLECTIONS ACTUALLY HAVE

I measured 8 verified collections instead of theorising. **Every single one:**

| attribute | rate |
|---|---|
| has image | **8/8 = 100%** |
| has banner | **8/8 = 100%** |
| has Twitter/X | **8/8 = 100%** |
| has website | **8/8 = 100%** |
| has Discord | 7/8 = 88% |
| has description | 7/8 = 88% |

**Our test collection had ZERO of these.** That is not a small gap — it is
the entire difference between "a contract exists" and "a collection exists".

### Owner : item ratio — OpenSea explicitly reviews this
```
rare-friends-genesis   451 /   967 = 0.466
pudgypenguins         5056 /  8888 = 0.569
azuki                 4376 / 10000 = 0.438
boredapeyachtclub     5597 /  9998 = 0.560
doodles-official      4545 /  9998 = 0.455
moonbirds             3353 /  9999 = 0.335
milady                5105 /  9976 = 0.512
cryptopunks           3817 /  9993 = 0.382
-----------------------------------------------
min 0.335   median 0.460   mean 0.465   max 0.569
```
**Every verified collection sits between 0.33 and 0.57.** Wash trading or
one-wallet hoarding produces a ratio far outside this band, which is exactly
what OpenSea screens for.

---

## 3. 🎯 THE REAL CONSTRAINT, QUANTIFIED

Combining the $50,000 gate, the "all items minted" rule, and the measured
owner ratio:

| supply | unique wallets needed (at 0.40) | price per item for $50k |
|---|---|---|
| 100 | **40** | $500.00 |
| 250 | **100** | $200.00 |
| 500 | **200** | $100.00 |
| 1,000 | **400** | $50.00 |
| 2,000 | **800** | $25.00 |

**This is the whole problem in one table.** Every row requires either a high
price or a lot of wallets. On a chain measured at **zero NFT buyers**, both
are hard.

### My honest read
- **Supply 250 @ $200** needs only **100 real buyers** — the smallest
  credible path to $50,000. But $200/item demands genuine belief.
- **Supply 1,000 @ $50** needs **400 buyers** — a much larger community.
- **Supply 100 @ $500** needs 40 buyers but $500 on an empty chain is
  implausible without an established name.

⚠️ **I am not recommending a number yet.** The community-building phase is
what determines which row is realistic. Picking now would be guessing.

---

## 4. COMMUNITY ROADMAP — EVERY PHASE HAS A MEASURABLE GATE

### Phase C0 — Identity foundation (before any public post)
| task | done when |
|---|---|
| Register `@coinkins` on X | owned |
| Register coinkins.xyz (+ .io/.com defensive) | owned |
| **USPTO TESS + WIPO search, classes 9 & 42** | **YOU** confirm clear |
| Create OpenSea account/username | owned |
| Discord or Telegram set up | owned |
| Profile art + banner produced | files exist |

**Cost: ~$40-60 domains. Gate: all five surfaces owned in ONE sitting.**
⚠️ Do not post publicly before this — the name gets sniped otherwise.

### Phase C1 — Proof of build in public (weeks 1-3)
The one asset we genuinely have: **we are demonstrably first and technical
on Arc.** That is a real story, not marketing fluff.

| task | measurable gate |
|---|---|
| Publish the Coinkins repo publicly | repo public |
| Write up "first SeaDrop mint on Arc" with tx hashes | post live |
| Post the verified Arc facts (USDC gas 18-dec, SeaDrop authenticity) | post live |
| Engage Arc/Circle developer channels | ≥1 acknowledgement |

**Gate to C2: 100 real X followers AND ≥3 non-bot replies per post.**
If we cannot get 100 followers, a 400-buyer mint is fantasy — better to learn
it here for free.

### Phase C2 — Art + metadata pipeline (weeks 3-6)
| task | gate |
|---|---|
| Decide art direction consistent with "Coinkins = little coins" | spec written |
| Build generative renderer OR pin to IPFS | **HTTP-verified URLs** |
| Test metadata on the existing test contract first | renders on OpenSea |
| Set `contractURI` with image + banner | decoded + verified |

**Gate to C3: metadata verifiably renders on OpenSea.** This is the exact
failure we just hit — it must be closed before launch.

### Phase C3 — Allowlist accumulation (weeks 6-10)
| task | gate |
|---|---|
| Open allowlist registration (wallet collection) | form live |
| Reward early community members | list grows |
| Publish supply + price only AFTER measuring list size | decision made on data |

**Gate to launch: allowlist ≥ 1.5x the unique wallets needed.**
For 250 supply → need 100 owners → **want ≥150 allowlist signups.**
The 1.5x covers the standard drop-off between signup and actual mint.

### Phase C4 — Launch
Only when C3's gate is met. Use OpenSea Studio (Arc confirmed available).
Two stages, as already proven working: allowlist then public.

### Phase C5 — Verification
Apply at `opensea.io/settings/verification` once $50k volume and full mint
are achieved. Pursue `opensea.io/partners` in parallel.

---

## 5. ⚠️ THE LOSS-MAKING RISK I MUST FLAG

**The dangerous action here is not spending money — it is spending TIME.**

- Hard cost of this whole plan: **~$40-60** (domains) + **~$0.25** (gas).
- The real risk: **8-10 weeks of work on a chain with zero demonstrated NFT
  buyers**, ending in a mint that does not sell out, which permanently
  forfeits the badge for that collection.

**This is why every phase has a gate.** The C1 gate (100 followers) costs
nothing and is deliberately placed early: if organic interest in an Arc NFT
project cannot reach 100 followers, we learn it in week 3 instead of week 10.

### What I will NOT do
- **Buy followers.** OpenSea screens for inorganic signals; fake community
  produces fake allowlists and a failed mint.
- **Wash trade.** Permanently forfeits the badge.
- **Promise a blue check.** Approval is discretionary — their words.

---

## 6. WHY "COMMUNITY FIRST" IS CORRECT — CONFIRMED BY DATA

Your instinct matches the measurement:
1. **100% of verified collections have Twitter + website + image + banner.**
   These are community assets, not contract features.
2. Owner:item ratio of 0.33-0.57 **cannot be faked** — it requires hundreds
   of distinct, willing buyers.
3. OpenSea's own criteria reward *"unique purchases by buyers in the last 30
   days"* and *"organic owner to item ratio"*.
4. We already proved the contract side costs **$0.22 and one afternoon**.
   The contract was never the bottleneck.

**Conclusion: the technical work is done. 100% of the remaining work is
demand generation.**

---

## 7. IMMEDIATE NEXT ACTIONS

**Yours (I cannot do these):**
1. **Trademark search** — USPTO TESS + WIPO, classes 9 & 42, for "Coinkins"
2. Register `@coinkins` on X + coinkins.xyz, in one sitting
3. Confirm you want to proceed with the Coinkins name after the TM check

**Mine (once you confirm the name is clear):**
1. Build `track_community.py` to measure follower/allowlist growth objectively
2. Design the metadata/art pipeline with **HTTP-verified** URLs
3. Test the full metadata render on the existing test contract (free-ish)
4. Prepare the real launch config, supply/price decided by **C3 data**

---

## 8. STILL UNVERIFIED
- ⬜ Whether OpenSea renders our fixed metadata (indexer lag)
- ⬜ Whether OpenSea Studio lets us attach our **already-deployed** token to
  a Drop, or requires deploying through Studio itself
- ⬜ Trademark status of "Coinkins"
- ⬜ Whether any organic demand for Arc NFTs exists at all — **C1 tests this**
