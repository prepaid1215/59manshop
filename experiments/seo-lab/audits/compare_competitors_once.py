#!/usr/bin/env python3
"""One-pass, transient competitor HTML similarity comparison.
Frozen URL inventory; no page replacement; robots-aware. Raw HTML lives only
inside a TemporaryDirectory on the Actions runner and is never uploaded.
"""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.robotparser import RobotFileParser

from competitor_sample_http import UA, ascii_url, get, extract_heading, classify

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "sample_urls_20261016.tsv"
SIMILARITY = ROOT / "similarity.py"
OUT = ROOT / "COMPETITOR_SIMILARITY_ONCE_20261016.json"
SEED = 20261016
DELAY = 1.0
EXCLUDE_GEO_WORDS = {"번호이동", "자동", "연동", "작동", "변동", "활동", "운동", "행동"}


def infer_geo_name(url, h1):
    """For script-based paths prefer last explicit Hangul locality token;
    for romanized paths try locality in the visible H1. If uncertain return
    empty and report count separately; don't fabricate a Korean name."""
    path = unquote(urlsplit(url).path)
    slug = path.rstrip("/").split("/")[-1]
    if slug.endswith("선불폰"):
        slug = slug[:-3]
    if slug.endswith("선불유심"):
        slug = slug[:-4]
    if re.search(r"[가-힣]", slug):
        tokens = re.findall(r"[가-힣0-9]+(?:동|읍|면|리|가)", slug)
        tokens = [t for t in tokens if t not in EXCLUDE_GEO_WORDS]
        if tokens:
            # Some paths prefix the municipality; return the most local
            # terminal segment, but retain source for later verification.
            return tokens[-1], "url_korean"
    tokens = re.findall(r"[가-힣0-9]+(?:동|읍|면|리|가)", h1)
    tokens = [t for t in tokens if t not in EXCLUDE_GEO_WORDS]
    if tokens:
        return tokens[-1], "h1_korean_heuristic"
    # Latin path name (e.g. gil-dong) is genuinely visible in URL/HTML;
    # may not strip the Korean spelling from body, report as such.
    latin = re.search(r"[a-z0-9-]+-(?:dong|eup|myeon|ri)$", slug, re.I)
    if latin:
        return latin.group(0), "latin_slug_not_korean_normalized"
    return "", "name_unavailable"


def category(site, url, frozen, h1):
    if frozen == "hub_candidate":
        return "hub_excluded"
    kind, _ = classify(url, frozen, "", h1)
    if kind in {"regional_hub", "other_or_unclear"}:
        return "unverified_type_excluded"
    if site == "ntelact":
        p = unquote(urlsplit(url).path)
        return "postpaid" if p.startswith("/알뜰폰/") else "prepaid"
    return "regional_prepaid_or_general"


