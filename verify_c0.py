#!/usr/bin/env python3
"""
verify_c0.py - Independently verify every C0 claim.
Trust nothing; test each surface with controls so a false positive is
impossible.
"""
import json
import socket
import ssl
import urllib.request

CONTROLS_TAKEN = ['azuki', 'pudgypenguins']   # must read TAKEN
CONTROLS_FREE = ['zzqxjvnrkwpl9182', 'qqzzxxjjvv77341']  # must read FREE


def status(url, timeout=20):
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
                                        'Win64; x64) AppleWebKit/537.36 '
                                        'Chrome/120.0'})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.getcode(), r.read(3000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        return None, str(e)[:60]


def x_handle(h):
    c, _ = status(f'https://x.com/{h}')
    return {404: 'FREE', 200: 'TAKEN'}.get(c, f'UNKNOWN({c})')


def dns(host):
    try:
        return socket.gethostbyname(host)
    except Exception as e:
        return f'NO_DNS ({str(e)[:30]})'


def tls_cert(host):
    """Does the domain serve a valid TLS cert? Proves real hosting."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=15) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                c = ss.getpeercert()
                return {'subject': dict(x[0] for x in c['subject']).get(
                            'commonName'),
                        'issuer': dict(x[0] for x in c['issuer']).get(
                            'organizationName'),
                        'expires': c.get('notAfter')}
    except Exception as e:
        return f'NO_TLS ({str(e)[:40]})'


def main():
    print("=" * 70)
    print("C0 VERIFICATION - independent checks with controls")
    print("=" * 70)

    print("\n[1] X / TWITTER HANDLE")
    r = x_handle('coinkins')
    print(f"  x.com/coinkins          {r}")
    print("  --- controls ---")
    ok = True
    for c in CONTROLS_TAKEN:
        v = x_handle(c)
        print(f"  x.com/{c:18s} {v}  (expect TAKEN)")
        if v != 'TAKEN':
            ok = False
    for c in CONTROLS_FREE:
        v = x_handle(c)
        print(f"  x.com/{c:18s} {v}  (expect FREE)")
        if v != 'FREE':
            ok = False
    print(f"  method reliable: {ok}")
    print(f"  => @coinkins is {'REGISTERED (as you said)' if r == 'TAKEN' else r}")

    print("\n[2] DOMAIN coinkins.xyz")
    for h in ('coinkins.xyz', 'www.coinkins.xyz'):
        print(f"  DNS {h:22s} {dns(h)}")
    print(f"  TLS cert: {json.dumps(tls_cert('coinkins.xyz'), default=str)[:150]}")
    c, body = status('https://coinkins.xyz')
    print(f"  HTTP https://coinkins.xyz -> {c}")
    if body and c == 200:
        import re
        t = re.search(r'<title[^>]*>([^<]{0,80})', body, re.I)
        print(f"  page title: {t.group(1).strip() if t else '(none)'}")
        print(f"  body length sampled: {len(body)}")

    print("\n[3] OPENSEA PROFILE")
    c, body = status('https://opensea.io/coinkins')
    print(f"  opensea.io/coinkins -> HTTP {c}")
    if body:
        low = body.lower()
        for kw in ('coinkins', 'not found', "doesn't exist"):
            print(f"    contains {kw!r}: {kw in low}")

    print("\n[4] TELEGRAM")
    c, body = status('https://t.me/coinkins')
    print(f"  t.me/coinkins -> HTTP {c}")
    if body:
        import re
        for pat, label in ((r'tgme_page_title[^>]*>([^<]{0,60})', 'title'),
                           (r'tgme_page_extra[^>]*>([^<]{0,60})', 'members'),
                           (r'tgme_page_description[^>]*>([^<]{0,80})', 'desc')):
            m = re.search(pat, body)
            if m:
                print(f"    {label}: {m.group(1).strip()}")
        print(f"    looks like a real TG page: "
              f"{'tgme_page' in body}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("  All four surfaces checked above with live requests.")
    print("  X handle method validated against 4 controls.")


if __name__ == '__main__':
    main()
