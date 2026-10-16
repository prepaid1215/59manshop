# 59man.shop 첫 신규 SEO 페이지 배포 기록 — 2026-10-15

> 이 문서는 실험 브랜치 전용 기록이다. `main`의 공개 GitHub Pages에는 업로드하지 않는다.

## 배포 완료 (확인)

- **기존 운영 사이트를 새로 만든 것이 아니라**, `main`에서 기존 19개 sitemap URL과 noindex 안내 스텁을 유지하던 상태에서 신규 의도별 색인 대상 랜딩 3개를 적용했다.
- 운영 기준 커밋(변경 전): `aeff28f84e158f7eedc1d3f48d93dfb3b3b358f4`.
- 실험 브랜치의 콘텐츠 출처: `44bac27d31316420d56fd0eabddeeeb876a890ea` (`seo-lab-v01`).
- 운영 배포 커밋: `b5d3bb46c7d92731f5eb1dbf72a456ab752f82ec`.
- GitHub Pages workflow 실행: `38715802279` (`pages build and deployment`, completed/success, 해당 main 커밋).
- 배포 당시 변경 파일은 **아래 6개만**. `experiments/` 전체와 `신림동-선불폰-개통/index.html`은 운영 트리에 없다.
- sitemap.xml 19 → 22개 URL, 신규 URL은 `index,follow` + self-canonical, 홈과 /guide의 내부링크 추가.
- 배포 전 정적 검증: sitemap URL의 파일 매칭 누락 0, 6개 파일 내부 링크 깨진 경로 0, sitemap 중복 0.
- **실시간 HTTP 200/canonical 확인 미완료**: 응답 확인 도구의 신규 주소 접근이 차단되었으며 사용자 브라우저에서 확인해야 한다. GitHub Pages workflow 성공과 live HTTP 검증은 구분한다.

## 게시된 정확한 파일 (main과 실험 브랜치가 같은 blob SHA)

| 파일 | blob SHA |
|---|---|
| `선불폰-개통/index.html` | `a18f805cae54f08f6f4b0d4fd7ac1ffc25807a60` |
| `선불폰-개통방법/index.html` | `cf2d7773beaca78e25e8728e4c60c77a82152764` |
| `선불폰-셀프개통/index.html` | `6d70a070b07c147b61ab8e3ea6e0d6d32d140f59` |
| `sitemap.xml` | `8c47ae6b2b18736444f4020b87eff4d199a28027` |
| `index.html` | `69e7cb8cfae1690288fe9d4c7cf66f44cd61b9f9` |
| `guide/index.html` | `60e3a26cf143ea85ebd584f31122a79fc285f3f8` |

## 배포 전에 수집하지 못한 기준선 — 결과 해석 시 반드시 고려

이전 `PREDEPLOY_GATES_20261015.md`의 3개 항목(기존 19개 URL의 네이버 색인 상태, 신규 3개 키워드 × PC/모바일 6화면, GA4 from 파라미터 도착)이 **모두 완료되지 않은 채** 사용자의 진행 승인으로 배포되었다. 이 항목을 완료한 것으로 소급 기재하지 않는다.

- 배포 전 main 트리 해시·robots·sitemap 구성은 GitHub 기록으로 복원 가능.
- 과거 저장된 PC SERP 화면 일부는 각 수집 당시의 상태로만 참조한다.
- 이후에 수집하는 네이버 SERP·서치어드바이저·GA4는 **배포 후 측정값**이므로 배포 전 기준선이라고 표기하지 않는다.
- `?from=` 쿼리는 출처 표식일 뿐, 외부 `n-telecom.co.kr`의 신청·개통 완료와 자동 연동된다는 증거가 없다.

## 실험 다음 순서

1. 사용자 브라우저에서 아래 3개 신규 URL 및 `sitemap.xml`의 200 응답/본문/정상 링크를 확인한다.
2. 네이버 서치어드바이저에서 신규 URL별 수집·색인 상태를 캡처하고 검색결과에 등장하는지 SERP Lens로 관측한다.
3. `preplan.site/?from=59man_선불폰-개통` 접속 시 GA4 page_location 기록을 확인한다. 이후 신청 페이지 이탈 클릭/실제 개통 건수는 별도로 측정한다.
4. 배포 후 **7일·14일** 관찰: 네이버 검색 결과에 등장 여부, 검색어/기기/블록 후보 위치, 유입/개통시작 신호. 색인 전에도 '검색되지 않음 = 미색인'으로 판단하지 않는다.
5. 초기 결과에 근거해 다음 경쟁사 구조 복제 실험(지역·주제·내부링크)을 소규모로 설계한다. `preplan.site` 지역 페이지 조사는 이 실험의 선행조건이 아니다.

## Claude 독립 검토 요청

기준 운영 커밋 `b5d3bb46c7d92731f5eb1dbf72a456ab752f82ec` 및 이 배포 기록이 올라간 `seo-lab-v01` 후속 커밋을 비교하여: 배포가 정확히 6개 파일뿐인지, 신규 페이지 3개의 SEO 메타·링크가 정상인지, 결과 측정에서 기준선 미확인을 과장하지 않는지 검토할 것.
