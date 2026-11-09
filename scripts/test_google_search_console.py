"""Offline tests: never contact Google or require credentials."""
import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).with_name("google_search_console.py")
spec = importlib.util.spec_from_file_location("gsc", path)
gsc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gsc)


class SitemapAutomationTests(unittest.TestCase):
    def test_sitemap_api_endpoint(self):
        self.assertEqual(
            gsc.sitemap_api_url(),
            "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3A59man.shop/"
            "sitemaps/https%3A%2F%2Fwww.59man.shop%2Fsitemap.xml",
        )

    def test_published_targets_are_in_local_sitemap(self):
        items = gsc.parse_sitemap((gsc.ROOT / "sitemap.xml").read_bytes())
        self.assertEqual(len(items), 35)
        self.assertTrue(all(gsc.ORIGIN + path in items for path in gsc.PRIORITY))

    def test_missing_lastmod_not_allowed(self):
        xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               '<url><loc>https://www.59man.shop/</loc></url></urlset>')
        with self.assertRaisesRegex(ValueError, "lastmod"):
            gsc.parse_sitemap(xml)

    def test_foreign_url_not_allowed(self):
        xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               '<url><loc>https://example.org/</loc><lastmod>2026-11-09</lastmod></url></urlset>')
        with self.assertRaisesRegex(ValueError, "Unexpected sitemap URL"):
            gsc.parse_sitemap(xml)

    def test_duplicate_url_not_allowed(self):
        item = '<url><loc>https://www.59man.shop/</loc><lastmod>2026-11-09</lastmod></url>'
        xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + item + item + '</urlset>'
        with self.assertRaisesRegex(ValueError, "duplicate"):
            gsc.parse_sitemap(xml)


if __name__ == "__main__":
    unittest.main()
