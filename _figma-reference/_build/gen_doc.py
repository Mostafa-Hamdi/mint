# Coded product pages (no drawn backgrounds): all HTML/CSS, styled by css/doc.css.
# usage: python -I gen_doc.py <project>      (run before finalize.py; gen2 no longer builds these pages)
import os, sys, json, html
from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
P = sys.argv[1]
NAME = {'pils': 'MINT PILs', 'consent': 'MINT CONSENT'}
esc = html.escape

# ---------- assets ----------
# white product logos (wordmark white, accent green)
for p in ('pils', 'consent'):
    src = open(os.path.join(P, 'assets/img/logo-%s.svg' % p), encoding='utf-8').read()
    open(os.path.join(P, 'assets/img/logo-%s-white.svg' % p), 'w', encoding='utf-8', newline='\n').write(
        src.replace('#00A48F', '#FFFFFF'))


def resized(name, widths, prefix=None):
    """web copies of a design photo: assets/img/<prefix>-<w>.jpg; returns (srcset, largest)"""
    prefix = prefix or name
    im0 = None
    for w in widths:
        out = os.path.join(P, 'assets/img/%s-%d.jpg' % (prefix, w))
        if not os.path.exists(out):
            im0 = im0 or Image.open(os.path.join(P, 'assets/v2/%s.jpg' % name)).convert('RGB')
            im = im0.resize((w, round(im0.height * w / im0.width)), Image.LANCZOS)
            im.save(out, quality=78, optimize=True, progressive=True)
    return (', '.join('assets/img/%s-%d.jpg %dw' % (prefix, w, w) for w in widths),
            'assets/img/%s-%d.jpg' % (prefix, widths[-1]))


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
            out.append(f'<li><a href="{href}"{attrs}>{esc(label)}</a></li>')
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


def tail(prod, out, js=False):
    extra = '\n<script src="js/doc.js"></script>' if js else ''
    return f'''{footer(prod, out)}
<script type="application/json" id="sticky-cfg">{cfg(prod)}</script>
<script src="js/ui.js"></script>{extra}
</body>
</html>
'''


def doc_hero(prod, h1, img_name, alt, sub=''):
    """navy page hero: product logo, title, optional subtitle, breadcrumb, photo. Returns (preload, html)."""
    srcset, big = resized(img_name, (720, 1280), 'hero-' + img_name) if img_name != 'b939e3018b' else resized(img_name, (720, 1280), 'hero-doc')
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


CHEV = '<span class="acc-c" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span>'
PLAY = '<span class="vid-play" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg></span>'
TEST_VIDEO = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4'


def accordion(items, uid, open_first=True):
    """items: (question, answer_html, video_thumb or None)"""
    out = []
    for i, (q, a, thumb) in enumerate(items):
        is_open = open_first and i == 0
        vid = ''
        if thumb:
            vid = (f'<button type="button" class="vid" data-video="{TEST_VIDEO}" data-title="{esc(q)}" aria-label="Play video: {esc(q)}">'
                   f'<img src="{thumb}" alt="" width="1200" height="675" loading="lazy" decoding="async">{PLAY}<span class="vid-cap">Watch the video</span></button>')
        out.append(f'''    <div class="acc-i{' open' if is_open else ''}">
      <h2><button class="acc-q" type="button" id="{uid}-{i}-q" aria-expanded="{'true' if is_open else 'false'}" aria-controls="{uid}-{i}-a"><span>{esc(q)}</span>{CHEV}</button></h2>
      <div class="acc-a" id="{uid}-{i}-a" role="region" aria-labelledby="{uid}-{i}-q"><div class="acc-in"><div class="acc-body"><p>{a}</p>{vid}</div></div></div>
    </div>
''')
    return '  <div class="acc">\n' + ''.join(out) + '  </div>\n'


