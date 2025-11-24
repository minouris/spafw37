#!/usr/bin/env python3
"""
Find built wheel and sdist in `dist/`, extract Requires-Python from the wheel METADATA,
and print three lines: wheel_path, sdist_path (empty string if none), requires_python.
Exit codes:
  2 - no wheel found
  3 - METADATA missing inside wheel
  4 - Requires-Python missing
  5 - sdist required but not found
"""
import sys, os, glob, zipfile, re

def main():
    dist = sys.argv[1] if len(sys.argv) > 1 else 'dist'
    require_sdist = (len(sys.argv) > 2 and sys.argv[2].lower() in ('1','true','yes'))

    wheels = glob.glob(os.path.join(dist, '*.whl'))
    if not wheels:
        print('ERROR: No wheel files found in dist/', file=sys.stderr)
        sys.exit(2)

    # prefer py3 tagged wheels
    pattern = re.compile(r'py3-none-any|py2.py3-none-any|py3-none-any')
    selected = None
    for w in wheels:
        if pattern.search(w):
            selected = w
            break
    if not selected:
        selected = wheels[0]

    sdists = glob.glob(os.path.join(dist, '*.tar.gz'))
    selected_sdist = sdists[0] if sdists else ''

    with zipfile.ZipFile(selected) as z:
        meta = None
        for name in z.namelist():
            if name.endswith('METADATA'):
                meta = name
                break
        if not meta:
            print('ERROR: METADATA not found inside wheel', file=sys.stderr)
            sys.exit(3)
        data = z.read(meta).decode('utf-8', errors='ignore')
        m = re.search(r'^Requires-Python:\s*(.+)$', data, flags=re.M|re.I)
        req = m.group(1).strip() if m else ''
        if not req:
            print('ERROR: Requires-Python not present in METADATA', file=sys.stderr)
            sys.exit(4)

    if require_sdist and not selected_sdist:
        print('ERROR: No sdist found but require_sdist is true', file=sys.stderr)
        sys.exit(5)

    # Print the values (one per line)
    print(selected)
    print(selected_sdist)
    print(req)

if __name__ == '__main__':
    main()
