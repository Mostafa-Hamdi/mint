# Builds every page of the site as plain HTML (no framework), styled by css/ui.css + css/doc.css.
# usage: python -I _figma-reference/_build/build.py <project>     then: python -I _figma-reference/_build/finalize.py <project>
#
# Also writes handoff/partials/ (header config, footers, contact form) for the backend developer.
import os, sys, json, html
from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
P = sys.argv[1]
ORIG = os.path.join(S, '..', 'originals')          # design photos (not deployed)
esc = html.escape

# ---------------------------------------------------------------- settings the backend will change
LOGIN_URL = '#'                       # "Log in" buttons (header + home cards)
CONTACT_ENDPOINT = '/api/contact'     # every contact form posts here (POST, form-encoded)
DEMO_FORMS = True                     # True: forms stay on the page and show the thank-you note (no backend yet)
GUIDE_VIDEO = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4'   # test clip until real videos exist

NAME = {'mintformed': 'MINTFORMED', 'pils': 'MINT PILs', 'consent': 'MINT CONSENT'}


# ---------------------------------------------------------------- assets
def white_logos():
    for p in ('pils', 'consent'):
        src = open(os.path.join(P, 'assets/img/logo-%s.svg' % p), encoding='utf-8').read()
        open(os.path.join(P, 'assets/img/logo-%s-white.svg' % p), 'w', encoding='utf-8', newline='\n').write(src.replace('#00A48F', '#FFFFFF'))


def resized(name, widths, prefix=None, ext='jpg'):
    """web copies of a design photo: assets/img/<prefix>-<w>.jpg; returns (srcset, largest)"""
    prefix = prefix or name
    im0 = None
    for w in widths:
        out = os.path.join(P, 'assets/img/%s-%d.jpg' % (prefix, w))
        if not os.path.exists(out):
            im0 = im0 or Image.open(os.path.join(ORIG, '%s.%s' % (name, ext))).convert('RGB')
            im = im0.resize((w, round(im0.height * w / im0.width)), Image.LANCZOS)
            im.save(out, quality=78, optimize=True, progressive=True)
    return (', '.join('assets/img/%s-%d.jpg %dw' % (prefix, w, w) for w in widths), 'assets/img/%s-%d.jpg' % (prefix, widths[-1]))


# ---------------------------------------------------------------- icons
ICON = {
    'chev': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
    'play': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg>',
    'login': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg>',
    'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
}
CHEV = '<span class="acc-c" aria-hidden="true">%s</span>' % ICON['chev']
PLAY = '<span class="vid-play" aria-hidden="true">%s</span>' % ICON['play']
SOCIAL = (
    '<a href="#" aria-label="X"><svg viewBox="0 0 36.28 32.78" aria-hidden="true"><path d="M22.6156 13.513L35.1418 0H30.3783L20.5426 10.6102L13.0114 0H0L13.1768 18.5623L0 32.7759H4.76351L15.2388 21.465L23.2662 32.7759H36.2776L22.6046 13.5241L22.6156 13.513ZM6.71521 3.46999H11.2472L29.5734 29.2948H25.0415L6.71521 3.46999Z"/></svg></a>'
    '<a href="#" aria-label="LinkedIn"><svg viewBox="76.27 0.96 29.94 30.86" aria-hidden="true"><path d="M80.269 9.0131C82.4735 9.0131 84.2606 7.21057 84.2606 4.98702C84.2606 2.76347 82.4735 0.960938 80.269 0.960938C78.0645 0.960938 76.2773 2.76347 76.2773 4.98702C76.2773 7.21057 78.0645 9.0131 80.269 9.0131Z"/><path d="M83.3005 11.6953H77.2469C77.0825 11.6953 76.9492 11.8297 76.9492 11.9956V31.5144C76.9492 31.6802 77.0825 31.8146 77.2469 31.8146H83.3005C83.465 31.8146 83.5983 31.6802 83.5983 31.5144V11.9956C83.5983 11.8297 83.465 11.6953 83.3005 11.6953Z"/><path d="M106.204 19.0678V30.4676C106.204 31.2017 105.609 31.8134 104.87 31.8134H100.878C100.151 31.8134 99.5442 31.2128 99.5442 30.4676V21.0808C99.5442 19.2346 98.0556 17.7332 96.2252 17.7332C94.3948 17.7332 92.9062 19.2346 92.9062 21.0808V30.4676C92.9062 31.2017 92.3107 31.8134 91.5719 31.8134H87.5803C86.8525 31.8134 86.2461 31.2128 86.2461 30.4676V13.0287C86.2461 12.2946 86.8415 11.6829 87.5803 11.6829H91.5719C92.2997 11.6829 92.9062 12.2835 92.9062 13.0287V13.885C94.2404 12.15 96.4347 11.0156 98.8936 11.0156C102.565 11.0156 106.204 13.696 106.204 19.0678Z"/></svg></a>'
    '<a href="#" aria-label="YouTube"><svg viewBox="146.2 3.15 36.25 26.48" aria-hidden="true"><path d="M177.675 3.15625H150.98C148.344 3.15625 146.205 5.3139 146.205 7.972V24.8104C146.205 27.4685 148.344 29.6261 150.98 29.6261H177.675C180.31 29.6261 182.45 27.4685 182.45 24.8104V7.972C182.45 5.3139 180.31 3.15625 177.675 3.15625ZM168.622 17.559L161.201 21.2959C160.341 21.7296 159.338 21.0957 159.338 20.1392V12.6543C159.338 11.6867 160.341 11.0638 161.201 11.4976L168.622 15.2456C169.57 15.7239 169.57 17.0918 168.622 17.5701V17.559Z"/></svg></a>'
)


