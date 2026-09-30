#!/usr/bin/env python3
"""
research_demand.py - Measure what SUCCESSFUL collections actually have,
instead of guessing what "community building" means.

Method: pull real data for collections that DID achieve verification and
volume, and compare their observable attributes. Uses the public OpenSea
endpoints; falls back gracefully when rate-limited so we never fabricate.
"""
import json
import time
import urllib.request

# Mix of: the Arc-era comparable, plus established blue-chips, plus a
# recent successful launch. All chosen because they ARE verified.
TARGETS = [
    'rare-friends-genesis',     # Robinhood chain, verified in ~2 days
    'pudgypenguins',
    'azuki',
    'boredapeyachtclub',
    'doodles-official',
    'moonbirds',
    'milady',
    'cryptopunks',
]


def get(url, tries=3):
    last = ''
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=25))
        except Exception as e:
            last = str(e)[:60]
            time.sleep(2.0 * (i + 1))
    return {'_err': last}


def main():
    print("=" * 78)
    print("WHAT DO VERIFIED COLLECTIONS ACTUALLY HAVE?")
    print("=" * 78)
    rows = []
    for slug in TARGETS:
        c = get(f"https://api.opensea.io/api/v2/collections/{slug}")
        if '_err' in c:
            print(f"  {slug:24s} UNAVAILABLE ({c['_err']})")
            continue
        s = get(f"https://api.opensea.io/api/v2/collections/{slug}/stats")
        tot = s.get('total', {}) if '_err' not in s else {}
        row = {
            'slug': slug,
            'supply': c.get('total_supply'),
            'safelist': c.get('safelist_status'),
            'has_desc': bool((c.get('description') or '').strip()),
            'has_img': bool(c.get('image_url')),
            'has_banner': bool(c.get('banner_image_url')),
            'twitter': c.get('twitter_username'),
            'discord': bool((c.get('discord_url') or '').strip()),
            'website': bool((c.get('project_url') or '').strip()),
            'volume': tot.get('volume'),
            'owners': tot.get('num_owners'),
            'sales': tot.get('sales'),
        }
        rows.append(row)
        print(f"\n  {slug}")
        print(f"    supply {row['supply']}  safelist {row['safelist']}")
        print(f"    volume {row['volume']}  owners {row['owners']}  "
              f"sales {row['sales']}")
        print(f"    desc {row['has_desc']}  image {row['has_img']}  "
              f"banner {row['has_banner']}")
        print(f"    twitter {row['twitter']!r}  discord {row['discord']}  "
              f"site {row['website']}")
        time.sleep(1.5)

    if not rows:
        print("\n  NO DATA - all requests failed. Not inventing numbers.")
        return

    print()
    print("=" * 78)
    print("PATTERN ANALYSIS (only over collections we actually fetched)")
    print("=" * 78)
    n = len(rows)
    print(f"  sample size: {n}")
    for field, label in (('has_desc', 'has description'),
                         ('has_img', 'has image'),
                         ('has_banner', 'has banner'),
                         ('discord', 'has discord'),
                         ('website', 'has website')):
        c = sum(1 for r in rows if r[field])
        print(f"    {label:20s} {c}/{n}  ({100*c/n:.0f}%)")
    tw = sum(1 for r in rows if r['twitter'])
    print(f"    {'has twitter':20s} {tw}/{n}  ({100*tw/n:.0f}%)")

    # owner:item ratio - OpenSea explicitly reviews this
    print()
    print("  OWNER : ITEM RATIO (OpenSea reviews this for verification)")
    for r in rows:
        try:
            ratio = r['owners'] / r['supply']
            print(f"    {r['slug']:24s} {r['owners']:>7} / {r['supply']:>6} "
                  f"= {ratio:.3f}")
        except Exception:
            print(f"    {r['slug']:24s} incomplete data")

    json.dump(rows, open('/webapp/arc-nft/demand_research.json', 'w'),
              indent=2)
    print("\n  saved -> demand_research.json")


if __name__ == '__main__':
    main()
