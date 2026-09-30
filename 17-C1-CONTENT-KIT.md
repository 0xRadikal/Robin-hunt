# 17 — C1 CONTENT KIT (build-in-public, fact-based)
**Date:** 2026-09-16
**Gate C0: ✅ PASS** — all surfaces verified independently (see §1)
**Gate C1 target: ≥100 real X followers. Current: 1.**

---

## 1. ✅ C0 VERIFIED INDEPENDENTLY (not taken on trust)

| surface | verification method | result |
|---|---|---|
| **X** `@coinkins` | x.com status + 4 controls | **TAKEN** — `Coinkins (@Coinkins) / X`, 1 follower, 18 following, joined Sep 2026 |
| **Domain** `coinkins.xyz` | **RDAP registry** (authoritative) | **REGISTERED** 2026-09-16 16:59:09Z → 2027-09-16, NS `ns1/ns2.unstoppabledomains.com` |
| **OpenSea** `/coinkins` | headless browser page title | **EXISTS** — `Coinkins - Profile \| OpenSea` |
| **Telegram** `t.me/coinkins` | og:title + tgme_page_extra parse | **EXISTS** — `1 subscriber` |

### ⚠️ A tooling bug this exposed — and the fix
My first check reported the domain as `NO_DNS` and I could have wrongly told
you it was not registered. Both `8.8.8.8` and `1.1.1.1` returned **NXDOMAIN**.

**Cause:** the domain was **minutes old** and in registry status `add period`.
DNS had not propagated. **DNS is not a valid test of registration.**

**Fix:** `track_community.py` now queries **RDAP** (the registry itself), and
reports DNS separately as `dns:propagating`. Same class of fix for Telegram:
`t.me` returns HTTP 200 for *non-existent* handles too, so status alone is
meaningless — it now parses `og:title` and the subscriber count.

**Both checks now validate against controls before being trusted.**

⚠️ **Action for you:** `coinkins.io` and `coinkins.com` are still **AVAILABLE**.
The nameservers indicate Unstoppable Domains. If you want defensive coverage,
register them — but this is optional, not a blocker.

---

## 2. OUR ONE GENUINE ASSET

We are not a hype project with nothing behind it. We have **on-chain,
independently verifiable proof** that we did real engineering work on Arc
before almost anyone else:

```
Token contract  0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846
Chain           Arc mainnet (5042)
Total gas cost  $0.224763 for 9 transactions

TX1 deploy ERC721SeaDrop   0x717a8030e952c2ab08e7ed61a0e6f8d13932e4655ebe6e540c3cdef5386fef11
TX7 mintAllowList (free)   0x30e5d30dbeb86c1d108d8be544962c7846d7292caca57c8e5859da472cb65c79
TX9 mintPublic (0.1 USDC)  0x67de2bc47826a45dca9c7255c0e4449fdbdeb6be0d6b3d935dc0b9550ac82590
```
**Anyone can verify these.** That is the difference between a claim and a fact,
and it is the only credible foundation for a community on a brand-new chain.

---

## 3. POST PLAN — each post has ONE verifiable fact

Rule: **every post contains something checkable.** No "wen mint", no
"gm", no fake scarcity. Facts attract the technical audience that actually
exists on a Circle-backed chain.

### Post 1 — the hook (launch the account)
> We deployed a full OpenSea SeaDrop collection on Arc — allowlist mint +
> paid public mint — for **$0.22 total gas**.
>
> Contract: `0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846`
> 9/9 transactions, all verifiable on chain.
>
> Thread on everything we learned 🧵

### Post 2 — a fact almost nobody knows
> Arc's gas token is **USDC at 18 decimals**.
>
> Not 6. **18.**
>
> If you assume 6 you are off by a factor of 10¹². We proved it by decoding
> real tx values on-chain, then confirmed it in Circle's own docs.

### Post 3 — the authenticity proof
> Is Arc's SeaDrop the real canonical OpenSea SeaDrop?
>
> We byte-diffed it against Ethereum's. **34 bytes differ out of 21,081.**
> Those 34 bytes are the chainId (`0x13b2` = 5042) and the derived EIP-712
> domain separator.
>
> It is authentic. Same logic, different chain.

