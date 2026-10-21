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
