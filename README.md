# MINTFORMED

Static HTML/CSS site (no framework) built from the Mint-pils Figma design.

MINTFORMED pages: index, about, contact, cookies, piftick. Responsive from phone to desktop.

Deploy: Vercel, Framework preset "Other", no build command, output directory = root.

`_figma-reference/` holds the design exports and build sources; it is excluded from deploys via `.vercelignore`.

## MINT CONSENT / MINT PILs pages

| Page | File |
|---|---|
| MINT CONSENT home, guide, pricing, PIF TICK, cookies | `consent.html`, `consent-guide.html`, `consent-pricing.html`, `consent-piftick.html`, `consent-cookies.html` |
| MINT PILs home, guide, pricing, PIF TICK, cookies, legal | `pils.html`, `pils-guide.html`, `pils-pricing.html`, `pils-piftick.html`, `pils-cookies.html`, `pils-legal.html` |

All pages are plain HTML/CSS (no drawn backgrounds). The product pages are written by
`_figma-reference/_build/gen_doc.py` from content kept as data / partials in the same folder
(`cookies_content.html`, `piftick_content.html`, `legal_content.html`), styled by `css/doc.css`,
with `js/doc.js` for accordions, the video player, the country choice and the Legal section nav.
Web-sized photos (`assets/img/<name>-<width>.jpg`) are made from the design photos in `_figma-reference/originals/`.

### Rebuilding
1. `python -I _figma-reference/_build/gen.py` — MINTFORMED pages (index, about, contact, cookies, piftick);
   CSS from `style.src.css` via `build_css.py`.
2. `python -I _figma-reference/_build/gen_doc.py .` — the 11 MINT CONSENT / MINT PILs pages.
3. `python -I _figma-reference/_build/make_about.py .` — `consent-about.html` / `pils-about.html` from `about.html`.
4. `python -I _figma-reference/_build/finalize.py .` — last step, safe to re-run: SEO tags (description, canonical, Open Graph,
   JSON-LD), `robots.txt` + `sitemap.xml` (domain from `MINT_SITE`, default `https://mint-rdwd.vercel.app`), skip link +
   `main` landmark, one `h1` per page. Security and cache headers live in `vercel.json`.

`legal_content.html` was produced once from the Figma Legal frame by `build_legal.py`; edit it directly from now on.
The old drawing pipeline (`gen2.py`, `prerender.html`, `bake.py`, `runs.py`) is kept in `_build/` for reference only.
