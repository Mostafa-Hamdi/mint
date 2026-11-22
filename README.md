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
1. `python gen2.py <svg dir> <project>` — writes the 11 pages from the Figma SVG exports.
2. Serve the project (e.g. `python -m http.server 5500`), copy `_figma-reference/_build/prerender.html` into the project root,
   and run `msedge --headless=new --virtual-time-budget=300000 --dump-dom http://localhost:5500/prerender.html > dump.html`.
3. `python bake.py <project> dump.html` — writes the re-flowed text into the pages, so they open already laid out.
   (`js/v2.js` only re-flows text that was not baked.)
