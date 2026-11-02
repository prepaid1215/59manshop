# 59man.shop IndexNow 수동 제출

기존 GitHub Actions 자동 제출(`.github/workflows/indexnow.yml`)을 유지하면서 Windows에서 필요할 때 수동 제출할 수 있는 도구입니다.

## 실행

1. 저장소에서 `indexnow-59man.bat`와 `indexnow-59man.ps1`을 **같은 폴더**에 둡니다.
2. Windows에서 `indexnow-59man.bat`를 더블클릭합니다.
3. `1`은 현재 공개 사이트맵 전체 URL, `2`는 신규/수정한 URL 1개, `3`은 URL 조회만 하고 실제로 보내지 않는 시험 실행입니다.

## 동작 방식

- 공개된 `https://www.59man.shop/b10edb20efd14a1666dd9f0930f45ac5.txt`의 키가 정확한지 먼저 검사합니다.
- 전체 제출은 *공개 사이트*의 `/sitemap.xml`을 읽습니다. GitHub 저장소의 파일과 공개 사이트가 다르면 공개된 목록을 기준으로 합니다.
- 요청 URL은 반드시 `https://www.59man.shop/` 호스트여야 합니다.
- 네이버 공식 IndexNow 엔드포인트로 JSON POST를 한 번 전송합니다.
- HTTP `200` 또는 `202`는 **접수/키 검증 대기**를 뜻합니다. 실제 색인은 보장되지 않습니다.

## 운영 주의

- 처음에는 전체 사이트맵을 한 번 제출하고, 이후에는 새로 만든 페이지나 변경한 페이지를 `2`번으로 제출하세요. 전체 URL을 매일 반복 제출하지 마세요.
- GitHub Actions 자동 제출이 이미 동작합니다. BAT는 자동 제출이 누락되었을 때의 보조 수단입니다.
- `noindex`인 페이지, 이전 주소, 중복 페이지는 사이트맵에 넣거나 수동 제출하지 마세요.
- Google은 IndexNow 수집 대상이 아닙니다. Google Search Console과 XML sitemap은 별도로 유지해야 합니다.

## 현재 사이트 참고

- 정규 URL 호스트: `www.59man.shop`
- 기존 소유권 키 재사용: `b10edb20efd14a1666dd9f0930f45ac5`
- 수동 제출 프로그램은 사이트 파일이나 SEO 메타태그를 수정하지 않습니다.
