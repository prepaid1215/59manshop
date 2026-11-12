#!/usr/bin/env python3
"""Check all indexable sitemap URLs and their real page modification dates.

Usage:
  python scripts/sync_sitemap_lastmod.py          # write dates
  python scripts/sync_sitemap_lastmod.py --check  # CI validation only

Only update a date when its HTML content changes. Never mark every URL as
updated merely because the sitemap file itself was regenerated.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://www.59man.shop/"
URL_RE = re.compile(r"(<url><loc>(https://www\.59man\.shop/[^<]*)</loc>)(?:<lastmod>[^<]*</lastmod>)?(</url>)")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def modified(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=ROOT,
                      capture_output=True, text=True, check=True).stdout.strip():
        return dt.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
    value = git("log", "-1", "--format=%cs", "--", relative)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"No committed modification date: {relative}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    xml = SITEMAP.read_text(encoding="utf-8")
    seen = set()

    def update(match: re.Match[str]) -> str:
        before, url, after = match.groups()
        if url in seen:
            raise ValueError(f"Duplicate sitemap URL: {url}")
        seen.add(url)
        parsed = urlsplit(url)
        if parsed.query or parsed.fragment or not url.startswith(BASE):
            raise ValueError(f"Unexpected sitemap URL: {url}")
        path = ROOT / unquote(parsed.path).lstrip("/") / "index.html"
        if not path.is_file():
            raise ValueError(f"Missing HTML for: {url}")
        return before + "<lastmod>" + modified(path) + "</lastmod>" + after

    expected = URL_RE.sub(update, xml)
    if len(seen) != xml.count("<url>") or not seen:
        raise ValueError(f"Sitemap entries invalid: {len(seen)} matched out of {xml.count('<url>')} URLs")
    if args.check:
        if expected != xml:
            print("Sitemap lastmod out of sync; run python scripts/sync_sitemap_lastmod.py", file=sys.stderr)
            return 1
        print(f"Sitemap: {len(seen)} URLs, lastmod dates verified against Git history")
        return 0
    if expected != xml:
        SITEMAP.write_text(expected, encoding="utf-8")
        print(f"Updated sitemap lastmod for {len(seen)} URLs")
    else:
        print("Sitemap dates already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
