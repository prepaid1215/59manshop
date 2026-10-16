#!/usr/bin/env python3
"""Read-only HTTP + page-type verification of the frozen 120 competitor URL sample.
Fetches robots.txt once/site then at most 20 approved HTML URLs with a delay.
Never archives competitor HTML, never retries failures, never invents replacements.
"""
import csv
import html
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit, unquote
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "sample_urls_20261016.tsv"
OUTPUT = ROOT / "competitor_sample_http_20261016.result.json"
UA = "SEOResearchReadOnly/1.0"
LIMIT_BYTES = 1_500_000
DELAY_SECONDS = 1.0
TIMEOUT_SECONDS = 15


def ascii_url(url):
    u = urlsplit(url)
    if u.scheme != "https" or not u.hostname or u.username or u.password:
        raise ValueError("Only public HTTPS URLs without credentials allowed")
    host = u.hostname.encode("idna").decode("ascii")
    netloc = host + ((":" + str(u.port)) if u.port else "")
    return urlunsplit((u.scheme, netloc, quote(u.path, safe="/%"), u.query, ""))


def same_site(a, b):
    return urlsplit(ascii_url(a)).hostname.removeprefix("www.") == urlsplit(ascii_url(b)).hostname.removeprefix("www.")


class RedirectOnlyWithinSite(HTTPRedirectHandler):
    def __init__(self, origin, parser):
        self.origin, self.parser = origin, parser
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        newurl = ascii_url(newurl)
        if not same_site(newurl, self.origin):
            raise ValueError("redirect_to_other_host")
        if not self.parser.can_fetch(UA, newurl):
            raise ValueError("redirect_disallowed_by_robots")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url, origin, parser=None, mode="html"):
    safe_url = ascii_url(url)
    opener = build_opener(RedirectOnlyWithinSite(origin, parser)) if parser else build_opener()
    req = Request(safe_url, headers={
        "User-Agent": UA, "Accept-Encoding": "identity",
        "Accept": "text/html,application/xhtml+xml" if mode == "html" else "text/plain",
    })
    try:
        with opener.open(req, timeout=TIMEOUT_SECONDS) as response:
            data = response.read(LIMIT_BYTES + 1)
            if len(data) > LIMIT_BYTES:
                return {"http_status": response.status, "error": "html_exceeds_byte_limit"}
            final_url = response.geturl()
            if not same_site(final_url, origin):
                return {"http_status": response.status, "error": "final_host_mismatch"}
            ctype = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            result = {"http_status": response.status, "final_url": final_url, "content_type": ctype, "bytes": len(data)}
            if mode == "html" and ctype not in {"text/html", "application/xhtml+xml"}:
                result["error"] = "non_html_response"
            else:
                result["_body"] = data.decode("utf-8", "replace")
            return result
    except HTTPError as e:
        return {"http_status": e.code, "error": "http_error"}
    except (URLError, TimeoutError, OSError, ValueError) as e:
        return {"http_status": None, "error": type(e).__name__ + ":" + str(e)[:100]}


