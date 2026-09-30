#!/usr/bin/env python3
"""
track_community.py - Objectively measure community growth against the gates
in doc 16. No vanity metrics, no guessing.

Records a timestamped snapshot each run so progress is provable over time,
and evaluates each phase gate as PASS/FAIL against hard numbers.

Usage:
    python3 track_community.py            # snapshot + gate evaluation
    python3 track_community.py --history  # show all past snapshots
"""
import json
import os
import sys
import time
import urllib.request

HANDLE = 'coinkins'
DOMAINS = ['coinkins.xyz', 'coinkins.io', 'coinkins.com']
OS_SLUG = 'coinkins'
TELEGRAM = 'coinkins'
HISTORY = '/webapp/arc-nft/community_history.json'

# Gates from doc 16 - derived from measured data, not invented
GATE_C1_FOLLOWERS = 100      # before investing in art
GATE_C3_MULTIPLIER = 1.5     # allowlist must exceed needed owners by 1.5x
OWNER_RATIO = 0.40           # observed median across 8 verified collections


def http_status(url, timeout=15):
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req, timeout=timeout).getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def check_x_handle(handle):
    """
    x.com returns 404 for free handles, 200 for taken ones.
    Controls verified this discriminates correctly (doc 06).
    twitter.com returns 301 for everything -> no signal, not used.
    """
    s = http_status(f'https://x.com/{handle}')
    if s == 404:
        return 'FREE'
    if s == 200:
        return 'TAKEN'
    return f'UNKNOWN({s})'


def check_domain(d):
    """
    RDAP registry lookup, NOT DNS.
    Lesson: coinkins.xyz was registered but returned NXDOMAIN from both
    8.8.8.8 and 1.1.1.1 because it was minutes old and in 'add period'.
    DNS is therefore NOT a valid registration test. RDAP is authoritative.
    """
    import socket
    tld = d.rsplit('.', 1)[-1]
    try:
        req = urllib.request.Request(
            f'https://rdap.centralnic.com/{tld}/domain/{d}',
            headers={'User-Agent': 'Mozilla/5.0'})
        j = json.load(urllib.request.urlopen(req, timeout=20))
        ev = {e.get('eventAction'): e.get('eventDate')
              for e in j.get('events', [])}
        reg = (ev.get('registration') or '')[:10]
        exp = (ev.get('expiration') or '')[:10]
        dnsok = 'yes'
        try:
            socket.gethostbyname(d)
        except Exception:
            dnsok = 'propagating'
        return f'REGISTERED {reg}->{exp} dns:{dnsok}'
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 'AVAILABLE'
        return f'RDAP_ERR({e.code})'
    except Exception as e:
        return f'RDAP_FAIL({str(e)[:24]})'


def check_opensea(slug):
    s = http_status(f'https://api.opensea.io/api/v2/collections/{slug}')
    if s == 200:
        return 'EXISTS'
    if s in (400, 404):
        return 'FREE'
    if s == 401:
        return 'NEEDS_KEY'
    return f'UNKNOWN({s})'


def check_telegram(h):
    """
    t.me returns 200 for both existing and non-existing handles, so status
    alone is NOT a signal. Real channels expose og:title and a
    'N subscriber(s)' string in tgme_page_extra. Parse those instead.
    """
    import re
    c, body = 0, ''
    try:
        req = urllib.request.Request(
            f'https://t.me/{h}', headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=20)
        c = r.getcode()
        body = r.read(20000).decode('utf-8', 'ignore')
    except Exception as e:
        return f'ERR({str(e)[:24]})'
    if 'tgme_page' not in body:
        return 'NO_PAGE'
    m = re.search(r'tgme_page_extra[^>]*>([^<]{0,40})', body)
    subs = m.group(1).strip() if m else '?'
    return f'EXISTS ({subs})'


def load_history():
    if os.path.exists(HISTORY):
        return json.load(open(HISTORY))
    return []