# ---------------------------------------------------------------- header config (the header itself is built by js/ui.js)
def cfg(brand):
    if brand == 'mintformed':
        c = {'name': 'MINTFORMED', 'logo': 'assets/img/logo.svg', 'home': 'index.html',
             'links': [{'label': 'Home', 'href': 'index.html'},
                       {'label': 'Products', 'menu': [
                           {'label': 'MINT CONSENT', 'href': 'consent.html', 'logo': 'assets/img/logo-consent.svg', 'note': 'Digital consent, explained in clear language.'},
                           {'label': 'MINT PILs', 'href': 'pils.html', 'logo': 'assets/img/logo-pils.svg', 'note': 'Illustrated, interactive patient leaflets.'}]},
                       {'label': 'About Us', 'href': 'about.html'}, {'label': 'Contact Us', 'href': 'contact.html'}],
             'tabs': [{'label': 'Home', 'href': 'index.html', 'icon': 'home'},
                      {'label': 'Products', 'icon': 'grid', 'sheet': [
                          {'label': 'MINT CONSENT', 'href': 'consent.html', 'logo': 'assets/img/logo-consent.svg', 'note': 'Digital consent, explained clearly'},
                          {'label': 'MINT PILs', 'href': 'pils.html', 'logo': 'assets/img/logo-pils.svg', 'note': 'Illustrated, interactive leaflets'}]},
                      {'label': 'About', 'href': 'about.html', 'icon': 'info'}, {'label': 'Contact', 'href': 'contact.html', 'icon': 'mail'}]}
    else:
        p = brand
        c = {'name': NAME[p], 'logo': f'assets/img/logo-{p}.svg', 'home': p + '.html',
             'links': [{'label': 'Home', 'href': p + '.html'}, {'label': 'About', 'href': p + '-about.html'}, {'label': 'Guide', 'href': p + '-guide.html'},
                       {'label': 'Pricing', 'href': p + '-pricing.html'}, {'label': 'Contact Us', 'href': p + '.html', 'section': 'contact'}],
             'tabs': [{'label': 'Home', 'href': p + '.html', 'icon': 'home'}, {'label': 'Guide', 'href': p + '-guide.html', 'icon': 'book'},
                      {'label': 'Pricing', 'href': p + '-pricing.html', 'icon': 'tag'}, {'label': 'About', 'href': p + '-about.html', 'icon': 'info'},
                      {'label': 'Contact', 'href': p + '.html', 'section': 'contact', 'icon': 'mail'}],
             'family': [
                 {'label': 'MINTFORMED', 'href': 'index.html', 'logo': 'assets/img/logo.svg', 'note': 'Back to the main site', 'main': True},
                 {'label': 'MINT CONSENT', 'href': 'consent.html', 'logo': 'assets/img/logo-consent.svg', 'note': 'Digital consent, explained clearly', 'current': p == 'consent'},
                 {'label': 'MINT PILs', 'href': 'pils.html', 'logo': 'assets/img/logo-pils.svg', 'note': 'Illustrated, interactive leaflets', 'current': p == 'pils'},
                 {'label': 'MINT FAMILY', 'note': 'The family health app', 'soon': True}]}
    c['login'] = LOGIN_URL
    return json.dumps(c, ensure_ascii=False)


# ---------------------------------------------------------------- footers
def _links(items, here):
    out = []
    for label, href, sec in items:
        attrs = f' data-section="{sec}"' if sec else ''
        if href == here and not sec: attrs += ' aria-current="page"'
        out.append(f'<li><a href="{href}"{attrs}>{esc(label)}</a></li>')
    return '<ul>' + ''.join(out) + '</ul>'


BRAND_BLOCK = '''    <div class="doc-foot-brand">
      <a href="index.html"><img src="assets/img/logo-white.svg" alt="MINTFORMED" width="150" height="56"></a>
      <p class="doc-foot-tag">Be Informed With<br>MINTFORMED</p>
      <p class="doc-foot-acc">Accredited by</p>
      <img class="doc-foot-badge" src="assets/img/pif-badge-white.svg" alt="Trusted Information Creator – Patient Information Forum" width="136" height="80" loading="lazy">
    </div>'''


