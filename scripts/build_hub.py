#!/usr/bin/env python3
"""Apply shared responsive HTML components without rewriting existing article content.

Run build_guide.py, build_pages.py, then this script. Re-running is safe.
"""
import html
import json
import re
from pathlib import Path
from guide_visuals import guide_illustration, art_img

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'data/guides.json').read_text(encoding='utf-8'))
CATS = {c['key']: c for c in DATA['categories']}
GUIDES = DATA['guides']
ICONS = {'all':'all','check':'check','sim':'sim','self':'self','esim':'esim','move':'move','plan':'plan','fix':'fix'}
VERSION = '20261026-read1'
CHEV = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>'


def icon(cat):
    return '<img src="/img/icons/guides-%s.svg" width="32" height="32" alt="" aria-hidden="true">' % ICONS[cat]


def category_key(url):
    current = next((g for g in GUIDES if g['href'].split('#')[0] == url), None)
    if current:
        return current['cat']
    legacy = {'/guide/activation/':'self', '/guide/arrears-suspension/':'move',
              '/guide/kt-baro-usim/':'sim', '/guide/lg-onechip/':'sim',
              '/guide/plans/':'plan', '/guide/usim/':'sim'}
    if url in legacy:
        return legacy[url]
    # Older noindex routes still need a relevant list and mobile return link.
    if any(word in url for word in ('요금제', '충전', '/guide/plans/')): return 'plan'
    if '미납' in url or '번호이동' in url: return 'move'
    if any(word in url for word in ('안됨', '실패', '인식')): return 'fix'
    if '셀프' in url or url == '/guide/activation/': return 'self'
    if any(word in url for word in ('유심', '원칩', '/guide/usim/')): return 'sim'
    return 'check'


def context_card(g, number, selected):
    return ('<a class="context-card%s" href="%s"%s><span class="context-number">%02d</span><span><small>%s</small><b>%s</b><span class="context-desc">%s</span></span>%s</a>' % (
        ' is-selected' if g['href'].split('#')[0] == selected else '', html.escape(g['href']),
        ' aria-current="page"' if g['href'].split('#')[0] == selected else '', number,
        html.escape(CATS[g['cat']]['label']), html.escape(g['title']), html.escape(g['desc']), CHEV))


def context(url):
    cat = category_key(url)
    group = [g for g in GUIDES if g['cat'] == cat]
    return ('<aside class="guide-context" aria-label="같은 주제 가이드"><a class="context-back" href="/guide/#%s">'
            '<span aria-hidden="true">←</span> %s 목록</a><div class="context-list"><div class="context-heading">%s<h2>%s</h2><span>%d개 가이드</span></div>%s'
            '<a class="context-all" href="/guide/">모든 가이드 찾아보기 %s</a></div>'
            '<div class="context-help"><span class="section-kicker">도움이 필요하신가요?</span><b>어느 단계에서 막히셨나요?</b><p>화면을 보내 주시면 확인을 도와드려요.</p><a href="https://pf.kakao.com/_akxmKn/chat" rel="noopener">카카오톡 상담 %s</a></div></aside>' % (
                cat, html.escape(CATS[cat]['label']), icon(cat), html.escape(CATS[cat]['label']), len(group),
                ''.join(context_card(g, n, url) for n,g in enumerate(group,1)), CHEV, CHEV))


def categories(url):
    selected = category_key(url)
    items = []
    for c in DATA['categories']:
        key = c['key']
        count = len(GUIDES) if key == 'all' else sum(g['cat'] == key for g in GUIDES)
        items.append('<a class="gc-tile%s" href="/guide/%s">%s<b>%s</b><small>%d개 가이드</small></a>' % (
            ' is-active' if key == selected else '', '' if key == 'all' else '#'+key,
            '<span class="gc-ic">'+icon(key)+'</span>', html.escape(c['label']), count))
    return '<nav class="gc-tiles detail-categories" aria-label="상황별 가이드">' + ''.join(items) + '</nav>'