### Post 4 — a warning that saves people money
> Do NOT deploy your own SeaDrop on Arc.
>
> We compiled it ourselves to compare: **469 distinct byte deltas, 38.7% of
> the bytecode differs** from the deployed one. A self-compiled copy is
> non-canonical and OpenSea's indexer expects the canonical address.
>
> Use `0x00005EA00Ac477B1030CE78506496e8C2dE24bf5`.

### Post 5 — the gas trap
> Arc gas moved **31 → 299 gwei within hours** while we were working.
>
> Also: `eth_maxPriorityFeePerGas` returns **0** on Arc. Trust it and your
> tx hangs forever. Protocol floor is 20 gwei.
>
> Always read `eth_feeHistory` live. Never hardcode.

### Post 6 — admitting a mistake (this builds more trust than wins)
> We burned $0.0126 on a reverted tx because we hardcoded a gas limit.
>
> Storing ~890 chars of on-chain metadata needs **697,558 gas**. We guessed
> 220,000. Out of gas.
>
> Measured properly: 4 chars → 48,889 · 400 chars → 350,280 · 893 → 697,558.

### Post 7 — the honest state of the chain
> Uncomfortable data: we scanned 100 NFT collections on Arc.
>
> **0 verified. 0 volume.**
>
> We are not pretending there is a crowd here. We are building early and
> saying so out loud.

---

## 4. WHY THIS APPROACH AND NOT NORMAL NFT MARKETING

Measured in doc 16: 100% of verified collections have X + website + image +
banner. But that tells us what they *have*, not how they *started*.

What we can reason about from evidence:
- Arc is a **Circle L1 with institutional validators** (BlackRock, Visa,
  Mastercard, NYSE). Its early population is **developers and finance
  infrastructure people**, not PFP flippers.
- Therefore **technical credibility is the right currency here**, and we
  happen to already have it.
- `rare-friends-genesis` reached verification in ~2 days on a new chain with
  **fully on-chain generative SVG art** — a technical artifact, not a
  marketing campaign.

⚠️ **I am not claiming this will work.** Gate C1 (100 followers) is precisely
the test of whether it works, and it costs nothing but time.

---

## 5. WHAT I WILL NOT DO
- ❌ Buy followers or engagement — OpenSea screens for inorganic signals
- ❌ Fabricate roadmap promises (no "utility", no fake partnerships)
- ❌ Announce a mint date before gate C3 is met
- ❌ Claim a blue check is coming — approval is discretionary

---

## 6. NEXT: C2 — METADATA PIPELINE (cost-critical)

Measured: **~890 chars of on-chain metadata = ~700,000 gas = ~$0.056 per write.**

For 1,000 items written individually that is **~$56 plus 700M gas** — and it
would take 1,000 transactions. **Not viable as one-write-per-token.**

Two viable designs:
| approach | cost | pros | cons |
|---|---|---|---|
| **A. On-chain generative renderer** (rare-friends model) | one deploy, ~$0.20-1.00 | permanent, no server, no 404 ever, strong "real on-chain" story | needs a compact SVG algorithm; more contract work |
| **B. Single IPFS base URI** | pinning cost only | simple, standard, any art style | depends on pinning staying alive; must HTTP-verify |

**My recommendation: A.** It matches our technical positioning, matches what
the one successful new-chain collection did, and structurally eliminates the
404 failure we already hit.

⚠️ **Loss warning:** option A requires writing and testing a renderer
contract. That is real engineering time. If it fails to sell out afterwards,
that time is sunk. **C1 must pass first** — that is the point of the gate.

---

## 7. IMMEDIATE ACTIONS

**Yours:**
1. Post content 1-7 on `@coinkins` (spread over days, not all at once)
2. Point `coinkins.xyz` at something — even a one-page site with the contract
   address and tx hashes
3. Optionally register `.io` / `.com` defensively
4. Report real follower count back so the tracker stays honest:
   `python3 track_community.py --set-followers N`

**Mine (after C1 passes):**
1. Design + test the on-chain renderer
2. Verify metadata renders on OpenSea using the existing test contract
3. Prepare launch config with supply/price chosen from **C3 data**
