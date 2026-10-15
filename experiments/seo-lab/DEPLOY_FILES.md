# 운영 배포 파일 목록 (seo-lab-v01 → main)

`.nojekyll` 때문에 GitHub Pages는 저장소 파일을 가공 없이 공개한다.
`seo-lab-v01`을 통째로 병합하면 `experiments/` 문서(경쟁사 구조 분석, 계획 URL, 기록 양식)가
`https://www.59man.shop/experiments/seo-lab/...` 주소로 열린다. 그러므로 **브랜치 병합 대신 아래 파일만 반영한다.**

## 반영할 파일 (6개)
`deploy-files.txt`와 같은 목록이다.

| 파일 | 변경 내용 |
|---|---|
| `선불폰-개통/index.html` | noindex 안내 → 색인 대상 랜딩 (신청 조건·요금제·유심) |
| `선불폰-개통방법/index.html` | noindex 안내 → 색인 대상 랜딩 (준비물·인증·입력 형식) |
| `선불폰-셀프개통/index.html` | noindex 안내 → 색인 대상 랜딩 (조건·문제 해결) |
| `sitemap.xml` | 19 → 22개 URL |
| `index.html` | '많이 찾는 안내'에 신규 3개 링크 추가 (색인 정책·canonical 변경 없음) |
| `guide/index.html` | '추가 주제 안내'에 신규 3개 링크 추가 (색인 정책·canonical 변경 없음) |

## 반영하지 않을 경로
- `experiments/` 전체

## 반영 예시 (승인 후 운영자가 직접 실행)
```
git checkout main
git show seo-lab-v01:experiments/seo-lab/deploy-files.txt | xargs git checkout seo-lab-v01 --
git status   # experiments/ 가 없는지 확인
```
반영 전에 `baseline-template.csv`의 기준선을 먼저 기록한다. 배포 후 IndexNow·색인 요청은 별도 승인 사항이다.
