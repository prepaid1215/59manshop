#!/usr/bin/env python3
"""Notify Naver IndexNow only about pages changed in a deployed main commit.

The public ownership key is intentionally hosted at the site root.
Do not send historic pages wholesale or noindex-only URLs.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.59man.shop"
HOST = "www.59man.shop"
KEY = "b10edb20efd14a1666dd9f0930f45ac5"
KEY_URL = f"{SITE}/{KEY}.txt"
API = "https://searchadvisor.naver.com/indexnow"


def git(*args):
    return subprocess.check_output(["git", "-c", "core.quotePath=false", *args], cwd=ROOT, text=True)


def normalize(url):
    parts = urllib.parse.urlsplit(url.strip())
    if parts.scheme != "https" or parts.netloc != HOST or parts.query or parts.fragment:
        return None
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/%-._~")
    return SITE + path


def sitemap(source):
    xml = ET.fromstring(source)
    return {u for n in xml.iter() if n.tag.endswith("loc") and n.text
            if (u := normalize(n.text))}


def page_url(path):
    if path == "index.html":
        return SITE + "/"
    if not path.endswith("/index.html"):
        return None
    return normalize(SITE + "/" + path[:-10])


def file_for_url(url):
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lstrip("/")
    if ".." in Path(path).parts:
        raise ValueError("Unsafe path")
    return ROOT / path / "index.html" if path else ROOT / "index.html"


def is_indexable(url):
    file = file_for_url(url)
    if not file.is_file():
        return False
    html = file.read_text(encoding="utf-8")
    robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)', html, re.I)
    canonical = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html, re.I)
    return (robots is not None and "noindex" not in robots.group(1).lower()
            and canonical is not None and normalize(canonical.group(1)) == url)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "59man-indexnow/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (OSError, TimeoutError):
        return 0, b""


def deployed(urls, sitemap_changed):
    if fetch(KEY_URL) != (200, KEY.encode("utf-8")):
        return False
    if sitemap_changed and fetch(SITE + "/sitemap.xml") != (200, (ROOT / "sitemap.xml").read_bytes()):
        return False
    for url in urls:
        local = file_for_url(url)
        status, body = fetch(url)
        if local.is_file() and (status != 200 or body != local.read_bytes()):
            return False
        if not local.is_file() and status not in (404, 410):
            return False
    return True


def main():
    # "auto" runs after deployment: first activation sends a site snapshot once,
    # subsequent commits send only actual newly added, updated or removed pages.
    scope = os.environ.get("INDEXNOW_SCOPE", "auto").lower()
    dry_run = os.environ.get("INDEXNOW_DRY_RUN", "false").lower() == "true"
    if scope not in ("auto", "all", "changed"):
        print(f"Unknown INDEXNOW_SCOPE={scope!r}", file=sys.stderr)
        return 2

    before = os.environ.get("INDEXNOW_BEFORE", "")
    after = os.environ.get("INDEXNOW_AFTER", "HEAD")
    new_sitemap = sitemap((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    if not new_sitemap:
        print("Empty or invalid sitemap URL set", file=sys.stderr)
        return 2

    if scope == "all":
        changed = {url for url in new_sitemap if is_indexable(url)}
        sitemap_changed = True
        print("Explicit full-site IndexNow notification requested")
    else:
        if not before or set(before) == {"0"}:
            if scope == "changed":
                before = git("rev-parse", "HEAD^").strip()
            else:
                print("No prior commit available: no automatic URL notification")
                return 0
        changes = git("diff", "--name-status", "--no-renames", before, after).splitlines()
        try:
            old_sitemap = sitemap(git("show", f"{before}:sitemap.xml"))
        except subprocess.CalledProcessError:
            old_sitemap = set()
        changed = set()
        sitemap_changed = False
        initial_install = False
        for line in changes:
            if "\t" not in line:
                continue
            status, path = line.split("\t", 1)
            if path == "sitemap.xml":
                sitemap_changed = True
            if (path == KEY + ".txt" and status.startswith("A")):
                initial_install = True
            url = page_url(path)
            if not url:
                continue
            if status.startswith("D") and url in old_sitemap:
                changed.add(url)
            elif url in new_sitemap and is_indexable(url):
                changed.add(url)
            elif url in old_sitemap and url not in new_sitemap:
                changed.add(url)
        changed.update(url for url in new_sitemap - old_sitemap if is_indexable(url))
        changed.update(old_sitemap - new_sitemap)
        if scope == "auto" and initial_install:
            # First activation: reproduce the verified full-list bootstrap pattern
            # exactly once. Future pushes notify changes only.
            changed = {url for url in new_sitemap if is_indexable(url)}
            sitemap_changed = True
            print("First IndexNow activation: notifying the initial sitemap snapshot")
    if not changed:
        print("No changed indexable URLs: nothing to submit")
        return 0
    print(f"Prepared {len(changed)} URLs (scope={scope}); all URLs are from the site's sitemap")
    if dry_run:
        for url in sorted(changed):
            print("DRY RUN:", url)
        return 0

    print(f"Waiting for the published GitHub Pages files to match {len(changed)} submitted URLs")
    for attempt in range(30):
        if deployed(sorted(changed), sitemap_changed):
            break
        if attempt < 29:
            time.sleep(20)
    else:
        print("Live pages do not match commit; no IndexNow submission", file=sys.stderr)
        return 1

    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEY_URL,
                       "urlList": sorted(changed)}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "59man-indexnow/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Naver IndexNow HTTP {resp.status}: {len(changed)} URLs submitted")
            return 0 if resp.status in (200, 202) else 1
    except urllib.error.HTTPError as exc:
        print(f"Naver IndexNow HTTP {exc.code}: {exc.read(300)!r}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
