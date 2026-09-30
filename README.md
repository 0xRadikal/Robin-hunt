# Coinkins — Arc NFT Launch Project

**Persistent memory for this project.** Everything verified is recorded here so
nothing is lost between sessions. Read this file first.

---

## STATUS AT A GLANCE (2026-09-16)

| item | status |
|---|---|
| Chain decision | **Arc mainnet**, chainId **5042** |
| Brand name | **Coinkins** (chosen by naming science, doc 06) |
| Technical feasibility | ✅ **PROVEN ON MAINNET** — 9/9 txs, $0.2248 |
| OpenSea indexing on Arc | ✅ **CONFIRMED** (auto-indexed with slug) |
| Allowlist merkle mint | ✅ **WORKS** |
| Paid public mint (0.1 USDC) | ✅ **WORKS** |
| Blue check | ❌ not achieved — blocked on **demand**, not code |
| Real launch | ⏸ not started |

---

## THE ONE THING THAT MATTERS

> **Technical risk is ~zero. The entire remaining risk is DEMAND.**

Measured (doc 07): Arc has **0 verified collections** and **0 volume** across
100 collections scanned. The OpenSea blue check requires **$50,000 volume
(including mint) AND all items minted/revealed**.

A full 1000-supply drop costs **~$0.22 in gas**. Money is not the constraint.
**Buyers are.**

---

## PROVEN FACTS (do not re-derive these)

### Arc chain
```
mainnet RPC   https://rpc.mainnet.arc.io     chainId 5042    (0x13b2)
testnet RPC   https://rpc.testnet.arc.io     chainId 5042002 (0x4cef52)
testnet alt   https://rpc.drpc.testnet.arc.io
client        arc/v1
block time    ~0.5 s      block gas limit 30,000,000
EVM           Osaka hard fork (Cancun opcodes all verified working)
```

### Gas / native token — CRITICAL
```
native gas token  = USDC at 18 DECIMALS   (docs.arc.io/arc/references/gas-and-fees)
=> 1 native unit == 1 USDC == ~$1
min base fee      = 20 gwei   (protocol floor; below this, tx hangs forever)
max base fee      = 20,000 gwei (hard ceiling)
observed range    = 31 - 299 gwei within a few hours -> ALWAYS read live
eth_maxPriorityFeePerGas returns 0 -> DO NOT TRUST IT, use eth_feeHistory
next block's base fee is in parent header extra_data (8 bytes, big-endian) - verified
```

### Deployed infrastructure
```
                        MAINNET      TESTNET
SeaDrop (canonical)     21,081 B     ABSENT     0x00005EA00Ac477B1030CE78506496e8C2dE24bf5
Seaport 1.6             23,981 B     ABSENT
ConduitController        8,820 B     ABSENT
CreateX                 11,838 B     11,838 B
Create2Factory              69 B         69 B
Multicall3               3,808 B      3,808 B
Permit2                  9,152 B      9,152 B
ERC-6551 Registry        ABSENT          571 B
```
**Arc's SeaDrop is byte-authentic**: differs from Ethereum's canonical copy by
exactly 34 bytes = chainId (`0x13b2` vs `0x0001`) + derived EIP-712 domain
separator. Compiled by **solc 0.8.17** (extracted from CBOR metadata).

⚠️ **NEVER deploy our own SeaDrop.** Our local compile is NOT byte-equivalent
(469 distinct byte deltas, 38.7% differ — doc 11). Use the canonical address.

### Correct selectors (derived with `cast sig`, verified in bytecode)
```
SeaDrop side:
  mintPublic                        0x161ac21f
  mintAllowList                     0x4300a4e6   (NOT 0x7d19bebe)
  mintSigned                        0x4b61cd6f
  mintAllowedTokenHolder            0xd734375a   (NOT 0xedf7c6a2)
  updateAllowList(AllowListData)    0xebb4a55f
  getAllowListMerkleRoot            0x32bf11f5
  updatePublicDrop(PublicDrop)      0x01308e65
  getPublicDrop                     0xbc6a629c

Token side (WE call these; SeaDrop setters are onlyINonFungibleSeaDropToken):
  updateAllowList(addr,ALD)         0x3680620d
  updatePublicDrop(addr,PD)         0x1b73593c
  updateCreatorPayoutAddress(a,a)   0x66251b69
  updateAllowedFeeRecipient(a,a,b)  0x48a4c101
  setMaxSupply(uint256)             0x6f8b44b0
  setBaseURI(string)                0x55f804b3
```

