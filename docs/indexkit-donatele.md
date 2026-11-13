# 59man.shop × donatele — IndexKit 실험 C

시작 준비일: 2026-11-13 · 실험 링크 공개일: **운영 배포 확인 시 확정** · 상태: **실험 페이지 구현·검증**

## 목표

[donatele](https://blog.naver.com/donatele) 원문 10개를 유사한 검색 주제 5쌍으로 묶은 뒤, 각 쌍에서 1개씩 59man.shop에 일반 HTML 링크를 게시합니다. 나머지 5개는 대조군이며 59man.shop에 링크를 걸지 않습니다. 두 군의 구글 검색 관측 변화를 7·14·28일 동안 비교합니다.

- **실험군:** 업무용 전화, 미납정지, GS25 유심, 1년 요금제 비교, 카카오톡 변경의 원문 5개.
- **대조군:** 각 주제에서 대응하는 다른 원문 5개. URL을 공개 HTML에 넣지 않고 SHA-256 체크섬만 `data/indexkit-donatele-treatment.json`에 기록합니다.
- 무작위 배정 방식: 주제별 두 후보 URL을 `SHA256("59man-indexkit-C-v1\n" + normalized-url)`로 정렬해 작은 쪽이 실험군입니다. 공개 후 배정 변경 금지.

## 실제 구현

- `/indexkit/`: 본문을 복제하지 않은 주제별 원문 5개와 자체 설명, 59man.shop 가이드 링크
- `/` 및 `/guide/`: /indexkit/로 연결
- `/sitemap.xml`: 외부 Naver 글 주소는 추가하지 않고 **이 사이트의 /indexkit/만** 추가
- `scripts/check_indexkit_donatele.py`: 5개 treatment 존재, 5개 control 누출 없음, 내부 링크 정상과 sitemap 검사
- `.github/workflows/indexkit-donatele-ci.yml`: CI 자동 검증
- 후보 수집: `scripts/indexkit_donatele_candidates.py` 및 Actions `indexkit-donatele-candidates.yml`; donatele RSS 글 50개 수집 성공

## RSS 처리: 실험 오염 방지

- 59man.shop의 기존 **ntelecom59 RSS 자동 목록 51개는 변경하지 않음**.
- 도메인별 장기 짝은 `donatele ↔ 59man.shop`으로 정했지만, donatele RSS 전체 수집을 /blog/에 바로 공개하면 대조군도 링크가 생깁니다.
- 첫 7/14/28일 실험이 끝나거나 통계 설계를 별도로 확정하기 전까지 donatele 전체 RSS 목록 공개를 보류합니다.
- RSS를 donatele로 바꿀 때는 반드시 대조군 해시 필터링 및 모든 공개 HTML/JSON의 대조군 URL 검사를 먼저 통과시켜야 합니다.

## 사전 기준점과 한계

2026-11-13에 정확한 제목 중심의 공개 검색을 했지만 해당 원문이 검색 결과에 없다는 사실은 **구글 미색인의 증거가 아닙니다.** Google 소유권 기반 URL Inspection은 네이버 외부 글에 적용할 수 없습니다. 사전 상태는 `unverified`로 기록합니다.

실험 시작 시 운영 배포 페이지 200, indexable, canonical, sitemap, 내부 링크와 다섯 개 외부 URL을 확인하고 최초 공개 날짜를 데이터 파일에 기록합니다. 
그 뒤 7/14/28일에 같은 검색 방법으로 실험군과 대조군을 관측합니다.
- 구글 검색에서 발견되었다는 결과만으로 외부 원문의 실제 색인/수집 내부 상태를 단정하지 않습니다.
- 이미 검색에 나오던 글은 관찰표에서 구분합니다.
- 실험군의 외부 링크는 `nofollow` 없이 일반 `a href`로 제공합니다. 백링크는 **색인을 강제하지 않습니다**.

## 후속 실험

IndexKit 5:5 평가가 끝난 뒤 키자드형 글별 독립 안내 페이지를 별도 실험으로 검토합니다. 이 단계에서는 독립 페이지를 추가하지 않습니다.
