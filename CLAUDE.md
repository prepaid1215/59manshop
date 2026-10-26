# 59man.shop brand and SEO guardrails

This repository powers https://www.59man.shop/ .

## Fixed brand names (revised on `ui/renewal`, 2026-10 — owner decision)
- Official website/operating brand (59man.shop): **59만모바일**. The former website brand "59만선불폰" is retired: use 59만모바일 in the header/footer, breadcrumbs, `<title>` suffix, Open Graph `og:site_name`, image alt text, and the homepage `WebSite` JSON-LD `name`.
- Website `alternateName` may include `59man.shop`.
- Generic search keywords ("선불폰", "선불유심", "앤텔레콤 선불폰") stay in body text and titles; only the brand name changed.
- Separate activation/conversion service at https://preplan.site/ is wording-wise "59만모바일 개통 페이지" / "59만모바일 개통 시작하기"; keep those labels and the `preplan.site` CTA links.
- The operating business 상호 is **59만모바일** (footer business info, homepage `Organization` JSON-LD `name`/`legalName`, `url` = https://preplan.site). Legal fields must match the actual business registration.
- The `?from=` parameter on preplan.site CTA links is allowed for conversion measurement. External tracking parameters such as `utm_`, `fbclid`, `gclid` are forbidden on any link.

## Change safety
- Brand renames must never touch URLs, slugs, canonical, robots, sitemap, or index/noindex decisions.
- Do not change existing URLs, canonical, robots, sitemap, index/noindex decisions, or conversion destinations as part of a website-brand correction.
- The SEO plan involves topic pages, regional landing pages, internal linking and conversion paths. Treat this as separate from brand naming.
- Ask for explicit confirmation before changing the website brand again (last change: 59만선불폰 → 59만모바일 on `ui/renewal`).

## Phase 2 noindex exception
- Allowed ONLY for the phase 2 work (branch `seo/phase2`), and ONLY for these two pages:
  - `/알뜰폰-셀프개통-안됨/`: `noindex,follow` -> `index,follow` (kept page; add to sitemap, `og:type=article`, BreadcrumbList).
  - `/알뜰폰-셀프개통-실패/`: becomes a redirect stub (`noindex,follow` + canonical to the kept page + meta refresh).
- Do not change `noindex`/`index` for any other page.

## Fixed paths
- Do NOT rename, move, or delete the `v4-1` folder or anything under `/v4-1/` (including `/v4-1/topic/*`). These paths are permanently fixed. Internal links, canonical, and sitemap entries that point to `/v4-1/...` must stay as they are.

## Checks
- Run `python scripts/check_site.py` before opening a PR (`--table` prints the title/description/canonical table for indexable pages). It must report 0 broken links.

## Responsive information hub (owner request, 2026-10-25)
- Design basis: phone width 390–480px. The latest owner request follows the v2.6.2 reference plugin: desktop 8-category selector and two-column visual guide cards, mobile three-column selector followed by a category hero, subfilters and one-column visual list. Detail routes keep the topic list beside the original article on PC.
- Mobile flow is category → scroll to list → original detail URL; a visible back control returns to the chooser. All guide cards use native detail anchors on desktop and mobile. Existing hash links and q searches remain supported, as do the reference plugin's guide_category query aliases. Related links remain at the end of the article.
- Header on every page: brand + hamburger menu on mobile (`<details class="top-menu">` + `/assets/site.js`), full navigation on desktop. Keep 홈 / 가이드 / 요금제 / 유심 안내 / 개통 시작하기 / 카카오톡 상담 accessible.
- Every non-stub page ends with `<nav class="bottom-bar">`: "개통 시작하기" (preplan.site link, `?from=` allowed) + "카톡 상담" (https://pf.kakao.com/_akxmKn/chat).
- Pages load `/assets/hub.css?v=VERSION` and `/assets/site.js` (deferred); `/guide/` also loads the dedicated `/assets/guide-hub.css` and `/assets/guide.js`. Old preview CSS has been removed. When shared CSS/JS change, bump the version on every page (`python scripts/bump_css.py <version>`) and set VERSION in scripts/build_hub.py.
- Brand colour is blue (`--blue`); pink is not part of the design. Design tokens live in `:root` of the stylesheet.
- Category and card illustrations are generated transparent 512×512 WebP assets in `/img/guide-art/`, in a matched brand-blue 3D style. UI controls (search, menu, arrows, brand mark) remain SVG. Prompts and use mappings are recorded in data/illustration-prompts.json and scripts/guide_visuals.py. Keep real product photos and activation captures visible and separate from illustrations.
- Do not show the `preplan.site` domain in visible text (body, footer, buttons). Links (`href`) and JSON-LD may use it. Footer wording: "개통은 59만모바일 개통 페이지에서 진행됩니다".
- Prices, purchase places and conditions come only from the operator's fact sheet (kept outside this repo, never committed).

## URL policy (renewal)
- New guide detail pages use top-level slugs: `https://www.59man.shop/{slug}/`. Category is a data attribute, never part of the URL. `/guide/` stays as the hub.
- Existing indexed URLs (including `/v4-1/topic/*`) stay untouched until a real HTTP 301 is available. `<meta refresh>` is not a substitute for 301. DNS/proxy changes are a separate, explicitly approved task.

## Content rules
- Facts (prices, plans, conditions, hours, phone numbers) come only from the operator fact sheet kept outside this repo. Mark changeable items with a date ("2026년 10월 기준") and "신청 화면이 최종 기준".
- Content pages: answer first, question-style h2, tables followed by a short explanation, and a visible FAQ (`<section class="faq">` with `<h3>` questions). FAQPage JSON-LD is allowed only when its questions match the visible FAQ exactly (check_site.py enforces this).
- Never write: skipping identity verification as a whole or using someone else's name/certificate ("인증 없이", "신분증 없이", "타인 명의"), absolute guarantees ("100%", "무조건", "누구나", "거절 없음"), or superlatives that compare with other companies ("최저가", "업계 최저", "1위").
- Allowed when stated accurately with a date: "안면인증 실패해도 다음 단계로 진행 가능 (신청 화면의 안면인증 안정화 기간 안내, 2026년 10월 기준) — 간편인증은 필수", "신용조회가 없어 신용불량·연체 이력만으로 거절되지 않음 (가입제한·회선 수 제한은 별도 확인)", "앤텔레콤 선불 요금제 중 월 요금이 가장 낮은 요금제", "월 12,100원부터".
- 59만모바일 tablet owner member number (태블릿 소유자 회원번호) is 2893496. It is used in the 앤텔레콤 membership app route (e.g., customers with only a Naver certificate, which the web activation page does not support). Never use another dealer's number.
- Activation screen facts confirmed from real captures (2026-10): prepaid eSIM is L망 only (K망 shows eSIM only when 후불 is selected); USIM delivery costs 3,700원 shipping with bank-account owner verification (max 5 tries/day); K망 daily base fee 396=1,320원, 459=1,530원. Screenshots must have the browser address bar, system bars, QR codes and all personal data (name, birth date, phone, IMEI/EID) removed or blurred.


## Direction A 고객지원형 디자인 (2026-10-25)
- 59man.shop은 앤텔레콤 질문 답변 탐색과 실제 개통을 연결하는 고객지원 사이트다. 모든 질문의 답변이 수록되어 있다고 과장하지 않는다.
- 흰 배경, 진한 본문, 브랜드 블루, 읽기 쉬운 목록. 최신 사용자 요청에 따라 직접 생성한 3D WebP 일러스트를 사용하며 단순 UI 아이콘은 SVG를 유지한다.
- 실제 유심·제품과 공식 개통 화면에는 실물 이미지 사용. 사실은 운영자 정책팩을 기준으로 검증한다.
- 공통 디자인은 /assets/hub.css 하나로 관리한다. 새 페이지 생성 시 scripts/build_hub.py의 공통 구조를 적용한다.
- 홈 검색은 /guide/?q=... 를 사용한다. 검색에 없는 내용은 카카오톡 상담으로 연결한다.
- canonical·robots·sitemap·URL·index/noindex·preplan.site CTA는 디자인 변경 때문에 임의로 바꾸지 않는다.


## Mobile hub design and index-first QA (2026-10-25)
- 최우선 목표: 실제 색인 → 목표 키워드 검색 노출 → 사용자 방문 → 선불폰 개통. UI 완료는 검색 성과와 동일하지 않다.
- 모바일 390–480px 기준으로 3열 카테고리 → 일러스트·세부 필터·목록 → 기존 상세 URL 흐름을 따른다. /guide/ PC는 v2.6.2의 8개 카테고리와 2열 일러스트 카드 구성이다.
- 흰 바탕·브랜드 블루 #175CD3·절제된 테두리. 카테고리·카드는 일관된 질감의 투명 3D WebP, 검색·메뉴·화살표는 SVG를 활용한다. 실제 제품·신청 화면은 유지한다.
- /guide/ 생성 시 카테고리 → 안내 목록과 궁금한 질문 → 자주 찾는 답변 순으로 렌더한다. 변경은 scripts/build_guide.py에도 동기화한다.
- robots, canonical, sitemap, index/noindex, 개별 URL과 preplan.site 전환 목적지를 디자인 수정 때문에 변경하지 않는다.
- 디자인 완료 후에도 사이트맵 등록 수와 실제 색인 수를 구분하여 안내한다.

## 2026-10-25 브랜드 블루 최종 원칙
- 공식 브랜드 포인트는 #175CD3. 기존 핑크는 사용하지 않는다.
- 최신 사용자 요청: 카테고리·가이드 카드 시각 요소는 /img/guide-art/의 직접 생성한 블루 3D WebP를 사용한다. 기존 SVG는 단순 UI 컨트롤용으로 유지한다.
- 유심 실사 및 신청 스크린샷은 SVG로 변경하지 않는다.
- scripts/build_guide.py는 v2.6.2 참고 템플릿의 구조와 동일한 WebP 매핑을 생성해야 한다.
- 모든 디자인 배포 전 SEO 체크: 기존 URL, sitemap, canonical, robots, 내부 링크 및 개통 CTA를 유지하고 check_site.py를 통과한다.


## 2026-10-25 UI polish after review
- PR #5 final polish: mobile category chooser must not use an artificial screen-height empty region, text in guide cards should remain readable at 390px.
- Detail cover art is added only for known guide URLs and is visibly distinguished as editorial artwork; existing real product photos and form captures remain unchanged.
- Keep scripts/build_hub.py idempotent and match generated detail HTML; don't edit canonical, robots, sitemap, or original text.
- CSS uses /assets/hub.css and guide-only /assets/guide-hub.css with cache version art3.


## Mobile-only non-negotiable — 2026-10-25 correction
- 59man.shop is a MOBILE-ONLY service experience. At all browser widths (390, 430, 480, 1024, 1440), content must stay centered and never exceed **480px**. Desktop screens must NOT expand into PC layouts.
- Header always uses mobile hamburger; NEVER desktop navigation. Home keeps one-column cards and compact category grid. Guide uses THREE columns of category tiles and a SINGLE column of guide cards. Detail pages do NOT show desktop sidebars. Footer and bottom action bar retain mobile width.
- Reference screenshots describe visual composition only. They do not authorize implementing desktop two-column layouts. Ignore previous lines that suggest PC two-column presentation; this explicit owner rule overrides them.
- CSS remediation is in assets/hub.css and assets/guide-hub.css with version 20261025-mobile-only. Future generators and page edits MUST preserve the mobile shell.
- Verify with browser at 390/430/480/1024/1440 before merging, then verify sitemap, robots, canonical, index/noindex, existing text and conversion links stay unchanged.

## Homepage conversion-first policy (2026-10-25)
- Homepage / is a mobile-only activation conversion landing, while /guide/ remains an SEO search and answer hub.
- First viewport: concrete value proposition, confirmed operating constraints, primary preplan.site CTA, second KakaoTalk CTA. Then scenario choices, plan prices, SIM cards, steps, FAQ and search as secondary route.
- Every plan CTA sends to selection on activation page; no claim the rate is pre-selected. Preserve `?from=` distinct labels.
- Never claim instant approval or guaranteed opening. Acceptance and approval are separate. Mobile shell is max 480px even on PC.
- Only change homepage structure and assets/home-landing.css. Preserve page URLs, canonical, robots, sitemap, official rates, core copy, and all old topic links.


## 2026-10-26 home v2 (conversion and index protection)
- 480px mobile-only shell. Homepage is conversion-focused, not a full duplicate of the /guide/ knowledge base.
- No duplicated preparation card: three existing guide links are preserved as a concise pre-step navigation within the 5-step process. Existing 3 FAQ items remain.
- Extras (category nav, tablet owner membership reference, benefits) remain accessible inside native details, not deleted. Reference helpful guides use compact text links instead of giant cards.
- Always compare href preservation and canonical/meta/JSON-LD against main before deploying.

## Guide navigation control regression (2026-10-26)
- A desktop browser still uses the centered 480px mobile shell. Control styling cannot rely on @media(max-width:768px) alone. Apply mobile breadcrumb back button and filter chip styling at all viewport widths.
- Verify computed CSS of #gh-back at both 390px and 1440px; neither can show native browser-button appearance.

## Article readability (2026-10-26)
- 59만모바일 상세페이지는 실제 읽기 쉬운 한국어 모바일 본문이 우선. 본문 기본 16px/line-height 약 1.82, 제목 21~22px, 단락 간 충분한 여백, 대비 좋은 텍스트·링크, 표의 가로 스크롤을 지원한다.
- PC도 동일한 480px 모바일 단일 컬럼. 인덱싱 URL, canonical, robots, sitemap, 기존 글·개통 CTA 변경 금지.
- 독자가 답을 빠르게 이해할 수 있는 핵심 요약 및 소제목의 위계를 유지하고, 과도한 배지/테두리/AI 일러스트 추가를 피한다.
