# MINTFORMED website — backend handoff

A static front end: **plain HTML + CSS + vanilla JavaScript**. No framework, no bundler, no npm.
Every page works as-is from any web server; nothing needs compiling to serve it.

Live preview: https://mint-rdwd.vercel.app

---

## 1. What's in the box

```
index.html  about.html  contact.html  cookies.html  piftick.html        MINTFORMED (main site)
pils.html   pils-about.html   pils-guide.html   pils-pricing.html        MINT PILs site
pils-piftick.html   pils-cookies.html   pils-legal.html
consent.html  consent-about.html  consent-guide.html  consent-pricing.html   MINT CONSENT site
consent-piftick.html  consent-cookies.html                             (Legal is shared: pils-legal.html)

css/ui.css     header, phone tab bar, cookie banner, skip link, focus styles (every page)
css/doc.css    page sections: heroes, cards, accordions, tables, forms, footer (every page)
js/ui.js       header, tab bar, product switcher, in-page section links, cookie banner, forms (every page)
js/doc.js      accordions, video player, pricing country choice, Legal section nav (only pages that need them)
assets/img/    logos, icons, web-sized photos      assets/v2/  two design images still in use
robots.txt  sitemap.xml

handoff/partials/   the shared pieces, ready to turn into your templates (see §3)
```

Fonts come from Google Fonts (Montserrat, Poppins). There are no other third-party scripts or styles.

## 2. Page anatomy (identical on all 18 pages)

```html
<head> … meta, SEO block (<!-- seo --> … <!-- /seo -->), fonts, css/ui.css, css/doc.css </head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <main class="doc" id="main"> … page sections … </main>
  <footer class="doc-foot"> … </footer>                         ← one of 3 footers
  <script type="application/json" id="sticky-cfg">{…}</script>  ← header/tab-bar config for this site
  <script src="js/ui.js"></script>
  <script src="js/doc.js"></script>                             ← only on guide, pricing, legal
</body>
```

The **header and the phone tab bar are not in the HTML**: `js/ui.js` builds them from the JSON in
`#sticky-cfg`. To change a menu, change that JSON (one per site, in `handoff/partials/header-config-*.json`).

## 3. Turning it into templates

`handoff/partials/` holds the pieces that repeat on every page:

