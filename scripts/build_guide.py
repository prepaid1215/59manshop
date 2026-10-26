#!/usr/bin/env python3
"""Static /guide/ adapter for the reference v2.6.2 PHP directory layout.

Original routes, index decisions and copy remain in data/guides.json and HTML.
This replaces the old hub's markup, not just its CSS. Standard library only.
"""
import html
import json
import re
from pathlib import Path
from guide_visuals import FILTERS, art_img, illustration, guide_illustration
from build_hub import transform

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'data/guides.json').read_text(encoding='utf-8'))
PAGE = ROOT / 'guide/index.html'
CATS = {c['key']: c for c in DATA['categories']}
GUIDES = [g for _, g in sorted(enumerate(DATA['guides']), key=lambda pair:(pair[1].get('order', pair[0]),pair[0])) if g.get('visible', True)]
BY_HREF = {g['href']:g for g in GUIDES}
COUNTS = {k:len(GUIDES) if k == 'all' else sum(g['cat']==k for g in GUIDES) for k in CATS}
esc = html.escape
CHEV = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>'
BACK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m14 5-7 7 7 7M7 12h13"/></svg>'
SEARCH = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>'
BULB = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M9 18h6M10 21h4M8 15a6 6 0 1 1 8 0l-1 3H9z"/></svg>'


def category_art(key):
    if key == 'all':
        return '<span class="gh-all-icon"><svg viewBox="0 0 28 28" width="28" height="28" fill="currentColor" aria-hidden="true"><rect width="11" height="11" rx="3"/><rect x="16" width="11" height="11" rx="3"/><rect y="16" width="11" height="11" rx="3"/><rect x="16" y="16" width="11" height="11" rx="3"/></svg></span>'
    return art_img(illustration(key),64,eager=True)


