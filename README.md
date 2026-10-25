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

`build_guide.py` regenerates all 23 static guide cards using the supplied v2.6.2
plugin's directory structure: PC eight-category chooser and two-column visual
cards; mobile three-column chooser, category hero, subfilters and native detail
links. Existing hash routes and the plugin's query aliases both work. It reads
optional `order` and `visible` fields without replacing the content model.
`build_hub.py` applies the shared header, light footer, desktop topic
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
node scripts/render_visual_qa.cjs
```

The browser check renders every non-redirect route at 390, 430, 480, 1024 and
1440px, checks page overflow, images, duplicate IDs and overlapping text, and
exercises category/search, history, mobile navigation, subfilters, category return,
category reorder, native desktop links, query aliases, conversion links and the
no-JavaScript fallback. Screenshots and reports are under `reports/`. The visual
capture script records chooser/list/eSIM/detail/quick-start states at 1440, 390
and 430px. Full-page and section captures hide only the fixed bottom bar to avoid
stamping it over the long image; viewport captures retain the actual mobile bar.

Design tokens and responsive layouts live in `assets/hub.css`. Update the VERSION
constant in `scripts/build_hub.py` and run `scripts/bump_css.py VERSION` when
changing shared assets. `/guide/` uses dedicated `assets/guide-hub.css` for its
v2.6.2 page components; old preview styles were removed from the shared CSS.

## Generated artwork

Nine new illustrations were created with the built-in image generator, inspected,
then converted to transparent 512×512 WebP under `img/guide-art/`. UI controls
remain SVG. Real SIM photos and official activation captures remain unchanged;
the guide's previous real thumbnails are preserved in a visible reference gallery.
Prompts: `data/illustration-prompts.json`. Mapping: `scripts/guide_visuals.py`.
Transparency/size/file checks: `reports/illustration-validation.json`.
