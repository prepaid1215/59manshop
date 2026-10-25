#!/usr/bin/env python3
"""Compare all routes, head metadata, body text, links and real images to a Git ref.

python scripts/check_preservation.py [--base 727568f]
Uses only the standard library. Additions are allowed; original content is required.
"""
import collections
import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding='utf-8')


class Snapshot(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.head = False
        self.body = False
        self.skip = 0
        self.metadata, self.links, self.images, self.text = [], set(), set(), collections.Counter()
        self.feed(source)
        self.title = re.findall(r'<title>(.*?)</title>', source, re.S)
        self.ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'head': self.head = True
        if tag == 'body': self.body = True
        if tag in ('script', 'style'): self.skip += 1
        if self.head and (tag == 'meta' or (tag == 'link' and a.get('rel') != 'stylesheet')):
            self.metadata.append([tag, sorted(attrs)])
        if tag == 'a' and 'href' in a: self.links.add(a['href'])
        if tag == 'img' and 'src' in a:
            src = a['src']
            if not any(x in src for x in ('/img/ui/', '/img/icons/', 'mascot', 'brand-59man')):
                self.images.add(src)

    def handle_endtag(self, tag):
        if tag == 'head': self.head = False
        if tag == 'body': self.body = False
        if tag in ('script', 'style'): self.skip -= 1

    def handle_data(self, data):
        if self.body and not self.skip:
            value = re.sub(r'\s+', ' ', data).strip()
            if value: self.text[value] += 1


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args], cwd=ROOT).decode('utf-8')


def check(base):
    files = git('ls-tree', '-r', '--name-only', base).splitlines()
    old_pages = [x for x in files if x.endswith('index.html')]
    new_pages = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('index.html') if '.git' not in p.parts}
    errors, rows = [], []
    if set(old_pages) != new_pages: errors.append('HTML route set changed')
    for filename in old_pages:
        if not (ROOT / filename).exists(): continue
        old = Snapshot(git('show', base + ':' + filename))
        new = Snapshot((ROOT / filename).read_text(encoding='utf-8'))
        issues = []
        if old.metadata != new.metadata or old.title != new.title or old.ld != new.ld:
            issues.append('SEO head metadata/title/JSON-LD changed')
        if old.links - new.links: issues.append('removed links: ' + str(sorted(old.links - new.links)))
        if old.images - new.images: issues.append('removed real images: ' + str(sorted(old.images - new.images)))
        missing = old.text - new.text
        if missing: issues.append('removed body text: ' + str(dict(missing)))
        rows.append({'file': filename, 'passed': not issues, 'issues': issues})
        errors.extend(filename + ': ' + i for i in issues)
    for filename in ('robots.txt', 'sitemap.xml', 'CNAME'):
        before = subprocess.check_output(['git', 'show', base + ':' + filename], cwd=ROOT)
        after = (ROOT / filename).read_bytes()
        if before.replace(b'\r\n', b'\n') != after.replace(b'\r\n', b'\n'): errors.append(filename + ' changed')
    report = {'base': git('rev-parse', base).strip(), 'pages': len(old_pages), 'failures': errors, 'results': rows}
    out = ROOT / 'reports/seo-preservation.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Preservation: %d pages; %d failures' % (len(old_pages), len(errors)))
    for e in errors: print(e)
    return not errors


if __name__ == '__main__':
    base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else '727568f'
    sys.exit(0 if check(base) else 1)
