#!/usr/bin/env python3
"""59man.shop 정적 사이트 점검 스크립트 (표준 라이브러리만 사용).

사용법:  python scripts/check_site.py [--table]

- 로컬 http.server로 저장소 루트를 서비스하고(GitHub Pages와 같은 디렉터리 → index.html 규칙),
  모든 내부 링크·자산이 200으로 응답하는지 확인한다.
- sitemap.xml ↔ index,follow 페이지 일치, canonical, og:site_name, og:type,
  JSON-LD, 이미지 alt, /v4-1/ 경로 유지 여부를 점검한다.
- --table: 색인 대상 페이지의 title / description / canonical 표를 Markdown으로 출력한다.
실패 항목이 하나라도 있으면 종료 코드 1.
"""
import html
import http.server
import json
import re
import socketserver
import struct
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://www.59man.shop'
BRAND = '59만선불폰'
V4_TOPICS = ['esim-new', 'kt-nfc-compare', 'network-activation', 'plan-396',
             'plan-compare', 'sim-buy-where', 'weekend-activation']

sys.stdout.reconfigure(encoding='utf-8')
errors = []
org_assets = []  # (url, 설명) Organization logo/image 절대 URL


def fail(msg):
    errors.append(msg)


def read(p):
    return Path(p).read_text(encoding='utf-8')


def url_of(p):
    rel = p.relative_to(ROOT).as_posix()
    return '/' if rel == 'index.html' else '/' + rel[:-len('index.html')]


def meta(h, attr, key):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(key)), h)
    return html.unescape(m.group(1)) if m else None


pages = {url_of(p): read(p) for p in sorted(ROOT.rglob('index.html')) if '.git' not in p.parts}
sitemap = set(re.findall(r'<loc>' + re.escape(BASE) + r'(/[^<]*)</loc>', read(ROOT / 'sitemap.xml')))
indexable = {u for u, h in pages.items() if 'noindex' not in (meta(h, 'name', 'robots') or '')}

# 1) sitemap ↔ 색인 대상 일치
for u in sitemap - indexable:
    fail('sitemap에 있으나 noindex 또는 없는 페이지: %s' % u)
for u in indexable - sitemap:
    fail('색인 대상인데 sitemap에 없음: %s' % u)
if not re.search(r'Sitemap: ' + re.escape(BASE) + '/sitemap.xml', read(ROOT / 'robots.txt')):
    fail('robots.txt에 Sitemap 줄 없음')

