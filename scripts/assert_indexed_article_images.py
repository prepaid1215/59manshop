#!/usr/bin/env python3
"""Index-wide visual inventory & factual graphic references.
Checks every sitemap detail article and the 20 refreshed illustration placements.
This verifies presence, XML integrity, meaningful alt/captions and asset paths,
not aesthetic preference or SEO indexing outcomes.
"""
from pathlib import Path
from html import unescape
import xml.etree.ElementTree as ET
import re,json,sys
root=Path(__file__).resolve().parent.parent
routes=[unescape(x) for x in re.findall(r'<loc>https://www\.59man\.shop(/[^<]+)</loc>',(root/'sitemap.xml').read_text())]
routes=[p for p in routes if p not in ['/','/guide/']]
expected={
'/앤텔레콤-웹개통/':['activation-hours-new.svg'],
'/v4-1/topic/esim-new/':['esim-new-setup.svg'],
'/다이소-유심/':['usim-gogobi-back.webp','network-sim-number-format.svg'],
'/kt-바로유심/':['usim-kt-photo.webp'],
'/v4-1/topic/kt-nfc-compare/':['nfc-sim-options.svg'],
'/lg-원칩/':['lg-onechip-model-serial.svg','usim-lg-photo.webp'],
'/v4-1/topic/network-activation/':['network-sim-number-format.svg'],
'/알뜰폰-셀프개통-번호이동/':['new-vs-transfer.svg'],
'/v4-1/topic/plan-396/':['k396-plan-overview.svg'],
'/v4-1/topic/plan-compare/':['l464-data-condition.svg'],
'/편의점-선불유심-셀프개통/':['usim-kt-photo.webp','network-sim-number-format.svg'],
'/v4-1/topic/sim-buy-where/':['sim-stores-network.svg'],
'/미납정지-선불폰/':['number-move-eligibility.svg'],
'/v4-1/topic/weekend-activation/':['activation-hours-new.svg'],
'/선불폰-개통/':['new-vs-transfer.svg'],
'/선불폰-개통방법/':['sim-stores-network.svg','platform-rule-03.webp'],
'/선불폰-셀프개통/':['activation-three-prep.svg'],
'/알뜰폰-셀프개통-안됨/':['activation-troubleshoot.svg'],
'/태블릿-소유자-회원번호/':['platform-tablet-process.svg'],
'/선불폰-충전-방법/':['recharge-recommended.svg']
}
issues=[];checks=[];new_figures=0;all_images=0
for url in routes:
  p=root/url.lstrip('/')/'index.html'
  if not p.is_file():issues.append('missing HTML '+str(p));continue
  html=p.read_text()
  m=re.search(r'<article\b[\s\S]*?</article>',html)
  if not m:issues.append('missing article '+url);continue
  a=m[0]
  imgs=re.findall(r'<img\b[^>]*>',a)
  all_images+=len(imgs)
  figures=re.findall(r'<figure\s+class="sm-editorial-figure[^"]*"[\s\S]*?</figure>',a)
  if url in expected and len(figures)<len(expected[url]):
    issues.append(f'{url} expected >= {len(expected[url])} editorial figures but got {len(figures)}')
  for f in figures:
    source=re.search(r'<img\b[^>]*src="([^"]+)"',f)
    alt=re.search(r'<img\b[^>]*alt="([^"]+)"',f)
    cap=re.search(r'<figcaption>(.*?)</figcaption>',f,re.S)
    if not source or not alt or not cap:issues.append('missing img/alt/caption '+url);continue
    src=source[1]
    imgp=root/src.lstrip('/')
    if not imgp.is_file():issues.append('missing asset '+src)
    if len(unescape(re.sub('<[^>]+>','',alt[1])).strip())<12:issues.append('alt too short '+url+' '+src)
    if len(unescape(re.sub('<[^>]+>','',cap[1])).strip())<12:issues.append('caption too short '+url+' '+src)
    new_figures+=1
  for asset in expected.get(url,[]):
    if not any(asset in f for f in figures):issues.append('absent expected '+url+' '+asset)
  for tag in imgs:
    sm=re.search(r'src="([^"]+)"',tag)
    if not sm:continue
    src=sm[1]
    if src.startswith('/') and not (root/src.lstrip('/')).exists():issues.append('missing article image '+url+' '+src)
  can=re.search(r'<link rel="canonical" href="([^"]+)"',html)
  if not can or can[1]!='https://www.59man.shop'+url:issues.append('canonical changed '+url)
  checks.append({'url':url,'images':len(imgs),'new_figures':len(figures),'updated':url in expected})
if len(routes)!=26:issues.append('expected 26 indexed detail articles, got '+str(len(routes)))
if len(expected)!=20:issues.append('expected 20 illustrated pages')
if new_figures<24:issues.append('expected 24 new placements got '+str(new_figures))
for svg in (root/'img'/'editorial').glob('*.svg'):
  try:
    ET.parse(svg)
    if svg.stat().st_size<500:issues.append('suspiciously tiny svg '+str(svg))
  except Exception as e:issues.append('SVG invalid '+str(svg)+' '+str(e))
report={'indexed_detail_pages':len(routes),'newly_illustrated_pages':len(expected),'new_editorial_figure_placements':new_figures,'total_article_image_tags':all_images,'created_editorial_svg_count':len(list((root/'img'/'editorial').glob('*.svg'))),'issues':issues,'by_page':checks}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(issues))
