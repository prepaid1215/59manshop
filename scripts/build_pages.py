#!/usr/bin/env python3
"""상세페이지 공통 구성 적용 스크립트 (재실행해도 결과가 같다).

- 경로 표시(breadcrumb)를 제목 위로 올리고 '홈 › 가이드 › 카테고리 › 제목' 형태로 만든다.
  (JSON-LD BreadcrumbList·URL·canonical·robots는 건드리지 않는다.)
- 가이드 허브(data/guides.json)에 있는 상세페이지 아래에 제목 영역 대표 일러스트(page-art)를 넣는다.
사용법: python scripts/build_pages.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_art import CAT_ILL, ill_svg  # noqa: E402

DATA = json.loads((ROOT / 'data' / 'guides.json').read_text(encoding='utf-8'))
CATS = {c['key']: c for c in DATA['categories']}
BYHREF = {g['href']: g for g in DATA['guides']}
SEP = '<span class="crumb-sep" aria-hidden="true">›</span>'

CRUMB_RE = re.compile(r'<p class="crumb">(.*?)</p>', re.S)
BAR_RE = re.compile(r'<nav class="crumb-bar".*?</nav>', re.S)
ART_RE = re.compile(r'<div class="site page-art-wrap">.*?</div>', re.S)


def url_of(p):
    rel = p.relative_to(ROOT).as_posix()
    return '/' if rel == 'index.html' else '/' + rel[:-len('index.html')]


def crumb_html(url, h1):
    g = BYHREF.get(url)
    if g:
        c = CATS[g['cat']]
        return ('<a href="/">홈</a>' + SEP + '<a href="/guide/">가이드</a>' + SEP +
                '<a href="/guide/#%s">%s</a>' % (g['cat'], html.escape(c['label'])) + SEP +
                '<span class="crumb-now" aria-current="page">%s</span>' % html.escape(g['title']))
    return None


def art_html(g):
    ill = g.get('ill') or CAT_ILL[g['cat']]
    second = {'check': 'clock', 'sim': 'phone', 'self': 'sim', 'esim': 'phone', 'move': 'shield', 'plan': 'bolt', 'fix': 'alert'}[g['cat']]
    return ('<div class="site page-art-wrap"><figure class="page-art" role="img" aria-label="%s 안내 일러스트">'
            '<span class="pa-main">%s</span><span class="pa-sub">%s</span><span class="pa-dot pa-d1"></span><span class="pa-dot pa-d2"></span></figure></div>'
            % (html.escape(g['title']), ill_svg(ill, 132), ill_svg(second, 72)))


changed = 0
for p in sorted(ROOT.rglob('index.html')):
    if '.git' in p.parts:
        continue
    u = url_of(p)
    if u in ('/', '/guide/'):
        continue
    s = p.read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in s or '<section class="hero' not in s:
        continue
    o = s
    h1 = re.search(r'<h1>([^<]*)</h1>', s)
    # 1) breadcrumb
    m = CRUMB_RE.search(s)
    if m:
        inner = crumb_html(u, h1.group(1) if h1 else '')
        if inner is None:
            inner = m.group(1).replace(' · ', SEP)
        s = CRUMB_RE.sub('', s, count=1)
        s = BAR_RE.sub('', s)
        bar = '<nav class="crumb-bar" aria-label="경로"><div class="site"><p class="crumb">' + inner + '</p></div></nav>'
        s = s.replace('<section class="hero', bar + '<section class="hero', 1)
    # 2) page art
    g = BYHREF.get(u)
    if g and 'hero-art' not in s:
        s = ART_RE.sub('', s)
        s = re.sub(r'(<section class="hero[^>]*>.*?</section>)', lambda mm: mm.group(1) + art_html(g), s, count=1, flags=re.S)
    if s != o:
        p.write_text(s, encoding='utf-8', newline='')
        changed += 1
print('build_pages: %d개 페이지 갱신' % changed)
