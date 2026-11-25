# Coded product pages (no drawn backgrounds): page hero + document content + product footer, all HTML/CSS.
# usage: python -I gen_doc.py <project>      (run before finalize.py; replaces the gen2 output for these pages)
import os, sys, json, html
from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
P = sys.argv[1]

PAGES = [
    # out, product, title, hero title, content partial
    ('pils-cookies.html', 'pils', 'MINT PILs – Cookies', 'Cookies', 'cookies_content.html'),
    ('consent-cookies.html', 'consent', 'MINT CONSENT – Cookies', 'Cookies', 'cookies_content.html'),
]
NAME = {'pils': 'MINT PILs', 'consent': 'MINT CONSENT'}

# assets: white product logos (wordmark white, accent green) and a web-sized hero photo
for p in ('pils', 'consent'):
    src = open(os.path.join(P, 'assets/img/logo-%s.svg' % p), encoding='utf-8').read()
    open(os.path.join(P, 'assets/img/logo-%s-white.svg' % p), 'w', encoding='utf-8', newline='\n').write(
        src.replace('#00A48F', '#FFFFFF'))
hero_src = os.path.join(P, 'assets/v2/b939e3018b.jpg')
for w in (720, 1280):
    out = os.path.join(P, 'assets/img/hero-doc-%d.jpg' % w)
    if not os.path.exists(out):
        im = Image.open(hero_src).convert('RGB')
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(out, quality=80, optimize=True, progressive=True)

SOCIAL = (
    '<a href="#" aria-label="X"><svg viewBox="0 0 36.28 32.78" aria-hidden="true"><path d="M22.6156 13.513L35.1418 0H30.3783L20.5426 10.6102L13.0114 0H0L13.1768 18.5623L0 32.7759H4.76351L15.2388 21.465L23.2662 32.7759H36.2776L22.6046 13.5241L22.6156 13.513ZM6.71521 3.46999H11.2472L29.5734 29.2948H25.0415L6.71521 3.46999Z"/></svg></a>'
    '<a href="#" aria-label="LinkedIn"><svg viewBox="76.27 0.96 29.94 30.86" aria-hidden="true"><path d="M80.269 9.0131C82.4735 9.0131 84.2606 7.21057 84.2606 4.98702C84.2606 2.76347 82.4735 0.960938 80.269 0.960938C78.0645 0.960938 76.2773 2.76347 76.2773 4.98702C76.2773 7.21057 78.0645 9.0131 80.269 9.0131Z"/><path d="M83.3005 11.6953H77.2469C77.0825 11.6953 76.9492 11.8297 76.9492 11.9956V31.5144C76.9492 31.6802 77.0825 31.8146 77.2469 31.8146H83.3005C83.465 31.8146 83.5983 31.6802 83.5983 31.5144V11.9956C83.5983 11.8297 83.465 11.6953 83.3005 11.6953Z"/><path d="M106.204 19.0678V30.4676C106.204 31.2017 105.609 31.8134 104.87 31.8134H100.878C100.151 31.8134 99.5442 31.2128 99.5442 30.4676V21.0808C99.5442 19.2346 98.0556 17.7332 96.2252 17.7332C94.3948 17.7332 92.9062 19.2346 92.9062 21.0808V30.4676C92.9062 31.2017 92.3107 31.8134 91.5719 31.8134H87.5803C86.8525 31.8134 86.2461 31.2128 86.2461 30.4676V13.0287C86.2461 12.2946 86.8415 11.6829 87.5803 11.6829H91.5719C92.2997 11.6829 92.9062 12.2835 92.9062 13.0287V13.885C94.2404 12.15 96.4347 11.0156 98.8936 11.0156C102.565 11.0156 106.204 13.696 106.204 19.0678Z"/></svg></a>'
    '<a href="#" aria-label="YouTube"><svg viewBox="146.2 3.15 36.25 26.48" aria-hidden="true"><path d="M177.675 3.15625H150.98C148.344 3.15625 146.205 5.3139 146.205 7.972V24.8104C146.205 27.4685 148.344 29.6261 150.98 29.6261H177.675C180.31 29.6261 182.45 27.4685 182.45 24.8104V7.972C182.45 5.3139 180.31 3.15625 177.675 3.15625ZM168.622 17.559L161.201 21.2959C160.341 21.7296 159.338 21.0957 159.338 20.1392V12.6543C159.338 11.6867 160.341 11.0638 161.201 11.4976L168.622 15.2456C169.57 15.7239 169.57 17.0918 168.622 17.5701V17.559Z"/></svg></a>'
)


def footer(p, here):
    legal = 'pils-legal.html'
    col1 = [('Privacy Policy', legal, 'privacy'), ('FAQ’s', legal, 'faq'), ('Terms and Conditions', legal, 'terms'),
            ('Refunds Policy', legal, 'refunds'), ('Copyright Information', legal, 'copyright'), ('MINTFORMED', 'index.html', None)]
    col2 = [('Pricing', p + '-pricing.html', None), ('About AMPM', p + '-about.html', None), ('Tutorials and Guides', p + '-guide.html', None),
            ('Cookies', p + '-cookies.html', None), ('PIFTICK', p + '-piftick.html', None)]

    def ul(items):
        out = []
        for label, href, sec in items:
            attrs = f' data-section="{sec}"' if sec else ''
            if href == here: attrs += ' aria-current="page"'
            out.append(f'<li><a href="{href}"{attrs}>{html.escape(label)}</a></li>')
        return '<ul>' + ''.join(out) + '</ul>'
    return f'''<footer class="doc-foot">
  <div class="doc-wrap">
    <div class="doc-foot-brand">
      <a href="index.html"><img src="assets/img/logo-white.svg" alt="MINTFORMED" width="150" height="56"></a>
      <p class="doc-foot-tag">Be Informed With<br>MINTFORMED</p>
      <p class="doc-foot-acc">Accredited by</p>
      <img class="doc-foot-badge" src="assets/img/pif-badge-white.svg" alt="Trusted Information Creator – Patient Information Forum" width="136" height="80" loading="lazy">
    </div>
    <nav class="doc-foot-nav" aria-label="Footer">{ul(col1)}{ul(col2)}</nav>
    <div class="doc-foot-bar">
      <p>© 2026 | All Rights Reserved | Powered by AMPM Training</p>
      <div class="doc-foot-social">{SOCIAL}</div>
    </div>
  </div>
</footer>'''


def cfg(prod):
    p_ = prod
    c = {'name': NAME[prod], 'logo': f'assets/img/logo-{p_}.svg', 'home': p_ + '.html',
         'links': [{'label': 'Home', 'href': p_ + '.html'}, {'label': 'About', 'href': p_ + '-about.html'}, {'label': 'Guide', 'href': p_ + '-guide.html'},
                   {'label': 'Pricing', 'href': p_ + '-pricing.html'}, {'label': 'Contact Us', 'href': p_ + '.html', 'section': 'contact'}],
         'tabs': [{'label': 'Home', 'href': p_ + '.html', 'icon': 'home'}, {'label': 'Guide', 'href': p_ + '-guide.html', 'icon': 'book'},
                  {'label': 'Pricing', 'href': p_ + '-pricing.html', 'icon': 'tag'}, {'label': 'About', 'href': p_ + '-about.html', 'icon': 'info'},
                  {'label': 'Contact', 'href': p_ + '.html', 'section': 'contact', 'icon': 'mail'}]}
    c['family'] = [
        {'label': 'MINTFORMED', 'href': 'index.html', 'logo': 'assets/img/logo.svg', 'note': 'Back to the main site', 'main': True},
        {'label': 'MINT CONSENT', 'href': 'consent.html', 'logo': 'assets/img/logo-consent.svg', 'note': 'Digital consent, explained clearly', 'current': prod == 'consent'},
        {'label': 'MINT PILs', 'href': 'pils.html', 'logo': 'assets/img/logo-pils.svg', 'note': 'Illustrated, interactive leaflets', 'current': prod == 'pils'},
        {'label': 'MINT FAMILY', 'note': 'The family health app', 'soon': True}]
    return json.dumps(c)


for out, prod, title, h1, partial in PAGES:
    content = open(os.path.join(S, partial), encoding='utf-8').read()
    page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="theme-color" content="#3A495B">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="preload" as="image" href="assets/img/hero-doc-1280.jpg" imagesrcset="assets/img/hero-doc-720.jpg 720w, assets/img/hero-doc-1280.jpg 1280w" imagesizes="(max-width: 767px) 100vw, 50vw">
  <link href="css/ui.css" rel="stylesheet">
  <link href="css/doc.css" rel="stylesheet">
</head>
<body>
<main class="doc" id="main" tabindex="-1">
  <section class="doc-hero">
    <div class="doc-wrap">
      <div>
        <img class="doc-hero-logo" src="assets/img/logo-{prod}-white.svg" alt="{NAME[prod]}" width="186" height="82">
        <h1>{html.escape(h1)}</h1>
        <p class="doc-hero-sub">Data Protection Policy</p>
        <nav class="doc-crumb" aria-label="Breadcrumb"><ol><li><a href="{prod}.html">Home</a></li><li><span aria-current="page">{html.escape(h1)}</span></li></ol></nav>
      </div>
      <img class="doc-hero-img" src="assets/img/hero-doc-1280.jpg" srcset="assets/img/hero-doc-720.jpg 720w, assets/img/hero-doc-1280.jpg 1280w" sizes="(max-width: 767px) 100vw, 50vw" alt="A doctor holding a phone showing a confirmed MINT {'PIL' if prod == 'pils' else 'consent'}, with a colleague greeting a patient behind him" width="1280" height="956" fetchpriority="high">
    </div>
  </section>
{content}</main>
{footer(prod, out)}
<script type="application/json" id="sticky-cfg">{cfg(prod)}</script>
<script src="js/ui.js"></script>
</body>
</html>
'''
    open(os.path.join(P, out), 'w', encoding='utf-8', newline='\n').write(page)
    print('wrote', out)