def main():
    if '--history' in sys.argv:
        h = load_history()
        print(f"snapshots: {len(h)}")
        for s in h:
            print(f"  {s['date']}  x={s.get('x_handle')}  "
                  f"followers={s.get('followers')}  "
                  f"allowlist={s.get('allowlist')}")
        return

    snap = {
        'ts': int(time.time()),
        'date': time.strftime('%Y-%m-%d %H:%M', time.gmtime()),
    }

    print("=" * 66)
    print("COINKINS COMMUNITY TRACKER")
    print(f"  {snap['date']} UTC")
    print("=" * 66)

    print("\n--- PHASE C0: identity surfaces ---")
    snap['x_handle'] = check_x_handle(HANDLE)
    print(f"  x.com/{HANDLE:16s} {snap['x_handle']}")
    snap['domains'] = {}
    for d in DOMAINS:
        r = check_domain(d)
        snap['domains'][d] = r
        print(f"  {d:22s} {r}")
    snap['opensea'] = check_opensea(OS_SLUG)
    print(f"  opensea/{OS_SLUG:14s} {snap['opensea']}")
    snap['telegram'] = check_telegram(TELEGRAM)
    print(f"  t.me/{TELEGRAM:17s} {snap['telegram']}")

    owned = (snap['x_handle'] == 'TAKEN'
             and any(v.startswith('REGISTERED')
                     for v in snap['domains'].values())
             and str(snap.get('telegram', '')).startswith('EXISTS'))
    print(f"\n  C0 GATE (all surfaces owned): "
          f"{'PASS' if owned else 'NOT YET'}")
    if not owned:
        print("    -> register @coinkins + coinkins.xyz in ONE sitting")
        print("    -> AND complete the USPTO/WIPO trademark check first")

    # Follower + allowlist counts cannot be scraped reliably without auth.
    # They are entered manually so the number is always REAL, never invented.
    print("\n--- PHASE C1/C3: growth metrics (manual entry) ---")
    print("  These are NOT scraped. Enter real numbers via:")
    print("    python3 track_community.py --set-followers N --set-allowlist N")
    for flag, key in (('--set-followers', 'followers'),
                      ('--set-allowlist', 'allowlist')):
        if flag in sys.argv:
            snap[key] = int(sys.argv[sys.argv.index(flag) + 1])
    hist = load_history()
    prev = hist[-1] if hist else {}
    for key in ('followers', 'allowlist'):
        if key not in snap:
            snap[key] = prev.get(key, 0)
        print(f"  {key:12s} {snap[key]}"
              f"{'  (carried forward)' if key not in sys.argv else ''}")

    print("\n--- GATE EVALUATION ---")
    f = snap['followers']
    print(f"  C1 gate: followers >= {GATE_C1_FOLLOWERS}")
    print(f"    current {f} -> {'PASS' if f >= GATE_C1_FOLLOWERS else 'FAIL'}")
    if f < GATE_C1_FOLLOWERS:
        print(f"    need {GATE_C1_FOLLOWERS - f} more before investing in art")

    a = snap['allowlist']
    print(f"\n  C3 gate depends on chosen supply:")
    print(f"  {'supply':>7} {'owners needed':>14} {'allowlist target':>17} "
          f"{'status':>8}")
    for supply in (100, 250, 500, 1000):
        need = int(supply * OWNER_RATIO)
        target = int(need * GATE_C3_MULTIPLIER)
        ok = 'PASS' if a >= target else 'FAIL'
        print(f"  {supply:>7} {need:>14} {target:>17} {ok:>8}")
    print(f"\n    current allowlist = {a}")
    print("    -> the largest supply whose target you clear is the")
    print("       largest launch you can credibly sell out")

    hist.append(snap)
    json.dump(hist, open(HISTORY, 'w'), indent=2)
    print(f"\n  snapshot saved ({len(hist)} total) -> {HISTORY}")


if __name__ == '__main__':
    main()
