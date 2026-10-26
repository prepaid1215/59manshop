# 59만모바일 본문 이미지 업로드 폴더

1. 사이트의 `/tools/photo-manager/`에서 글과 이미지 위치를 선택합니다.
2. 사진을 WebP로 내려받습니다.
3. 이 폴더에 GitHub의 Add file → Upload files로 해당 파일을 올립니다.
4. Commit changes를 누르면 GitHub Pages 배포 후 글에 자동으로 표시됩니다.

파일명 예시: `선불폰-개통방법--01.webp` 또는 `v4-1--topic--plan-396--02.webp`
사진이 없다면 방문자 화면에 빈 공간은 표시되지 않습니다.
글 주소에 `?image-slots=1`을 붙이면 등록 전에도 사진 위치를 확인할 수 있습니다.

주의: 신분증, 연락처, 인증 QR코드, IMEI/EID, 고객 개인정보가 드러나는 사진은 업로드하지 않습니다.

## 공통 카드 이미지
앤텔레콤 선불폰 개통 방법 페이지의 간편인증·신분증·eSIM 카드에 사용합니다.
이미지가 없으면 기존 문자형 아이콘 또는 기본 안내 그림을 그대로 보여줍니다.

필수 인증 로고:
- common-auth-kakao.webp
- common-auth-toss.webp
- common-auth-pass.webp
- common-auth-kb.webp
- common-auth-shinhan.webp

선택 안내 그림:
- common-id-resident.webp
- common-id-driver.webp
- common-id-mobile.webp
- common-esim.webp

인증 로고 권장 정사각 256x256px 이상, 안내 그림은 512x512px 이상.
브랜드 제공자에 의해 사용이 허용된 이미지 또는 사용 권한이 있는 그림을 사용하세요.
실제 신분증/개인정보/인증 QR/EID/IMEI 이미지 업로드 금지.
