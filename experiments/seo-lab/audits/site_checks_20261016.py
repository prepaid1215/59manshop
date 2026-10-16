#!/usr/bin/env python3
"""Read-only site verification and exact preplan regional sitemap overlap audit.
This script performs at most six public HTTP GETs, does not alter any service
or perform crawling, and does not assert Naver indexing from HTML status.
"""
import csv
import gzip
import html
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SITE = "https://www.59man.shop"
URLS = [
    SITE + "/선불폰-개통/",
    SITE + "/선불폰-개통방법/",
    SITE + "/선불폰-셀프개통/",
    SITE + "/sitemap.xml",
    "https://preplan.site/region-sitemap.xml",
]
USER_AGENT = "Mozilla/5.0 (compatible; ManualSEOReadOnly/1.0; one-time audit)"
MANIFEST = Path(__file__).resolve().parents[1] / "bulk1000" / "manifest.tsv"
OUTPUT = Path(__file__).with_name("site_checks_20261016.result.json")


def retrieve(url):
    target = urlsplit(url)
    safe_url = target._replace(path=quote(target.path, safe="/%")).geturl()
    req = Request(safe_url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, identity"})
    try:
        with urlopen(req, timeout=18) as resp:
            payload = resp.read(12_000_000)
            encoding = resp.headers.get("Content-Encoding", "").lower()
            if encoding == "gzip":
                payload = gzip.decompress(payload)
            return {
                "status": resp.status, "url": resp.url,
                "bytes": len(payload), "body": payload.decode("utf-8", "replace")
            }
    except HTTPError as exc:
        return {"status": exc.code, "url": url, "error": f"HTTP {exc.code}"}
    except (URLError, TimeoutError, OSError) as exc:
        return {"status": None, "url": url, "error": str(exc)[:200]}


def xml_locs(data):
    root = ET.fromstring(data)
    return [elem.text.strip() for elem in root.iter() if elem.tag.rsplit("}", 1)[-1] == "loc" and elem.text]


def normalize_region_path(url):
    # An exact match is only a one-segment URL /<dong>선불폰/.
    p = unquote(urlsplit(url).path).strip("/")
    if p.count("/") != 0 or not p.endswith("선불폰"):
        return None
    return p[:-len("선불폰")]


def inspect_page(result):
    if result.get("status") != 200 or "body" not in result:
        return {k: v for k, v in result.items() if k != "body"}
    body = result["body"]
    robots = re.search(r'<meta\s+name=["\x27]robots["\x27]\s+content=["\x27]([^"\x27]+)', body, re.I)
    canon = re.search(r'<link\s+rel=["\x27]canonical["\x27]\s+href=["\x27]([^"\x27]+)', body, re.I)
    title = re.search(r'<title>(.*?)</title>', body, re.I | re.S)
    return {
        "status": result["status"], "final_url": result["url"], "bytes": result["bytes"],
        "robots": robots.group(1) if robots else None,
        "canonical": html.unescape(canon.group(1)) if canon else None,
        "title": html.unescape(title.group(1).strip()) if title else None,
        "has_h1": bool(re.search(r"<h1\b", body, re.I)),
    }


def main():
    if not MANIFEST.exists():
        raise SystemExit("manifest.tsv missing")
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        items = list(csv.DictReader(handle, delimiter="\t"))
    if len(items) != 1000:
        raise SystemExit(f"manifest is not 1000 rows: {len(items)}")
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(retrieve, URLS))
    by_url = {URLS[i]: results[i] for i in range(len(URLS))}
    page_results = {u: inspect_page(by_url[u]) for u in URLS[:3]}
    site_map = by_url[URLS[3]]
    preplan = by_url[URLS[4]]
    site_map_info = {"http_status": site_map.get("status"), "error": site_map.get("error")}
    if site_map.get("status") == 200:
        try:
            locs = xml_locs(site_map["body"])
            site_map_info.update({"locs": len(locs), "unique_locs": len(set(locs)), "new_3_present": {
                url: url in set(locs) for url in URLS[:3]}})
        except ET.ParseError as exc:
            site_map_info["parse_error"] = str(exc)
    preplan_info = {"http_status": preplan.get("status"), "error": preplan.get("error")}
    if preplan.get("status") == 200:
        try:
            locs = xml_locs(preplan["body"])
            dong_set = {normalize_region_path(u) for u in locs}
            dong_set.discard(None)
            overlaps = [r for r in items if r["dong"] in dong_set]
            preplan_info.update({
                "sitemap_entries": len(locs),
                "direct_root_region_names": len(dong_set),
                "candidate_overlap_exact_root_region": len(overlaps),
                "candidate_not_matched": 1000 - len(overlaps),
                "cohorts": dict(Counter(r["cohort"] for r in overlaps)),
                "examples": [r["province"] + " " + r["dong"] for r in overlaps[:15]]
            })
        except ET.ParseError as exc:
            preplan_info["parse_error"] = str(exc)
    report = {
        "notice": "HTTP 200, sitemap listing and site:SERP are not equivalent to Naver crawling/indexing",
        "site_pages": page_results, "site_sitemap": site_map_info,
        "preplan_sitemap_overlap": preplan_info,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
