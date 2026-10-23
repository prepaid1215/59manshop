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

## Mobile-only layout (owner decision, 2026-10: PC-specific layout is NOT built)
- Design basis: phone width 390–480px. Every page uses one 480px column at every screen width; PC shows the same phone layout (centered column). No PC two-column layout, no PC-only navigation, no `@media(min-width:...)` desktop rules.
- Category, list and detail pages all use the same mobile UI. Do not add a sidebar (`<aside class="side">`); related links appear once at the end of the article in `<nav class="related">`.
- Header on every page: brand + hamburger menu (`<details class="top-menu">` + `/assets/site.js`) with 홈 / 가이드 / 요금제 / 유심 안내 / 개통 시작하기 / 카카오톡 상담.
- Every non-stub page ends with `<nav class="bottom-bar">`: "개통 시작하기" (preplan.site link, `?from=` allowed) + "카톡 상담" (https://pf.kakao.com/_akxmKn/chat).
- Pages load `/assets/v4-1-final.css?v=YYYYMMDDx` and `/assets/site.js` (deferred); `/guide/` also loads `/assets/guide.js`. When CSS/JS change, bump the `?v=` value on every page (`python scripts/bump_css.py <version>`).
- Brand colour is blue (`--blue`); pink is not part of the design. Design tokens live in `:root` of the stylesheet.
- Illustrations: supplied SVG assets live in `/img/ui/` and are used as `<img class="ill">`; real product graphics, screen captures and official logos are never replaced by illustrations.
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
