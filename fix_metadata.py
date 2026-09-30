#!/usr/bin/env python3
"""
fix_metadata.py - PROVE the mint/overview page problem is metadata, not chain
support, by fixing the live test collection.

ROOT CAUSE ESTABLISHED:
  our tokenURI -> https://arweave.net/apft-placeholder/1  = HTTP 404
  rare-friends  -> data:application/json;base64,...       = fully on-chain
OpenSea renders images/description from tokenURI + contractURI. With a 404
there is nothing to render, so the collection page stays blank.

FIX (two txs, both cheap):
  1. setBaseURI  -> a data: URI so tokenURI returns real on-chain metadata
  2. setContractURI -> collection-level name/description/image

Note on ERC721ContractMetadata.tokenURI: it concatenates baseURI + tokenId
when baseURI does not end in "/", so a single shared data URI is returned
for every token only if the contract supports that. We VERIFY the actual
returned value after the tx rather than assuming.

TESTNET-SAFE: gates identical to deploy_b1.py, mainnet deliberate.
"""
import base64
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, '/webapp/arc-nft')
from arclib import (rpc, to_int, MAINNET, CHAIN_ID_MAINNET,  # noqa: E402
                    sample_base_fee, priority_fee)

CAST = '/root/.foundry/bin/cast'
KEYFILE = '/root/wallet-test.env'
WALLET = '0xa842e3aB069562Db379c35Dd52C77ef214324004'
TOKEN = '0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846'
MIN_BASE_FEE_GWEI = 20.0
CAP_USD = 0.40


def key():
    m = re.search(r'0x[0-9a-fA-F]{64}', open(KEYFILE).read())
    return m.group(0)


def b64_json(obj):
    raw = json.dumps(obj, separators=(',', ':')).encode()
    return 'data:application/json;base64,' + base64.b64encode(raw).decode()


def svg_data_uri(label, color):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="512" '
           f'height="512" viewBox="0 0 8 8" shape-rendering="crispEdges">'
           f'<rect width="8" height="8" fill="{color}"/>'
           f'<path fill="#fff" d="M1 1h6v1H1zM1 3h6v1H1zM1 5h6v1H1z"/>'
           f'</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(
        svg.encode()).decode()


def fees():
    st = sample_base_fee(MAINNET, n=4, stride=2)
    pf = priority_fee(MAINNET)
    tip = pf['p50'] if pf else 1.0
    return max(st['max'] * 1.5 + tip, MIN_BASE_FEE_GWEI), tip


def call(to, data):
    return rpc(MAINNET, 'eth_call',
               [{'to': to, 'data': data}, 'latest']).get('result')


def dstr(h):
    if not h or len(h) < 130:
        return None
    b = bytes.fromhex(h[2:])
    ln = int.from_bytes(b[32:64], 'big')
    return b[64:64 + ln].decode('utf-8', 'ignore')


