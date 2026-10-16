#!/usr/bin/env python3
"""Conservative competitor sitemap discovery; metadata only, no page HTML fetch.
Max 1 robots request + 8 sitemap requests per host. Honors robots.txt.
No archived HTML or full sitemap contents enter the Git repository.
"""
import gzip
import json
import random
import re
import time
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, unquote
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

UA = "SEOResearchReadOnly/1.0"
SEED = 20261016
MAX_MAPS = 8
MAX_BYTES = 6_000_000
TARGETS = [
    ("sunbulphone_shop", "https://xn--wr3bt9d38v.shop"),
    ("mbrothers", "https://www.mbrothers.kr"),
    ("usimon", "https://usimon.pages.dev"),
    ("sunbul_guide", "https://xn--220b76v3wcwvf85v.kr"),
    ("ntelecomdasi", "https://ntelecomdasi.com"),
    ("ntelact", "https://ntelact.com"),
]
OUT = Path(__file__).resolve().with_name("competitor_sitemap_discovery.result.json")


def fetch(url):
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/xml,text/xml,text/plain,*/*;q=0.1", "Accept-Encoding": "identity"})
    try:
        with urlopen(req, timeout=12) as r:
            raw = r.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                return {"status": r.status, "final_url": r.url, "error": "response_exceeds_byte_limit"}
            if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
                raw = gzip.decompress(raw)
                if len(raw) > MAX_BYTES:
                    return {"status": r.status, "final_url": r.url, "error": "decoded_response_too_large"}
            return {"status": r.status, "final_url": r.url, "body": raw.decode("utf-8", "replace")}
    except HTTPError as e:
        return {"status": e.code, "final_url": url, "error": "http_error"}
    except (OSError, TimeoutError, URLError, ValueError) as e:
        return {"status": None, "final_url": url, "error": type(e).__name__ + ": " + str(e)[:120]}


def is_same_host(root, candidate):
    a, b = urlsplit(root).hostname, urlsplit(candidate).hostname
    if not a or not b:
        return False
    return a.removeprefix("www.") == b.removeprefix("www.")


def classify_region(url):
    p = unquote(urlsplit(url).path).lower()
    # Exclude image, RSS and document assets even when their path contains /region/.
    if re.search(r"\\.(?:jpg|jpeg|png|webp|svg|gif|xml|pdf|mp4)(?:$|/)", p):
        return False
    if re.search(r"/[가-힣0-9]{2,}동/?$", p):
        return True
    if re.search(r"/(?:region|regions|area|지역)(?:/|$)", p):
        return True
    if re.search(r"/(?:dong|동)(?:/|$)", p):
        return True
    if re.search(r"/(?:알뜰폰/)?dong/", p):
        return True
    if re.search(r"[가-힣0-9]{2,}동(?:선불폰|선불유심|/|-|$)", p):
        return True
    return False


def read_sitemap(payload):
    root = ET.fromstring(payload)
    tag = lambda node: node.tag.rsplit("}", 1)[-1]
    typ = tag(root)
    if typ not in {"urlset", "sitemapindex"}:
        raise ValueError("unexpected XML root: " + typ)
    parent_name = "url" if typ == "urlset" else "sitemap"
    locs = []
    # Only direct <url><loc> or <sitemap><loc>; do NOT count nested <image:loc>.
    for parent in root:
        if tag(parent) != parent_name:
            continue
        for node in parent:
            if tag(node) == "loc" and node.text:
                locs.append(node.text.strip())
                break
    return typ, locs


def inspect(name, root):
    result = {
        "name": name, "origin": root, "robots": {}, "sitemap_attempts": [],
        "candidate_regional_urls": 0, "sample_seed": SEED, "sample_urls": [],
        "status": "not_checked", "limitations": [],
    }
    robot_url = root + "/robots.txt"
    rob = fetch(robot_url)
    result["robots"] = {"url": robot_url, "status": rob["status"], "error": rob.get("error")}
    rp = RobotFileParser()
    if rob["status"] == 200 and rob.get("body") is not None:
        rp.parse(rob["body"].splitlines())
        result["robots"]["disallows_sitemap"] = not rp.can_fetch(UA, root + "/sitemap.xml")
        candidates = [
            line.split(":", 1)[1].strip() for line in rob["body"].splitlines()
            if line.lower().lstrip().startswith("sitemap:")
        ]
    elif rob["status"] == 404:
        rp.parse([])
        candidates = []
        result["robots"]["notice"] = "404 robots: no robots restrictions supplied"
    else:
        result["status"] = "blocked_or_robots_unavailable"
        result["limitations"].append("Robots policy unavailable, skipped sitemap probing rather than guessing")
        return result
    seeds = candidates + [root + "/sitemap.xml", root + "/sitemap_index.xml"]
    queue = deque(dict.fromkeys(seeds))
    visited = set()
    found_urls = set()
    sitemap_indexes = 0
    while queue and len(visited) < MAX_MAPS:
        url = queue.popleft()
        if url in visited:
            continue
        if not is_same_host(root, url):
            result["limitations"].append("Cross-domain sitemap reference skipped")
            continue
        if not rp.can_fetch(UA, url):
            result["sitemap_attempts"].append({"url": url, "status": "robots_disallowed"})
            continue
        visited.add(url)
        got = fetch(url)
        rec = {"url": url, "http_status": got.get("status"), "error": got.get("error")}
        if got.get("status") == 200 and got.get("body"):
            try:
                typ, locs = read_sitemap(got["body"])
                rec.update({"xml_type": typ, "loc_entries": len(locs)})
                if typ == "sitemapindex":
                    sitemap_indexes += 1
                    for child in locs:
                        if len(queue) >= 80:
                            result["limitations"].append("Sitemap queue capped at 80")
                            break
                        if is_same_host(root, child):
                            queue.append(child)
                else:
                    found_urls.update(u for u in locs if is_same_host(root, u))
            except (ET.ParseError, ValueError) as e:
                rec["xml_error"] = str(e)[:100]
        result["sitemap_attempts"].append(rec)
        time.sleep(0.5)
    regional = sorted(u for u in found_urls if classify_region(u))
    sample = random.Random(SEED).sample(regional, min(20, len(regional)))
    result["sitemap_files_fetched"] = len(visited)
    result["sitemap_indexes_found"] = sitemap_indexes
    result["unique_discovered_urls"] = len(found_urls)
    result["raw_url_examples"] = sorted(found_urls)[:6]
    result["candidate_regional_urls"] = len(regional)
    result["sample_urls"] = sorted(sample)
    result["sitemap_queue_unprocessed"] = len(queue)
    if queue:
        result["limitations"].append("Only first 8 sitemap documents inspected; NOT a site-wide count or unbiased sample")
    if regional:
        result["status"] = "partial_regional_sample" if len(regional) < 20 or queue else "regional_sample_ready"
    else:
        result["status"] = "no_regional_urls_discovered"
        result["limitations"].append("Could not establish regional sitemap sample. Do not force or infer zero regional pages.")
    return result


def main():
    report = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "method": "robots-aware public XML sitemap discovery only, one-time, no HTML sampling",
        "limits": {"sitemaps_per_site": MAX_MAPS, "max_bytes_each": MAX_BYTES, "request_pause_seconds": 0.5},
        "sites": [],
    }
    for name, root in TARGETS:
        report["sites"].append(inspect(name, root))
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for x in report["sites"]:
        print(json.dumps({
            "site": x["name"], "status": x["status"], "robots": x["robots"],
            "sitemap_docs": x.get("sitemap_files_fetched", 0),
            "candidate_region_urls": x["candidate_regional_urls"],
            "sample_count": len(x["sample_urls"]), "limitations": x["limitations"],
        }, ensure_ascii=False))

if __name__ == "__main__":
    main()
