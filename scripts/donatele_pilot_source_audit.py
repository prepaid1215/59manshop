#!/usr/bin/env python3
"""Inspect ONLY 3 public donatele RSS posts for accurate independent summaries.
Output stays in GitHub Actions artifact; no source text is published automatically.
"""
from __future__ import annotations
import html
from html.parser import HTMLParser
import json
import re
import sys
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

POSTS = {
    "224461969164": "daiso-purple-sim",
    "224455417391": "lg-onechip-number",
    "224461955165": "kt-396-vs-459-data",
}
RSS = "https://rss.blog.naver.com/donatele.xml"

class CleanText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "br", "div", "li", "h2", "h3"):
            self.text.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag in ("p", "div", "li"):
            self.text.append("\n")
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

def main():
    req = urllib.request.Request(RSS, headers={
        "User-Agent": "Mozilla/5.0 (59man-SourceAudit/1.0)",
        "Accept": "application/xml, application/rss+xml, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=35) as response:
        raw = response.read(3_000_000)
    feed = ET.fromstring(raw)
    results = []
    for item in feed.findall(".//item"):
        link = item.findtext("link") or item.findtext("guid") or ""
        match = re.search(r"/donatele/(\d{10,20})", link)
        if not match or match.group(1) not in POSTS:
            continue
        ident = match.group(1)
        desc = item.findtext("description") or ""
        encoded = item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or ""
        raw_html = encoded if len(encoded) > len(desc) else desc
        parser = CleanText()
        parser.feed(html.unescape(raw_html))
        cleaned = re.sub(r"[ \t]+", " ", "".join(parser.text))
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        results.append({
            "blog_post_id": ident,
            "guide": POSTS[ident],
            "title": item.findtext("title") or "",
            "source_url": "https://m.blog.naver.com/donatele/" + ident,
            "rss_description_chars": len(desc),
            "rss_content_encoded_chars": len(encoded),
            "extracted_chars": len(cleaned),
            "source_excerpt": cleaned[:8000],
        })
    dest = Path("/tmp/donatele-pilot-source-audit.json")
    dest.write_text(json.dumps({"source": RSS, "found": len(results), "posts": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Pilot RSS entries matched:", len(results))
    for p in results:
        print(p["blog_post_id"], "extracted_chars", p["extracted_chars"], "rss_description_chars", p["rss_description_chars"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