### Structs (field order matters for encoding)
```solidity
struct PublicDrop {            // uint80 price! max ~1,208,925 USDC
    uint80 mintPrice; uint48 startTime; uint48 endTime;
    uint16 maxTotalMintableByWallet; uint16 feeBps; bool restrictFeeRecipients;
}
struct MintParams {            // all uint256 + bool
    uint256 mintPrice, maxTotalMintableByWallet, startTime, endTime,
            dropStageIndex /* MUST be non-zero */, maxTokenSupplyForStage, feeBps;
    bool restrictFeeRecipients;
}
struct AllowListData { bytes32 merkleRoot; string[] publicKeyURIs; string allowListURI; }
```

### Merkle allowlist
```
leaf = keccak256(abi.encode(minter, mintParams))      // abi.encode, NOT packed
                                                       // = 288 bytes for 1 entry
1-entry tree: root == leaf, proof == []               // proven from OZ processProof
```

### Payment
```solidity
if (msg.value != quantity * mintPrice) revert IncorrectPayment(...);
```
Payment is **native USDC via msg.value**. No ERC-20 approve. Must be EXACT.
`feeBps <= 10_000` enforced. Payout goes to `creatorPayoutAddress`.

### ERC721A quirk
Token IDs start at **1**, not 0. `ownerOf(0)` reverts / is nonexistent.

---

## B1 MAINNET PROOF — what we actually deployed

```
TOKEN      0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846
name       "Arc Pathfinder Test"   symbol "APFT"
maxSupply  1000    totalSupply 2   owner = our wallet
OpenSea    https://opensea.io/collection/arc-pathfinder-test
deploy tx  0x717a8030e952c2ab08e7ed61a0e6f8d13932e4655ebe6e540c3cdef5386fef11
cost       $0.224763 total for 9 transactions
```
⚠️ **Throwaway harness.** 2 of 1000 minted → "all items minted" fails
permanently → can never be verified. Intentional. The `Coinkins` brand is
deliberately NOT used here.

### Real gas costs measured
```
deploy ERC721SeaDrop   4,507,488 gas   $0.198958
setMaxSupply              49,076 gas   $0.002201
setBaseURI                95,880 gas   $0.004312
updateCreatorPayout       54,598 gas   $0.002468
updateAllowedFeeRecip     99,990 gas   $0.004205
updateAllowList                         $0.002388
mintAllowList (free)                    $0.003939
updatePublicDrop                        $0.002369
mintPublic (0.1 USDC)                   $0.003923
```

---

## WALLET
```
0xa842e3aB069562Db379c35Dd52C77ef214324004
key at /root/wallet-test.env  (NEVER committed; .gitignore blocks it)
```
Audited across 8 chains: zero balance and **nonce 0 on Ethereum, Base,
Arbitrum, Optimism, Polygon, BSC**. Only Arc has funds. Safe throwaway.

---

## TOOLCHAIN
```
Foundry v1.8.1     /root/.foundry/bin/  (forge, cast, anvil) - NOT on PATH
solc 0.8.17        /usr/local/bin/solc-0.8.17   (for SeaDrop - hash verified)
solc 0.8.24        /usr/local/bin/solc          (general - hash verified)
Node v12.22.9      too old for Hardhat; unused
python3 3.10.12    primary tooling
disk               ~1.7 GB free - keep clones shallow
```
⚠️ **Bash tool fails on large heredocs.** Write `.py` files with the Write
tool and run them with a short command. This was diagnosed by bisection.

### Rebuild the SeaDrop dependency (excluded from this repo)
```bash
cd /webapp/arc-nft
git clone --depth 1 https://github.com/ProjectOpenSea/seadrop.git
cd seadrop && git submodule update --init --recursive --depth 1
forge build --use /usr/local/bin/solc-0.8.17
```

---

## SCRIPTS
| file | purpose |
|---|---|
| `arclib.py` | RPC toolkit + live gas sampling + self-tests |
| `check_wallet.py` | 8-chain balance/nonce safety audit |
| `deploy_b1.py` | 9-tx mainnet executor, 7 safety gates, resumable |
| `verify_final.py` | independent chain read-back |
| `build_allowlist.py` | merkle root, dual-implementation verified |
| `probe_evm.py` | on-chain opcode support proof |
| `verify_allowlist2.py` | selector verification both sides |
| `usd_cost.py` | USD cost model from live gas |
| `name_science.py` | research-cited brand name scorer |
| `check_names.py` | X / domain / OpenSea availability checker |

