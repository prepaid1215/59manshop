# 59man.shop — 1,000 URL 구조 실험 (2026-10-16)

**상태:** 실험 브랜치에만 있는 후보 1,000개와 생성 도구. 운영 배포 안 함.

목표: preplan.site에서 대량 등록했을 때 발견·검색 노출이 잘 되지 않았던 상황과 독립적으로, 59man.shop에서 사이트맵·허브·관련 문서 링크의 차이를 비교.

## 근거와 1,000개 후보
- 원본: https://github.com/wellsa-ai/admincode-kr 의 data/legal_dong.json
- 원천: 행정안전부 법정동코드, 파일 `meta.generated=2026-10-01`, blob `fa376fc79cd35f4ffad1f0ab7030fbf812653658`
- 1개 시도에만 있는 '동' 명칭 1,000개 선별. 지명만으로 가게 존재, 재고, 실제 방문서비스 등은 추론하지 않는다.
- 고정 해시로 후보 선별, A·B·C·D 250개씩. 행정구역 개편 여부와 시군구 계층은 실제 공개 전 재확인.

## 링크 구조 비교
- A (250): 사이트맵만
- B (250): 사이트맵 + 시·도 허브
- C (250): 사이트맵 + 같은 비교군/시도 문서의 상호 링크
- D (250): 사이트맵 + 허브 + 문서 간 링크
- URL 형식은 4개 실험군에서 동일한 `/bulk-lab/{시도}/{동}-선불폰/`이다.
- 현재 운영되는 `sitemap.xml`의 22개 URL은 보존. publish 생성 시 250개씩 4개 신규 sitemap + 허브 sitemap + index가 생긴다. 기존 sitemap은 덮어쓰지 않는다.
- B/D 허브에 접근하려면 향후 메인·guide에서 `/bulk-lab-hub/` 내부링크를 별도로 연결해야 한다.

## 실행 (Node 20+ / Windows)
```powershell
node experiments/seo-lab/bulk1000/generate.cjs --check
node experiments/seo-lab/bulk1000/generate.cjs --preview --out .\bulk1000-preview
```
기본 `--preview`는 **noindex,follow**인 검수용 HTML 1,000개와 허브 미리보기를 생성한다. 실험 브랜치는 Pages 운영 배포 대상이 아니다.

검색노출용 파일 생성 명령 `--publish`는 **전체 1,000건**에 `editorial_status=approved`, 지역별 유용한 고유 설명 120자 이상, HTTPS 출처가 입력되지 않으면 오류로 중단한다. 지명만 바꾼 복제 본문으로 발행하지 않기 위한 최소 방어장치이며, 이 조건 통과 자체가 콘텐츠 품질을 보증하지는 않는다.

**주의:** 1,000개 후보/미리보기 생성과 네이버 자동색인 검증 성공은 다르다. 실제 운영 공개에는 콘텐츠 원본성·요금제·주소 사실검증, 정적 링크/사이트맵 검사, 서치어드바이저·SERP 기준선, 사용자 승인 필요. `seo-lab-v01` 전체를 main에 병합하면 내부 실험 문서도 Pages에 노출되므로 금지.

### 현재 GitHub 기준선
- 운영 main: `b5d3bb46c7d92731f5eb1dbf72a456ab752f82ec` (신규 3개 상세 페이지 포함).
- 실험: `baf1b7d850eb6820d2f2fb210cabb560b2686f13` (이 커밋의 부모).
- 실험 사이트 코드/콘텐츠/이미지/경쟁사 문구를 무단 복제하지 않는다.
