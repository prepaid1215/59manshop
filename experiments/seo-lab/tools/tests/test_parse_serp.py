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

    def test_cards_in_one_section_share_block(self):
        body=('<div class="api_subject_bx"><ul>'+''.join(
            f'<li class="bx"><div class="total_wrap"><a class="title_link" href="https://blog.naver.com/u{i}/22300{i}">블로그 글 제목 {i}</a></div></li>'
            for i in range(3))+'</ul></div>')
        rows,_,_=parse_html(body.encode())
        self.assertEqual([r["block_order"] for r in rows],[1,1,1])
        self.assertEqual([r["rank_in_block"] for r in rows],[1,2,3])

    def test_lst_total_is_not_ad(self):
        body=('<div class="api_subject_bx"><ul class="lst_total"><li class="bx"><div class="total_wrap">'
              '<a class="link_tit" href="https://www.59man.shop/선불폰-개통/">선불폰 개통 안내</a></div></li></ul></div>')
        rows,_,_=parse_html(body.encode())
        self.assertEqual(rows[0]["block_type"],"WEB")
        self.assertEqual(rows[0]["organic_rank"],1)

    def test_powerlink_is_ad(self):
        body=('<div class="api_subject_bx"><div class="powerlink"><div class="total_wrap">'
              '<a class="link_tit" href="https://ads.example.com/x">광고 사이트 제목</a></div></div></div>')
        rows,_,_=parse_html(body.encode())
        self.assertEqual(rows[0]["block_type"],"AD")

    def test_news_section_not_counted_as_web(self):
        body=('<div class="api_subject_bx news"><div class="total_wrap">'
              '<a class="news_tit" href="https://www.example-press.co.kr/article/1">선불폰 관련 기사 제목</a></div></div>')
        rows,_,_=parse_html(body.encode())
        self.assertEqual(rows[0]["block_type"],"OTHER")

if __name__=="__main__":
    unittest.main()