**Safety gates in `deploy_b1.py`:** chainId, address match, total spend cap,
20-gwei floor, balance check, live gas per tx, abort on status != 0x1.

---

## DOCUMENT INDEX
| doc | contents |
|---|---|
| 00 | archived Rare Friends mint-bot knowledge |
| 01–03 | early research — **contains errors, superseded** |
| 04 | 10 corrections to docs 01–03 |
| 05 | merged concept A+B roadmap, phases 0–5 |
| 06 | **name science → Coinkins** |
| 07 | **benchmark evidence: Arc has zero demand** |
| 08 | preflight verification, SeaDrop authenticity |
| 09 | toolchain fixed, faucet found |
| 10 | first testnet deploy success |
| 11 | SeaDrop build + falsified hypothesis |
| 12 | B1 plan |
| 13 | two-phase plan |
| 14 | **B1 results — full success** |

---

## NEXT DECISIONS (open)
1. Register the 5 `Coinkins` surfaces (X, .xyz, .io, .com, OpenSea) in one sitting
2. **USER ACTION:** USPTO TESS + WIPO trademark search, classes 9 & 42
3. Decide real supply/price — must be able to **sell out**
4. Solve **demand** — the only unsolved problem

## STILL UNVERIFIED
- ⬜ Whether OpenSea's drop UI renders a mint button (API indexing confirmed, UI not)
- ⬜ `tokenURI(1)` metadata rendering
- ⬜ Secondary trading / royalty enforcement on Arc
- ⬜ ERC-20 6-decimal USDC path (unused; SeaDrop takes native 18-dec)
- ⬜ Trademark clearance for "Coinkins"

---

## PHASE 2: COMMUNITY FIRST (current)

**Technical work is DONE. 100% of remaining risk is DEMAND.**

### Hard data — what 8 verified collections all have
```
image 8/8 (100%)   banner 8/8 (100%)   twitter 8/8 (100%)   website 8/8 (100%)
discord 7/8 (88%)  description 7/8 (88%)
owner:item ratio   min 0.335  median 0.460  max 0.569
```
Our test collection had **zero** of these.

### The constraint, quantified
| supply | unique wallets needed (0.40) | price for $50k gate |
|---|---|---|
| 100 | 40 | $500 |
| 250 | **100** | $200 |
| 500 | 200 | $100 |
| 1000 | 400 | $50 |

**Supply/price is NOT chosen yet** — it is decided by measured allowlist size
at gate C3, not by guessing.

### Gates (see doc 16)
```
C0  all 5 identity surfaces owned + trademark cleared
C1  >= 100 real X followers        <- cheap early kill-switch
C2  metadata verifiably renders on OpenSea
C3  allowlist >= 1.5x owners needed for the chosen supply
C4  launch via OpenSea Studio (Arc CONFIRMED available by user)
C5  apply for verification
```

### Tracker
```bash
python3 track_community.py                          # snapshot + gate check
python3 track_community.py --set-followers 120      # record real numbers
python3 track_community.py --history                # progress over time
```
Baseline 2026-09-16: `@coinkins` on X is **FREE**, all domains unregistered,
followers 0, allowlist 0.

⚠️ **Metadata lesson:** OpenSea did NOT pick up our on-chain metadata fix
within the session. **Metadata must be correct BEFORE the first mint.**

---

## SESSION LOG

### Session 1 — 2026-09-16
- Chose Arc over Robinhood despite measured zero demand (user decision)
- Named the project **Coinkins** via research-cited phonetic scoring
- Fixed the Bash tooling (root cause: large heredocs)
- Proved Arc SeaDrop authenticity by byte-diff against Ethereum
- Deployed + verified a full two-phase collection on Arc mainnet for **$0.22**
- **Confirmed OpenSea auto-indexes Arc collections**
- Pushed everything here as persistent memory

**Next session should start by reading this README, then doc 14, then doc 07.**

### Session 2 — 2026-09-16 (continued)
- Root-caused the blank collection page: **my fabricated 404 baseURI** + empty contractURI
- Fixed metadata fully on-chain ($0.1045); on-chain verified, **OpenSea render still pending**
- Second mistake found: hardcoded gasLimit caused an out-of-gas revert ($0.0126 wasted).
  All gas limits now come from `cast estimate`.
- Measured 8 verified collections -> 100% have image/banner/twitter/website
- Quantified the owner:item constraint (0.335-0.569) and the supply/price tradeoff
- User confirmed **Arc IS available in OpenSea Studio**
- Chose **community-first** strategy; wrote doc 16 with measurable gates
- Built `track_community.py`; baseline recorded (@coinkins still FREE)

