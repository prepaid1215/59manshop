# 오프라인 네이버 SERP 분석 도구

네이버 검색 사이트에 요청을 보내지 않습니다. 직접 일반 브라우저로 검색한 뒤 저장한 HTML과 PNG를 읽어 잠정 분석합니다. 광고·AI 브리핑·비표준 화면은 파서가 놓치거나 잘못 묶을 수 있으므로 **스크린샷과 사람이 대조하기 전에는 순위를 확정하지 않습니다**.

## 입력 준비
- PC: 직접 브라우저에서 네이버 검색 후 HTML 저장 및 화면 캡처.
- 모바일: 실제 휴대폰의 검색 화면 캡처와 저장 가능한 HTML(없는 경우 PNG만 따로 보관).
- 키워드별 실제 조회 시간(KST)을 파일명에 포함.
- 형식: 20261015-1430_pc_선불폰 개통.html 및 같은 이름의 .png. 모바일은 mo.
- 원본은 Git 저장소 **밖의 사적 폴더**에만 저장. 공개 GitHub에 업로드 금지.
- 사이트 상태·페이지 구조에 따라 수동 저장 HTML이 실제 렌더링 DOM과 다를 수 있습니다. PNG만으로는 이 파서가 결과를 추출하지 않습니다.

## 실행
1. Python에 beautifulsoup4 설치: python -m pip install beautifulsoup4
2. 저장소 루트에서 실행:
   python experiments/seo-lab/tools/parse_serp.py --raw-dir "C:\Private\serp_raw" --update-baseline
3. 자동 생성된 결과 파일을 검토:
   - experiments/seo-lab/serp_results.csv: 발견 결과 1건당 1행, URL별 HTML SHA-256
   - experiments/seo-lab/serp_share_YYYYMMDD.csv: 키워드/기기별 상위 10개 추정 분포
   - experiments/seo-lab/baseline-observed.csv: 기존 44행 템플릿의 복사본; 실측만 수정. 미확인 유지.
   - experiments/seo-lab/target_query_review.csv: 기존 19개에 대한 실제 검색어 대체 후보(승인 대기)
   - experiments/seo-lab/SERP_BASELINE_REPORT_YYYYMMDD.md: 분석 성공/실패 요약

## 측정 해석과 주의
- HTML에서 추출된 원순위는 실제 네이버 검색화면과 다를 수 있습니다.
- 추출하지 못한 사이트는 색인 실패가 아닙니다.
- 기존 기준선 CSV는 덮어쓰지 않고 별도 파일로 출력합니다.
- 59man.shop의 신규 3개 페이지가 운영 main에 미배포된 동안은 현재 사이트의 상태로 판단하지 않습니다.
- 네이버 서치어드바이저의 소유 사이트 수집/색인 상태는 사이트 소유자가 별도로 확인해야 합니다.
- 과거 PC/모바일 파일의 채널 분포가 같다는 이유만으로 실제 같은 화면이었다고 판단하지 않습니다. 원본별 SHA와 PNG를 검토합니다.

**제한:** 네이버 HTML의 카드 마크업이 변하면 일부 결과가 누락됩니다. 화면 순서와 그룹은 반드시 검수하며, 이를 검증 없이 노출 성공 데이터로 취급하지 마세요.
