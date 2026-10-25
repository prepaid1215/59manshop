# 59manshop

Responsive information hub for 59만모바일. Plain static HTML, CSS and JavaScript;
no production build service or client framework is required.

The `design/information-hub-20261025` redesign starts from production main
`727568f5f479a1b719adb231e3d22b09401f6a9a`. It must be reviewed before merging.

## Generate and validate

```sh
python scripts/build_guide.py
python scripts/build_pages.py
python scripts/build_hub.py
python scripts/check_site.py
python scripts/check_preservation.py --base 727568f
```

`build_guide.py` regenerates all 23 static guide cards and applies the shared hub
components. `build_hub.py` applies the shared header, light footer, desktop topic
browser and integrated article title without regenerating article copy. Both are
safe to run again. Update content through the existing content process; this
redesign does not change titles, descriptions, article text, URLs or indexing.

`check_preservation.py` compares every existing HTML route, SEO head metadata,
title, JSON-LD, body text, links and real image URLs with the specified Git ref.
It also compares robots.txt, sitemap.xml and CNAME. Additions are allowed;
removing original content fails the check.

## Browser verification

Install Playwright locally (`npm install --no-save --package-lock=false playwright`
and `npx playwright install chromium`) or use the bundled desktop runtime. A
`PLAYWRIGHT_MODULE` environment variable can identify another installed module.
With the server running in a separate terminal:

```sh
python scripts/serve_preview.py
node scripts/verify_hub.cjs
node scripts/render_qa.cjs
```

The browser check renders every non-redirect route at 390, 430, 480, 1024 and
1440px, checks page overflow, images, duplicate IDs and overlapping text, and
exercises category/search, history, mobile navigation, desktop preview, fetch
failure, conversion links and the no-JavaScript fallback. Screenshots and reports
are under `reports/`. Desktop preview never changes canonical URLs or browser
history; its “상세페이지에서 보기” link opens the original detail route.

Design tokens and responsive layouts live in `assets/hub.css`. Update the VERSION
constant in `scripts/build_hub.py` and run `scripts/bump_css.py VERSION` when
changing shared assets. Legacy CSS files are kept for reference and are not loaded.