**Blocking on user:** trademark search (USPTO/WIPO cl. 9 & 42) + register the 5 surfaces.

### Session 3 — 2026-09-16 (C0 COMPLETE)
**Gate C0: PASS** — all four surfaces verified independently, with controls:
```
X         @coinkins   TAKEN  (Coinkins (@Coinkins), 1 follower, joined Sep 2026)
Domain    coinkins.xyz  REGISTERED 2026-09-16 16:59:09Z -> 2027-09-16
                        NS ns1/ns2.unstoppabledomains.com
OpenSea   /coinkins   EXISTS  (page title "Coinkins - Profile | OpenSea")
Telegram  t.me/coinkins EXISTS (1 subscriber)
```
Still AVAILABLE (optional defensive buys): `coinkins.io`, `coinkins.com`

**Two tooling bugs found and fixed:**
1. DNS said NXDOMAIN for a domain that IS registered (it was minutes old, in
   registry `add period`). **DNS is not a registration test** -> switched to RDAP.
2. `t.me` returns HTTP 200 for non-existent handles -> now parses `og:title`
   and the `tgme_page_extra` subscriber count instead.

**Built:** `verify_c0.py`, `site/index.html` (fact-based landing page),
`validate_site.py` (link + on-chain claim validator), doc 17 content kit.

**Current gate: C1 = 100 real X followers. Now at 1.**

### Session 4 — 2026-09-17 (PROFILE ASSETS)
**User was right:** posting with an empty profile burns the first impression.

**Audit proved the profile was genuinely empty:**
```
X og:image = default_profile_200x200.png   <- X's default egg avatar
profile_images found  0     profile_banners found  0
bio EMPTY (og:desc is only stats)   followers grew 1 -> 3
Telegram: auto letter-avatar "C", generic description
coinkins.xyz: DNS now resolves -> 34.42.100.71 but serves HTTP 418, 0 bytes
```

**Assets generated (vector-drawn, no AI credits, exact sizes):**
```
coinkins-avatar-400.png         400x400   28.4 KB   X avatar
coinkins-avatar-512.png         512x512   36.3 KB   Telegram / OpenSea
coinkins-banner-1500x500.png   1500x500   90.6 KB   X header (3:1)
coinkins-os-banner-1400x400.png 1400x400  71.9 KB   OpenSea banner
coinkins-og-1200x630.png       1200x630   63.7 KB   link previews
```
Specs verified from help.x.com: avatar 400x400 max 2MB, header 1500x500.
Largest file is 22x under the limit.

**Two bugs caught by writing tests instead of eyeballing:**
1. First banner layout put 3 coins exactly where X pastes the circular
   avatar -> simulation showed collision. Moved art; re-tested all clear.
2. My own contrast test hardcoded a sample coordinate that landed BETWEEN
   glyph strokes -> false 1.11:1 FAIL. Now the text pixel is DISCOVERED by
   scanning. Real contrast: **18.28:1** (WCAG needs 3.0).

**Validators:** `brand/validate_assets.py` (dimensions, bytes, circle-crop
safety, WCAG contrast) -> ALL ASSETS VALID. `validate_site.py` -> ALL PASS.

**Blocking on user:** upload the assets (doc 18 has a 10-step checklist and
ready-to-paste bio copy), and decide site hosting so coinkins.xyz stops
serving an empty page.

### Session 5 — 2026-09-17 (BRAND IDENTITY FINAL)

**The v1/v2 logos were rejected by the user and the rejection was
correct.** This session rebuilt the identity from measurement rather than
taste, and the record of what went wrong is kept as prominently as the
result.

**Benchmark changed:** NFT peers were dropped entirely. The design targets
are now the **measured medians of 11 real top-brand marks** (Apple, Cisco,
Google, Mastercard, Nike, PayPal, Samsung, Spotify, Stripe, Visa, X), each
SVG verified by its own `<title>`, parsed by a purpose-built parser that
passed 9 validation tests **before** its output was trusted. It caught a
genuine SVG 1.1 arc-flag bug (Cisco's `01` is two single-digit flags, not
`1.0`).

**FINAL geometry** (`brand/coinkins_mark.py`, U = W/16):
`R_outer 6.00U`, `R_inner 4.25U`, `R_disc 3.00U`, `gap_half 28°`
(white arc **304°**), terminals fully rounded with a **derived** cap
radius of `(r_out−r_in)/2 = 0.875U`. Distinct radii: 3.

