#!/usr/bin/env python3
"""Official Google Search Console sitemap submission and priority URL monitoring.

This never calls the restricted Google Indexing API and never requests that
individual pages be indexed. OAuth credentials are injected by GitHub Actions.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "sc-domain:59man.shop"
ORIGIN = "https://www.59man.shop"
SITEMAP_URL = ORIGIN + "/sitemap.xml"
SCOPE = "https://www.googleapis.com/auth/webmasters"
NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
PRIORITY = (
    "/선불폰-개통방법/",
    "/선불폰-개통/",
    "/선불폰-셀프개통/",
    "/편의점-선불유심-셀프개통/",
    "/v4-1/topic/network-activation/",
    "/v4-1/topic/sim-buy-where/",
    "/v4-1/topic/weekend-activation/",
)


def sitemap_api_url():
    return (
        "https://www.googleapis.com/webmasters/v3/sites/"
        + urllib.parse.quote(SITE, safe="")
        + "/sitemaps/"
        + urllib.parse.quote(SITEMAP_URL, safe="")
    )


def parse_sitemap(raw):
    root = ET.fromstring(raw)
    if root.tag != NAMESPACE + "urlset":
        raise ValueError("Expected an XML sitemap urlset")
    urls = {}
    for row in root.findall(NAMESPACE + "url"):
        url = row.findtext(NAMESPACE + "loc")
        date = row.findtext(NAMESPACE + "lastmod")
        if not url or url in urls:
            raise ValueError("Sitemap URL missing or duplicate")
        parts = urllib.parse.urlsplit(url)
        if parts.scheme != "https" or parts.netloc != "www.59man.shop" or parts.query or parts.fragment:
            raise ValueError("Unexpected sitemap URL: " + url)
        if not date:
            raise ValueError("Missing sitemap lastmod for " + url)
        try:
            dt.date.fromisoformat(date)
        except ValueError:
            raise ValueError("Invalid lastmod for " + url) from None
        urls[url] = date
    if not urls:
        raise ValueError("Empty sitemap")
    return urls


def await_live_sitemap(local, attempts=16, interval=15):
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                SITEMAP_URL, headers={"User-Agent": "59man-GSC-sitemap/1.0", "Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(req, timeout=25) as response:
                remote = parse_sitemap(response.read())
            if remote == local:
                print("Published sitemap matches GitHub: " + str(len(local)) + " URLs")
                return
            print(f"Waiting for deployed sitemap (attempt {i+1}/{attempts})")
        except (ValueError, urllib.error.URLError, TimeoutError) as exc:
            print(f"Waiting for deployed sitemap (attempt {i+1}/{attempts}): {exc}")
        if i + 1 < attempts:
            time.sleep(interval)
    raise RuntimeError("Live sitemap does not match commit: Google submission cancelled")


def get_token():
    import google.auth
    from google.auth.transport.requests import Request
    credentials, _ = google.auth.default(scopes=[SCOPE])
    credentials.refresh(Request())
    return credentials.token


def google_api(url, token, method="GET", payload=None):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url, data=body, method=method, headers={
            "Authorization": "Bearer " + token, "Accept": "application/json",
            **({"Content-Type": "application/json; charset=utf-8"} if body is not None else {}),
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            print("GSC API " + method + " HTTP " + str(response.status))
            return json.loads(data) if data else {}
    except urllib.error.HTTPError as exc:
        reason = exc.read(1200).decode("utf-8", errors="replace")
        raise RuntimeError(f"Google Search Console API returned HTTP {exc.code}: {reason}") from None


def summary(lines):
    filename = os.environ.get("GITHUB_STEP_SUMMARY")
    if filename:
        with open(filename, "a", encoding="utf-8") as dest:
            dest.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("both", "submit", "inspect"), default="both")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wait-live", action="store_true")
    args = parser.parse_args()
    urls = parse_sitemap((ROOT / "sitemap.xml").read_bytes())
    targets = [ORIGIN + p for p in PRIORITY if ORIGIN + p in urls]
    print(f"Sitemap valid: {len(urls)} URLs; priority tracking: {len(targets)} URLs")
    if args.dry_run:
        print("DRY RUN: no Google authorization or request performed")
        return

    if args.mode in ("both", "submit") and args.wait_live:
        await_live_sitemap(urls)

    token = get_token()
    report = ["### Google Search Console", "", f"- Property: {SITE}"]
    if args.mode in ("both", "submit"):
        google_api(sitemap_api_url(), token, method="PUT")
        print("Sitemap submission accepted; this is not confirmation of indexing.")
        report.append("- Submitted sitemap: " + SITEMAP_URL + " (not a crawl/indexing guarantee)")
    if args.mode in ("both", "inspect"):
        report.extend(["", "| URL | Verdict | Coverage | Last crawl |", "|---|---|---|---|"])
        for url in targets:
            response = google_api(
                "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                token, method="POST",
                payload={"inspectionUrl": url, "siteUrl": SITE, "languageCode": "ko-KR"},
            )
            info = response.get("inspectionResult", {}).get("indexStatusResult", {})
            verdict = info.get("verdict", "UNKNOWN")
            coverage = info.get("coverageState", "No coverage information")
            crawl = info.get("lastCrawlTime", "None reported")
            print(f"{url}: {verdict} / {coverage} / {crawl}")
            report.append(f"| {url.replace(ORIGIN, '')} | {verdict} | {coverage.replace('|','/')} | {crawl} |")
    summary(report)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("GSC automatic task failed: " + str(exc), file=sys.stderr)
        sys.exit(1)