def estimate(tail):
    """
    Real gas estimate via `cast estimate`. NEVER guess a gas limit.
    Lesson learned: a 893-char setContractURI needs 697,558 gas, but I
    guessed 220,000 -> out-of-gas revert that still cost $0.0126.
    """
    p = subprocess.run(
        [CAST, 'estimate', '--rpc-url', MAINNET, '--from', WALLET] + tail,
        capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        sys.exit(f"ABORT: estimate failed: {p.stderr[:300]}")
    return int(p.stdout.strip())


def send(label, tail, pk, gl=None):
    # GATE: always estimate, never trust a hardcoded limit
    if gl is None:
        gl = int(estimate(tail) * 1.25)
        print(f"\n  [estimated gasLimit {gl:,} incl. 25% headroom]")
    max_fee, tip = fees()
    est = gl * max_fee / 1e9
    print(f"\n--- {label} ---")
    print(f"  maxFee {max_fee:.2f} gwei  gasLimit {gl:,}  worst ${est:.4f}")
    if est > CAP_USD:
        sys.exit(f"ABORT: ${est:.4f} exceeds cap ${CAP_USD}")
    cmd = [CAST, 'send', '--rpc-url', MAINNET, '--private-key', pk,
           '--gas-limit', str(gl),
           '--priority-gas-price', str(int(tip * 1e9)),
           '--gas-price', str(int(max_fee * 1e9)), '--json'] + tail
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        print('  STDERR', p.stderr[:500])
        sys.exit('ABORT: send failed')
    r = json.loads(p.stdout.strip())
    gu = to_int(r.get('gasUsed'))
    eff = to_int(r.get('effectiveGasPrice')) or 0
    print(f"  status {r.get('status')}  gasUsed {gu:,}  "
          f"cost ${gu*eff/1e18:.6f}")
    if r.get('status') not in ('0x1', 1):
        sys.exit('ABORT: reverted')
    return gu * eff / 1e18


def main():
    cid = to_int(rpc(MAINNET, 'eth_chainId')['result'])
    assert cid == CHAIN_ID_MAINNET, f"chainId {cid}"
    print(f"GATE chainId {cid} OK")
    pk = key()

    print("\n=== BEFORE ===")
    print(f"  tokenURI(1)   {dstr(call(TOKEN, '0xc87b56dd'+'1'.rjust(64,'0')))!r}")
    print(f"  contractURI() {dstr(call(TOKEN, '0xe8a3d485'))!r}")

    # ---- collection-level metadata ----
    contract_meta = b64_json({
        'name': 'Arc Pathfinder Test',
        'description': ('Technical proving harness for the Coinkins project. '
                        'Validates SeaDrop allowlist + public mint on Arc. '
                        'Not a real collection.'),
        'image': svg_data_uri('APFT', '#1a1a2e'),
        'external_link': 'https://github.com/0xRadikal/Coinkins',
        'seller_fee_basis_points': 500,
        'fee_recipient': WALLET,
    })
    print(f"\n  contractURI payload {len(contract_meta)} chars")

    spent = 0.0
    spent += send('setContractURI',
                  [TOKEN, 'setContractURI(string)', contract_meta],
                  pk)

    # ---- token-level metadata ----
    token_meta = b64_json({
        'name': 'Pathfinder',
        'description': 'On-chain proof that SeaDrop minting works on Arc.',
        'image': svg_data_uri('P', '#0f3460'),
        'attributes': [
            {'trait_type': 'Chain', 'value': 'Arc'},
            {'trait_type': 'Purpose', 'value': 'Technical Test'},
            {'trait_type': 'Standard', 'value': 'ERC721SeaDrop'},
        ],
    })
    print(f"\n  tokenURI payload {len(token_meta)} chars")
    spent += send('setBaseURI (data URI)',
                  [TOKEN, 'setBaseURI(string)', token_meta],
                  pk)

    print("\n=== AFTER (read back from chain) ===")
    t1 = dstr(call(TOKEN, '0xc87b56dd'+'1'.rjust(64, '0')))
    cu = dstr(call(TOKEN, '0xe8a3d485'))
    print(f"  tokenURI(1)   {(t1 or '')[:80]}...")
    print(f"  contractURI() {(cu or '')[:80]}...")

    # decode to prove it is valid JSON metadata
    for label, uri in (('tokenURI(1)', t1), ('contractURI()', cu)):
        if uri and 'base64,' in uri:
            try:
                m = json.loads(base64.b64decode(uri.split('base64,')[1]))
                print(f"\n  {label} decodes to valid JSON:")
                print(f"    name        {m.get('name')!r}")
                print(f"    description {(m.get('description') or '')[:56]!r}")
                print(f"    image       {(m.get('image') or '')[:44]}...")
                if m.get('attributes'):
                    print(f"    attributes  {len(m['attributes'])} traits")
            except Exception as e:
                print(f"  {label} DECODE FAILED: {e}")

    print(f"\n  total spent ${spent:.6f}")
    bal = to_int(rpc(MAINNET, 'eth_getBalance',
                     [WALLET, 'latest'])['result'])/1e18
    print(f"  balance now  {bal:.6f} USDC")


if __name__ == '__main__':
    main()