def strip_tags(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def extract_heading(content, kind):
    m = re.search(r"<" + kind + r"\b[^>]*>(.*?)</" + kind + r"\s*>", content, re.I | re.S)
    return strip_tags(m.group(1))[:140] if m else ""


def classify(url, saved_type, title, h1):
    path = unquote(urlsplit(url).path).lower().strip("/")
    # Never turn an obvious hub into a region detail on title keywords alone.
    if saved_type == "hub_candidate":
        return "regional_hub", "frozen_manifest_hub_flag"
    if re.fullmatch(r"지역/[^/]+/[^/]+", path) or re.fullmatch(r"region/[^/]+", path):
        return "regional_hub", "short_hierarchical_path"
    if path.startswith("알뜰폰/"):
        return "regional_postpaid_candidate", "url_category_alteulphone"
    if path.startswith("선불폰/") and len(path.split("/")) >= 2:
        return "regional_prepaid_candidate", "url_category_prepaid"
    if re.search(r"[가-힣0-9]{2,}동선불(?:폰|유심)", path):
        return "regional_prepaid_candidate", "url_contains_dong_prepaid"
    if path.startswith("지역/") and len(path.split("/")) >= 4:
        return "regional_candidate", "geo_hierarchy_deep"
    if path.startswith("region/") and len(path.split("/")) >= 2:
        return "regional_candidate", "region_path"
    if re.search(r"/[가-힣0-9]{2,}동$", "/" + path):
        return "regional_candidate", "dong_path"
    return "other_or_unclear", "insufficient_path_evidence"


def main():
    with SAMPLE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert len(rows) == 120 and len({r["url"] for r in rows}) == 120
    sites = defaultdict(list)
    for row in rows:
        assert row["seed"] == "20261016"
        sites[row["site"]].append(row)
    assert len(sites) == 6 and all(len(items) == 20 for items in sites.values())
    results = []
    for site, items in sites.items():
        origin = "https://" + urlsplit(ascii_url(items[0]["url"])).hostname
        robots_url = origin + "/robots.txt"
        r = get(robots_url, origin, mode="robots")
        robot_entry = {"site": site, "robots_http": r.get("http_status"), "robots_error": r.get("error")}
        rp = RobotFileParser()
        if r.get("http_status") == 200 and "_body" in r:
            rp.parse(r["_body"].splitlines())
            available = True
        elif r.get("http_status") == 404:
            rp.parse([])
            available = True
        else:
            available = False
        print(f"{site}: robots={r.get('http_status')} policy_available={available}", flush=True)
        for row in items:
            rec = {
                "site": site, "seed": int(row["seed"]), "url": row["url"],
                "frozen_candidate_type": row["candidate_type"],
                "robots_http": robot_entry["robots_http"],
            }
            try:
                allowed = available and rp.can_fetch(UA, ascii_url(row["url"]))
            except ValueError:
                allowed = False
            if not available:
                rec.update({"result": "robots_unavailable", "page_type": "not_checked"})
            elif not allowed:
                rec.update({"result": "robots_disallowed", "page_type": "not_checked"})
            else:
                result = get(row["url"], origin, parser=rp)
                rec["http_status"] = result.get("http_status")
                rec["final_url"] = result.get("final_url")
                rec["bytes"] = result.get("bytes")
                rec["content_type"] = result.get("content_type")
                if result.get("http_status") == 200 and "_body" in result:
                    raw = result["_body"]
                    title, h1 = extract_heading(raw, "title"), extract_heading(raw, "h1")
                    kind, why = classify(row["url"], row["candidate_type"], title, h1)
                    rec.update({"result": "html_200", "page_type": kind, "type_basis": why,
                                "has_title": bool(title), "has_h1": bool(h1),
                                "title_excerpt": title[:100], "h1_excerpt": h1[:100]})
                else:
                    rec.update({"result": result.get("error", "unclassified_response"), "page_type": "not_checked"})
                time.sleep(DELAY_SECONDS)
            results.append(rec)
        counts = Counter((x["result"], x["page_type"]) for x in results if x["site"] == site)
        print(json.dumps({"site": site, "n": len(items), "results": [
            {"result": state, "type": typ, "n": count} for (state, typ), count in sorted(counts.items())
        ]}, ensure_ascii=False), flush=True)
    report = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "method": "frozen TSV 120; robots.txt then <=20 HTML GET per site; no retries/replacements",
        "limits": {"delay_seconds": DELAY_SECONDS, "html_max_bytes": LIMIT_BYTES, "timeout_seconds": TIMEOUT_SECONDS},
        "important": "URL/path-based type labels are candidates, NOT manual content verification. Neither HTTP 200 nor sitemap listing proves Naver indexing.",
        "pages": results,
        "by_site": {},
    }
    for site, items in sites.items():
        group = [r for r in results if r["site"] == site]
        report["by_site"][site] = {
            "frozen_n": len(items),
            "result_counts": dict(Counter(r["result"] for r in group)),
            "page_type_counts": dict(Counter(r["page_type"] for r in group)),
            "html_200": sum(r["result"] == "html_200" for r in group),
        }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
