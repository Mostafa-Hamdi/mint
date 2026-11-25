# MINTFORMED

Static HTML site (Bootstrap 5 + Bootstrap Icons) built from the Mint-pils Figma design.

Pages: index, about, contact, cookies, piftick. Responsive at 1440 / 991 / 430.

Deploy: Vercel, Framework preset "Other", no build command, output directory = root.

`_figma-reference/` holds the design exports and build sources; it is excluded from deploys via `.vercelignore`.

## MINT CONSENT / MINT PILs pages

| Page | File |
|---|---|
| MINT CONSENT home, guide, pricing, PIF TICK, cookies | `consent.html`, `consent-guide.html`, `consent-pricing.html`, `consent-piftick.html`, `consent-cookies.html` |
| MINT PILs home, guide, pricing, PIF TICK, cookies, legal | `pils.html`, `pils-guide.html`, `pils-pricing.html`, `pils-piftick.html`, `pils-cookies.html`, `pils-legal.html` |

These pages are generated from the Figma frames (exported as SVG) by `_figma-reference/_build/gen2.py`:
each page holds the 1440 / 991 / 430 layouts; shapes and photos come from `assets/svg/*.svg` + `assets/v2/`,
and all text, links, form fields and buttons are real HTML on top (`css/v2.css`, `js/v2.js`).

### Rebuilding the product pages
0. Phones: render each 430 frame's text-free SVG (`assets/svg/<frame>.svg`) to PNG and run `python runs.py <png> runs/<frame>.txt`
   (the plain rows the phone spacing fit may repeat or remove; the current ones are in `_figma-reference/_build/runs/`).
1. `python gen2.py <svg dir> <project>` — writes the 11 pages from the Figma SVG exports.
2. Serve the project (e.g. `python -m http.server 5500`), copy `_figma-reference/_build/prerender.html` into the project root,
   and run `msedge --headless=new --virtual-time-budget=300000 --dump-dom http://localhost:5500/prerender.html > dump.html`.
3. `python bake.py <project> dump.html` — writes the re-flowed text into the pages, so they open already laid out.
   (`js/v2.js` only re-flows text that was not baked.)
4. `python make_about.py <project>` — builds `consent-about.html` / `pils-about.html` (About inside each product site)
5. `python -I gen_doc.py <project>` — coded pages (no drawings): `pils.html`, `consent.html`, `pils-guide.html`, `consent-guide.html`, `pils-pricing.html`, `consent-pricing.html`, `pils-cookies.html`, `consent-cookies.html` from `cookies_content.html` + `css/doc.css` (gen2 no longer builds these). The MINTFORMED `cookies.html` uses the same content via `body_cookies.html`.
6. `python -I finalize.py <project>` — last step, safe to re-run: SEO tags (description, canonical, Open Graph, JSON-LD), `robots.txt` + `sitemap.xml` (domain from `MINT_SITE`, default `https://mint-rdwd.vercel.app`), skip link + `main` landmark, one `h1` per layout, no Bootstrap JS / inline handlers, lazy decor images. Security and cache headers live in `vercel.json`.
   and points the product pages' About links to them.
