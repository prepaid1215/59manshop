#!/usr/bin/env python3
"""Offline regression tests for SEO audit utilities, no network access."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

audit = load("audit_site_checks", "site_checks_20261016.py")
similarity = load("audit_similarity", "similarity.py")

class AuditTests(unittest.TestCase):
    def test_prefixed_matches(self):
        cases = [
            ("관악구신사동", "신사동", True),
            ("강남구신사동", "신사동", True),
            ("용인시수지구상현동", "상현동", True),
            ("신사동", "신사동", False),
            ("강남신사동", "신사동", False),
            ("대신사동", "신사동", False),
            ("신사동선불폰", "신사동", False),
        ]
        for slug, name, expected in cases:
            with self.subTest(slug=slug, name=name):
                self.assertEqual(audit.prefixed_match(slug, name), expected)

    def test_jaccard_not_zero_for_missing_text(self):
        self.assertIsNone(similarity.jaccard(set(), {"abcdef"}))
        self.assertIsNone(similarity.jaccard(set(), set()))
        self.assertEqual(similarity.jaccard({"abcdef"}, {"abcdef"}), 1.0)

    def test_pipeline_sample_reproducibility(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            names = []
            for i, (name, body) in enumerate([
                ("신사동", "동일한 안내입니다. 같은 조건을 확인하세요."),
                ("가산동", "동일한 안내입니다. 같은 조건을 확인하세요."),
                ("역삼동", "번호이동은 기존 회선 상태를 확인해야 합니다."),
            ]):
                page = root / f"{i}.html"
                page.write_text(f"<html><head><title>{name} 안내</title></head><body><main><h1>{name}</h1><p>{body}</p></main></body></html>", encoding="utf-8")
                names.append(f"{i}.html\t{name}")
            mapping = root / "names.tsv"
            mapping.write_text("\n".join(names) + "\n", encoding="utf-8")
            reports = []
            for n in (1, 2):
                dest = root / f"audit{n}.json"
                subprocess.run([
                    sys.executable, str(ROOT / "similarity.py"),
                    "--pages", str(root), "--names", str(mapping),
                    "--n", "3", "--seed", "20261016", "--out", str(dest)
                ], check=True, capture_output=True, text=True)
                reports.append(json.loads(dest.read_text(encoding="utf-8")))
            self.assertEqual(reports[0]["sample"], reports[1]["sample"])
            self.assertEqual(reports[0]["similarity"], reports[1]["similarity"])
            self.assertEqual(reports[0]["similarity"]["body"]["pairs"], 3)
            self.assertIn("body_boilerplate_removed", reports[0]["similarity"])

    def test_competitor_region_classifier(self):
        disc = load("audit_discovery", "competitor_sitemap_discovery.py")
        cases = [
            ("https://x.com/region/seoul.jpg", False),
            ("https://x.com/region/map.png", False),
            ("https://x.com/번호이동/", False),
            ("https://x.com/선불폰/번호이동", False),
            ("https://x.com/번호이동-방법/", False),
            ("https://x.com/신림동/", True),
            ("https://x.com/신림동선불폰/", True),
            ("https://usimon.pages.dev/region/gwangju/dong-gu/geum-dong/", True),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                self.assertEqual(disc.classify_region(url), expected)

    def test_frozen_120_candidates_unchanged(self):
        import csv
        disc = load("audit_discovery_samples", "competitor_sitemap_discovery.py")
        file = ROOT / "sample_urls_20261016.tsv"
        with file.open(encoding="utf-8", newline="") as handle:
            samples = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(samples), 120)
        from collections import Counter
        self.assertTrue(all(n == 20 for n in Counter(x["site"] for x in samples).values()))
        for row in samples:
            with self.subTest(url=row["url"]):
                self.assertTrue(disc.classify_region(row["url"]))

if __name__ == "__main__":
    unittest.main()
