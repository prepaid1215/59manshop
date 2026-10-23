# 59man.shop brand and SEO guardrails

This repository powers https://www.59man.shop/ .

## Fixed brand names
- Website brand (59man.shop): **59만선불폰**.
- Keep the same website brand in the visible header/footer, breadcrumbs, page title suffix, Open Graph `og:site_name`, image alt text referring to the website brand, and homepage `WebSite` JSON-LD `name`.
- Website `alternateName` may include `59man.shop`; do NOT set `59만모바일` or `59만모바일 선불폰` as the site's official name or alias without an explicit user request.
- Separate activation/conversion service at https://preplan.site/ : **59만모바일**. Preserve its `preplan.site` CTA links and wording such as `59만모바일 개통 페이지` and `59만모바일 개통 시작하기`. These are NOT the 59man.shop website brand.
- Exception (explicit user request, phase 1): the operating business is 상호 **59만모바일**. The footer business info and the homepage `Organization` JSON-LD (`name`/`legalName` = 59만모바일, `url` = https://preplan.site) use it, and the homepage `WebSite` JSON-LD links to it via `publisher`. The website brand and `WebSite` `name` stay **59만선불폰**.
- The `?from=` parameter on preplan.site CTA links is allowed for conversion measurement. External tracking parameters such as `utm_`, `fbclid`, `gclid` are forbidden on any link.

## Change safety
- Never bulk-replace `59만모바일` inside activation instructions, CTAs or preplan.site labels simply to unify the 59man.shop site name.
- Do not change existing URLs, canonical, robots, sitemap, index/noindex decisions, or conversion destinations as part of a website-brand correction.
- The SEO plan involves topic pages, regional landing pages, internal linking and conversion paths. Treat this as separate from brand naming.
- Ask for explicit confirmation before changing the website brand again.

## Phase 2 noindex exception
- Allowed ONLY for the phase 2 work (branch `seo/phase2`), and ONLY for these two pages:
  - `/알뜰폰-셀프개통-안됨/`: `noindex,follow` -> `index,follow` (kept page; add to sitemap, `og:type=article`, BreadcrumbList).
  - `/알뜰폰-셀프개통-실패/`: becomes a redirect stub (`noindex,follow` + canonical to the kept page + meta refresh).
- Do not change `noindex`/`index` for any other page.

## Fixed paths
- Do NOT rename, move, or delete the `v4-1` folder or anything under `/v4-1/` (including `/v4-1/topic/*`). These paths are permanently fixed. Internal links, canonical, and sitemap entries that point to `/v4-1/...` must stay as they are.

## Checks
- Run `python scripts/check_site.py` before opening a PR (`--table` prints the title/description/canonical table for indexable pages). It must report 0 broken links.

## Mobile-only layout (seo/mobile)
- Every page uses one 480px column at every screen width (PC shows the same phone layout). No sidebar (`<aside class="side">`); related links appear once at the end of the article in `<nav class="related">`.
- Every non-stub page ends with `<nav class="bottom-bar">`: "개통 시작하기" (preplan.site link, `?from=` allowed) + "카톡 상담" (https://pf.kakao.com/_akxmKn/chat).
- All pages load only `/assets/v4-1-final.css?v=YYYYMMDDx`. When the CSS changes, bump the `?v=` value on every page so browsers do not keep the old file.
- Do not show the `preplan.site` domain in visible text (body, footer, buttons). Links (`href`) and JSON-LD may use it. Footer wording: "개통은 59만모바일 개통 페이지에서 진행됩니다".
- Prices, purchase places and conditions come only from the operator's fact sheet (kept outside this repo, never committed).

## Content rules
- Facts (prices, plans, conditions, hours, phone numbers) come only from the operator fact sheet kept outside this repo. Mark changeable items with a date ("2026년 10월 기준") and "신청 화면이 최종 기준".
- Content pages: answer first, question-style h2, tables followed by a short explanation, and a visible FAQ (`<section class="faq">` with `<h3>` questions). FAQPage JSON-LD is allowed only when its questions match the visible FAQ exactly (check_site.py enforces this).
- Never write: skipping identity verification as a whole or using someone else's name/certificate ("인증 없이", "신분증 없이", "타인 명의"), absolute guarantees ("100%", "무조건", "누구나", "거절 없음"), or superlatives that compare with other companies ("최저가", "업계 최저", "1위").
- Allowed when stated accurately with a date: "안면인증 실패해도 다음 단계로 진행 가능 (신청 화면의 안면인증 안정화 기간 안내, 2026년 10월 기준) — 간편인증은 필수", "신용조회가 없어 신용불량·연체 이력만으로 거절되지 않음 (가입제한·회선 수 제한은 별도 확인)", "앤텔레콤 선불 요금제 중 월 요금이 가장 낮은 요금제", "월 12,100원부터".
- 59만모바일 tablet owner member number (태블릿 소유자 회원번호) is 2893496. It is used in the 앤텔레콤 membership app route (e.g., customers with only a Naver certificate, which the web activation page does not support). Never use another dealer's number.