def render():
    parts = ['<div class="hub-meta"><nav class="crumb-bar crumb-inline" aria-label="경로"><p class="crumb"><a href="/">홈</a><span class="crumb-sep" aria-hidden="true">›</span><span class="crumb-now" aria-current="page">가이드</span></p></nav><p class="updated">업데이트: <time datetime="2026-10-23">2026년 10월 23일</time></p></div>']
    parts.append('<section class="gh-directory" id="gh-directory" aria-labelledby="gh-title"><header class="gh-directory-top"><div><div class="gh-label">N-TELECOM GUIDES</div><p class="gh-legacy-kicker">앤텔레콤 가이드</p><h1 id="gh-title">상황에 맞게 찾아보세요</h1><p>개통에 필요한 내용을 상황별로 정리했어요. 검색하거나 항목을 선택하면 상황별 안내를 확인할 수 있어요. 찾는 답변이 없으면 카카오톡으로 문의하세요.</p></div><form class="gh-search" id="gc-form" role="search"><label class="sr-only" for="gc-q">가이드 검색</label>'+SEARCH+'<input id="gc-q" name="q" type="search" placeholder="궁금한 내용을 검색해 보세요 (예: 안면인증, eSIM, 요금제)" autocomplete="off"><button class="gh-clear" type="button" id="gc-clear" aria-label="검색어 지우기" hidden>×</button></form></header><nav class="gh-categories" aria-label="카테고리">')
    for key,c in CATS.items():
        parts.append('<button type="button" class="gc-tile gh-category%s" data-cat="%s" aria-pressed="%s"><span class="gh-category-art">%s</span><span><b>%s</b><small>%d개 가이드</small></span></button>' % (
            ' is-active' if key=='all' else '',key,'true' if key=='all' else 'false',category_art(key),esc(c['label']),COUNTS[key]))
    parts.append('</nav></section>')
    parts.append('<section class="gh-category-view" id="gc-section" aria-labelledby="gc-title"><nav class="gh-breadcrumb" aria-label="선택한 분류"><button id="gh-back" type="button">'+BACK+'카테고리 선택</button><span>개통 안내</span><span aria-hidden="true">›</span><b id="gh-current">전체보기</b></nav><div class="gh-category-hero"><span class="gh-heading-icon" id="gc-head-ic">'+art_img(illustration('all'),64)+'</span><div><span class="gh-selected" id="gh-selected">선택한 카테고리: 전체보기</span><h2 id="gc-title">전체보기</h2><p id="gc-desc">'+esc(CATS['all']['desc'])+'</p></div>'+art_img(illustration('all'),256,'gh-category-art',True)+'<span class="gh-count" id="gc-total"><b>'+str(len(GUIDES))+'</b>개</span></div><div class="gh-subfilters" id="gh-subfilters" role="group" aria-label="세부 분류"></div><p class="sr-only" id="gh-status" role="status" aria-live="polite"></p><ul class="gc-list gh-guide-grid" id="gc-list">')
    for n,g in enumerate(GUIDES,1):
        tags=g.get('tags') or g.get('kw','').split()[:3]
        parts.append('<li data-cat="%s"><a class="gc-card" href="%s" data-kw="%s"><span class="gh-guide-copy"><span class="gh-guide-meta"><span class="gc-num" aria-hidden="true">%02d</span><span class="gc-tag">%s</span></span><b class="gh-guide-title">%s</b><span class="gc-desc">%s</span><span class="gh-guide-tags">%s</span></span>%s<span class="gc-chev">%s</span></a></li>' % (
            g['cat'],esc(g['href'],quote=True),esc(g.get('kw',''),quote=True),n,esc(CATS[g['cat']]['label']),esc(g['title']),esc(g['desc']),''.join('<span>'+esc(t)+'</span>' for t in tags),art_img(guide_illustration(g),512,'gh-guide-art'),CHEV))
    parts.append('</ul><p class="gc-empty" id="gc-empty" hidden>찾는 안내가 없으신가요? 다른 검색어를 입력하거나 <a href="https://pf.kakao.com/_akxmKn/chat" rel="noopener">카카오톡 상담으로 질문해 주세요</a>.</p><aside class="gh-esim-note" id="gh-esim-note" hidden><b>eSIM 개통 전 확인하세요</b><p>지원 기종과 개통 조건은 <a href="/v4-1/topic/esim-new/">L망 eSIM 신규개통 안내</a>에서 확인하세요.</p></aside></section>')
    parts.append('<section class="gh-quick" aria-labelledby="gc-quick-h"><header><div><div class="gh-label">QUICK START</div><span class="gh-quick-kicker">자주 찾는 답변</span><h2 id="gc-quick-h">먼저 확인해 보세요</h2></div><a href="/앤텔레콤-선불폰-개통-방법/">처음 오셨나요?'+CHEV+'</a></header><div class="gh-quick-grid">')
    for n,x in enumerate(DATA['quick'],1):
        g=BY_HREF[x['href']]
        parts.append('<a class="gh-quick-card%s" href="%s"><span class="gh-quick-meta"><span>%02d</span>%s</span><b>%s</b><span class="gh-quick-desc">%s</span>%s<span class="gh-quick-go">안내 보기%s</span></a>' % (' is-hot' if n==1 else '',esc(g['href']),n,esc(x['label']),esc(g['title']),esc(g['desc']),art_img(guide_illustration(g),512,'gh-quick-art'),CHEV))
    parts.append('</div></section>')
    parts.append('<section class="gh-proof" aria-labelledby="gh-proof-title"><header><span class="gh-label">REAL GUIDE</span><h2 id="gh-proof-title">실제 화면으로 확인하세요</h2><p>실제 유심 사진과 개통 화면을 함께 확인할 수 있어요.</p></header><div class="gh-proof-grid">')
    for g in GUIDES:
        if g.get('img'):
            parts.append('<a href="%s"><img src="%s" width="96" height="96" alt="%s 실제 안내 자료" loading="lazy"><span>%s</span>%s</a>' % (esc(g['href']),esc(g['img']),esc(g['title']),esc(g['title']),CHEV))
    parts.append('</div></section><section class="gh-ask"><h2>'+BULB+'이런 내용이 궁금하신가요?</h2><ul>')
    for x in DATA['asks']:
        parts.append('<li><a href="%s"><span>%s</span>%s</a></li>' % (esc(x['href']),esc(x['text']),CHEV))
    parts.append('</ul></section><section class="gh-cta"><h2>바로 개통하고 싶으신가요?</h2><p>필요한 내용을 확인했다면 개통을 시작하거나 카카오톡으로 물어보세요.</p><div class="cta"><a class="button" href="https://preplan.site/?from=59man_guide">개통 시작하기 →</a><a class="button alt" href="https://pf.kakao.com/_akxmKn/chat" rel="noopener">카카오톡 상담하기</a></div></section>')
    return '<main id="main-content" class="site content"><div class="layout"><article class="article">'+''.join(parts)+'</article></div></main>'


def build():
    page=PAGE.read_text(encoding='utf-8')
    page=re.sub(r'<main\b[^>]*>.*?</main>',lambda _m:render(),page,count=1,flags=re.S)
    payload={k:{'label':c['label'],'desc':c['desc'],'art':illustration(k),'filters':FILTERS.get(k,[])} for k,c in CATS.items()}
    page=re.sub(r'<script id="gc-data"[^>]*>.*?</script>','',page,flags=re.S)
    page=page.replace('</body>','<script id="gc-data" type="application/json">'+json.dumps(payload,ensure_ascii=False).replace('</',r'<\/')+'</script></body>')
    page=re.sub(r'<body[^>]*>','<body class="guide-hub visual-guide is-category-all">',page,count=1)
    page=transform(page,'/guide/')
    if '/assets/guide-hub.css' not in page:
        page=page.replace('</head>','<link rel="stylesheet" href="/assets/guide-hub.css?v=20261026-read1"></head>')
    page=re.sub(r'(/assets/guide-hub\.css\?v=)[^"]+',lambda m:m.group(1)+'20261025-mobile',page)
    PAGE.write_text(page,encoding='utf-8',newline='')
    print('Visual guide: %d static cards, v2.6.2 directory layout' % len(GUIDES))


if __name__=='__main__':
    build()
