#!/usr/bin/env python3
"""Pre-deployment integrity checks for the 59man.shop IndexKit C pilot."""
from __future__ import annotations
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/indexkit-donatele-treatment.json"
HUB = ROOT / "indexkit/index.html"
SITEMAP = ROOT / "sitemap.xml"
HOME = ROOT / "index.html"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.metas = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs)
        elif tag in {"meta", "link"}:
            self.metas.append((tag, attrs))

def digest(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def normalized_blog_url(url):
    parts = urlsplit(url)
    if parts.hostname not in {"blog.naver.com", "m.blog.naver.com"}:
        return None
    pieces = parts.path.strip("/").split("/")
    if len(pieces) == 2 and pieces[0] == "donatele" and re.fullmatch(r"\d{6,20}", pieces[1]):
        return f"https://m.blog.naver.com/donatele/{pieces[1]}"
    return None

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["schemaVersion"] == 1
    treatments = data["treatment"]
    controls = set(data["controlUrlSha256"])
    assert len(treatments) == 5 and len(controls) == 5
    assert all(re.fullmatch(r"[0-9a-f]{64}", c) for c in controls)
    urls = [t["url"] for t in treatments]
    assert len(set(urls)) == 5
    assert all(normalized_blog_url(url) == url for url in urls)
    assert not ({digest(url) for url in urls} & controls), "Treatment/control overlap"

    page = HUB.read_text(encoding="utf-8")
    home = HOME.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    p = LinkParser(); p.feed(page)
    links = [l for l in p.links if normalized_blog_url(l.get("href", ""))]
    assert len(links) == 5, f"Expected five Naver links on hub, got {len(links)}"
    assert set(normalized_blog_url(l["href"]) for l in links) == set(urls)
    assert all("nofollow" not in l.get("rel", "").split() for l in links)
    assert "index,follow" in page and 'rel="canonical" href="https://www.59man.shop/indexkit/"' in page
    assert '/indexkit/' in home and 'https://www.59man.shop/indexkit/' in sitemap
    assert "blog.naver.com/donatele" not in sitemap

    for item in treatments:
        assert item["title"] in page, f"Missing visible title {item['title']}"
        guide = ROOT / item["guide"].lstrip("/") / "index.html"
        assert guide.exists(), f"Internal guide link missing: {guide}"
    assert page.count("<!-- C_TREATMENT_LINK_START -->") == 1
    assert page.count("<!-- C_TREATMENT_LINK_END -->") == 1

    # Scan every served HTML and JSON file for any accidental reference to the five controls.
    # The exact control URLs remain outside this public repository; their hashes are enough
    # for catching direct Naver links in output. Static RSS remains ntelecom59 until a later
    # separately reviewed phase.
    scanned, donatele = 0, set()
    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in {".html", ".json", ".xml"}:
            continue
        if ".git" in file.parts or "node_modules" in file.parts:
            continue
        scanned += 1
        body = file.read_text(encoding="utf-8", errors="replace")
        for value in re.findall(r"https?://(?:m\.)?blog\.naver\.com/donatele/\d{6,20}", body):
            normalized = normalized_blog_url(value)
            if normalized:
                donatele.add(normalized)
                assert digest(normalized) not in controls, f"CONTROL LINK LEAKED: {file}"
    assert donatele == set(urls), f"Unexpected donatele URL in public files: {donatele - set(urls)}"
    print(f"IndexKit C PASS: 5 treatment links / 5 hashed controls / {scanned} HTML-JSON-XML files scanned")
    print("Baseline Google index status: unverified (never infer no-index from missing public search result).")

if __name__ == "__main__":
    main()