| File | Use it for |
|---|---|
| `head.html` | the `<head>` (put each page's `<title>` and SEO block in) |
| `footer-mintformed.html`, `footer-pils.html`, `footer-consent.html` | the footer for each of the 3 sites |
| `header-config-*.json` | the `#sticky-cfg` JSON for each site (header + tab bar menus, login link) |
| `contact-form.html` | the contact form (same on every page that has one) |

Everything between `<main …>` and `</main>` is that page's own content.
In a footer, the link to the current page gets `aria-current="page"` (the partials have none set).

## 4. What the backend needs to connect

### 4.1 Contact form → `POST /api/contact`
Used on: `contact.html`, `pils.html`, `consent.html`, `pils-pricing.html`, `consent-pricing.html`.

| Field | Type | Notes |
|---|---|---|
| `first_name` | text, required, ≤ 80 | |
| `last_name` | text, required, ≤ 80 | |
| `email` | email, required, ≤ 160 | |
| `telephone` | text, optional, ≤ 40 | |
| `message` | text, required, ≤ 4000 | |
| `source` | hidden | which page sent it: `mintformed-contact`, `pils-home`, `consent-home`, `pils-pricing`, `consent-pricing` |
| `website` | hidden honeypot | **must be empty**; if it has a value, treat it as spam and drop it silently |

- Body: `multipart/form-data` (sent by `fetch` with `FormData`), header `Accept: application/json`, same origin.
- Reply with JSON: `{ "ok": true }` on success, or `{ "ok": false, "message": "…" }` (any non-2xx also counts as failure).
  The page shows the thank-you note on success and the `message` (or a default text) on failure, keeping what the user typed.
- **Validate everything on the server** (the `required`/`maxlength` attributes are only a convenience) and rate-limit the endpoint.
- If you use CSRF tokens, add a hidden `<input name="…" value="…">` to `contact-form.html`; it is sent with the rest.
- **Go live:** the forms currently carry `data-demo` (they show the thank-you without sending anything).
  Remove `data-demo` from the `<form class="cf" …>` tag and they post for real. Without JavaScript the form still
  posts normally to the same URL, so a plain redirect-back response works too.

### 4.2 "Log in" links
Placeholders (`#`) in: the header button (`"login"` in each `#sticky-cfg` JSON), the two product cards on
`index.html`, and the "MINT Platform" link on the About pages. The links in the page HTML carry `data-login`
(`grep -n data-login *.html` finds them all); the header button reads `"login"` from the JSON. Point them at the platform's login URL.

### 4.3 Pricing → country → Contact
`pils-pricing.html` asks clinics for their country (`uk` / `ksa` / `eg`). With JavaScript it stores the choice in
`sessionStorage["mint-section"]` and opens `contact.html` scrolled to that office (`data-anchor="uk|ksa|eg"`).
Without JavaScript it goes to `contact.html?country=uk` (etc.). If you later give each country its own page, change the
form's `action` / the redirect in `js/doc.js` (search for `cty-form`).

### 4.4 Guide videos
The thumbnails on `pils-guide.html` / `consent-guide.html` play a **test clip**. Each thumbnail is
`<button class="vid" data-video="URL" data-title="…">`; put the real video URL in `data-video`.
If the videos are hosted on another domain, add that domain to `media-src` in the Content-Security-Policy (§5).

### 4.5 Cookie consent
The banner stores the visitor's choice in `localStorage["mint-cookie-consent"]` as
`{"functional":bool,"analytics":bool,"marketing":bool}` and fires a `mint:cookies` event on `document` with the same
object. **Load analytics / marketing tags only after the matching flag is `true`**, e.g.:

```js
function start(c) { if (c && c.analytics) { /* load analytics */ } }
try { start(JSON.parse(localStorage.getItem('mint-cookie-consent'))); } catch (e) {}
document.addEventListener('mint:cookies', function (e) { start(e.detail); });
```

### 4.6 In-page section links (no `#hash` URLs)
Links like `<a href="pils-legal.html" data-section="refunds">` open that page scrolled to `[data-anchor="refunds"]`
(handled by `js/ui.js`). Keep `data-section` / `data-anchor` pairs when templating. Anchors in use:
`contact` (product homes and pricing), `uk` `ksa` `eg` `form` (contact.html), `terms` `privacy` `faq` `refunds` `copyright` (pils-legal.html).

### 4.7 Domain / SEO
Each page has a description, canonical URL, Open Graph/Twitter tags, and the home page has Organization JSON-LD.
They point at `https://mint-rdwd.vercel.app`. For the real domain, search and replace that URL in the pages,
`robots.txt` and `sitemap.xml`, in one go.

## 5. Server settings to set on your server

Send these headers on every response (adjust the CSP when you add domains):

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; media-src 'self' https://interactive-examples.mdn.mozilla.net; object-src 'none'; connect-src 'self'; frame-src 'none'; form-action 'self'; base-uri 'self'; frame-ancestors 'self'; upgrade-insecure-requests
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
Cross-Origin-Opener-Policy: same-origin
```

- The pages have **no inline scripts, no inline `style` attributes and no inline event handlers**, which is why the CSP
  needs no `'unsafe-inline'`. Keep it that way (put new JS in `js/`, new styles in `css/`).
  The only inline `<script>` blocks are `type="application/json"` (header config) and `type="application/ld+json"` (SEO); browsers don't execute them.
- If the API lives on another domain, add it to `connect-src` and to `form-action`.
- Caching: `assets/` → `public, max-age=604800, stale-while-revalidate=2592000`; `css/`, `js/` and HTML →
  `max-age=0, must-revalidate`, because the file names carry no version. If you add hashed file names, CSS/JS can be cached for a year.

## 6. Changing content

Edit the pages directly: they are clean, readable HTML with no generated markup to work around.
Shared parts (head, footers, header JSON, contact form) repeat on every page, so once they become your templates,
change them in one place. Long texts (Cookies, Legal, PIF TICK) are ordinary paragraphs, lists and headings in the pages.

## 7. Checklist before launch

- [ ] `/api/contact` built (validation, honeypot, rate limit, email/CRM), `data-demo` removed from the forms
- [ ] Login URLs set (`data-login` links + `"login"` in the header JSON)
- [ ] Real guide videos in `data-video` (and their domain in the CSP `media-src`)
- [ ] Social links (X, LinkedIn, YouTube in the footer; the CEO's LinkedIn on the About pages) — currently `#`
- [ ] Real domain in canonical / Open Graph / `sitemap.xml` / `robots.txt`
- [ ] Security + cache headers from §5 on the server
- [ ] Analytics (if any) gated on the cookie choice (§4.5)
