#!/usr/bin/env python3
"""
audit_profile.py - Audit what is ACTUALLY missing from each profile.
No assumptions: parse the live pages and report only what is observable.
"""
import re
import urllib.request


def fetch(url, timeout=25):
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
                                        'Win64; x64) AppleWebKit/537.36 '
                                        'Chrome/120.0'})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.getcode(), r.read(200000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        return None, str(e)[:60]


def audit_x():
    print("=" * 70)
    print("X / TWITTER @coinkins")
    print("=" * 70)
    c, h = fetch('https://x.com/coinkins')
    print(f"  HTTP {c}   bytes {len(h)}")
    if not h:
        print("  no body")
        return
    checks = {
        'og:title': r'og:title"\s+content="([^"]*)"',
        'og:description': r'og:description"\s+content="([^"]*)"',
        'og:image': r'og:image"\s+content="([^"]*)"',
    }
    for k, pat in checks.items():
        m = re.search(pat, h)
        v = m.group(1) if m else None
        print(f"  {k:16s} {v!r}")

    # default X avatar detection
    has_default_avatar = 'default_profile' in h or 'default_profile_images' in h
    print(f"\n  default avatar markers present: {has_default_avatar}")
    # look for profile_images (a real uploaded avatar lives here)
    imgs = set(re.findall(r'pbs\.twimg\.com/profile_images/[^\s"\\]+', h))
    banners = set(re.findall(r'pbs\.twimg\.com/profile_banners/[^\s"\\]+', h))
    print(f"  profile_images found : {len(imgs)}")
    for i in list(imgs)[:3]:
        print(f"      {i[:90]}")
    print(f"  profile_banners found: {len(banners)}")
    for b in list(banners)[:3]:
        print(f"      {b[:90]}")

    # bio / description from og
    m = re.search(r'og:description"\s+content="([^"]*)"', h)
    desc = m.group(1) if m else ''
    # X puts "N followers · N following. Joined ..." when there is no bio
    generic = bool(re.match(r'^\d+ followers', desc))
    print(f"\n  bio appears EMPTY (og:desc is just stats): {generic}")
    print(f"  -> {'NEEDS BIO' if generic else 'has some bio text'}")


def audit_telegram():
    print()
    print("=" * 70)
    print("TELEGRAM t.me/coinkins")
    print("=" * 70)
    c, h = fetch('https://t.me/coinkins')
    print(f"  HTTP {c}   bytes {len(h)}")
    if not h:
        return
    for pat, lab in (
            (r'og:title"\s+content="([^"]*)"', 'og:title'),
            (r'og:description"\s+content="([^"]*)"', 'og:description'),
            (r'og:image"\s+content="([^"]*)"', 'og:image'),
            (r'tgme_page_extra[^>]*>([^<]{0,60})', 'subscribers')):
        m = re.search(pat, h)
        print(f"  {lab:16s} {m.group(1).strip() if m else None!r}")
    # telegram shows a letter-avatar placeholder when no photo is set
    has_photo = 'tgme_page_photo_image' in h
    print(f"\n  has profile photo: {has_photo}")
    m = re.search(r'og:description"\s+content="([^"]*)"', h)
    d = m.group(1) if m else ''
    print(f"  description is generic ('Telegram: t.me/...'): "
          f"{d.strip().startswith('Telegram:')}")


def audit_opensea():
    print()
    print("=" * 70)
    print("OPENSEA /coinkins")
    print("=" * 70)
    c, h = fetch('https://opensea.io/coinkins')
    print(f"  HTTP {c}   bytes {len(h)}")
    if not h:
        return
    for pat, lab in (
            (r'<title[^>]*>([^<]{0,90})', 'title'),
            (r'og:image"\s+content="([^"]*)"', 'og:image'),
            (r'og:description"\s+content="([^"]*)"', 'og:description')):
        m = re.search(pat, h, re.I)
        print(f"  {lab:16s} {m.group(1).strip() if m else None!r}")


def audit_domain():
    print()
    print("=" * 70)
    print("DOMAIN coinkins.xyz")
    print("=" * 70)
    import socket
    try:
        ip = socket.gethostbyname('coinkins.xyz')
        print(f"  DNS resolves -> {ip}")
    except Exception as e:
        print(f"  DNS: NOT RESOLVING YET ({str(e)[:40]})")
    c, h = fetch('https://coinkins.xyz')
    print(f"  HTTPS -> {c}")


def main():
    audit_x()
    audit_telegram()
    audit_opensea()
    audit_domain()
    print()
    print("=" * 70)
    print("NOTE: X serves a JS app to bots; absence of a marker is not")
    print("absolute proof. Findings above are observable facts only.")
    print("=" * 70)


if __name__ == '__main__':
    main()
