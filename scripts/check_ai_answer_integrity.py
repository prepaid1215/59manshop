#!/usr/bin/env python3
"""Verify that visible FAQ answers, metadata and topic links agree.

This is a consistency audit, not a promise of AI citation or search ranking.
Uses Python's standard library only.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.59man.shop"
ORG_ID = BASE + "/#organization"
FAQ_ID = BASE + "/faq/#collection"
errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def clean(markup: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", markup)).split())


def schemas(markup: str) -> list[dict]:
    result = []
    for raw in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', markup):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                result.append(parsed)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON-LD: {exc}")
    return result


hub = (ROOT / "faq" / "index.html").read_text(encoding="utf-8")
hub_schemas = schemas(hub)
collection = next((v for v in hub_schemas if v.get("@type") == "CollectionPage"), None)
check(collection is not None, "FAQ index: CollectionPage metadata missing")
visible = [
    (url, html.unescape(name))
    for url, name in re.findall(
        r'<a class="aq-link-card" href="([^"]+)"><span>([^<]+)</span>', hub
    )
]
check(bool(visible), "FAQ index: no visible question links")

if collection:
    check(collection.get("@id") == FAQ_ID, "FAQ collection @id mismatch")
    index = collection.get("mainEntity", {})
    check(index.get("@type") == "ItemList", "FAQ index: ItemList missing")
    items = index.get("itemListElement", [])
    check(index.get("numberOfItems") == len(visible), "FAQ index: item count mismatch")
    check(len(items) == len(visible), "FAQ index: visible links != JSON-LD items")
    for pos, ((href, question), entry) in enumerate(zip(visible, items), 1):
        check(entry.get("position") == pos, f"FAQ index item {pos}: wrong position")
        check(entry.get("name") == question, f"FAQ index item {pos}: question differs")
        check(entry.get("item") == BASE + href, f"FAQ index item {pos}: link differs")
    for role in ("author", "publisher"):
        check(collection.get(role, {}).get("@id") == ORG_ID,
              f"FAQ collection: {role} identity mismatch")

sitemap_data = ElementTree.fromstring(
    (ROOT / "sitemap.xml").read_text(encoding="utf-8")
)
sitemap_urls = {
    item.text for item in sitemap_data.findall(".//{*}loc")
    if item.text
}
for href, question in visible:
    check(href.startswith("/") and href.endswith("/"),
          f"FAQ link isn't a site path: {href}")
    check(BASE + href in sitemap_urls,
          f"FAQ link missing from sitemap: {href}")
    target = ROOT / unquote(href.lstrip("/")) / "index.html"
    check(target.is_file(), f"FAQ link target missing: {href}")

article_count = 0
for path in ROOT.rglob("index.html"):
    if ".git" in path.parts:
        continue
    markup = path.read_text(encoding="utf-8")
    article = next(
        (v for v in schemas(markup) if v.get("@type") == "Article"
         and v.get("isPartOf", {}).get("@id") == FAQ_ID), None
    )
    if article is None:
        continue

    article_count += 1
    url = BASE + "/" + path.relative_to(ROOT).parent.as_posix() + "/"
    check(article.get("mainEntityOfPage") == url,
          f"{path}: canonical schema URL differs")
    check(article.get("@id") == url + "#article",
          f"{path}: Article @id differs")
    check(f'rel="canonical" href="{url}"' in markup,
          f"{path}: missing canonical")
    check("noindex" not in markup and "nosnippet" not in markup,
          f"{path}: disallowed index/snippet")
    check(url in sitemap_urls, f"{path}: article not in sitemap")
    for role in ("author", "publisher"):
        check(article.get(role, {}).get("@id") == ORG_ID,
              f"{path}: {role} does not reference organization")
    heading = re.search(r'<h1>([\s\S]*?)</h1>', markup)
    check(heading is not None, f"{path}: no visible H1")
    if heading:
        check(clean(heading.group(1)) == html.unescape(article.get("headline", "")),
              f"{path}: headline differs from visible H1")
    answer = re.search(
        r'<section class="answer-card">\s*<h2>[\s\S]*?</h2>\s*'
        r'<p>([\s\S]*?)</p>\s*</section>', markup
    )
    check(answer is not None, f"{path}: visible main answer missing")
    if answer:
        check(clean(answer.group(1)) == article.get("abstract", ""),
              f"{path}: Article abstract differs from visible answer")
        check(len(clean(answer.group(1))) >= 55,
              f"{path}: answer is too short to be useful")

check(article_count >= 48,
      f"Expected at least 48 individually linked FAQ articles; got {article_count}")
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
check("User-agent: OAI-SearchBot\nAllow: /" in robots,
      "OAI-SearchBot allow directive missing")
check("Sitemap: " + BASE + "/sitemap.xml" in robots,
      "Sitemap declaration missing in robots.txt")

print(f"AI answer integrity: {len(visible)} question links; {article_count} "
      f"article summaries; {len(sitemap_urls)} indexed URLs")
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("PASS: FAQ links, visible answers, entity identity and JSON-LD are consistent")
