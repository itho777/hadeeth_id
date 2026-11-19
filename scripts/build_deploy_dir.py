"""Build a clean deploy directory for the Cloudflare Worker.

WHY THIS EXISTS
Wrangler with `assets.directory = "."` walked 1,382,002 files and died at the
4 GB heap. `.assetsignore` did not reduce that count at all (measured: 1,382,002
before and after). Rather than depend on ignore-file semantics, we stage exactly
what the site serves into `dist/` and point wrangler at that.

WHAT SHIPS  (anything a browser or the Worker may request)
  *.html, css/, js/, assets/           site shell
  data/hadiths/                        per-hadith JSON
  data/commentaries/                   syarah JSON
  data/chapters/, data/lidwa-chapters/ chapter metadata
  data/api/                            legacy ndjson API
  data/editions/                       edition indexes
  data/rawis/                          narrator profiles
  data/links/, data/meta/              link graphs / meta
  data/mapping-stats.json              published mapping summary
  _headers, _redirects                 Pages/Workers routing

WHAT DOES NOT SHIP
  .git, .github, .wrangler, node_modules
  data/sources/          raw upstream input (652k files)
  scratch/, scripts/, tmp*/
  *.log, *.py, *.db, *_links.json, backups

Usage:  python scripts/build_deploy_dir.py [--force]
"""
import os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')

SHIP_DIRS = [
    'css', 'js', 'assets',
    'data/hadiths', 'data/commentaries', 'data/chapters', 'data/lidwa-chapters',
    'data/api', 'data/editions', 'data/rawis', 'data/links', 'data/meta',
    'data/commentaries/en',
]
SHIP_FILES = ['_headers', '_redirects']
SKIP_FILE_SUFFIX = ('.map',)
SKIP_NAMES = {'Thumbs.db', 'Desktop.ini'}


def main():
    if os.path.isdir(DIST):
        if '--force' not in sys.argv:
            print(f'{DIST} exists. Re-run with --force to rebuild.')
            return
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    file_count = 0

    # top-level html
    for f in sorted(os.listdir(ROOT)):
        if f.endswith('.html') and os.path.isfile(os.path.join(ROOT, f)):
            shutil.copy2(os.path.join(ROOT, f), os.path.join(DIST, f))
            file_count += 1

    for f in SHIP_FILES:
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(DIST, f))
            file_count += 1

    for rel in SHIP_DIRS:
        src = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.isdir(src):
            continue
        dst_base = os.path.join(DIST, rel.replace('/', os.sep))
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
            rel_dir = os.path.relpath(root, src)
            target = dst_base if rel_dir == '.' else os.path.join(dst_base, rel_dir)
            os.makedirs(target, exist_ok=True)
            for f in files:
                if f.endswith(SKIP_FILE_SUFFIX) or f in SKIP_NAMES:
                    continue
                try:
                    shutil.copy2(os.path.join(root, f), os.path.join(target, f))
                    file_count += 1
                except OSError as e:
                    print('skip', f, e)

    # the published mapping summary the docs page reads
    ms = os.path.join(ROOT, 'data', 'mapping-stats.json')
    if os.path.isfile(ms):
        os.makedirs(os.path.join(DIST, 'data'), exist_ok=True)
        shutil.copy2(ms, os.path.join(DIST, 'data', 'mapping-stats.json'))
        file_count += 1

    total = sum(len(f) for _, _, f in os.walk(DIST))
    print(f'staged {total} files into {DIST}')
    for d in ('css', 'js', 'assets', 'data/hadiths', 'data/commentaries', 'data/api'):
        p = os.path.join(DIST, d.replace('/', os.sep))
        if os.path.isdir(p):
            n = sum(len(f) for _, _, f in os.walk(p))
            print(f'  {d}: {n}')


if __name__ == '__main__':
    main()