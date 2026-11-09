# 59man.shop - Google Search Console 자동 연결

이 워크플로는 구글의 공식 Search Console API를 사용하며 네이버 IndexNow 워크플로는 건드리지 않습니다.

## 동작

- sitemap.xml이 포함된 main 배포 시, 공개된 사이트맵과 저장소 파일의 URL 및 lastmod가 일치하면 구글 Search Console에 사이트맵을 다시 제출합니다.
- 동시에 기존 미색인 7개 URL의 구글 색인 상태를 조회합니다.
- 매일 한국 시간 08:30에 우선순위 7개 URL을 검사합니다.
- GitHub Actions 페이지에서 수동으로 both / submit / inspect 모드를 실행할 수 있습니다.
- 이 작업은 색인 생성 요청 버튼을 자동 클릭하는 것이 아니며 구글봇의 방문이나 최종 색인을 보장하지 않습니다.

## 최초 1회 연결: 서비스 계정 JSON 방식

1. https://console.cloud.google.com 에서 Google Cloud 프로젝트를 선택하거나 생성합니다.
2. API 및 서비스 > 라이브러리에서 Google Search Console API를 활성화합니다.
3. IAM 및 관리자 > 서비스 계정에서 전용 서비스 계정(예: 59man-gsc)을 생성합니다.
4. 서비스 계정 키 탭에서 JSON 키를 생성하고 비공개로 보관합니다.
5. Google Search Console > 도메인 속성 59man.shop > 설정 > 사용자 및 권한에서 서비스 계정 이메일을 전체 권한 사용자로 추가합니다.
6. GitHub 저장소 prepaid1215/59manshop > Settings > Secrets and variables > Actions에서 New repository secret을 선택합니다.
7. Secret 이름은 GSC_SERVICE_ACCOUNT_JSON, 값은 JSON 파일 내용 전체로 저장합니다. 키 내용을 채팅이나 GitHub 코드에 공유하지 마세요.
8. GitHub > Actions > Google Search Console auto sitemap and URL monitor > Run workflow > both로 실행해 결과를 확인합니다.

## 키 없는 인증: Workload Identity Federation (보안상 권장)

Google Cloud에서 GitHub OIDC Workload Identity Pool/Provider를 만들고, prepaid1215/59manshop의 main만 신뢰하도록 제한합니다.
GitHub 저장소 Actions variables에 GSC_WIF_PROVIDER (provider 전체 식별자) 및 GSC_SERVICE_ACCOUNT (서비스 계정 이메일)를 추가합니다.
해당 서비스 계정에 workloadIdentityUser 위임 권한을 설정하고 Search Console 속성에 전체 권한을 부여해야 합니다.
두 변수가 모두 존재하면 WIF가 JSON 키보다 우선합니다.
공식 가이드: https://github.com/google-github-actions/auth

## 인증 연결 전

인증 값이 없으면 API 전송은 시도하지 않으며 GitHub 실행 요약에 미연결이라고 명확하게 표시합니다.
이 기능은 Google Search Console 무료 API를 사용하므로 유료 GSC Wizard 구독이 필요하지 않습니다.
인증 전까지 자동 제출·색인 상태 조회가 작동한다고 보고해서는 안 됩니다.

공식 API: https://developers.google.com/webmaster-tools/v1/sitemaps/submit
공식 URL 상태 검사: https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect
