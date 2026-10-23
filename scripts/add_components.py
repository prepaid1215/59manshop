#!/usr/bin/env python3
"""이미지형 정보 카드(신분증 종류·유심 종류) 삽입 스크립트. 재실행해도 중복 삽입되지 않는다.

- 신분증 카드: 실제 신분증 사진/로고를 쓰지 않고, 개인정보·문구가 없는 추상 일러스트(scripts/guide_art.py)로 표현한다.
- 유심 카드: 저장소에 있는 실제 제품 그래픽(webp)을 사용하고, 가격·망·구매 정보는 기존 페이지(/편의점-선불유심/)의 표와 같은 값만 쓴다.
사용법: python scripts/add_components.py
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_art import ill_svg  # noqa: E402


def card(art, name, line, extra=''):
    return '<li><figure><span class="ic-art">%s</span><figcaption><b>%s</b><span>%s</span>%s</figcaption></figure></li>' % (art, name, line, extra)


def img(src, alt, w, h):
    return '<img src="%s" alt="%s" width="%d" height="%d" loading="lazy">' % (src, alt, w, h)


ID_CARDS = ('<div class="img-cards img-cards--id" role="group" aria-label="신원확인에 쓰는 신분증"><p class="img-cards-title">신원확인에 쓰는 신분증</p><ul class="img-cards-grid">'
            + card(ill_svg('idcard', 72), '주민등록증', '실물 촬영 또는 PASS 앱 확인')
            + card(ill_svg('license', 72), '운전면허증', '실물 촬영 또는 PASS 앱 확인')
            + card(ill_svg('mobileid', 72), '모바일 신분증', '행안부 모바일 신분증 앱')
            + '</ul><p class="img-cards-note">그림은 이해를 돕기 위한 예시이며 실제 신분증이 아닙니다. 신원확인 방법은 신청 화면 안내가 최종 기준입니다.</p></div>')

SIM_CARDS = ('<div class="img-cards img-cards--sim" role="group" aria-label="유심 종류"><p class="img-cards-title">유심 4종 한눈에 보기</p><ul class="img-cards-grid">'
             + card(img('/kt-baro-usim-graphic.webp', 'KT 바로유심', 112, 140), 'KT 바로유심', 'K망 · 8,800원', '<em>NFC</em>')
             + card(img('/lg-onechip-graphic.webp', 'LG 모두의 원칩', 126, 126), '모두의 원칩', 'L망 · 8,800원', '<em>NFC</em>')
             + card(img('/gogobi-usim-graphic.webp', '다이소 고고비 유심', 112, 140), '다이소 고고비', 'L망 · 5,000원')
             + card(ill_svg('esim', 96), 'eSIM', 'L망 · 발급비 2,750원', '<em>실물 없음</em>')
             + '</ul><p class="img-cards-note">2026년 10월 기준. 판매처와 실제 가격은 매장·시점에 따라 달라질 수 있습니다.</p></div>')

JOBS = [
    ('앤텔레콤-선불폰-개통-방법/index.html', r'<div class="auth-grid".*?</div>', ID_CARDS, 'img-cards--id'),
    ('앤텔레콤-선불폰-개통-방법/index.html', r'<p>유심을 아직 사지 않았다면[^<]*<a[^>]*>[^<]*</a>[^<]*</p>', SIM_CARDS, 'img-cards--sim'),
    ('편의점-선불유심/index.html', r'<p class="updated">2026년 10월 기준</p>', SIM_CARDS, 'img-cards--sim'),
]
for rel, anchor, html, marker in JOBS:
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    if marker in s:
        print(rel, marker, 'already')
        continue
    m = re.search(anchor, s, re.S)
    if not m:
        print(rel, marker, 'NO ANCHOR')
        continue
    s = s[:m.end()] + html + s[m.end():]
    p.write_text(s, encoding='utf-8', newline='')
    print(rel, marker, 'inserted')