def footer(brand, here):
    bar = f'''    <div class="doc-foot-bar">
      <p>© 2026 | All Rights Reserved | Powered by AMPM Training</p>
      <div class="doc-foot-social">{SOCIAL}</div>
    </div>'''
    if brand == 'mintformed':
        row = _links([('About Us', 'about.html', None), ('Terms and Conditions', 'pils-legal.html', 'terms'), ('PIFTICK', 'piftick.html', None),
                      ('Cookies', 'cookies.html', None), ('Contact Us', 'contact.html', None)], here)
        middle = f'''    <div class="doc-foot-info">
      <div><img src="assets/img/icon-location.svg" alt="" width="40" height="40"><div><h2>Our Address</h2><p>9 High Street, Wellington,<br>Somerset, UK TA21 8QT</p></div></div>
      <div><img src="assets/img/icon-send.svg" alt="" width="40" height="40"><div><h2>Contact us</h2><p><a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a></p></div></div>
      <nav class="doc-foot-row" aria-label="Footer">{row}</nav>
    </div>'''
    else:
        legal = 'pils-legal.html'
        col1 = [('Privacy Policy', legal, 'privacy'), ('FAQ’s', legal, 'faq'), ('Terms and Conditions', legal, 'terms'),
                ('Refunds Policy', legal, 'refunds'), ('Copyright Information', legal, 'copyright'), ('MINTFORMED', 'index.html', None)]
        col2 = [('Pricing', brand + '-pricing.html', None), ('About AMPM', brand + '-about.html', None), ('Tutorials and Guides', brand + '-guide.html', None),
                ('Cookies', brand + '-cookies.html', None), ('PIFTICK', brand + '-piftick.html', None)]
        middle = f'    <nav class="doc-foot-nav" aria-label="Footer">{_links(col1, here)}{_links(col2, here)}</nav>'
    return f'''<footer class="doc-foot">
  <div class="doc-wrap">
{BRAND_BLOCK}
{middle}
{bar}
  </div>
</footer>'''


# ---------------------------------------------------------------- page shell
def head(title, preload=''):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="theme-color" content="#3A495B">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  {preload}
  <link href="css/ui.css" rel="stylesheet">
  <link href="css/doc.css" rel="stylesheet">
</head>
<body>
'''


def page(out, brand, title, main_html, preload='', js=False):
    extra = '\n<script src="js/doc.js"></script>' if js else ''
    text = (head(title, preload) + '<main class="doc" id="main" tabindex="-1">\n' + main_html + '</main>\n' + footer(brand, out) +
            f'\n<script type="application/json" id="sticky-cfg">{cfg(brand)}</script>\n<script src="js/ui.js"></script>{extra}\n</body>\n</html>\n')
    open(os.path.join(P, out), 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote', out)


# ---------------------------------------------------------------- components
def photo_hero(img, alt, h1_html, body_html='', short=False, widths=(960, 1600, 2400), ext='jpg'):
    hs, hbig = resized(img, widths, ext=ext)
    pre = f'<link rel="preload" as="image" href="{hbig}" imagesrcset="{hs}" imagesizes="100vw">'
    return pre, f'''<section class="home-hero{' hero-short' if short else ''}">
  <img src="{hbig}" srcset="{hs}" sizes="100vw" alt="{esc(alt)}" width="2400" height="1600" fetchpriority="high">
  <div>
    <h1>{h1_html}</h1>
{body_html}  </div>
</section>
'''


def doc_hero(prod, h1, img, alt, sub=''):
    """navy page hero: product logo, title, optional subtitle, breadcrumb, photo"""
    srcset, big = resized(img, (720, 1280), 'hero-doc' if img == 'b939e3018b' else 'hero-' + img)
    pre = f'<link rel="preload" as="image" href="{big}" imagesrcset="{srcset}" imagesizes="(max-width: 767px) 100vw, 50vw">'
    sub_html = f'\n        <p class="doc-hero-sub">{esc(sub)}</p>' if sub else ''
    return pre, f'''  <section class="doc-hero">
    <div class="doc-wrap">
      <div>
        <img class="doc-hero-logo" src="assets/img/logo-{prod}-white.svg" alt="{NAME[prod]}" width="186" height="82">
        <h1>{esc(h1)}</h1>{sub_html}
        <nav class="doc-crumb" aria-label="Breadcrumb"><ol><li><a href="{prod}.html">Home</a></li><li><span aria-current="page">{esc(h1)}</span></li></ol></nav>
      </div>
      <img class="doc-hero-img" src="{big}" srcset="{srcset}" sizes="(max-width: 767px) 100vw, 50vw" alt="{esc(alt)}" width="1280" height="956" fetchpriority="high">
    </div>
  </section>
