#!/usr/bin/env python3
"""Collect donatele Naver RSS candidates for IndexKit C without publishing links.

This script only writes an Actions artifact (not a tracked file or a public webpage).
Do not use the output for RSS pages until a treatment/control assignment exists.
"""
import argparse
import email.utils
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BLOG_ID = "donatele"
FEED_URL = f"https://rss.blog.naver.com/{BLOG_ID}.xml"

def normalize_url(raw):
    try:
        u = urllib.parse.urlsplit(str(raw).strip())
        if u.scheme not in {"http", "https"} or u.hostname not in {"blog.naver.com", "m.blog.naver.com"}:
            return None
        path = u.path.rstrip("/")
        direct = re.fullmatch(r"/([a-zA-Z0-9_-]+)/([0-9]{6,20})", path)
        if direct and direct.group(1).lower() == BLOG_ID:
            return f"https://m.blog.naver.com/{BLOG_ID}/{direct.group(2)}"
        if path.lower() in {"/postview.naver", "/postview.nhn"}:
            query = urllib.parse.parse_qs(u.query)
            if (query.get("blogId") or query.get("blogid")) == [BLOG_ID]:
                number = (query.get("logNo") or query.get("logno") or [""])[0]
                if re.fullmatch(r"[0-9]{6,20}", number):
                    return f"https://m.blog.naver.com/{BLOG_ID}/{number}"
    except (TypeError, ValueError, AttributeError):
        pass
    return None

def parse_feed(xml_bytes):
    root = ET.fromstring(xml_bytes)
    entries, seen = [], set()
    for item in root.findall(".//item"):
        url = normalize_url(item.findtext("link") or item.findtext("guid") or "")
        if not url or url in seen:
            continue
        title = " ".join((item.findtext("title") or "").split())[:150]
        if not title:
            continue
        date = ""
        published = item.findtext("pubDate") or ""
        if published:
            try:
                date = email.utils.parsedate_to_datetime(published).date().isoformat()
            except (ValueError, TypeError):
                pass
        seen.add(url)
        entries.append({"title": title, "url": url, "date": date})
    return entries

def fetch_feed():
    req = urllib.request.Request(FEED_URL, headers={
        "User-Agent": "Mozilla/5.0 (compatible; 59manIndexKitCandidate/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=25) as response:
        payload = response.read(2_500_001)
    if len(payload) > 2_500_000:
        raise ValueError("Feed too large")
    return parse_feed(payload)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Write only to an ephemeral Actions artifact path")
    args = parser.parse_args()
    try:
        entries = fetch_feed()
        if len(entries) < 10:
            raise ValueError(f"Only {len(entries)} posts: at least 10 needed for 5/5 experiment")
        result = {"source": FEED_URL, "blogId": BLOG_ID,
                  "collectedAt": datetime.now(timezone.utc).isoformat(),
                  "note": "Candidates only. No links have been published or assigned.",
                  "count": len(entries), "candidates": entries[:100]}
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"IndexKit C candidates collected: {len(entries)} from {BLOG_ID}. No URLs published.")
        return 0
    except Exception as exc:
        print(f"::error::Could not collect donatele RSS candidates: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