# 2) 페이지별 메타 점검
for u, h in pages.items():
    can = re.search(r'rel="canonical" href="([^"]*)"', h)
    if not can:
        fail('canonical 없음: %s' % u)
        continue
    if u in indexable and can.group(1) != BASE + u:
        fail('색인 대상 canonical 불일치: %s -> %s' % (u, can.group(1)))
    if u in indexable:
        if meta(h, 'property', 'og:site_name') != BRAND:
            fail('og:site_name != %s: %s' % (BRAND, u))
        if not re.search(r'<title>[^<]+ - ?59만선불폰</title>|<title>[^<]+\| 59만선불폰</title>', h):
            fail('title 접미사 이상: %s' % u)
        want = 'website' if u in ('/', '/guide/') else 'article'
        if meta(h, 'property', 'og:type') != want:
            fail('og:type %s 이어야 함: %s' % (want, u))
        for im in re.findall(r'<img[^>]*>', h):
            if 'alt=' not in im:
                fail('img alt 속성 없음: %s %s' % (u, im))
        # JSON-LD
        blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)]
        types = [b.get('@type') for b in blocks]
        if u == '/':
            if 'Organization' not in types or 'WebSite' not in types:
                fail('메인에 Organization/WebSite JSON-LD 필요: %s' % types)
            for b in blocks:
                if b.get('@type') == 'WebSite':
                    if b.get('name') != BRAND:
                        fail('WebSite JSON-LD name != %s' % BRAND)
                    if b.get('publisher', {}).get('@id') != next((o.get('@id') for o in blocks if o.get('@type') == 'Organization'), None):
                        fail('WebSite publisher가 Organization @id를 가리켜야 함')
                if b.get('@type') == 'Organization':
                    if b.get('address', {}).get('postalCode') != '46220':
                        fail('Organization.address.postalCode 46220 필요')
                    for k in ('logo', 'image'):
                        vals = b.get(k)
                        vals = vals if isinstance(vals, list) else [vals]
                        if not vals or not vals[0]:
                            fail('Organization.%s 없음' % k)
                        for v in vals:
                            if v:
                                if not v.startswith(BASE + '/') or '?' in v:
                                    fail('Organization.%s는 쿼리 없는 %s 절대 URL이어야 함: %s' % (k, BASE, v))
                                else:
                                    org_assets.append((v, k))
                    for k in ('name', 'legalName', 'taxID', 'url', 'telephone', 'address', 'contactPoint', 'sameAs'):
                        if not b.get(k):
                            fail('Organization.%s 없음' % k)
        else:
            if 'BreadcrumbList' not in types:
                fail('BreadcrumbList 없음: %s' % u)
            for b in blocks:
                if b.get('@type') == 'BreadcrumbList':
                    last = b['itemListElement'][-1]
                    if last['item'] != BASE + u:
                        fail('BreadcrumbList 마지막 항목이 현재 페이지가 아님: %s' % u)
        if 'FAQPage' in types:
            # 화면에 FAQ가 없는 FAQPage는 금지
            fail('FAQPage JSON-LD는 화면 FAQ가 있을 때만 허용: %s' % u)
    # 추적 파라미터 금지
    if re.search(r'utm_|[?&]fbclid=|[?&]gclid=', h):
        fail('추적 쿼리 파라미터 발견: %s' % u)
    if 'TODO(' in h:
        fail('미해결 TODO 남아 있음: %s' % u)
    # 푸터 (리다이렉트용 스텁 제외)
    # 화면 텍스트에 preplan.site 도메인 표기 금지 (href·JSON-LD·script 제외)
    vis = re.sub(r'<head>.*?</head>|<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    if 'preplan.site' in re.sub(r'<[^>]+>', ' ', vis):
        fail('화면 텍스트에 preplan.site 도메인 노출: %s' % u)
    # 모바일 전용 레이아웃: 사이드바 없음, 하단 고정 바 있음 (스텁 제외)
    if '<footer class="footer">' in h:
        if '<aside class="side">' in h:
            fail('사이드바가 남아 있음(모바일 전용 레이아웃): %s' % u)
        if '<nav class="bottom-bar"' not in h or 'https://pf.kakao.com/_akxmKn/chat" rel="noopener">카톡 상담' not in h:
            fail('하단 고정 바(개통 시작하기 + 카톡 상담) 없음: %s' % u)
    if '<footer class="footer">' in h:
        for need in ('preplan.site/">59만모바일 개통 페이지</a>에서 진행됩니다', '774-56-00506', '주영돈', '(46220) 부산광역시 금정구 금강로 670', 'tel:+821073058253', 'https://pf.kakao.com/_akxmKn/chat"'):
            if need not in h:
                fail('푸터 항목 누락(%s): %s' % (need, u))

# 2-1) 내부 링크가 noindex 페이지로 가지 않는지 (홈, /guide/, 색인 페이지의 관련 안내 사이드바)
def internal_links(h, scope=None):
    if scope:
        m = re.search(scope, h, re.S)
        h = m.group(0) if m else ''
    return set(re.findall(r'href="(/[^"#?]*)', h))


for u in ('/', '/guide/'):
    for ref in sorted(internal_links(pages[u])):
        if ref in pages and ref not in indexable:
            fail('%s 에서 noindex 페이지로 링크: %s' % (u, ref))
for u in sorted(indexable - {'/', '/guide/'}):
    for ref in sorted(internal_links(pages[u], r'<nav class="related".*?</nav>')):
        if ref in pages and ref not in indexable and ref != '/':
            fail('%s 관련 안내가 noindex 페이지로 링크: %s' % (u, ref))

# 2-2) 리다이렉트 스텁: noindex + 올바른 canonical(색인 대상, 자기 자신 아님) + meta refresh 일치
for u, h in pages.items():
    can = re.search(r'rel="canonical" href="([^"]*)"', h)
    if not can or can.group(1) == BASE + u:
        continue
    target = can.group(1)[len(BASE):] if can.group(1).startswith(BASE) else None
    if 'noindex' not in (meta(h, 'name', 'robots') or ''):
        fail('canonical이 다른 페이지를 가리키는데 noindex가 아님: %s' % u)
    if target not in indexable or target not in sitemap:
        fail('스텁 %s 의 canonical 대상이 색인 대상/sitemap에 없음: %s' % (u, target))
    mr = re.search(r'<meta http-equiv="refresh" content="0; url=([^"]*)"', h)
    if not mr:
        fail('스텁 %s 에 meta refresh(0초)가 없음' % u)
    elif urllib.parse.unquote(mr.group(1)) != urllib.parse.unquote(target):
        fail('스텁 %s 의 meta refresh(%s)와 canonical(%s) 불일치' % (u, mr.group(1), target))

# 2-3) /guide/ 허브: 5단계, 업데이트일, 색인 단계 페이지가 모두 한 번씩 들어 있는지
gh = pages['/guide/']
for name in ('개통 전 확인', '준비물', '개통하기', '막힐 때', '개통 후'):
    if '<h2>%s</h2>' % name not in gh:
        fail('/guide/ 에 단계 없음: %s' % name)
if not re.search(r'<p class="updated">업데이트: <time datetime="\d{4}-\d{2}-\d{2}">', gh):
    fail('/guide/ 업데이트일 표시 없음')
hub_links = re.findall(r'<ul class="guide-links">.*?</ul>', gh, re.S)
hub_refs = [r for blk in hub_links for r in re.findall(r'<li><a href="(/[^"]*)"', blk)]
want = sorted(indexable - {'/', '/guide/'})
hub_pages = [r.split('#')[0] for r in hub_refs]
if set(hub_pages) != set(want):
    fail('/guide/ 허브 링크가 색인 단계 페이지와 불일치: 누락 %s / 초과 %s' % (
        sorted(set(want) - set(hub_pages)), sorted(set(hub_pages) - set(want))))
# 한 페이지가 여러 칸에 들어갈 수 있는 것은 #앵커로 구분된 섹션 링크뿐이고, 앵커는 대상 페이지에 실제로 있어야 함
plain = [r for r in hub_refs if '#' not in r]
if len(plain) != len(set(plain)):
    fail('/guide/ 허브에 앵커 없이 중복된 링크가 있음')
for r in hub_refs:
    if '#' in r:
        page, anchor = r.split('#', 1)
        if page not in pages or ('id="%s"' % anchor) not in pages[page]:
            fail('/guide/ 허브 앵커 대상이 없음: %s' % r)

# 3) /v4-1/ 경로 고정
for t in V4_TOPICS:
    if ('/v4-1/topic/%s/' % t) not in pages:
        fail('/v4-1/topic/%s/ 경로가 사라짐 (경로 변경 금지)' % t)

# 4) 로컬 서버로 내부 링크 200 확인
class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass


class QuietServer(socketserver.TCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        pass


srv = QuietServer(('127.0.0.1', 0), Quiet)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

targets = {}
for u, h in pages.items():
    for ref in re.findall(r'(?:href|src)="(/[^"#?]*)', h):
        if ref.startswith('//'):
            continue
        targets.setdefault(ref, u)
for ref in ['/', '/sitemap.xml', '/robots.txt'] + sorted(sitemap):
    targets.setdefault(ref, 'sitemap/robots')

for v, k in org_assets:
    targets.setdefault(v[len(BASE):], 'Organization.' + k)

for ref, src in sorted(targets.items()):
    q = urllib.parse.quote(ref, safe='/')
    try:
        with urllib.request.urlopen('http://127.0.0.1:%d%s' % (port, q), timeout=10) as r:
            r.read()
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    if code != 200:
        fail('깨진 링크 %s (%s) <- %s' % (ref, code, src))
srv.shutdown()
for v, k in org_assets:
    f = ROOT / urllib.parse.unquote(v[len(BASE) + 1:])
    if f.suffix.lower() == '.png' and f.exists():
        w, h = struct.unpack('>II', f.read_bytes()[16:24])
        if w < 112 or h < 112 or abs(w - h) > max(w, h) * 0.2:
            fail('Organization.%s 이미지가 112x112 이상 정사각형에 가깝지 않음: %s (%dx%d)' % (k, v, w, h))

# 5) 표 출력
if '--table' in sys.argv:
    print('| URL | title | description | canonical |')
    print('|---|---|---|---|')
    for u in sorted(indexable, key=lambda x: (x != '/', x)):
        h = pages[u]
        t = html.unescape(re.search(r'<title>([^<]*)', h).group(1))
        d = meta(h, 'name', 'description') or ''
        c = re.search(r'rel="canonical" href="([^"]*)"', h).group(1)
        print('| %s | %s | %s | %s |' % (u, t.replace('|', '\\|'), d.replace('|', '\\|'), c))

print('검사 페이지 %d개 (색인 %d / noindex %d), 내부 링크·자산 %d개' % (
    len(pages), len(indexable), len(pages) - len(indexable), len(targets)))
if errors:
    print('실패 %d건' % len(errors))
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('모두 통과: 깨진 링크 0개, sitemap=색인 대상 일치, 메타/JSON-LD 정상')
