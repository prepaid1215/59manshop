#!/usr/bin/env python3
"""Offline preview validation of 10 error-guide drafts. Never fetches URLs."""
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs
from html.parser import HTMLParser
import itertools, re, statistics, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
paths=[
 "선불폰-다른-판매자에게-배정", "선불폰-usim-모델정보-없음",
 "선불폰-안면인증-실패","주민등록증-발급일자-오류",
 "번호이동-사전동의-실패","번호이동-90일-미경과",
 "선불폰-희망번호-조회-실패","선불폰-개통후-데이터-안됨",
 "유심-인식-안됨","선불폰-가입제한-다회선"
]
HOST="https://www.59man.shop"
assert len(paths)==10 and len(set(paths))==10

class Scan(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.tags=[];self.links=[];self.titles=[];self.h1=[];self.canon=[];self.robots=[]
  self.in_title=False;self.in_h1=False;self.in_section=False;self.sections=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append(tag)
  if tag=="title":self.in_title=True
  if tag=="h1":self.in_h1=True
  if tag=="section":self.in_section=True
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href"))
  if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content"))
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
  if tag=="h1":self.in_h1=False
  if tag=="section":self.in_section=False
 def handle_data(self,data):
  s=data.strip()
  if s:
   if self.in_title:self.titles.append(s)
   if self.in_h1:self.h1.append(s)
   if self.in_section:self.sections.append(s)

def jaccard(a,b):
 s=lambda x:{x[i:i+6] for i in range(max(0,len(x)-5))}
 x,y=s(a),s(b)
 return len(x&y)/len(x|y) if x and y else 0

texts=[]
codes=set()
for slug in paths:
 file=ROOT/slug/"index.html"
 assert file.is_file(),file
 html=file.read_text(encoding="utf-8")
 v=Scan();v.feed(html)
 assert len(v.canon)==1 and v.canon[0]==f"{HOST}/{slug}/",(slug,v.canon)
 assert v.robots==["index,follow"],(slug,v.robots)
 assert len(v.h1)==1 and len(v.titles)==1,(slug,v.h1,v.titles)
 assert len(v.sections)>=9,(slug,len(v.sections))
 cta=[url for url in v.links if url.startswith("https://preplan.site/?from=")]
 assert cta,slug
 expected="59man_"+slug
 assert all(parse_qs(urlsplit(x).query).get("from")==[expected] for x in cta),(slug,cta)
 assert expected not in codes,(slug,expected)
 codes.add(expected)
 for href in v.links:
  if not href.startswith("/") or href.startswith("//"):continue
  dest=ROOT/unquote(urlsplit(href).path).strip("/")/"index.html"
  if href=="/":dest=ROOT/"index.html"
  assert dest.is_file(),(slug,href)
 txt=re.sub(r"\s+","", " ".join(v.sections))
 texts.append((slug,txt))
site=ROOT/"sitemap.xml"
root=ET.parse(site).getroot()
locs=[x.text for x in root.iter() if x.tag.endswith("loc") and x.text]
assert len(locs)==32 and len(set(locs))==32,len(locs)
for slug in paths: assert f"{HOST}/{slug}/" in locs,slug
hub=(ROOT/"선불폰-셀프개통/index.html").read_text(encoding="utf-8")
for slug in paths:assert f'href="/{slug}/"' in hub,("missing hub link",slug)
pairs=[(x,y,round(jaccard(a,b),3)) for (x,a),(y,b) in itertools.combinations(texts,2)]
assert all(value<1 for _,_,value in pairs),"Identical article bodies"
print({"checked_pages":len(paths),"sitemap_total":len(locs),"distinct_cta":len(codes),
       "internal_links":"resolved","hub_links":len(paths),
       "body_similarity_mean":round(statistics.mean(v for _,_,v in pairs),3),
       "body_similarity_max":max(v for _,_,v in pairs)})