def write(out, text):
    open(os.path.join(P, out), 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote', out)


# ---------- document pages (cookies) ----------
DOCS = [
    ('pils-cookies.html', 'pils', 'MINT PILs – Cookies', 'Cookies', 'cookies_content.html'),
    ('consent-cookies.html', 'consent', 'MINT CONSENT – Cookies', 'Cookies', 'cookies_content.html'),
]
ds, dbig = resized('b939e3018b', (720, 1280), 'hero-doc')
for out, prod, title, h1, partial in DOCS:
    content = open(os.path.join(S, partial), encoding='utf-8').read()
    pre = f'<link rel="preload" as="image" href="{dbig}" imagesrcset="{ds}" imagesizes="(max-width: 767px) 100vw, 50vw">'
    alt = 'A doctor holding a phone showing a confirmed MINT %s, with a colleague greeting a patient behind him' % ('PIL' if prod == 'pils' else 'consent')
    main = f'''<main class="doc" id="main" tabindex="-1">
  <section class="doc-hero">
    <div class="doc-wrap">
      <div>
        <img class="doc-hero-logo" src="assets/img/logo-{prod}-white.svg" alt="{NAME[prod]}" width="186" height="82">
        <h1>{esc(h1)}</h1>
        <p class="doc-hero-sub">Data Protection Policy</p>
        <nav class="doc-crumb" aria-label="Breadcrumb"><ol><li><a href="{prod}.html">Home</a></li><li><span aria-current="page">{esc(h1)}</span></li></ol></nav>
      </div>
      <img class="doc-hero-img" src="{dbig}" srcset="{ds}" sizes="(max-width: 767px) 100vw, 50vw" alt="{esc(alt)}" width="1280" height="956" fetchpriority="high">
    </div>
  </section>
{content}</main>
'''
    write(out, head(title, pre) + main + tail(prod, out))


# ---------- product home pages ----------
HOMES = [
    ('pils.html', 'pils', 'MINT PILs', dict(
        img='8e6c824a8c', alt='A doctor talking a patient through her treatment',
        lines=['Medical Information', 'Notable and Trusted'], hl='MINT PILs',
        text='Our interactive MINT PILs were created with the idea of empowering patients with the knowledge they need to take control of their treatment. '
             'They discuss general issues in health as well as specific health problems in a simple, yet comprehensive manner, without losing touch with the culture and society the patient is in.'),
     [
        dict(tone='navy', img='ece03e7fe6', alt='A tablet showing an interactive MINT PIL', h='MINT PILs', sub='is one of the services provided by AMPM Training Ltd.',
             text='AMPM Training was established with a vision of improving healthcare provision through enhancing communication. It operates under a team with over 25 years of experience '
                  'in healthcare delivery and training medical staff. We aspire to a healthcare culture based on transparency and communication that develops mutual trust and understanding.'),
        dict(tone='teal', img='b3918e43d2', alt='A clinician reviewing patient information on a laptop', h='MINT PILs',
             text='Our MINT PILs division is involved in patient edification, which we believe goes beyond patient education into a more spiritual level of enlightenment. '
                  'This is important for a holistic form of healing. We have designed our MINT PILs to be visual to capture the social issues and feelings, as well as added interactivity '
                  'to enhance the user experience. The acronym stands for Medical Information Notable and Trusted. Accordingly, our information is based on the requirements of the community '
                  'and is based on the latest guidance and is all referenced. We are working with PIF Tick, “The UK’s quality mark for trusted health information”, to ensure our leaflets '
                  'are produced using a professional and structured process.'),
     ]),
    ('consent.html', 'consent', 'MINT CONSENT', dict(
        img='2a2e37ab46', alt='A doctor in a modern clinic',
        lines=['Clear information', 'Informed decisions'], hl='MINT CONSENT',
        text='MINT CONSENT is a digital consent platform. It transforms the informed consent process by providing patients with clear, accessible information '
             'before they agree to a medical procedure or treatment.'),
     [
        dict(tone='navy', img='ba5f7735ff', alt='A doctor going through procedure information with a patient', h='MINT CONSENT',
             text='Instead of relying solely on a single consultation, patients can review procedure information, benefits, risks, alternatives, and aftercare instructions at their own pace, '
                  'from home or on their mobile device. This empowers patients and allows them to arrive at decisions confidently and at their own pace.'),
        dict(tone='teal', img='3972c53769', alt='A clinician using MINT CONSENT in a modern clinic', h='MINT CONSENT',
             text='For healthcare professionals, MINT CONSENT supports more consistent and structured communication with patients. Standardised procedure information helps ensure that key topics '
                  'are discussed while allowing clinicians to personalise conversations according to each patient’s individual circumstances. Digital consent platforms can also document when '
                  'information has been provided, when consent forms have been completed, and any questions or concerns raised by the patient, creating a clear record that supports good clinical '
                  'practice and shared decision-making.'),
        dict(tone='navy', img='dc6a663cea', alt='The MINT CONSENT platform on screen', h='MINT CONSENT',
             text='For hospitals and healthcare organisations, MINT CONSENT offers an opportunity to improve efficiency, standardisation and governance across multiple departments and sites. '
                  'MINT CONSENT and MINT PILs (patient information leaflets) can be centrally managed, updated and distributed, helping to ensure patients receive consistent, high-quality information.'),
     ]),
]

CONTACT = '''<section class="contact" data-anchor="contact" aria-labelledby="contact-h">
  <div class="doc-wrap">
    <div class="contact-box">
      <div>
        <p class="contact-kicker">GET IN TOUCH</p>
        <h2 id="contact-h">Fill in the form to <span>Contact us directly</span></h2>
        <form class="cf" action="#" method="post">
          <label>First Name<input name="first" autocomplete="given-name" placeholder="First Name" required></label>
          <label>Last Name<input name="last" autocomplete="family-name" placeholder="Last Name" required></label>
          <label class="full">Email<input type="email" name="email" autocomplete="email" placeholder="Email" required></label>
          <label class="full">Telephone<input type="tel" name="tel" autocomplete="tel" placeholder="Telephone"></label>
          <label class="full">Your Message<textarea name="message" placeholder="Your Message" required></textarea></label>
          <button type="submit">Send</button>
          <p class="cf-ok" role="status" hidden>Thank you, we have your message and will get back to you soon.</p>
        </form>
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

for out, prod, title, hero, feats in HOMES:
    hs, hbig = resized(hero['img'], (960, 1600, 2400))
    pre = f'<link rel="preload" as="image" href="{hbig}" imagesrcset="{hs}" imagesizes="100vw">'
    h1 = ''.join('<span>%s</span>' % esc(l) for l in hero['lines']) + '<span class="hl">%s</span>' % esc(hero['hl'])
    parts = [f'''<main class="doc" id="main" tabindex="-1">
<section class="home-hero">
  <img src="{hbig}" srcset="{hs}" sizes="100vw" alt="{esc(hero['alt'])}" width="2400" height="1792" fetchpriority="high">
  <div>
    <h1>{h1}</h1>
    <p>{esc(hero['text'])}</p>
  </div>
</section>
''']
    for i, f in enumerate(feats):
        fs, fbig = resized(f['img'], (720, 1200))
        cls = 'feat' + (' feat-teal' if f['tone'] == 'teal' else '') + (' feat-rev' if i % 2 else '')
        sub = f'<p class="feat-sub">{esc(f["sub"])}</p>' if f.get('sub') else ''
        parts.append(f'''<section class="{cls}">
  <div class="doc-wrap">
    <div class="feat-card"><h2>{esc(f['h'])}</h2>{sub}<p>{esc(f['text'])}</p></div>
    <img class="feat-img" src="{fbig}" srcset="{fs}" sizes="(max-width: 767px) 100vw, 56vw" alt="{esc(f['alt'])}" width="1200" height="896" loading="lazy" decoding="async">
  </div>
</section>
''')
    parts.append(CONTACT + '</main>\n')
    write(out, head(title, pre) + ''.join(parts) + tail(prod, out))


# ---------- guides ----------
THUMB = 'assets/v2/crop-9fc5176411.jpg'
GUIDES = [
    ('pils-guide.html', 'pils', 'MINT PILs – Guides', 'b09a4483d0', 'A clinician using the MINT platform', [
        ('How to register for a clinic account?',
         'You can now register individual clinic accounts as opposed to a full institute account. These accounts allow you to send '
         'educational content to your patients, unrelated to institutional accounts.', THUMB),
        ('How to use your clinic or professional account on MINT PILs?',
         'The MINT Platform allows you to access MINT Patient Information Leaflets in your clinic and send them to your patients. '
         'The following video shows how to use your account to educate patients, set your favourites and send MINT PILs to your patients.', THUMB),
        ('How to add a Brand Engagement Message to your account?',
         'When you use the MINT Platform to send patient information material, you can send a small reminder to your patients with your name, '
         'qualifications and contact details. Patients will know and remember the doctor that cares. The following video will show you how to '
         'create a Brand Engagement Message with the MINT Team.', THUMB),
    ]),
    ('consent-guide.html', 'consent', 'MINT CONSENT – Guides', 'da7ded2ff4', 'A clinician using MINT CONSENT', [
        ('Why choose MINT CONSENT?',
         'You can now register individual clinic accounts as opposed to a full institute account. These accounts allow you to send '
         'educational content to your patients, unrelated to institutional accounts. The following video shows how to register.', THUMB),
        ('How do I register on MINT CONSENT?',
         'Contact us by using the <a href="consent.html" data-section="contact">contact form</a> or by email on '
         '<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a>.', None),
    ]),
]
for out, prod, title, img, alt, items in GUIDES:
    safe = [(q, a if '<a ' in a else esc(a), t) for q, a, t in items]
    pre, hero = doc_hero(prod, 'Guides', img, alt)
    main = ('<main class="doc" id="main" tabindex="-1">\n' + hero +
            '<section class="acc-sec" aria-label="Guides">\n<div class="doc-wrap">\n' + accordion(safe, prod + '-g') + '</div>\n</section>\n</main>\n')
    write(out, head(title, pre) + main + tail(prod, out, js=True))


# ---------- pricing ----------
CTY = [('uk', 'United Kingdom'), ('ksa', 'Saudi Arabia'), ('eg', 'Egypt')]


def country_form():
    opts = ''.join(f'<label class="cty-opt"><input type="radio" name="country" value="{v}"><span class="flag f-{v}" aria-hidden="true"></span>{n}</label>'
                   for v, n in CTY)
    return f'''    <p class="price-lead">For clinics, please select your country to continue to the relevant page.</p>
    <form class="cty-form" action="contact.html" method="get">
      <fieldset><legend>Select your country</legend><div class="cty-opts">{opts}</div></fieldset>
      <p class="cty-msg" role="alert"></p>
      <button class="cty-go" type="submit">Continue</button>
    </form>
'''


PRICING = [
    ('pils-pricing.html', 'pils', 'MINT PILs – Pricing', '407c55b7b4', 'A clinician with a patient in a modern clinic', True),
    ('consent-pricing.html', 'consent', 'MINT CONSENT – Pricing', '2a2e37ab46', 'A doctor in a modern clinic', False),
]
for out, prod, title, img, alt, clinics in PRICING:
    pre, hero = doc_hero(prod, 'Pricing', img, alt)
    note = (f'<p class="price-note">For hospitals and medical institutes, please contact us on our email '
            f'<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a> or use the '
            f'<a href="{out}" data-section="contact">form below</a>. We will tailor a quote based on your needs.</p>\n')
    main = ('<main class="doc" id="main" tabindex="-1">\n' + hero +
            '<section class="price-sec" aria-label="Pricing">\n  <div class="doc-wrap">\n' + (country_form() if clinics else '') +
            '    ' + note + '  </div>\n</section>\n' + CONTACT + '</main>\n')
    write(out, head(title, pre) + main + tail(prod, out, js=True))