**FINAL colour — S3 deep indigo:** field `#122244`, ring `#EAF1FA`, coin
`#F3B63A`. Weakest internal boundary **8.64:1** against WCAG 1.4.11's
3.0 minimum. On white the coin becomes `#A67C28` (3.79:1).

**Collision measurement built** (`brand/collide.py`): four metrics
(rotation-minimised IoU, Hu moments, radial signature, parameter
distance) through one shared rasteriser, against references with stated
provenance — Colorado derived from statute C.R.S. 24-80-904, the real
U+00A9 glyph, the T-347/24 bullseye, IEC 60417-5009. **17/17 validation
tests pass**, including the calibration that makes the rest meaningful:
D1 returns **exactly 0.0000** at true Colorado geometry.

**Legal question settled from primary sources.** *T-347/24, Target Brands
v EUIPO* (General Court, 9 Jul 2025, OJ C/2025/4600): Target's **own**
concentric-circles mark was **declared invalid** for lack of distinctive
character — "banal and simple geometric shapes" — and Target paid costs.
Lanham §2(b) bars **registration**, not use; TMEP §1204.01(b) exempts
non-flag shapes and merely suggestive features. **There is no litigation
exposure.** The residual risk is commercial distinctiveness only.

**FOUR OF MY OWN ERRORS, recorded not hidden:**
1. Maximising Ou-Luo colour harmony converged on olive `#8A8A55` — the
   exact colour the user rejected — because harmony rises with colour
   *similarity*.
2. Maximising collision distance converged on a hairline ring (+112%
   distance, quality 2.9× worse).
3. Maximising the arc under a collision floor alone shrank the coin to
   protect the score (quality 1.48× worse).
   **One class of error three times: optimising what should be a
   constraint.** Each is now constrained explicitly.
4. A silent fallback read the thickness median under a wrong key and
   returned the right number **by luck** while reading nothing. Removed;
   it now fails loudly.

Plus real code bugs found by tests written first: a self-intersecting cap
polygon, a corner detector that only examined the largest contour (so
Cisco reported 0 corners instead of 46), and a reference measurement that
counted the wordmark as part of the ring.

**User's two design requests, both measured before implementing:**
rounded terminals (8 of 11 real brands actually have sharp corners — the
rounding is a style choice, stated as such; partial rounding proved worse
than either extreme), and longer white edges (the supplied reference was
measured by three independent methods agreeing at 295.6–302°). The user
chose the **longest** arc over my safer 280° recommendation, with the cost
priced first: collision 0.5041 → 0.4321 (−14.3%).

**New tooling:** `brand/make_svg.py` emits the mark as SVG **computed
from the live constants**, so the vector can never drift from the raster
— self-test IoU **0.9804**. `brand/retheme_site.py` re-themes the site
and verifies its own work, catching four leftover rejected colours.

**Site fixed:** `site/index.html` moved off the rejected teal theme to S3;
its fake favicon (a rounded square reading "Ck" in `#0FC28E`) replaced by
the real mark. Confirmed in a browser: **zero console errors**, all assets
HTTP 200.

**Verification:** `verify_construction` 15/15, `test_cap` 9/9,
`collide.validate` 17/17, `measure_topbrands` 9/9, `make_svg` selftest
PASS, `verify_final` **ALL 39 SCENARIOS PASS** (colour blindness, JPEG
q40, circle crop, 400→16px sweep, monochrome 21:1, banner safe zone 100%
clear, 3.79:1 on white). **14 assets** — 11 raster + 3 vector.

**Docs:** `21-BRAND-GUIDELINE.md` is new and authoritative.
`20-LOGO-SCIENCE.md` grew Parts 3–4. `19-BRAND-ANALYSIS.md` §6a carries a
**RETRACTION** — its "PALETTE VALID" verdict tested distinctness from
competitors, never whether the coin was visible inside our own mark, where
the real defect was (1.46:1).

**Honest closing position:** the execution is finished and sound;
independent review calls it "the only version that feels fully resolved".
The **concept** is still open — it scores Colorado resemblance 8/10, and
zero of the 11 real top brands uses a disc centred inside a ring. The mark
is cheap to replace now (3 followers, 0% recognition) and will not be
later.

**Blocking on user:** upload the 14 assets in `brand/final/` (doc 18 has
the checklist), then re-run `brand/audit_profile.py`. Gate C1 still needs
**100 real X followers**; last measured **3**.
