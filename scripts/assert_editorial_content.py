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
  'hrefs':set(re.findall(r'href="([^"]+)"',s)),
 }
for p in TARGETS:
 before=subprocess.check_output(['git','show','origin/main:'+p],cwd=ROOT).decode('utf-8')
 after=(ROOT/p).read_text('utf-8')
 a,b=parse(before),parse(after)
 for k in ['title','description','canonical','robots','h1','imgs']:
  if a[k]!=b[k]: errors.append(f'{p}: {k} changed')
 lost=a['hrefs']-b['hrefs']
 if lost: errors.append(f'{p}: links removed: {sorted(lost)}')
 if 'editorial-v2' not in after or '<p class="answer-lead">' not in after:
  errors.append(f'{p}: missing reader-first content')
 if 'https://preplan.site/' not in after or 'https://pf.kakao.com/_akxmKn/chat' not in after:
  errors.append(f'{p}: expected activation or contact link lost')
 if re.search(r'http://pf.kakao.com/_iNaeb|http://pf.kakao.com/_muGxnn',after):
  errors.append(f'{p}: reference site's contact URL accidentally copied')
page=(ROOT/TARGETS[0]).read_text('utf-8')
for token in ['카카오·토스·PASS','유심번호 19자리','모델코드 5자리','08:00~21:50','첫 충전','/편의점-선불유심/']:
 if token not in page: errors.append(f'activation page missing {token}')
sim=(ROOT/TARGETS[2]).read_text('utf-8')
for token in ['8,800원','5,000원','2,750원','NFC','다이소 고고비']:
 if token not in sim: errors.append(f'SIM page missing {token}')
arrears=(ROOT/TARGETS[1]).read_text('utf-8')
for token in ['기존 번호 그대로 번호이동은 불가','가입제한','L망','신규가입']:
 if token not in arrears: errors.append(f'arrears page missing {token}')
print(json.dumps({'checked':len(TARGETS),'errors':errors},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
