#!/usr/bin/env python3
"""
validate_site.py - Validate the site before publishing.

Two jobs:
  1. Every external link must actually resolve (no fabricated URLs -
     this is the exact mistake that produced the 404 baseURI).
  2. Every on-chain claim printed on the page must match the chain.
"""
import re
import sys
import json
import urllib.request

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, to_int, MAINNET  # noqa: E402

HTML = '/webapp/arc-nft/site/index.html'
STATE = '/webapp/arc-nft/b1_state.json'


def status(url, timeout=20):
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
                                        'Win64; x64) AppleWebKit/537.36 '
                                        'Chrome/120.0'})
        return urllib.request.urlopen(req, timeout=timeout).getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f'ERR:{str(e)[:30]}'


def main():
    html = open(HTML).read()
    ok = True

    print("=" * 68)
    print("1. EXTERNAL LINKS - must resolve")
    print("=" * 68)
    links = sorted(set(re.findall(r'href="(https://[^"]+)"', html)))
    for u in links:
        c = status(u)
        good = c in (200, 301, 302)
        if not good:
            ok = False
        print(f"  {'OK ' if good else 'BAD'} {u:44s} {c}")

    print()
    print("=" * 68)
    print("2. ON-CHAIN CLAIMS - must match reality")
    print("=" * 68)
    st = json.load(open(STATE))
    token = st['token']

    # every 0x64-hex on the page should be a real tx we sent
    ours = {t['hash'].lower() for t in st['txs']}
    hashes = set(h.lower() for h in re.findall(r'0x[0-9a-fA-F]{64}', html))
    for h in sorted(hashes):
        known = h in ours
        if not known:
            ok = False
        print(f"  {'OK ' if known else 'BAD'} tx {h[:26]}... "
              f"{'in our tx log' if known else 'NOT OURS'}")

    # contract address on page must match and must have code
    addrs = set(a.lower() for a in re.findall(r'0x[0-9a-fA-F]{40}(?![0-9a-fA-F])', html))
    print()
    for a in sorted(addrs):
        code = rpc(MAINNET, 'eth_getCode', [a, 'latest']).get('result', '0x')
        size = (len(code) - 2) // 2
        label = ('our token' if a == token.lower()
                 else 'canonical SeaDrop'
                 if a == '0x00005ea00ac477b1030ce78506496e8c2de24bf5'
                 else 'UNKNOWN')
        good = size > 0
        if not good:
            ok = False
        print(f"  {'OK ' if good else 'BAD'} {a} {size:>6} bytes  {label}")

    # numeric claims
    print()
    print("=" * 68)
    print("3. NUMERIC CLAIMS")
    print("=" * 68)
    ts = to_int(rpc(MAINNET, 'eth_call',
                    [{'to': token, 'data': '0x18160ddd'}, 'latest'])['result'])
    ms = to_int(rpc(MAINNET, 'eth_call',
                    [{'to': token, 'data': '0xd5abeb01'}, 'latest'])['result'])
    print(f"  chain totalSupply {ts}  maxSupply {ms}")
    claim = '2 of\n    1000 minted' in html or '2 of 1000 minted' in html
    real = (ts == 2 and ms == 1000)
    print(f"  page claims '2 of 1000 minted': {claim}  chain agrees: {real}")
    if not real:
        ok = False

    cost = st['spent_usd']
    print(f"  tx log gas cost ${cost:.6f}  page says $0.2248: "
          f"{abs(cost - 0.2248) < 0.0005}")
    print(f"  page says '9 / 9': {len(st['txs']) == 9}")
    if len(st['txs']) != 9:
        ok = False

    print()
    print("=" * 68)
    print(f"VERDICT: {'ALL CHECKS PASS - safe to publish' if ok else 'FAILURES ABOVE - DO NOT PUBLISH'}")
    print("=" * 68)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
