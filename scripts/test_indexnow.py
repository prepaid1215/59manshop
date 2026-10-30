"""Offline regression checks for the Naver IndexNow helper."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import submit_indexnow as m


class IndexNowTests(unittest.TestCase):
    def test_url_normalization_for_korean_paths(self):
        direct = m.normalize("https://www.59man.shop/선불폰-개통/")
        encoded = m.normalize("https://www.59man.shop/%EC%84%A0%EB%B6%88%ED%8F%B0-%EA%B0%9C%ED%86%B5/")
        self.assertEqual(direct, encoded)
        self.assertIsNone(m.normalize("https://preplan.site/선불폰-개통/"))
        self.assertIsNone(m.normalize("https://www.59man.shop/?from=test"))

    def test_index_path_mapping(self):
        self.assertEqual(m.page_url("index.html"), m.SITE + "/")
        self.assertEqual(m.page_url("선불폰-개통/index.html"), m.normalize(m.SITE + "/선불폰-개통/"))
        self.assertIsNone(m.page_url("assets/app.js"))

    def test_sitemap_only_our_domain(self):
        source = ('<urlset><url><loc>https://www.59man.shop/</loc></url>'
                  '<url><loc>https://preplan.site/</loc></url></urlset>')
        self.assertEqual(m.sitemap(source), {m.SITE + "/"})

    def test_only_indexable_self_canonical_html_is_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "good"
            target.mkdir()
            doc = target / "index.html"
            doc.write_text('<meta name="robots" content="index,follow">'
                           '<link rel="canonical" href="https://www.59man.shop/good/">',
                           encoding="utf-8")
            with patch.object(m, "ROOT", root):
                self.assertTrue(m.is_indexable(m.SITE + "/good/"))
                doc.write_text('<meta name="robots" content="noindex">'
                               '<link rel="canonical" href="https://www.59man.shop/good/">',
                               encoding="utf-8")
                self.assertFalse(m.is_indexable(m.SITE + "/good/"))

    def test_real_sitemap_has_local_indexable_pages(self):
        urls = m.sitemap((m.ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(urls), 20)
        self.assertTrue(all(m.file_for_url(url).is_file() for url in urls))
        self.assertTrue(all(m.is_indexable(url) for url in urls))


if __name__ == "__main__":
    unittest.main()