'''


def feature(i, tone, img, alt, h, text_html, sub='', more='', ext='jpg'):
    fs, fbig = resized(img, (720, 1200), ext=ext)
    cls = 'feat' + (' feat-teal' if tone == 'teal' else '') + (' feat-rev' if i % 2 else '')
    sub_html = f'<p class="feat-sub">{esc(sub)}</p>' if sub else ''
    return f'''<section class="{cls}">
  <div class="doc-wrap">
    <div class="feat-card"><h2>{esc(h)}</h2>{sub_html}<p>{text_html}</p>{more}</div>
    <img class="feat-img" src="{fbig}" srcset="{fs}" sizes="(max-width: 991px) 100vw, 56vw" alt="{esc(alt)}" width="1200" height="896" loading="lazy" decoding="async">
  </div>
</section>
'''


def accordion(items, uid, open_first=True, heading='h2'):
    """items: (question, answer_html, video_thumb or None)"""
    out = []
    for i, (q, a, thumb) in enumerate(items):
        is_open = open_first and i == 0
        vid = ''
        if thumb:
            vid = (f'<button type="button" class="vid" data-video="{GUIDE_VIDEO}" data-title="{esc(q)}" aria-label="Play video: {esc(q)}">'
                   f'<img src="{thumb}" alt="" width="1200" height="675" loading="lazy" decoding="async">{PLAY}<span class="vid-cap">Watch the video</span></button>')
        out.append(f'''    <div class="acc-i{' open' if is_open else ''}">
      <{heading}><button class="acc-q" type="button" id="{uid}-{i}-q" aria-expanded="{'true' if is_open else 'false'}" aria-controls="{uid}-{i}-a"><span>{esc(q)}</span>{CHEV}</button></{heading}>
      <div class="acc-a" id="{uid}-{i}-a" role="region" aria-labelledby="{uid}-{i}-q"><div class="acc-in"><div class="acc-body"><p>{a}</p>{vid}</div></div></div>
    </div>
''')
    return '  <div class="acc">\n' + ''.join(out) + '  </div>\n'


def contact_form(source):
    """the one contact form (all pages). Field names are the API contract — see HANDOFF.md"""
    demo = ' data-demo' if DEMO_FORMS else ''
    return f'''<form class="cf" action="{CONTACT_ENDPOINT}" method="post"{demo}>
          <input type="hidden" name="source" value="{source}">
          <label class="hp" aria-hidden="true">Leave empty<input name="website" tabindex="-1" autocomplete="off"></label>
          <label>First Name<input name="first_name" autocomplete="given-name" placeholder="First Name" maxlength="80" required></label>
          <label>Last Name<input name="last_name" autocomplete="family-name" placeholder="Last Name" maxlength="80" required></label>
          <label class="full">Email<input type="email" name="email" autocomplete="email" placeholder="Email" maxlength="160" required></label>
          <label class="full">Telephone<input type="tel" name="telephone" autocomplete="tel" placeholder="Telephone" maxlength="40"></label>
          <label class="full">Your Message<textarea name="message" placeholder="Your Message" maxlength="4000" required></textarea></label>
          <button type="submit">Send</button>
          <p class="cf-ok" role="status" hidden>Thank you, we have your message and will get back to you soon.</p>
          <p class="cf-err" role="alert" hidden></p>
        </form>'''


def contact_section(source):
    return f'''<section class="contact" data-anchor="contact" aria-labelledby="contact-h">
  <div class="doc-wrap">
    <div class="contact-box">
      <div>
        <p class="contact-kicker">GET IN TOUCH</p>
        <h2 id="contact-h">Fill in the form to <span>Contact us directly</span></h2>
        {contact_form(source)}
      </div>
      <div class="contact-loc">
        <h3>OUR LOCATION</h3>
        <ul>
          <li><img src="assets/img/icon-location.svg" alt="" width="26" height="26"><span>9 High Street, Wellington, Somerset, UK TA21 8QT</span></li>
          <li><img src="assets/img/icon-mail.svg" alt="" width="26" height="26"><a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>
'''


def partial(name):
    return open(os.path.join(S, name), encoding='utf-8').read()


# ================================================================ pages
white_logos()

# ---------- MINTFORMED home
pre, hero = photo_hero('hero-home', 'Clinicians in a hospital corridor', '<span>Be Informed With</span><span class="hl">MINTFORMED</span>', f'''    <p>Mintformed is the platform that gives you access to our <span class="g">MINT</span> products. It is powered and owned <span class="g">by AMPM Training.</span></p>
    <p class="hero-sub">Enhance your communication with patients and their families with:</p>
    <div class="hero-cards">
      <div class="hero-card"><a href="consent.html"><img src="assets/img/logo-consent.svg" alt="MINT CONSENT" width="190" height="84"></a><a class="btn-line" href="{LOGIN_URL}" data-login>{ICON['login']}Log in</a></div>
      <div class="hero-card"><a href="pils.html"><img src="assets/img/logo-pils.svg" alt="MINT PILs" width="190" height="84"></a><a class="btn-line" href="{LOGIN_URL}" data-login>{ICON['login']}Log in</a></div>
    </div>
