#!/usr/bin/env python3
"""59만모바일 신규 키워드 페이지 간의 본문 중복 정도 측정.
Threshold 30% is an internal editorial gate, NOT Google's indexing threshold.
Compare newly added pages to all 28 indexed pages, excluding global template sections.
"""
from pathlib import Path
from html import unescape
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
NEW=['/lg-모두의원칩-셀프개통/','/l망-464-요금제/','/l망-2-5gb-요금제/']
THRESHOLD=.30
def text_from(raw):
    m=re.search(r'<article\b[^>]*class="[^"]*\bdetail-article\b[^"]*"[^>]*>([\s\S]*?)</article>',raw)
    if not m:return ''
    s=m.group(1)
    for pattern in [r'<nav\b[\s\S]*?</nav>',r'<figure\b[\s\S]*?</figure>',r'<script\b[\s\S]*?</script>',r'<section class="activation-flow"[\s\S]*?</section>',r'<div class="steps"[\s\S]*?</div>']:
        s=re.sub(pattern,' ',s)
    s=re.sub(r'<[^>]+>',' ',s)
    s=unescape(s)
    return re.sub(r'\s+',' ',s).lower().strip()
def word_shingles(s):
    toks=re.findall(r'[가-힣a-z0-9]+',s)
    return {' '.join(toks[i:i+3]) for i in range(len(toks)-2)}
def char_shingles(s):
    s=re.sub(r'[^가-힣a-z0-9]','',s)
    return {s[i:i+12] for i in range(len(s)-11)}
def jac(a,b):
    if not a or not b:return 0.
    return len(a&b)/len(a|b)
xml=(ROOT/'sitemap.xml').read_text()
urls=re.findall(r'<loc>https://www\.59man\.shop(/[^<]*)</loc>',xml)
content={}
for u in urls:
    p=ROOT/('index.html' if u=='/' else u.lstrip('/')+'index.html')
    if not p.exists():raise SystemExit('Missing page: '+str(p))
    content[u]=text_from(p.read_text())
issues=[];scores=[]
for u in NEW:
    if u not in content:issues.append('Not in sitemap: '+u);continue
    if len(content[u])<850:issues.append('Too little unique editorial text: '+u)
    for v in urls:
        if v==u or not content[v]:continue
        w=jac(word_shingles(content[u]),word_shingles(content[v]))
        c=jac(char_shingles(content[u]),char_shingles(content[v]))
        score=max(w,c)
        scores.append((score,u,v,w,c))
        if score>THRESHOLD:
            issues.append(f'Similarity {score:.1%} > 30%: {u} vs {v}')
for i in range(len(NEW)):
    for j in range(i+1,len(NEW)):
        if NEW[i] not in content or NEW[j] not in content:continue
report={'method':'Maximum of word 3-shingle Jaccard and character 12-shingle Jaccard, unique article content only; excludes navigation, images and shared activation steps','threshold':THRESHOLD,'new_pages':NEW,'compared_indexable_pages':len(urls),'comparisons':len(scores),'top_pairs':[{'score_pct':round(s*100,2),'new':a,'against':b,'word_pct':round(w*100,2),'chars_pct':round(c*100,2)} for s,a,b,w,c in sorted(scores,reverse=True)[:12]],'errors':issues}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(issues))