def main():
    with SAMPLES.open(encoding="utf-8", newline="") as fp:
        rows = list(csv.DictReader(fp, delimiter="\t"))
    assert len(rows) == 120 and len({r["url"] for r in rows}) == 120
    bysite = defaultdict(list)
    for r in rows:
        assert r["seed"] == str(SEED)
        bysite[r["site"]].append(r)
    assert len(bysite) == 6 and all(len(v) == 20 for v in bysite.values())
    status = []
    measurements = {}
    with tempfile.TemporaryDirectory(prefix="competitor-once-") as scratch:
        tmp = Path(scratch)
        # Keeping all intermediate full HTML only in transient Actions scratch.
        for site, items in bysite.items():
            origin = "https://" + urlsplit(ascii_url(items[0]["url"])).hostname
            robots = get(origin + "/robots.txt", origin, mode="robots")
            rp = RobotFileParser()
            if robots.get("http_status") == 200 and "_body" in robots:
                rp.parse(robots["_body"].splitlines())
                robots_ready = True
            elif robots.get("http_status") == 404:
                rp.parse([])
                robots_ready = True
            else:
                robots_ready = False
            for idx, r in enumerate(items):
                entry = {"site": site, "url": r["url"], "candidate_type": r["candidate_type"], "robots_http": robots.get("http_status")}
                if r["candidate_type"] == "hub_candidate":
                    entry["status"] = "frozen_hub_excluded"
                elif not robots_ready:
                    entry["status"] = "robots_unavailable"
                elif not rp.can_fetch(UA, ascii_url(r["url"])):
                    entry["status"] = "robots_disallowed"
                else:
                    result = get(r["url"], origin, parser=rp)
                    entry["http_status"] = result.get("http_status")
                    entry["content_type"] = result.get("content_type")
                    if result.get("http_status") == 200 and "_body" in result:
                        raw = result["_body"]
                        h1 = extract_heading(raw, "h1")
                        group = category(site, r["url"], r["candidate_type"], h1)
                        entry["page_type"] = group
                        entry["has_h1"] = bool(h1)
                        if group == "unverified_type_excluded":
                            entry["status"] = "type_uncertain_excluded"
                        elif not h1:
                            entry["status"] = "h1_missing_excluded"
                        else:
                            name, source = infer_geo_name(r["url"], h1)
                            entry.update({"status": "included", "name": name, "name_source": source})
                            folder = tmp / (site + "_" + group)
                            folder.mkdir(exist_ok=True)
                            filename = str(idx).zfill(3) + ".html"
                            (folder / filename).write_text(raw, encoding="utf-8")
                            # Required name mapping; when blank, a token guaranteed not to match any HTML.
                            entry["temp_file"] = filename
                            entry["temp_folder"] = str(folder)
                            entry["fallback_no_name"] = not bool(name)
                    else:
                        entry["status"] = result.get("error", "bad_http_or_content_type")
                    time.sleep(DELAY)
                status.append(entry)
            print(json.dumps({"site_completed": site, "n": len(items),
                             "statuses": dict(Counter(r["status"] for r in status if r["site"] == site))}, ensure_ascii=False), flush=True)

        eligible = defaultdict(list)
        for row in status:
            if row["status"] == "included":
                eligible[(row["site"],row["page_type"])].append(row)
        for (site, group), records in sorted(eligible.items()):
            folder = Path(records[0]["temp_folder"])
            namesfile = tmp / (site + "_" + group + "_names.tsv")
            namesfile.write_text("".join(row["temp_file"] + "\t" + (row["name"] or "NOMATCH_LOCALITY_0000") + "\n" for row in records), encoding="utf-8")
            # similiarity.py sorts input files; with n>=2 it retains the entire
            # fixed candidate set. No replacements or additional sampling.
            if len(records) < 2:
                measurements[site + "_" + group] = {"n": len(records), "similarity": None, "note": "n<2"}
                continue
            outfile = tmp / (site + "_" + group + "_similarity.json")
            proc = subprocess.run([sys.executable, str(SIMILARITY), "--pages", str(folder),
                                   "--names", str(namesfile), "--n", str(len(records)),
                                   "--seed", str(SEED), "--out", str(outfile)],
                                   capture_output=True, text=True)
            if proc.returncode != 0:
                measurements[site + "_" + group] = {"n": len(records), "error": proc.stderr[-300:]}
                continue
            got = json.loads(outfile.read_text(encoding="utf-8"))
            measurements[site + "_" + group] = {
                "n": len(records), "pairs": got["similarity"]["body"]["pairs"],
                "region_names_from_url": sum(r["name_source"] == "url_korean" for r in records),
                "region_names_from_h1_heuristic": sum(r["name_source"] == "h1_korean_heuristic" for r in records),
                "latin_names_not_normalized_to_korean": sum(r["name_source"] == "latin_slug_not_korean_normalized" for r in records),
                "names_unavailable": sum(not r["name"] for r in records),
                "body_mean": got["similarity"]["body"]["mean"],
                "body_min": got["similarity"]["body"]["min"],
                "body_max": got["similarity"]["body"]["max"],
                "boilerplate_removed_mean": got["similarity"]["body_boilerplate_removed"]["mean"],
                "mean_body_chars": got["body_chars"]["raw_mean"],
                "mean_unique_body_chars": got["body_chars"]["boilerplate_removed_mean"],
                "no_unique_body_count": got["docs_with_no_unique_body"],
                "sample_urls": [r["url"] for r in records],
            }
    # Scratch dir (raw HTML) automatically deleted before reporting.
    report = {
        "scope": "One-time comparison of fixed public sitemap sample, not a Naver index test",
        "seed": SEED, "baseline_59man_preview_body_mean": 1.0,
        "method": "same similarity.py char-6-gram Jaccard after locality replacement; boilerplate 80%; site and category separated",
        "limits": "some romanized locality strings may not match the Korean text; compare results as descriptive, not SEO ranking signals",
        "status_counts": {site: dict(Counter(s["status"] for s in status if s["site"] == site)) for site in bysite},
        "measurements": measurements,
        "raw_html_uploaded": False,
        "status_details": [{k:v for k,v in row.items() if k not in {"temp_file","temp_folder"}} for row in status]
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    for key, value in measurements.items():
        print(json.dumps({"cohort": key, **{k:v for k,v in value.items() if k != "sample_urls"}}, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