def transform(page, url):
    if 'http-equiv="refresh"' in page: return page
    # One design system replaces the previous cascading override stylesheets.
    page = re.sub(r'<link rel="stylesheet" href="/assets/(?:v4-1-final|service-center)\.css[^\"]*">', '', page)
    if '/assets/hub.css' not in page:
        page = page.replace('</head>', '<link rel="stylesheet" href="/assets/hub.css?v=%s"></head>' % VERSION)
    page = re.sub(r'(/assets/hub\.css\?v=)[^\"]+', lambda match: match.group(1)+VERSION, page)
    page = page.replace('src="/assets/site.js"', 'src="/assets/site.js?v=%s"' % VERSION)
    page = page.replace('src="/assets/guide.js"', 'src="/assets/guide.js?v=%s"' % VERSION)
    page = re.sub(r'<img class="brand-mascot"[^>]*>', '<img class="brand-mascot" src="/img/icons/brand-mark.svg" width="36" height="36" alt="">', page)
    if 'class="brand-caption"' not in page:
        page = page.replace('<span>59만모바일</span></a>', '<span>59만모바일</span><span class="brand-caption">앤텔레콤 정보 가이드</span></a>', 1)
    if 'class="desktop-nav"' not in page:
        nav = '<nav class="desktop-nav" aria-label="주 메뉴">'
        for href,label in [('/','홈'),('/guide/','가이드'),('/v4-1/topic/plan-compare/','요금제'),('/편의점-선불유심/','유심 안내')]:
            active = url == href or (href == '/guide/' and url not in ('/','/v4-1/topic/plan-compare/','/편의점-선불유심/'))
            nav += '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if active else '', label)
        nav += '<a class="nav-apply" href="https://preplan.site/?from=59man_menu">개통 시작하기 '+CHEV+'</a></nav>'
        page = page.replace('<details class="top-menu">', nav+'<details class="top-menu">',1)
    if 'class="skip-link"' not in page:
        page = re.sub(r'(<body[^>]*>)', r'\1<a class="skip-link" href="#main-content">본문 바로가기</a>', page, count=1)
    page = re.sub(r'<div class="site page-art-wrap">.*?</div>', '', page, flags=re.S)
    page = re.sub(r'<img[^>]*class="(?:activation-mascot|home-brand)"[^>]*>', '', page)
    page = re.sub(r'(<span class="ic-art">)<svg\b.*?</svg>', lambda m:m.group(1)+icon('check'), page, flags=re.S)
    # Old decorative SVGs become the same flat brand icons used in navigation.
    page = re.sub(r'<img[^>]*src="/img/ui/[^\"]*"[^>]*>', icon('check'), page)
    if url == '/':
        def illustrated_feature(match):
            opening, href, content = match.groups()
            guide = next((g for g in GUIDES if g['href'] == href), None)
            if not guide:
                return match.group(0)
            if 'hf-art' in content:
                content = re.sub(r'(<img class="hf-art" src=")[^"]+',lambda m:m.group(1)+guide_illustration(guide),content,count=1)
                return opening + content + '</a>'
            content = re.sub(r'<img\b', '<img class="hf-proof"', content, count=1)
            content += art_img(guide_illustration(guide),512,'hf-art') + '<span class="hf-source">실제 안내 자료</span>'
            content += '<span class="hf-go">안내 보기' + CHEV + '</span>'
            return opening + content + '</a>'
        page = re.sub(r'(<a class="home-featured-card" href="([^"]+)">)(.*?)</a>',illustrated_feature,page,flags=re.S)
        if 'class="hero-checklist"' not in page:
            checklist = '<div class="hero-checklist"><div class="checklist-top">'+icon('check')+'<span>개통 전, 이것부터</span><span class="checklist-label">START HERE</span></div>'
            for n,cat,title,desc in [('01','check','신청 조건 확인','본인 명의 인증과 개통 가능 시간'),('02','sim','유심 · 요금제 선택','사용할 통신망에 맞게 준비'),('03','self','셀프개통 시작','신청부터 승인 · 첫 충전까지')]:
                checklist += '<a href="/guide/#%s"><span class="checklist-num">%s</span><span><b>%s</b><small>%s</small></span>%s</a>' % (cat,n,title,desc,CHEV)
            checklist += '<div class="checklist-bottom">준비부터 이용까지, 필요한 안내를 한곳에서</div></div>'
            page = page.replace('</div></div></section><main', '</div>'+checklist+'</div></section><main',1)
        # Move quick-start cards before category browsing, retaining their exact copy/links.
        if 'hub-home' not in page:
            purpose = re.search(r'<section class="purpose-grid">.*?</section>',page,re.S)
            featured = re.search(r'<section class="home-featured".*?</section>',page,re.S)
            if purpose and featured:
                page = page.replace(purpose.group(0),'',1)
                page = page.replace(featured.group(0),featured.group(0)+purpose.group(0),1)
            page = page.replace('<body class="home">','<body class="home hub-home">')
            page = re.sub(r'(<a class="home-featured-card"[^>]*>)', r'\1<span class="hf-number" aria-hidden="true"></span>',page)
    elif url != '/guide/' and 'detail-workspace' not in page:
        main = re.search(r'<main class="site content">(.*?)</main>', page, re.S)
        article = re.search(r'<article class="article">(.*?)</article>', main.group(1), re.S) if main else None
        if article:
            before = page[:main.start()]
            prefix_start = before.index('</header>') + len('</header>')
            prefix = before[prefix_start:]
            hero = re.search(r'<section class="hero[^>]*>.*?</section>', prefix, re.S)
            crumb = re.search(r'<nav class="crumb-bar".*?</nav>', prefix, re.S)
            heading = (crumb.group(0) if crumb else '') + (hero.group(0) if hero else '')
            heading = heading.replace('<div class="site">','<div class="detail-heading-inner">')
            extra = prefix
            if hero: extra = extra.replace(hero.group(0),'',1)
            if crumb: extra = extra.replace(crumb.group(0),'',1)
            content = article.group(1)
            if extra.strip():
                # Answer first; the existing activation flow follows the short answer.
                content = content.replace('</section>', '</section>'+extra,1)
            newmain = '<main class="site content detail-content">'+categories(url)+'<div class="detail-workspace">'+context(url)+'<article class="article detail-article">'+heading+content+'</article></div></main>'
            page = before[:prefix_start] + newmain + page[main.end():]
    if url not in ('/', '/guide/') and 'detail-workspace' in page:
        page = re.sub(r'<aside class="guide-context".*?</aside>', lambda _m:context(url), page, count=1, flags=re.S)
        page = re.sub(r'<nav class="gc-tiles detail-categories".*?</nav>', lambda _m:categories(url), page, count=1, flags=re.S)
    page = page.replace('<main class="site content"', '<main id="main-content" class="site content"',1)
    if 'id="main-content"' not in page:
        page = page.replace('<main class="site content detail-content"','<main id="main-content" class="site content detail-content"',1)
    # A contextual visual belongs to the article itself, after its heading.
    # Only known guide URLs receive generated art; official photos remain untouched.
    if url not in ('/', '/guide/') and 'detail-workspace' in page and 'detail-lead-visual' not in page:
        current_guide = next((g for g in GUIDES if g['href'].split('#')[0] == url), None)
        if current_guide:
            cover_src = guide_illustration(current_guide)
            cover = ('<figure class="detail-lead-visual" aria-label="주제별 안내 삽화">'
                     '<img src="%s" width="512" height="512" alt="" loading="eager" decoding="async">'
                     '</figure>') % html.escape(cover_src, quote=True)
            page = re.sub(r'(<section class="hero[^"]*"[^>]*>.*?</section>)',
                          lambda match: match.group(1) + cover, page,
                          count=1, flags=re.S)

    # Experimental reader-first layout for two high-intent guides.
    # Preserve all copy, heading text, canonical and conversion destinations.
    if url in ('/선불폰-개통방법/', '/미납정지-선불폰/') and 'detail-workspace' in page:
        page = page.replace('<article class="article detail-article">', '<article class="article detail-article editorial-v2">', 1)
        cover_match = re.search(r'<figure class="detail-lead-visual".*?</figure>', page, re.S)
        answer_match = re.search(r'<section class="answer-card">.*?</section>', page, re.S)
        if cover_match and answer_match and cover_match.start() < answer_match.start():
            cover = cover_match.group(0)
            page = page.replace(cover, '', 1)
            answer = re.search(r'<section class="answer-card">.*?</section>', page, re.S).group(0)
            rewritten = re.sub(r'(<h2[^>]*>.*?</h2>)', lambda m: m.group(1) + cover, answer, count=1, flags=re.S)
            page = page.replace(answer, rewritten, 1)
        chips_match = re.search(r'<nav class="jump-chips".*?</nav>', page, re.S)
        answer_match = re.search(r'<section class="answer-card">.*?</section>', page, re.S)
        if chips_match and answer_match and chips_match.start() < answer_match.start():
            chips = chips_match.group(0)
            page = page.replace(chips, '', 1)
            page = page.replace(answer_match.group(0), answer_match.group(0) + chips, 1)
        if '/assets/editorial-v2.css' not in page:
            page = page.replace('</head>', '<link rel="stylesheet" href="/assets/editorial-v2.css?v=20261026b"></head>', 1)


    # Answer-first editorial pilot: preserve the full original list in native details.
    if url in ('/선불폰-개통방법/', '/미납정지-선불폰/') and 'detail-workspace' in page:
        answer_match = re.search(r'<section class="answer-card">.*?</section>', page, re.S)
        if answer_match and 'answer-lead' not in answer_match.group(0):
            lead = ('신청서를 제출했다고 바로 사용할 수 있는 건 아닙니다. <strong>승인과 첫 충전, 유심 장착</strong>까지 마쳐야 합니다.'
                    if url == '/선불폰-개통방법/' else
                    '미납·정지된 기존 번호는 번호이동할 수 없습니다. <strong>본인 명의 선불 신규가입은 신청할 수 있지만</strong> 실제 개통 여부는 인증과 가입 조건에 따라 달라집니다.')
            answer = answer_match.group(0)
            listed = re.search(r'<ul class="check-list">.*?</ul>', answer, re.S)
            small_note = re.search(r'<p class="small-note">.*?</p>', answer, re.S)
            if listed:
                disclosure = ('<details class="answer-more"><summary>조건과 진행 순서 자세히 보기 <span aria-hidden="true">+</span></summary>'
                              '<div class="answer-more-content">' + listed.group(0) +
                              (small_note.group(0) if small_note else '') + '</div></details>')
                revised = answer.replace(listed.group(0), '', 1)
                if small_note:
                    revised = revised.replace(small_note.group(0), '', 1)
                revised = revised.replace('</h2>', '</h2><p class="answer-lead">' + lead + '</p>', 1)
                revised = revised.replace('</section>', disclosure + '</section>', 1)
                page = page.replace(answer, revised, 1)
        page = page.replace('editorial-v2.css?v=20261026b', 'editorial-v2.css?v=20261026c')

    # Keep every existing footer sentence, phone number and destination.
    if 'footer-grid' not in page:
        page = page.replace('<footer class="footer"><div class="site">','<footer class="footer"><div class="site footer-grid"><div class="footer-brand"><a href="/">'+icon('sim')+'<b>59만모바일</b></a><span>앤텔레콤 정보 가이드</span></div><div class="footer-info">',1)
        page = re.sub(r'(</div>)(</footer>)',r'</div>\1\2',page,count=1)
    if 'footer-grid' in page:
        page = re.sub(r'(</p>)\s*(?:</div>\s*)+</footer>', r'\1</div></div></footer>', page, count=1)
    if 'footer-info-title' not in page:
        page = page.replace('<div class="footer-info">','<div class="footer-info"><h2 class="footer-info-title">사업자 · 연락처</h2>',1)
    return page


if __name__ == '__main__':
    count = 0
    for p in ROOT.rglob('index.html'):
        if '.git' in p.parts: continue
        url = '/' + p.relative_to(ROOT).as_posix()[:-10]
        s = p.read_text(encoding='utf-8')
        output = transform(s, url)
        if output != s:
            p.write_text(output,encoding='utf-8',newline='')
            count += 1
    print('Shared hub layout: %d pages updated' % count)