''')
more = lambda href, label='More Info': f'<a class="more" href="{href}">{label} {ICON["arrow"]}</a>'
home = hero + feature(0, 'navy', 'home-consent', 'Doctors presenting the MINT CONSENT platform', 'MINT CONSENT',
                      'This is a digital consent platform. It focuses on giving the patient the relevant information needed to ensure an informed decision. '
                      'Every aspect of consent is explained in easy to understand language. The consent is fully adjustable to suit the needs of your patient. '
                      'You can choose to attach our PIF Tick certified MINT PILs.', more=more('consent.html')) \
    + feature(1, 'teal', 'home-pils', 'A doctor showing a patient a MINT PIL on a tablet', 'MINT PILs',
              'Our MINT PILs (Medical Information Notable and Trusted) are easy-to-read, illustrated leaflets designed for mobile use. They have videos and '
              'interactive elements incorporated within the PILs. They also have read-only and read-aloud versions to suit every need. For further information please go to '
              '<a href="https://ampmtraining.com" rel="noopener">AMPMTraining.com</a>.', more=more('pils.html')) \
    + feature(2, 'navy', 'home-family', 'A couple using the MINT FAMILY app', 'MINT FAMILY',
              'This is our app designed for patients and their families. It allows them to keep all the information they need in one place and to '
              'communicate with each other in health matters.', more='<span class="more soon">Coming Soon</span>')
page('index.html', 'mintformed', 'MINTFORMED – Be Informed With MINTFORMED', home, pre)


# ---------- About (MINTFORMED + one per product site)
def about_main(brand):
    pils_href = 'pils.html'
    pre, hero = photo_hero('hero-about', 'Nurses caring for a patient on a hospital ward', '<span>About AMPM Training</span>', short=True)
    body = hero + f'''<section class="band band-teal">
  <div class="doc-wrap">
    <h2>About AMPM Training</h2>
    <p>AMPM Training is a UK-based digital health education company headquartered in Wellington, Somerset. It was established in 2020. We specialise in digital patient education solutions that enhance health literacy and empower healthcare professionals to deliver better care.</p>
    <p>AMPM Training provides hospitals, pharmaceutical companies, and EMR vendors with trusted, compliant digital patient education solutions. We help hospitals to improve patient satisfaction, safety, and health literacy metrics while aligning with CQC, CBAHI, JCI, and GAHAR standards.</p>
    <p>Our solutions also support pharmaceutical brands in delivering patient-centered, regulatory-compliant materials, and provide EMR vendors with value-added modules that enhance their platforms and differentiate their offerings.</p>
  </div>
</section>
<section class="band band-navy band-center">
  <div class="doc-wrap">
    <h2>Our Commitment</h2>
    <p>At AMPM Training, we are committed to transform patient education with a balanced approach that combines:</p>
    <ul class="cols4">
      <li><img src="assets/img/icon-commit-1.svg" alt="" width="64" height="64"><h3>Technology</h3><p>User-friendly digital platforms.</p></li>
      <li><img src="assets/img/icon-commit-2.svg" alt="" width="64" height="64"><h3>Health Literacy</h3><p>Clear, accessible information for your patient.</p></li>
      <li><img src="assets/img/icon-commit-3.svg" alt="" width="64" height="64"><h3>Empathy</h3><p>Empowering human connections in healthcare.</p></li>
      <li><img src="assets/img/icon-commit-4.svg" alt="" width="64" height="64"><h3>Science</h3><p>Evidence-based content.</p></li>
    </ul>
  </div>
