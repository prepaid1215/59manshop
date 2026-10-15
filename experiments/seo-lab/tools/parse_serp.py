#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline Naver SERP HTML parser. Never uses HTTP, Playwright, or browser automation.

The extracted order is provisional: verify the saved screenshot before treating
any order or absence as an actual SERP measurement.
"""
import argparse
import csv
import hashlib
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

KST = timezone(timedelta(hours=9))
NAME = re.compile(r"^(\d{8}-\d{4})_(pc|mo)_(.+)\.html$", re.I)
TITLE = re.compile(r"total_tit|link_tit|title_link|api_txt_lines|tit_link|tit_main|ugc_title", re.I)
BOX = re.compile(r"api_subject_bx|total_wrap|ugc_item|ugcItem|web_wrap|lst_total|content_area|section_area|api_section", re.I)
AD = re.compile(r"powerlink|lst_total|ad_group|sp_ad|ad_item|ad_link", re.I)
INFRA = {"search.naver.com", "m.search.naver.com", "nid.naver.com",
         "m.naver.com", "help.naver.com", "nmap.place.naver.com",
         "ad.search.naver.com", "m.ad.search.naver.com"}
RESULT_FIELDS = ["query","device","observed_at_kst","block_order","block_type",
 "rank_in_block","organic_rank","result_url","domain","is_59man",
 "evidence_file","evidence_sha256"]
SHARE_FIELDS = ["query","device","observed_at_kst","extraction_status","organic_parsed",
 "top10_web","top10_blog","top10_cafe","top10_kin","top10_other",
 "top10_unclassified","observed_59man","evidence_file","evidence_sha256","notes"]
PILOT = {"선불폰 개통","선불폰 개통방법","선불폰 셀프개통"}

def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def cls(node):
    if not getattr(node,"get",None):
        return ""
    return " ".join(node.get("class",[]))+" "+(node.get("data-template-id") or "")

def clean_url(href):
    href=(href or "").strip()
    if href.startswith("//"):href="https:"+href
    if not href.startswith(("http://","https://")):return ""
    try:
        u=urlsplit(href);d=(u.hostname or "").lower()
        if not d or d in INFRA or d.endswith(".pstatic.net") or d in {"naver.me","me2.do"}:
            return ""
        if d in {"blog.naver.com","m.blog.naver.com","cafe.naver.com","m.cafe.naver.com"}:
            if not re.search(r"/[^/]+/\d+",u.path) and "ArticleRead.nhn" not in u.path:
                return ""  # exclude profiles and cafe home pages
        return href.split("#",1)[0]
    except ValueError:
        return ""

def area(domain):
    if domain in {"blog.naver.com","m.blog.naver.com"}:return "BLOG"
    if domain in {"cafe.naver.com","m.cafe.naver.com"}:return "CAFE"
    if domain in {"kin.naver.com","m.kin.naver.com"}:return "KIN"
    if domain in {"clip.naver.com","m.clip.naver.com","mate.naver.com"}:return "OTHER"
    if domain.endswith(".naver.com"):return "UNCLASSIFIED"
    return "WEB"

def is_ad(anchor):
    for parent in list(anchor.parents)[:4]:
        if AD.search(cls(parent)):return True
    return False

def parse_html(raw):
    doc=BeautifulSoup(raw.decode("utf-8-sig",errors="replace"),"html.parser")
    visible=doc.get_text(" ",strip=True)
    if any(s in visible for s in ("자동입력 방지","비정상적인 검색 요청","캡차를 입력","CAPTCHA")):
        return [],"수집 실패","captcha or access blocking"
    items=[];seen=set()
    for a in doc.select("a[href]"):
        href=clean_url(a.get("href",""))
        if not href or href in seen:continue
        label=a.get_text(" ",strip=True)
        if len(label)<4 or label in {"더보기","바로가기","공유","저장","길찾기","예약"}:
            continue
        if a.find_parent(["nav","header","footer"]) or a.find_parent(attrs={"aria-hidden":"true"}):
            continue
        if a.find_parent(class_=re.compile("ai_brief|aibrief|ai-summary",re.I)):
            continue  # AI source citations are not independent result cards
        box=a.find_parent(class_=BOX)
        if not box and not TITLE.search(cls(a)) and not a.find_parent("li",class_=re.compile("bx")):
            continue
        seen.add(href)
        d=(urlsplit(href).hostname or "").lower()
        t="AD" if is_ad(a) else area(d)
        group=("box",id(box)) if box else ("category",t)
        items.append((href,d,t,group))
    if not items:return [],"수집 실패","unrecognized HTML structure; manual inspection required"
    out=[];prior=None;block=0;pos=0;organic=0
    for href,d,t,group in items:
        if group!=prior:
            block+=1;pos=0;prior=group
        pos+=1
        if t!="AD":organic+=1
        out.append({"block_order":block,"block_type":t,"rank_in_block":pos,
                    "organic_rank":organic if t!="AD" else "",
                    "result_url":href,"domain":d,
                    "is_59man":"Y" if d in {"59man.shop","www.59man.shop"} else "N"})
    status="부분 추출(화면 대조 필요)" if organic>=10 else "부분 추출(상위 10개 미확인)"
    return out,status,f"{organic} organic links extracted; screenshot audit required"

def review_queries(template):
    suggestions={
      "/":"선불폰",
      "/앤텔레콤-선불폰-개통-방법/":"앤텔레콤 개통방법",
      "/앤텔레콤-웹개통/":"앤텔레콤 개통시간",
      "/v4-1/topic/esim-new/":"선불폰 eSIM 개통",
      "/다이소-유심/":"다이소 선불유심",
      "/kt선불폰-개통/":"KT 선불폰 개통",
      "/kt-바로유심/":"KT 바로유심 구매",
      "/v4-1/topic/kt-nfc-compare/":"KT 바로유심 NFC",
      "/lg-원칩/":"모두의 원칩 개통",
      "/v4-1/topic/network-activation/":"K망 L망 선불폰 차이",
      "/알뜰폰-셀프개통-번호이동/":"선불폰 번호이동",
      "/v4-1/topic/plan-396/":"앤텔레콤 396 요금제",
      "/v4-1/topic/plan-compare/":"선불폰 요금제 비교",
      "/편의점-선불유심-셀프개통/":"편의점 선불유심 개통",
      "/v4-1/topic/sim-buy-where/":"선불유심 구매처",
      "/편의점-선불유심/":"편의점 선불유심",
      "/미납정지-선불폰/":"미납 정지 선불폰",
      "/v4-1/topic/weekend-activation/":"주말 선불폰 개통",
      "/guide/":"선불폰 안내"}
    seen=set();out=[]
    for row in template:
        if row.get("page_group")!="기존19" or row["url"] in seen:continue
        seen.add(row["url"]);u=row["url"]
        out.append({"url":u,"current_target_query":row["target_query"],
                    "proposed_query":suggestions.get(urlsplit(u).path,"재선정 필요"),
                    "basis":"초안 후보(실제 검색 수요 및 SERP 미확인)","approval":"승인 대기"})
    return out

def update_baseline(template,summary,results):
    snapshots={(x["query"],x["device"]):x for x in summary}
    for row in template:
        key=(row.get("target_query"),row.get("device"))
        if key not in snapshots or key[0] not in PILOT:continue
        s=snapshots[key]
        if s["extraction_status"]=="수집 실패":
            row["naver_serp_appeared"]="수집 실패"
            continue
        matches=[x for x in results if (x["query"],x["device"])==key
                 and unquote(x["result_url"]).rstrip("/")==unquote(row["url"]).rstrip("/")]
        if matches:
            x=matches[0]
            row.update({"naver_serp_appeared":"관측(스크린샷 검증 대기)",
                        "serp_block":x["block_type"],"rank":x["organic_rank"],
                        "shown_url":x["result_url"],"checked_at_kst":s["observed_at_kst"],
                        "evidence":s["evidence_file"]+" sha256="+s["evidence_sha256"]})
        else:
            row["naver_serp_appeared"]="미확인(화면 대조 필요)"
            row["checked_at_kst"]=s["observed_at_kst"]
    return template

def main():
    p=argparse.ArgumentParser(description="Parse manually saved SERP HTML without network access.")
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--baseline",type=Path,default=Path(__file__).resolve().parents[1]/"baseline-template.csv")
    p.add_argument("--update-baseline",action="store_true",help="write baseline-observed.csv; never overwrite template")
    args=p.parse_args()
    root=Path(__file__).resolve().parents[3];rawdir=args.raw_dir.resolve()
    if not rawdir.is_dir():p.error(f"Missing evidence directory: {rawdir}")
    if rawdir==root or root in rawdir.parents:
        p.error("Store private raw HTML and PNG OUTSIDE the public Git repository.")
    summaries=[];results=[];skipped=[]
    for path in sorted(rawdir.glob("*.html")):
        m=NAME.match(path.name)
        if not m:
            skipped.append(f"bad filename: {path.name}");continue
        stamp,device,keyword=m.groups()
        try:
            when=datetime.strptime(stamp,"%Y%m%d-%H%M").replace(tzinfo=KST).isoformat(timespec="minutes")
        except ValueError:
            skipped.append(f"bad timestamp: {path.name}");continue
        data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
        found,status,note=parse_html(data)
        device="PC" if device.lower()=="pc" else "모바일"
        meta={"query":keyword,"device":device,"observed_at_kst":when,
              "evidence_file":path.name,"evidence_sha256":digest}
        results.extend([{**meta,**r} for r in found])
        ten=[r for r in found if r["block_type"]!="AD"][:10]
        counts=Counter(x["block_type"] for x in ten)
        if not path.with_suffix(".png").exists():note+="; PNG screenshot missing"
        summaries.append({**meta,"extraction_status":status,
            "organic_parsed":len([r for r in found if r["block_type"]!="AD"]),
            "top10_web":counts["WEB"],"top10_blog":counts["BLOG"],
            "top10_cafe":counts["CAFE"],"top10_kin":counts["KIN"],
            "top10_other":counts["OTHER"],"top10_unclassified":counts["UNCLASSIFIED"],
            "observed_59man":sum(r["is_59man"]=="Y" for r in ten),"notes":note})
    output=args.output_dir.resolve();output.mkdir(parents=True,exist_ok=True)
    day=datetime.now(KST).strftime("%Y%m%d")
    write_csv(output/"serp_results.csv",RESULT_FIELDS,results)
    write_csv(output/f"serp_share_{day}.csv",SHARE_FIELDS,summaries)
    if args.baseline.is_file():
        with args.baseline.open(encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f);fields=reader.fieldnames;template=list(reader)
        write_csv(output/"target_query_review.csv",
                  ["url","current_target_query","proposed_query","basis","approval"],
                  review_queries(template))
        if args.update_baseline:
            write_csv(output/"baseline-observed.csv",fields,
                      update_baseline(template,summaries,results))
    report=["# 오프라인 네이버 SERP 기준선 분석","",
            "원본 HTML을 사람이 저장한 다음 수동 분석한 자료입니다.",
            "파싱된 순위 및 블록 순서는 스크린샷 검증 전에는 확정할 수 없습니다.",
            "서치어드바이저 색인 상태: 미확인. 수집 실패/미확인 = 미색인 아님.","",
            "| 키워드 | 기기 | 상태 | 추출 일반 결과 | 근거 파일 |",
            "|---|---|---|---:|---|"]
    for s in summaries:
        report.append(f"| {s['query']} | {s['device']} | {s['extraction_status']} | {s['organic_parsed']} | {s['evidence_file']} |")
    if not summaries:report.append("| - | - | 미수집(입력 HTML 없음) | 0 | - |")
    report.extend(["","## 사람 검증 필요","- 추출 블록 및 실제 보이는 10개 결과를 PNG와 대조",
                   "- 원본 HTML/PNG는 외부 비공개 저장소에만 보관",
                   "- 기존 19개 대상 검색어 후보는 target_query_review.csv에서 승인 전 수정하지 않음"])
    report.extend(["- "+v for v in skipped])
    (output/f"SERP_BASELINE_REPORT_{day}.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(f"Read {len(summaries)} HTML evidence files; {len(results)} extracted results. {output}")

if __name__=="__main__":
    main()
