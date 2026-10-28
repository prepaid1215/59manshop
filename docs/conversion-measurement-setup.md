# 59만모바일 7차 전환 측정 구성 (2026-10-28)

## 측정 범위와 실제 반영 상태

- **59man.shop:** 별도 동의 후 Google Analytics 4(`G-N22WSXXPHH`)를 로드하고, preplan.site로 향하는 클릭을 `mm59_outbound_click`으로 보냅니다.
- **preplan.site:** 공개 HTML에 GTM `GTM-NB2K5MFQ`와 Google Ads `AW-16857600145`를 확인했습니다. 공개 GTM 자바스크립트에서 GA4 `G-N22WSXXPHH`도 확인했습니다.
- **워드프레스 연동:** 별도 `mm59-preplan-attribution.zip` 플러그인을 설치해야 preplan의 `mm59_preplan_visit`와 `mm59_application_handoff` dataLayer 이벤트가 생성됩니다. **사이트에 아직 설치되지 않았습니다.**
- **개통 완료:** 플랫폼의 실제 승인·충전 기록으로 검증하기 전에는 절대 완료 이벤트를 보내지 않습니다. 자동 완료 연동은 **미구현**입니다.
- **중요:** 공개 태그 ID 존재가 GA4 관리자 접근권한이나 성공적인 실제 수집을 증명하지는 않습니다.

## 이벤트 정의

| 단계 | 이벤트 | 발생 조건 | 준비 상태 |
|---|---|---|---|
| 59man 정보 페이지 방문 | GA4 `page_view` | 방문자가 통계에 동의한 경우 | 사이트 소스 반영 예정 |
| 59man → preplan 버튼 클릭 | `mm59_outbound_click` | preplan.site 도메인으로 가는 링크를 직접 클릭 | 사이트 소스 반영 예정 |
| preplan 유입 | `mm59_preplan_visit` | 설치된 워드프레스 연결 플러그인이 `from=59man_*` 감지 | 플러그인 설치 + GTM 태그 설정 필요 |
| preplan → 신청 플랫폼 이동 | `mm59_application_handoff` | 실제 신청으로 가는 링크·버튼에 `data-mm59-application="1"` 표시 후 클릭 | 버튼 속성 + GTM 설정 필요 |
| 실제 개통 완료 | `verified_activation` (예약 이름) | 본사/플랫폼 승인·충전 내역과 대조해 검증 | 현재 자동 추적 불가 |

**mm59_application_handoff는 개통 신청서 제출이나 개통 완료가 아닙니다.**

## 59man.shop 측정 방식

- `assets/activation-tracking.js`를 `assets/site.js`가 모든 페이지에서 불러옵니다.
- 최초 동의 전에는 Google Analytics 라이브러리를 불러오지 않습니다. 거절 선택 시 GA4 수집을 시작하지 않습니다. 푸터의 '방문 통계 설정'에서 선택을 변경할 수 있습니다.
- `from` 값이 이미 있으면 그대로 사용합니다. 없으면 페이지 경로와 버튼 위치로 `59man_...` 코드를 자동 생성하여, 클릭 시 이동 링크에 붙입니다.
- GA4 이벤트 파라미터: `source_code`, `source_path`, `placement`, `destination_type`.
- `destination_type=activation_home`: preplan.site의 홈. `information`: 상세 안내·블로그 등.
- 고객 이름·연락처·인증정보·유심번호·EID·IMEI 등은 이벤트에 포함하지 않습니다. 추가 쿼리 파라미터도 GA4 **커스텀 이벤트**에 전송하지 않습니다.
- 크로스도메인 링커는 59man 측에 설정했지만, 방문자·세션 연결 여부는 **GA4 관리자에서 양 도메인 설정 및 실제 테스트**가 필요합니다.

## preplan.site 워드프레스 설치·연결

1. `mm59-preplan-attribution.zip`을 워드프레스 **플러그인 → 새 플러그인 추가 → 플러그인 업로드**에서 설치·활성화합니다.
2. GTM 미리보기(태그 매니저 `GTM-NB2K5MFQ`)에서 `https://preplan.site/?from=59man_test_hero` 접속 시 dataLayer `mm59_preplan_visit`를 확인합니다.
3. GTM 사용자 정의 이벤트 트리거 `mm59_preplan_visit` 생성 → GA4 이벤트 태그, 이벤트명 `mm59_preplan_visit` 연결. Google 태그 ID는 `G-N22WSXXPHH`를 사용합니다.
4. GTM dataLayer 변수 `mm_source`, `mm_preplan_path`, `mm_source_site`, `mm_funnel_stage`를 만들고 GA4 이벤트 파라미터에 대응시킵니다. GTM 미리보기에서 확인 후 게시합니다.
5. 실제 신청 플랫폼을 **여는 버튼**에만 `data-mm59-application="1"` 속성을 달고, GTM Custom Event `mm59_application_handoff` 트리거·GA4 이벤트 태그를 설정합니다.
6. GA4 관리자 → 데이터 스트림 → 태그 설정 → 도메인 구성에 `www.59man.shop`과 `preplan.site`를 확인합니다. 중복 page_view 및 `_gl` 매개변수 전달 여부를 DebugView에서 확인합니다.
7. WordPress 기존 쿠키·개인정보 동의 정책과 GTM 태그 발화 조건을 확인합니다. 하나의 이벤트를 GTM과 gtag에서 중복 발화시키지 않습니다.

## 검증

- 59man 첫 방문: 동의 전 Google 태그 미로딩
- '동의' 클릭: GA4 구성 후 DebugView에서 방문·클릭 이벤트 확인
- '거절' 클릭: 클릭 구분 `from`만 링크에 남고 GA4 로딩 없음
- 원칩 페이지의 정보 링크는 `/lg-self/`, 개통 버튼은 홈 `/`
- preplan 유입: `mm59_preplan_visit`의 `mm_source`와 GA4 `page_location` 확인
- 신청 플랫폼으로 가는 버튼: `mm59_application_handoff`은 **이동 클릭만 집계**
- 개통 완료: 승인·충전 근거 없는 추정 이벤트는 발생하지 않아야 함

## 운영 참고

- **클릭수·유입수와 실개통수는 다른 KPI입니다.** GA4 이벤트 수만으로 매출·신규개통을 계산하지 않습니다.
- 실제 개통 결과는 사업자/플랫폼의 확정 데이터를 별도 대조해야 합니다.
- `?from=` 값이 전달되어도 최종 개통 전환이 자동으로 출처와 연결되는 것은 아닙니다.
- 별도 설치 없이 WordPress 쪽 단계 이벤트가 자동으로 동작하지 않습니다.
- sitemap, canonical, robots, 페이지 URL, 휴대폰 프로모션 문구는 이 작업에서 수정하지 않습니다.