</section>
<section class="band band-teal">
  <div class="doc-wrap ceo">
    <div class="ceo-text">
      <h2>Message from our CEO</h2>
      <p>When patient education moved online, something important got left behind: accessibility and connection.</p>
      <p>I founded <b>AMPM Training</b> because I saw a widening gap between what patients need and what they are actually receiving.</p>
      <p>In 2013, the UK’s push for a paperless NHS removed printed PILs from consultations. PDFs took their place. However, they are harder to find, harder to absorb, and disconnected from the patients’ care journey.</p>
      <p><b class="hl">Our goal was clear:</b> to reinvent patient education for the digital era. A solution that speaks the patient’s language visually, simply, and instantly. <b>That’s how <a href="{pils_href}">MINT PILs</a> and the <a href="{LOGIN_URL}" data-login>MINT Platform</a> came to life:</b> engaging, interactive content delivered at the point of care.</p>
      <p>Behind every informed patient is someone who cares enough to teach them well. That is the change we champion every day.</p>
    </div>
    <div class="ceo-card">
      <img src="assets/img/ceo.png" alt="Ahmed Samy Boraei" width="240" height="240" loading="lazy">
      <p class="nm">Ahmed Samy Boraei</p>
      <p class="rl">Chief Executive Officer<br>AMPM Training</p>
      <div class="ceo-links"><a href="mailto:info@ampmtraining.com" aria-label="Email Ahmed Samy Boraei"><img src="assets/img/icon-mail.svg" alt="" width="24" height="24"></a><a href="#" aria-label="Ahmed Samy Boraei on LinkedIn"><img src="assets/img/icon-linkedin-box.svg" alt="" width="24" height="24"></a></div>
    </div>
  </div>
</section>
<section class="band band-white band-center">
  <div class="doc-wrap">
    <h2>Our Global Presence</h2>
    <p><b>AMPM Training</b> is based in the United Kingdom and supports healthcare providers in several regions around the world.</p>
    <p><b>KSA:</b> We operate through our trusted local partner, The Branch of the Field Communication Company, supporting public and private healthcare institutions across the Gulf.</p>
    <p><b>Egypt:</b> We are represented by <b>AlAfaf Medical Services</b> (<b>AMS</b>).</p>
    <p>We believe every patient deserves clear, accessible, and culturally relevant information. Partner with <b>AMPM Training</b> and be part of this transformation.</p>
  </div>
</section>
<section class="band band-teal band-center">
  <div class="doc-wrap">
    <h2>We are proudly accredited by:</h2>
    <div class="acc-cards">
      <div class="acc-card"><p>PIF TICK</p><img src="assets/img/pif-badge.svg" alt="Trusted Information Creator – Patient Information Forum" width="130" height="76" loading="lazy"></div>
      <div class="acc-card"><p>CPD Standards Office</p><img src="assets/img/cpd-badge.svg" alt="Accredited CPD – The CPD Standards Office, CPD Provider 22605" width="130" height="110" loading="lazy"></div>
    </div>
  </div>
</section>
'''
    return pre, body


for out, brand, title in [('about.html', 'mintformed', 'About AMPM Training – MINTFORMED'),
                          ('pils-about.html', 'pils', 'About AMPM Training – MINT PILs'),
                          ('consent-about.html', 'consent', 'About AMPM Training – MINT CONSENT')]:
    pre, body = about_main(brand)
    page(out, brand, title, body, pre)


# ---------- MINTFORMED contact
def office(anchor, title, sub, rows):
    li = ''.join(f'<li><img src="assets/img/{ic}" alt="" width="22" height="22"><span>{t}</span></li>' for ic, t in rows)
    sub_html = f'<small>{esc(sub)}</small>' if sub else ''
    return f'<div class="office" data-anchor="{anchor}"><h2>{esc(title)}{sub_html}</h2><ul>{li}</ul></div>'


contact_main = f'''<section class="ct-page">
  <div class="doc-wrap ct-grid">
    <div>
      <h1>Contact Us</h1>
      {office('uk', 'United Kingdom', 'AMPM Training Ltd', [
          ('icon-location.svg', '9 High Street, Wellington, Somerset, UK TA21 8QT'),
          ('icon-reg.svg', 'Reg. No. 12428457'),
          ('icon-phone.svg', '<a href="tel:+441482278382">+44 14 82 27 8382</a>'),
          ('icon-send-sm.svg', '<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a>')])}
      {office('ksa', 'KSA', 'The Field of Communication Co.', [
          ('icon-phone.svg', '<a href="tel:+966543833370">+966 54 383 3370</a>'),
          ('icon-send-sm.svg', '<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a>')])}
      {office('eg', 'Egypt', 'AlAfaf Medical Services', [
          ('icon-phone.svg', '<a href="tel:+201025219198">+20 102 521 9198</a>'),
          ('icon-send-sm.svg', '<a href="mailto:info@alafafmedical.com">info@alafafmedical.com</a>')])}
    </div>
    <div class="ct-card" data-anchor="form">
      <p class="contact-kicker">CONTACT FORM</p>
      <h2>Fill in the form to <span>contact us directly</span></h2>
      {contact_form('mintformed-contact')}
    </div>
  </div>
