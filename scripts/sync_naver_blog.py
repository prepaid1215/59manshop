#!/usr/bin/env python3
"""Sync ntelecom59's public Naver RSS into crawlable static links on 59man.shop.

The feed contains external blog URLs: those URLs never enter 59man.shop's sitemap.
Uses Python's standard library; safe to run repeatedly and from GitHub Actions.
"""
import email.utils
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FEED_URL = "https://rss.blog.naver.com/ntelecom59.xml"
BLOG_HOME = "https://blog.naver.com/ntelecom59"
STATE = ROOT / "data/naver-blog-posts.json"
HOME = ROOT / "index.html"
LIST = ROOT / "blog/index.html"
SITEMAP = ROOT / "sitemap.xml"
TZ = ZoneInfo("Asia/Seoul")
MAX_ITEMS = 60

def permitted_url(value):
    """Avoid including unrelated, redirected, or potentially unsafe feed URLs."""
    try:
        u = urllib.parse.urlsplit(value.strip())
        if u.scheme not in ("http", "https") or u.hostname not in ("blog.naver.com", "m.blog.naver.com"):
            return None
        path = u.path.rstrip("/")
        if re.fullmatch(r"/ntelecom59/\d+", path):
            return "https://blog.naver.com" + path
        if path == "/PostView.naver":
            q = urllib.parse.parse_qs(u.query)
            if q.get("blogId") == ["ntelecom59"] and re.fullmatch(r"\d+", (q.get("logNo") or [""])[0]):
                return "https://blog.naver.com/ntelecom59/" + q["logNo"][0]
    except (ValueError, AttributeError):
        pass
    return None

def fetch_entries():
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                FEED_URL,
                headers={"User-Agent": "Mozilla/5.0 (compatible; 59manBlogRSS/1.0; +https://www.59man.shop/blog/)",
                         "Accept": "application/rss+xml, application/xml, text/xml, */*"},
            )
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = response.read(2_500_001)
            if len(payload) > 2_500_000:
                raise ValueError("RSS feed exceeds allowed size")
            root = ET.fromstring(payload)
            items = root.findall(".//item")
            entries = []
            for item in items:
                url = permitted_url(item.findtext("link") or item.findtext("guid") or "")
                if not url:
                    continue
                title = " ".join((item.findtext("title") or "").split())[:145]
                if not title:
                    continue
                date = ""
                raw_date = item.findtext("pubDate") or ""
                if raw_date:
                    try:
                        when = email.utils.parsedate_to_datetime(raw_date)
                        if when.tzinfo is None:
                            when = when.replace(tzinfo=TZ)
                        date = when.astimezone(TZ).strftime("%Y-%m-%d")
                    except (ValueError, TypeError, OverflowError):
                        pass
                entries.append({"title": title, "url": url, "date": date})
            if not entries:
                raise ValueError("No valid posts for the ntelecom59 blog were found in RSS")
            return entries
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(str(last_error))

def marker_replace(path, opening, closing, new_html):
    text = path.read_text(encoding="utf-8")
    if text.count(opening) != 1 or text.count(closing) != 1:
        raise ValueError(f"RSS markers missing or duplicated in {path}")
    prefix, remainder = text.split(opening, 1)
    _, suffix = remainder.split(closing, 1)
    modified = prefix + opening + "\n" + new_html + "\n" + closing + suffix
    if modified != text:
        path.write_text(modified, encoding="utf-8")
        return True
    return False

def render(posts, count):
    if not posts:
        return '<li class="blog-empty">최신 글은 블로그 RSS 연결 후 여기에 표시됩니다.</li>'
    lines = []
    for post in posts[:count]:
        title = html.escape(post["title"], quote=True)
        url = html.escape(post["url"], quote=True)
        stamp = html.escape(post.get("date") or "", quote=True)
        date_html = f'<time datetime="{stamp}">{stamp.replace("-", ".")}</time>' if stamp else ""
        lines.append(
            f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">'
            f'<span class="blog-post-title">{title}</span>{date_html}'
            f'<span class="blog-post-arrow" aria-hidden="true">↗</span></a></li>'
        )
    return "\n".join(lines)

def update_lastmod(url_path, today):
    document = SITEMAP.read_text(encoding="utf-8")
    target = "https://www.59man.shop" + url_path
    pattern = re.compile(r"(<url><loc>" + re.escape(target) + r"</loc><lastmod>)[^<]+(</lastmod></url>)")
    replacement, count = pattern.subn(lambda m: m.group(1) + today + m.group(2), document)
    if count != 1:
        raise ValueError("Missing sitemap entry: " + url_path)
    if document != replacement:
        SITEMAP.write_text(replacement, encoding="utf-8")

def main():
    try:
        fresh = fetch_entries()
    except Exception as error:
        print(f"::warning::Naver RSS was not accessible; existing page links preserved. {error}", file=sys.stderr)
        return 0

    old = []
    if STATE.exists():
        old = json.loads(STATE.read_text(encoding="utf-8")).get("posts", [])
    merged = []
    seen = set()
    for item in fresh + old:
        url = permitted_url(item.get("url", ""))
        title = " ".join(str(item.get("title", "")).split())[:145]
        if not url or not title or url in seen:
            continue
        seen.add(url)
        merged.append({"title": title, "url": url, "date": str(item.get("date", ""))[:10]})
        if len(merged) == MAX_ITEMS:
            break

    changed_home = marker_replace(HOME, "<!-- NAVER_BLOG_HOME_START -->",
                                  "<!-- NAVER_BLOG_HOME_END -->", render(merged, 4))
    changed_blog = marker_replace(LIST, "<!-- NAVER_BLOG_LIST_START -->",
                                  "<!-- NAVER_BLOG_LIST_END -->", render(merged, MAX_ITEMS))
    data = json.dumps({"blog": BLOG_HOME, "feed": FEED_URL, "posts": merged},
                      ensure_ascii=False, indent=2) + "\n"
    if not STATE.exists() or STATE.read_text(encoding="utf-8") != data:
        STATE.write_text(data, encoding="utf-8")
    if changed_home or changed_blog:
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        if changed_home:
            update_lastmod("/", today)
        if changed_blog:
            update_lastmod("/blog/", today)
    print(f"Updated Naver blog links: {len(fresh)} in current RSS, {len(merged)} retained; "
          f"home_changed={changed_home}, blog_changed={changed_blog}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
