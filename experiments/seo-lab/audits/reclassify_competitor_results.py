#!/usr/bin/env python3
"""Reclassify 120 saved competitor HTTP metadata rows without network requests."""
import argparse
import json
from collections import Counter
from pathlib import Path
from competitor_sample_http import classify

def correct(d):
    assert len(d["pages"]) == 120 and len({r["url"] for r in d["pages"]}) == 120
    changed = []
    for r in d["pages"]:
        if r["result"] != "html_200":
            continue
        kind, why = classify(r["url"], r["frozen_candidate_type"], r.get("title_excerpt", ""), r.get("h1_excerpt", ""))
        if kind != r.get("page_type"):
            changed.append({"url": r["url"], "from": r.get("page_type"), "to": kind})
        r["page_type"], r["type_basis"] = kind, why
    for site, summary in d["by_site"].items():
        pages = [r for r in d["pages"] if r["site"] == site]
        assert len(pages) == summary["frozen_n"]
        summary["page_type_counts"] = dict(Counter(r["page_type"] for r in pages))
    d["offline_reclassification"] = {"no_new_http_requests": True, "changed_count": len(changed), "changes": changed}
    return d

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="source", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    result = correct(json.loads(Path(a.source).read_text(encoding="utf-8")))
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result["offline_reclassification"], ensure_ascii=False))