</section>
'''
page('contact.html', 'mintformed', 'Contact Us – MINTFORMED', contact_main)

# ---------- cookies (3 sites)
cookies = partial('cookies_content.html')
pre, hero = photo_hero('hero-about', 'Nurses caring for a patient on a hospital ward', '<span>Cookies</span>', '    <p>Data Protection Policy</p>\n', short=True)
page('cookies.html', 'mintformed', 'Cookies – Data Protection Policy – MINTFORMED', hero + cookies, pre)
for prod in ('pils', 'consent'):
    alt = 'A doctor holding a phone showing a confirmed MINT %s, with a colleague greeting a patient behind him' % ('PIL' if prod == 'pils' else 'consent')
    pre, hero = doc_hero(prod, 'Cookies', 'b939e3018b', alt, 'Data Protection Policy')
    page(f'{prod}-cookies.html', prod, f'{NAME[prod]} – Cookies', hero + cookies, pre)

# ---------- PIF TICK (3 sites)
art = partial('piftick_content.html')
page('piftick.html', 'mintformed', 'AMPM Training gains PIF TICK accreditation – MINTFORMED', art)
for prod in ('pils', 'consent'):
    page(f'{prod}-piftick.html', prod, f'{NAME[prod]} – PIF TICK', art)

# ---------- product homes
HOMES = [
    ('pils', dict(img='8e6c824a8c', alt='A doctor talking a patient through her treatment', lines=['Medical Information', 'Notable and Trusted'],
                  text='Our interactive MINT PILs were created with the idea of empowering patients with the knowledge they need to take control of their treatment. '
                       'They discuss general issues in health as well as specific health problems in a simple, yet comprehensive manner, without losing touch with the culture and society the patient is in.'),
     [dict(tone='navy', img='ece03e7fe6', alt='A tablet showing an interactive MINT PIL', h='MINT PILs', sub='is one of the services provided by AMPM Training Ltd.',
           text='AMPM Training was established with a vision of improving healthcare provision through enhancing communication. It operates under a team with over 25 years of experience '
                'in healthcare delivery and training medical staff. We aspire to a healthcare culture based on transparency and communication that develops mutual trust and understanding.'),
      dict(tone='teal', img='b3918e43d2', alt='A clinician reviewing patient information on a laptop', h='MINT PILs',
           text='Our MINT PILs division is involved in patient edification, which we believe goes beyond patient education into a more spiritual level of enlightenment. '
                'This is important for a holistic form of healing. We have designed our MINT PILs to be visual to capture the social issues and feelings, as well as added interactivity '
                'to enhance the user experience. The acronym stands for Medical Information Notable and Trusted. Accordingly, our information is based on the requirements of the community '
                'and is based on the latest guidance and is all referenced. We are working with PIF Tick, “The UK’s quality mark for trusted health information”, to ensure our leaflets '
                'are produced using a professional and structured process.')]),
    ('consent', dict(img='2a2e37ab46', alt='A doctor in a modern clinic', lines=['Clear information', 'Informed decisions'],
                     text='MINT CONSENT is a digital consent platform. It transforms the informed consent process by providing patients with clear, accessible information '
                          'before they agree to a medical procedure or treatment.'),
     [dict(tone='navy', img='ba5f7735ff', alt='A doctor going through procedure information with a patient', h='MINT CONSENT',
           text='Instead of relying solely on a single consultation, patients can review procedure information, benefits, risks, alternatives, and aftercare instructions at their own pace, '
                'from home or on their mobile device. This empowers patients and allows them to arrive at decisions confidently and at their own pace.'),
      dict(tone='teal', img='3972c53769', alt='A clinician using MINT CONSENT in a modern clinic', h='MINT CONSENT',
           text='For healthcare professionals, MINT CONSENT supports more consistent and structured communication with patients. Standardised procedure information helps ensure that key topics '
                'are discussed while allowing clinicians to personalise conversations according to each patient’s individual circumstances. Digital consent platforms can also document when '
                'information has been provided, when consent forms have been completed, and any questions or concerns raised by the patient, creating a clear record that supports good clinical '
                'practice and shared decision-making.'),
      dict(tone='navy', img='dc6a663cea', alt='The MINT CONSENT platform on screen', h='MINT CONSENT',
           text='For hospitals and healthcare organisations, MINT CONSENT offers an opportunity to improve efficiency, standardisation and governance across multiple departments and sites. '
                'MINT CONSENT and MINT PILs (patient information leaflets) can be centrally managed, updated and distributed, helping to ensure patients receive consistent, high-quality information.')]),
]
for prod, h, feats in HOMES:
    h1 = ''.join('<span>%s</span>' % esc(l) for l in h['lines']) + '<span class="hl">%s</span>' % NAME[prod]
    pre, hero = photo_hero(h['img'], h['alt'], h1, f'    <p>{esc(h["text"])}</p>\n')
    body = hero + ''.join(feature(i, f['tone'], f['img'], f['alt'], f['h'], esc(f['text']), f.get('sub', '')) for i, f in enumerate(feats))
    page(f'{prod}.html', prod, NAME[prod], body + contact_section(f'{prod}-home'), pre)

# ---------- guides
THUMB = 'assets/v2/crop-9fc5176411.jpg'
GUIDES = [
    ('pils', 'b09a4483d0', 'A clinician using the MINT platform', [
        ('How to register for a clinic account?',
         'You can now register individual clinic accounts as opposed to a full institute account. These accounts allow you to send '
         'educational content to your patients, unrelated to institutional accounts.', THUMB),
        ('How to use your clinic or professional account on MINT PILs?',
         'The MINT Platform allows you to access MINT Patient Information Leaflets in your clinic and send them to your patients. '
         'The following video shows how to use your account to educate patients, set your favourites and send MINT PILs to your patients.', THUMB),
        ('How to add a Brand Engagement Message to your account?',
         'When you use the MINT Platform to send patient information material, you can send a small reminder to your patients with your name, '
         'qualifications and contact details. Patients will know and remember the doctor that cares. The following video will show you how to '
         'create a Brand Engagement Message with the MINT Team.', THUMB)]),
    ('consent', 'da7ded2ff4', 'A clinician using MINT CONSENT', [
        ('Why choose MINT CONSENT?',
         'You can now register individual clinic accounts as opposed to a full institute account. These accounts allow you to send '
         'educational content to your patients, unrelated to institutional accounts. The following video shows how to register.', THUMB),
        ('How do I register on MINT CONSENT?',
         'Contact us by using the <a href="consent.html" data-section="contact">contact form</a> or by email on '
         '<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a>.', None)]),
]
for prod, img, alt, items in GUIDES:
    safe = [(q, a if '<a ' in a else esc(a), t) for q, a, t in items]
    pre, hero = doc_hero(prod, 'Guides', img, alt)
    body = hero + '<section class="acc-sec" aria-label="Guides">\n<div class="doc-wrap">\n' + accordion(safe, prod + '-g') + '</div>\n</section>\n'
    page(f'{prod}-guide.html', prod, f'{NAME[prod]} – Guides', body, pre, js=True)

# ---------- pricing
CTY = [('uk', 'United Kingdom'), ('ksa', 'Saudi Arabia'), ('eg', 'Egypt')]
opts = ''.join(f'<label class="cty-opt"><input type="radio" name="country" value="{v}"><span class="flag f-{v}" aria-hidden="true"></span>{n}</label>' for v, n in CTY)
COUNTRY = f'''    <p class="price-lead">For clinics, please select your country to continue to the relevant page.</p>
    <form class="cty-form" action="contact.html" method="get">
      <fieldset><legend>Select your country</legend><div class="cty-opts">{opts}</div></fieldset>
      <p class="cty-msg" role="alert"></p>
      <button class="cty-go" type="submit">Continue</button>
    </form>
