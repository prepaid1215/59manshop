#!/usr/bin/env python3
"""가이드 허브(/guide/) 생성 스크립트 (표준 라이브러리만 사용).

data/guides.json 의 카테고리·가이드 목록으로 <main> 영역을 만든다.
- 검색엔진이 읽을 수 있도록 모든 카드가 정적 HTML로 들어간다.
- 카테고리 개수는 데이터에서 계산한다(하드코딩 없음).
- 새 가이드는 data/guides.json 에 한 항목을 추가하고 이 스크립트를 실행하면 목록·개수에 반영된다.
사용법: python scripts/build_guide.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'data' / 'guides.json').read_text(encoding='utf-8'))
PAGE = ROOT / 'guide' / 'index.html'

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_art import CAT_ILL, ILL, ill_svg  # noqa: E402

# 가이드별 썸네일/키워드/인기(quick start). href 기준.
META = {g['href']: g for g in DATA['guides']}
QUICK = [x['href'] for x in DATA['quick']]
QUICK_LABEL = [x['label'] for x in DATA['quick']]

CHEV = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>'
SEARCH = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/></svg>'
BULB = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/></svg>'
Q = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 0 1 4.8 1c0 1.7-2.4 2.2-2.4 3.7"/><path d="M12 17.2h.01"/></svg>'


def esc(s):
    return html.escape(s, quote=True)


def thumb(g, size=64):
    m = META[g['href']]
    if 'img' in m:
        cls = ' is-cover' if m.get('cover') else ''
        return '<span class="gc-thumb%s"><img src="%s" alt="" width="72" height="72" loading="lazy"></span>' % (cls, m['img'])
    return '<span class="gc-thumb">%s</span>' % ill_svg(m['ill'], size)


cats = {c['key']: c for c in DATA['categories']}
guides = DATA['guides']
for g in guides:
    assert g['href'] in META, g['href']
    assert g['cat'] in cats, g['cat']
counts = {k: sum(1 for g in guides if g['cat'] == k) for k in cats}
counts['all'] = len(guides)

parts = []
parts.append('<nav class="crumb-bar crumb-inline" aria-label="경로"><p class="crumb"><a href="/">홈</a><span class="crumb-sep" aria-hidden="true">›</span><span class="crumb-now" aria-current="page">가이드</span></p></nav>')
parts.append('<p class="updated">업데이트: <time datetime="2026-10-23">2026년 10월 23일</time></p>')
parts.append('<header class="gc-hero"><div class="gc-kicker">ALL GUIDES</div><h1>상황에 맞게 찾아보세요</h1>'
             '<p>개통에 필요한 내용을 상황별로 정리했어요. 원하는 항목을 선택하면 자세한 안내를 볼 수 있어요.</p>'
             '<form class="gc-search" id="gc-form" role="search"><label for="gc-q" class="sr-only">가이드 검색</label>' + SEARCH +
             '<input id="gc-q" type="search" placeholder="궁금한 내용을 검색해 보세요 (예: 안면인증, eSIM, 요금제)" autocomplete="off">'
             '<button type="button" class="gc-clear" id="gc-clear" aria-label="검색어 지우기" hidden>&times;</button></form></header>')

# QUICK START
byhref = {g['href']: g for g in guides}
q = ['<section class="gc-quick" aria-labelledby="gc-quick-h"><div class="gc-quick-head"><div><div class="gc-kicker">QUICK START</div><h2 id="gc-quick-h">먼저 확인해 보세요</h2></div>'
     '<a class="gc-first" href="/앤텔레콤-선불폰-개통-방법/">처음 오셨나요?' + CHEV + '</a></div><div class="gc-quick-grid">']
for i, h in enumerate(QUICK):
    g = byhref[h]
    q.append('<a class="gc-quick-card%s" href="%s"><span class="gc-qn">%02d</span><span class="gc-qtag">%s</span><b>%s</b><span class="gc-qdesc">%s</span>'
             '<span class="gc-qart">%s</span><span class="gc-qgo">안내 보기%s</span></a>' % (
                 ' is-hot' if i == 0 else '', esc(h), i + 1, esc(QUICK_LABEL[i]), esc(g['title']), esc(g['desc']),
                 ill_svg(META[h].get('ill') or CAT_ILL[g['cat']], 84), CHEV))
q.append('</div></section>')
parts.append(''.join(q))

# 카테고리 타일
t = ['<nav class="gc-tiles" aria-label="카테고리">']
for k, c in cats.items():
    t.append('<button type="button" class="gc-tile%s" data-cat="%s" aria-pressed="%s"><span class="gc-ic">%s</span><b>%s</b><small>%d개 가이드</small></button>' % (
        ' is-active' if k == 'all' else '', k, 'true' if k == 'all' else 'false', ill_svg(CAT_ILL[k], 44), esc(c['label']), counts[k]))
t.append('</nav>')
parts.append(''.join(t))

# 목록
c0 = cats['all']
parts.append('<div class="gc-split" id="gc-split"><section class="gc-section" id="gc-section"><div class="gc-head" id="gc-head"><span class="gc-head-ic" id="gc-head-ic">%s</span>'
             '<div><h2 id="gc-title">%s</h2><p id="gc-desc">%s</p></div><span class="gc-total" id="gc-total"><b>%d</b>개</span></div>' % (
                 ill_svg(CAT_ILL['all'], 44), esc(c0['label']), esc(c0['desc']), counts['all']))
parts.append('<ul class="gc-list" id="gc-list">')
for g in guides:
    parts.append('<li data-cat="%s"><a class="gc-card" href="%s" data-kw="%s"><span class="gc-num"></span><span class="gc-body">'
                 '<span class="gc-tag">%s</span><b>%s</b><span class="gc-desc">%s</span></span>%s<span class="gc-chev">%s</span></a></li>' % (
                     g['cat'], esc(g['href']), esc(META[g['href']]['kw']), esc(cats[g['cat']]['label']), esc(g['title']), esc(g['desc']), thumb(g), CHEV))
parts.append('</ul><p class="gc-empty" id="gc-empty" hidden>일치하는 가이드가 없어요. 다른 검색어로 찾아보거나 카테고리를 선택해 보세요.</p></section><aside class="gc-pane" id="gc-pane" aria-label="가이드 미리보기" hidden></aside></div>')

# 궁금하신가요
a = ['<section class="gc-ask"><h2>' + BULB + '이런 내용이 궁금하신가요?</h2><ul>']
for x in DATA['asks']:
    a.append('<li><a href="%s"><span>%s</span>%s</a></li>' % (esc(x['href']), esc(x['text']), CHEV))
a.append('</ul></section>')
parts.append(''.join(a))

parts.append('<section class="gc-cta"><h2>바로 개통하고 싶으신가요?</h2><p>필요한 내용을 확인했다면 개통을 시작하거나 카카오톡으로 물어보세요.</p>'
             '<div class="cta"><a class="button" href="https://preplan.site/?from=59man_guide">개통 시작하기 →</a>'
             '<a class="button alt" href="https://pf.kakao.com/_akxmKn/chat" rel="noopener">카카오톡 상담하기</a></div></section>')

main_html = ('<main class="site content"><div class="layout"><article class="article">' + ''.join(parts) + '</article></div></main>')

# 카테고리 데이터는 JS가 읽도록 JSON 한 덩어리로 전달(타일 아이콘 포함)
page = PAGE.read_text(encoding='utf-8')
page = re.sub(r'<main class="site content">.*?</main>', lambda m: main_html, page, count=1, flags=re.S)
payload = json.dumps({k: {'label': c['label'], 'desc': c['desc'], 'icon': ill_svg(CAT_ILL[k], 44)} for k, c in cats.items()}, ensure_ascii=False)
page = re.sub(r'<script id="gc-data"[^>]*>.*?</script>', '', page, flags=re.S)
page = page.replace('</body>', '<script id="gc-data" type="application/json">' + payload.replace('</', '<\\/') + '</script></body>', 1)
if '/assets/guide.js' not in page:
    page = page.replace('</body>', '<script src="/assets/guide.js" defer></script></body>', 1)
# 이전 인라인 스크립트(구버전 허브 JS) 제거
page = re.sub(r'<script>\(function\(\)\{var D=.*?</script>', '', page, flags=re.S)
if '<body class="guide-hub">' not in page:
    page = re.sub(r'<body[^>]*>', '<body class="guide-hub">', page, count=1)
PAGE.write_text(page, encoding='utf-8', newline='')
print('guide/index.html 생성: 가이드 %d개, 카테고리 %d개' % (len(guides), len(cats) - 1))
