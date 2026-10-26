#!/usr/bin/env python3
"""Protect SEO metadata, existing internal links, imagery, and operator facts during reader-first rewrite."""
from pathlib import Path
import re, json, subprocess, sys
ROOT=Path(__file__).resolve().parent.parent
TARGETS=['선불폰-개통방법/index.html','미납정지-선불폰/index.html','편의점-선불유심/index.html']
errors=[]
def attr(s,rx): return re.search(rx,s,re.S).group(1) if re.search(rx,s,re.S) else None
def parse(s):
 return {
  'title':attr(s,r'<title>(.*?)</title>'),
  'description':attr(s,r'<meta name="description" content="([^"]+)"'),
  'canonical':attr(s,r'<link rel="canonical" href="([^"]+)"'),
  'robots':attr(s,r'<meta name="robots" content="([^"]+)"'),
  'h1':attr(s,r'<h1[^>]*>(.*?)</h1>'),
  'imgs':sorted(re.findall(r'<img[^>]+src="([^"]+)"',s)),
  'hrefs':set(href for href in re.findall(r'href="([^"]+)"',s) if not href.startswith('/assets/')),
 }
for p in TARGETS:
 before=subprocess.check_output(['git','show','origin/main:'+p],cwd=ROOT).decode('utf-8')
 after=(ROOT/p).read_text('utf-8')
 a,b=parse(before),parse(after)
 for k in ['title','canonical','robots','h1','imgs']:
  if a[k]!=b[k]: errors.append(f'{p}: {k} changed')
 lost=a['hrefs']-b['hrefs']
 if lost: errors.append(f'{p}: links removed: {sorted(lost)}')
 if p != TARGETS[2] and ('승인 뒤' in after or '승인 후 첫 충전' in after or '승인 여부를 먼저 확인' in after):
  errors.append(f'{p}: outdated approval requirement')
 if 'editorial-v2' not in after or '<p class="answer-lead">' not in after:
  errors.append(f'{p}: missing reader-first content')
 if 'https://preplan.site/' not in after or 'https://pf.kakao.com/_akxmKn/chat' not in after:
  errors.append(f'{p}: expected activation or contact link lost')
 if re.search(r'http://pf.kakao.com/_iNaeb|http://pf.kakao.com/_muGxnn',after):
  errors.append(f"{p}: reference contact URL accidentally copied")
page=(ROOT/TARGETS[0]).read_text('utf-8')
for token in ['카카오·토스·PASS','유심번호 19자리','모델코드 5자리','08:00~21:50','요금을 충전','1899-7700','멤버십 앱','담당자 승인','/편의점-선불유심/']:
 if token not in page: errors.append(f'activation page missing {token}')
sim=(ROOT/TARGETS[2]).read_text('utf-8')
for token in ['8,800원','5,000원','2,750원','NFC','다이소 고고비']:
 if token not in sim: errors.append(f'SIM page missing {token}')
arrears=(ROOT/TARGETS[1]).read_text('utf-8')
for token in ['기존 번호 그대로 번호이동은 불가','가입제한','L망','신규가입']:
 if token not in arrears: errors.append(f'arrears page missing {token}')
for key in ['신청서 제출 → 요금 충전 → 사용','1899-7700']:
 if key not in arrears: errors.append(f'arrears page missing {key}')
for t in ['플랫폼 개통 후', '태블릿개통', '담당자 해피콜', '담당자 승인', '요금 충전']:
 if t not in page: errors.append(f'activation flow distinction missing {t}')
if '플랫폼 개통 후' not in arrears: errors.append('arrears guide does not distinguish platform follow-up call')
if '태블릿개통' not in sim: errors.append('SIM guide does not distinguish tablet happy call')

member=(ROOT/'태블릿-소유자-회원번호/index.html').read_text('utf-8')
for token in ['태블릿 소유자 회원번호 2893496','data-copy="2893496"','조회 회원명: 주*돈','담당자 해피콜 → 승인 → 요금 충전','승인 이후']:
 if token not in member: errors.append(f'member guide missing {token}')
for token in ['준비물, 본인인증, 유심정보와 요금제 선택','2893496','담당자 해피콜 → 담당자 승인 → 요금 충전']:
 if token not in page: errors.append(f'activation guide missing shared steps / tablet number: {token}')

# Keep all reference-blog dealer identifiers out of 59만모바일.
for p in TARGETS + ['태블릿-소유자-회원번호/index.html']:
 content=(ROOT/p).read_text('utf-8')
 for old in ['2879248','부*빈','라이프선불폰.com']:
  if old in content: errors.append(f'{p}: external reference identity leaked: {old}')
 if 'reference-style' not in content or 'class="reader-toc"' not in content:
  errors.append(f'{p}: missing reference-style layout')

print(json.dumps({'checked':len(TARGETS)+1,'errors':errors},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