'''
for prod, img, alt, clinics in [('pils', '407c55b7b4', 'A clinician with a patient in a modern clinic', True), ('consent', '2a2e37ab46', 'A doctor in a modern clinic', False)]:
    out = f'{prod}-pricing.html'
    pre, hero = doc_hero(prod, 'Pricing', img, alt)
    note = (f'<p class="price-note">For hospitals and medical institutes, please contact us on our email '
            f'<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a> or use the <a href="{out}" data-section="contact">form below</a>. '
            f'We will tailor a quote based on your needs.</p>\n')
    body = (hero + '<section class="price-sec" aria-label="Pricing">\n  <div class="doc-wrap">\n' + (COUNTRY if clinics else '') + '    ' + note +
            '  </div>\n</section>\n' + contact_section(f'{prod}-pricing'))
    page(out, prod, f'{NAME[prod]} – Pricing', body, pre, js=True)

# ---------- legal
legal = partial('legal_content.html').replace('{CHEV}', CHEV)
pre, hero = doc_hero('pils', 'Legal', '7ab5234145', 'A clinician reviewing documents')
page('pils-legal.html', 'pils', 'MINT PILs – Legal', hero + '<section class="legal-sec">\n<div class="doc-wrap">\n' + legal + '</div>\n</section>\n', pre, js=True)


# ================================================================ handoff partials (for the backend's templates)
H = os.path.join(P, 'handoff', 'partials')
os.makedirs(H, exist_ok=True)
for brand in ('mintformed', 'pils', 'consent'):
    open(os.path.join(H, f'footer-{brand}.html'), 'w', encoding='utf-8', newline='\n').write(footer(brand, '') + '\n')
    open(os.path.join(H, f'header-config-{brand}.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(json.loads(cfg(brand)), indent=2, ensure_ascii=False) + '\n')
open(os.path.join(H, 'head.html'), 'w', encoding='utf-8', newline='\n').write(head('{{ page title }}'))
open(os.path.join(H, 'contact-form.html'), 'w', encoding='utf-8', newline='\n').write(contact_form('{{ source }}') + '\n')
print('wrote handoff/partials')
