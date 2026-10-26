#!/usr/bin/env python3
"""Validate sitewide line breaks without changing published SEO or visible copy."""
from pathlib import Path
import subprocess, re, sys, json
ROOT=Path(__file__).resolve().parent.parent
files=[p for p in ROOT.rglob("index.html") if p.relative_to(ROOT).as_posix() not in {"index.html","guide/index.html","알뜰폰-셀프개통-실패/index.html","tools/photo-manager/index.html"} and ".git" not in p.parts]
errors=[]; changed=0
def article(s):
 m=re.search(r'<article\b[^>]*>[\s\S]*?</article>',s,re.I)
 return m.group(0) if m else ""
def visible(s): return re.sub(r'<[^>]*>','',s)
def links(s): return sorted(re.findall(r'href="([^"]+)"',s))
for p in files:
 relative=p.relative_to(ROOT).as_posix()
 try: before=subprocess.check_output(["git","show","origin/main:"+relative],cwd=ROOT).decode("utf8")
 except subprocess.CalledProcessError: errors.append(relative+": missing from main");continue
 after=p.read_text("utf8")
 if visible(article(before))!=visible(article(after)):errors.append(relative+": article text altered")
 if links(before)!=links(after):errors.append(relative+": href altered")
 for name,pattern in [("title",r'<title>.*?</title>'),("canonical",r'<link rel="canonical"[^>]*>'),("robots",r'<meta name="robots"[^>]*>'),("h1",r'<h1\b[^>]*>.*?</h1>')]:
  if re.findall(pattern,before,re.S)!=re.findall(pattern,after,re.S):errors.append(relative+": "+name+" changed")
 changed+=before!=after
manager=ROOT/"tools/photo-manager/index.html"
if not manager.is_file(): errors.append("missing image manager")
if not (ROOT/"img/article-photos/README.md").is_file():errors.append("missing upload folder")
print(json.dumps({"checked":len(files),"changed":changed,"errors":errors},ensure_ascii=False))
sys.exit(bool(errors))
