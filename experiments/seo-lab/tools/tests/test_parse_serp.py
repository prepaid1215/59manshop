"""Small local-only smoke tests. No network requests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from parse_serp import parse_html, clean_url, area

class ParserTests(unittest.TestCase):
    def test_offline_keyword_cards(self):
        body=('<div class="api_subject_bx"><a class="total_tit" href="https://www.59man.shop/선불폰-개통/">선불폰 개통 안내</a></div>'
              '<div class="api_subject_bx"><a class="total_tit" href="https://cafe.naver.com/example/12345">카페 선불폰 이용 후기</a></div>')
        rows,status,notes=parse_html(body.encode())
        self.assertEqual([r["block_type"] for r in rows],["WEB","CAFE"])
        self.assertEqual(rows[0]["is_59man"],"Y")
        self.assertIn("부분 추출",status)

    def test_captcha_not_false_zero(self):
        rows,status,_=parse_html("자동입력 방지 안내".encode())
        self.assertEqual(rows,[])
        self.assertEqual(status,"수집 실패")

    def test_opaque_link_is_excluded(self):
        self.assertFalse(clean_url("https://naver.me/abcde"))

if __name__=="__main__":
    unittest.main()
