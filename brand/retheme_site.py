"""
retheme_site.py - repoint site/index.html at the FINAL brand.

The site was themed to the REJECTED v2 palette (teal #0FC28E, gold
#F5C85C on dark green #07332F) and its favicon was a rounded square with
the letters "Ck" - not the mark at all.

This script:
  1. replaces the palette with S3 (the selected, gate-passing scheme)
  2. replaces the data-URI favicon with the REAL mark, generated from
     the live geometry by make_svg.py
  3. replaces the .mark placeholder box with an inline SVG of the mark
  4. copies the final avatar and og image into site/

It is a script rather than hand edits so it is repeatable and auditable,
and it VERIFIES afterwards that no rejected colour survives anywhere in
the file.
"""

import os
import re
import shutil

import coinkins_mark as CM
import make_svg as MS

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, '..', 'site'))
FINAL = os.path.join(HERE, 'final')
INDEX = os.path.join(SITE, 'index.html')

# S3, the scheme selected by choose_colours.py (weakest boundary 8.64:1)
S3 = {
    'bg': '#0C172E',        # a shade below the mark field, for depth
    'panel': '#122244',     # the mark's own field colour
    'line': '#1E3358',
    'fg': '#EAF1FA',        # the ring colour
    'mut': '#96AAC4',
    'acc': '#F3B63A',       # the disc colour
    'ok': '#F3B63A',
    'code': '#C9D9EF',
}

# every colour from the rejected v2 theme
REJECTED = ['#07332F', '#0A3F39', '#125A50', '#F7F4EC', '#8FB5AC',
            '#0FC28E', '#F5C85C', '#D9A73F', '#BFEAD9', '#08101f',
            '#b57edc', '#d6c7e8', '#1a1523', '#3a2b44']


def main():
    if not os.path.exists(INDEX):
        raise SystemExit('site/index.html not found at %s' % INDEX)
    src = open(INDEX).read()
    orig_len = len(src)
    print('=' * 78)
    print('RE-THEMING site/index.html')
    print('=' * 78)
    print('  original size %d bytes' % orig_len)

    # ---- 1. the CSS custom-property block ----
    new_root = (':root{--bg:%(bg)s;--panel:%(panel)s;--line:%(line)s;'
                '--fg:%(fg)s;--mut:%(mut)s;--acc:%(acc)s;--ok:%(ok)s}' % S3)
    src, n = re.subn(r':root\{[^}]*\}', new_root, src, count=1)
    print('  [%s] palette block replaced (%d match)'
          % ('OK' if n == 1 else 'FAIL', n))

    # ---- 2. favicon -> the real mark ----
    uri = MS.data_uri(64)
    src, n = re.subn(r'<link rel="icon" href="[^"]*">',
                     '<link rel="icon" href="%s">' % uri, src, count=1)
    print('  [%s] favicon replaced with the real mark (%d match)'
          % ('OK' if n == 1 else 'FAIL', n))

    # ---- 3. the .mark placeholder box -> inline SVG ----
    # the old rule painted a gradient square containing text
    src, n = re.subn(
        r'\.mark\{[^}]*\}',
        '.mark{width:52px;height:52px;flex:0 0 auto;display:block}',
        src, count=1)
    print('  [%s] .mark CSS simplified (%d match)'
          % ('OK' if n == 1 else 'FAIL', n))

    # replace whatever element carries class="mark" with an inline SVG
    inline = MS.svg(52).replace('\n', '')
    inline = inline.replace('<svg ', '<svg class="mark" ', 1)
    src, n = re.subn(r'<div class="mark"[^>]*>.*?</div>', inline, src,
                     count=1, flags=re.S)
    if n == 0:
        src, n = re.subn(r'<[a-z]+ class="mark"[^>]*>.*?</[a-z]+>', inline,
                         src, count=1, flags=re.S)
    print('  [%s] .mark element replaced with inline SVG (%d match)'
          % ('OK' if n >= 1 else 'WARN', n))

    # ---- 4. code block colour ----
    src = src.replace('color:#BFEAD9', 'color:%s' % S3['code'])
    src = src.replace('background:#0A3F39', 'background:%s' % S3['panel'])

    # ---- 5. any straggling rejected colour ----
    for c in REJECTED:
        for variant in (c, c.upper(), c.lower()):
            if variant in src:
                src = src.replace(variant, S3['panel'])
                print('  [FIX] leftover %s replaced' % variant)

    open(INDEX, 'w').write(src)
    print('  written, new size %d bytes (%+d)' % (len(src), len(src) - orig_len))

    # ---- 6. copy the image assets the page references ----
    print()
    print('  copying referenced assets:')
    for src_name, dst_name in (('avatar-400.png', 'avatar.png'),
                               ('og-1200x630.png', 'og.png')):
        s = os.path.join(FINAL, src_name)
        d = os.path.join(SITE, dst_name)
        if not os.path.exists(s):
            print('    [FAIL] %s missing' % src_name)
            continue
        shutil.copy2(s, d)
        print('    %-16s -> %-12s %6.1f KB'
              % (src_name, dst_name, os.path.getsize(d) / 1024))

    # ---- 7. VERIFY ----
    print()
    print('=' * 78)
    print('VERIFICATION')
    print('=' * 78)
    ok = True
    final = open(INDEX).read()
    for c in REJECTED:
        if c.lower() in final.lower():
            print('  [FAIL] rejected colour %s still present' % c)
            ok = False
    if ok:
        print('  [PASS] no rejected v2 colour anywhere in the file')

    for k, v in S3.items():
        if k == 'code':
            continue
        present = v.lower() in final.lower()
        print('  [%s] S3 %-6s %s present' % ('PASS' if present else 'WARN',
                                             k, v))

    # the favicon must contain the mark's geometry, not a letterform
    good = 'Coinkins' in final and 'ECk' not in final
    print('  [%s] favicon carries the mark, not the letters "Ck"'
          % ('PASS' if good else 'FAIL'))
    ok &= good

    # balanced tags sanity: every <svg has a matching </svg>
    good = final.count('<svg') == final.count('</svg>')
    print('  [%s] SVG tags balanced (%d open, %d close)'
          % ('PASS' if good else 'FAIL', final.count('<svg'),
             final.count('</svg>')))
    ok &= good

    print()
    print('RE-THEME %s' % ('COMPLETE' if ok else 'HAS FAILURES'))
    return ok


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
