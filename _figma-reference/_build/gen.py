# Assembles the static pages from shared header/footer + per-page body fragments.
import os, sys
S = os.path.dirname(os.path.abspath(__file__))
OUT = r'C:\Users\Mosta\OneDrive\Desktop\flow\mint-pils'

HEAD = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="theme-color" content="#3A495B">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <link href="css/style.css" rel="stylesheet">
  <link href="css/ui.css" rel="stylesheet">
</head>
<body>
<div class="page pg-{pg}">
'''

def header(active, h92):
    def a(key):
        return ' class="active"' if key == active else ''
    return f'''
  <!-- ============================== HEADER ============================== -->
  <header class="site-header{' h92' if h92 else ''}">
    <div class="frame">
      <a class="hdr-logo abs" href="index.html" aria-label="MINTFORMED home"><img src="assets/img/logo.svg" alt="MINTFORMED"></a>
      <button class="hdr-burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
      <div class="hdr-menu">
        <ul class="hdr-nav" id="site-nav">
          <li class="nav-home"><a{a('home')} href="index.html">Home</a></li>
          <li class="nav-products">
            <button class="nav-trigger" type="button" aria-expanded="false" aria-controls="mega">Products <i class="bi bi-chevron-down"></i></button>
            <div class="mega" id="mega">
              <p class="mega-kicker">Our products</p>
              <a class="mega-item" href="consent.html">
                <span class="mi-logo"><img src="assets/img/logo-consent.svg" alt=""></span>
                <span class="mi-txt"><b>MINT CONSENT</b><small>Digital consent, explained in clear language.</small></span>
                <i class="bi bi-arrow-right mi-go"></i>
              </a>
              <a class="mega-item" href="pils.html">
                <span class="mi-logo"><img src="assets/img/logo-pils.svg" alt=""></span>
                <span class="mi-txt"><b>MINT PILs</b><small>Illustrated, interactive patient leaflets.</small></span>
                <i class="bi bi-arrow-right mi-go"></i>
              </a>
              <span class="mega-item is-soon" aria-disabled="true">
                <span class="mi-logo mi-family"><i class="bi bi-people"></i></span>
                <span class="mi-txt"><b>MINT FAMILY</b><small>The family health app.</small></span>
                <em class="mi-pill">Coming soon</em>
              </span>
            </div>
          </li>
          <li class="nav-about"><a{a('about')} href="about.html">About Us</a></li>
          <li class="nav-contact"><a{a('contact')} href="contact.html">Contact Us</a></li>
        </ul>
        <a class="btn-login hdr-login abs" href="#"><img src="assets/img/icon-login.svg" alt="">Log in</a>
      </div>
    </div>
  </header>
'''

FOOTER = '''
  <!-- ============================== FOOTER ============================== -->
  <footer class="site-footer{fcls}">
    <div class="frame">
      <a class="ft-logo abs" href="index.html"><img src="assets/img/logo-white.svg" alt="MINTFORMED"></a>
      <p class="ft-tag abs">Be Informed With MINTFORMED</p>
      <div class="ft-block">
        <span class="ft-ico ft-loc-ico abs"><img src="assets/img/icon-location.svg" alt=""></span>
        <div>
          <p class="ft-h ft-addr-h abs">Our Address</p>
          <p class="ft-txt ft-addr abs">9 High Street,Wellington,<br>Somerset, UKTA21 8QT</p>
        </div>
      </div>
      <div class="ft-block">
        <span class="ft-ico ft-mail-ico abs"><img src="assets/img/icon-send.svg" alt=""></span>
        <div>
          <p class="ft-h ft-cont-h abs">Contact us</p>
          <p class="ft-txt ft-mail abs"><a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a></p>
        </div>
      </div>
      <p class="ft-copy abs">© 2026| All Rights Reserved | Powered by AMPM Training</p>
      <div class="ft-social">
        <a class="s-x" href="#" aria-label="X"><svg viewBox="0 0 36.28 32.78" aria-hidden="true"><path d="M22.6156 13.513L35.1418 0H30.3783L20.5426 10.6102L13.0114 0H0L13.1768 18.5623L0 32.7759H4.76351L15.2388 21.465L23.2662 32.7759H36.2776L22.6046 13.5241L22.6156 13.513ZM6.71521 3.46999H11.2472L29.5734 29.2948H25.0415L6.71521 3.46999Z"/></svg></a>
        <a class="s-in" href="#" aria-label="LinkedIn"><svg viewBox="76.27 0.96 29.94 30.86" aria-hidden="true"><path d="M80.269 9.0131C82.4735 9.0131 84.2606 7.21057 84.2606 4.98702C84.2606 2.76347 82.4735 0.960938 80.269 0.960938C78.0645 0.960938 76.2773 2.76347 76.2773 4.98702C76.2773 7.21057 78.0645 9.0131 80.269 9.0131Z"/><path d="M83.3005 11.6953H77.2469C77.0825 11.6953 76.9492 11.8297 76.9492 11.9956V31.5144C76.9492 31.6802 77.0825 31.8146 77.2469 31.8146H83.3005C83.465 31.8146 83.5983 31.6802 83.5983 31.5144V11.9956C83.5983 11.8297 83.465 11.6953 83.3005 11.6953Z"/><path d="M106.204 19.0678V30.4676C106.204 31.2017 105.609 31.8134 104.87 31.8134H100.878C100.151 31.8134 99.5442 31.2128 99.5442 30.4676V21.0808C99.5442 19.2346 98.0556 17.7332 96.2252 17.7332C94.3948 17.7332 92.9062 19.2346 92.9062 21.0808V30.4676C92.9062 31.2017 92.3107 31.8134 91.5719 31.8134H87.5803C86.8525 31.8134 86.2461 31.2128 86.2461 30.4676V13.0287C86.2461 12.2946 86.8415 11.6829 87.5803 11.6829H91.5719C92.2997 11.6829 92.9062 12.2835 92.9062 13.0287V13.885C94.2404 12.15 96.4347 11.0156 98.8936 11.0156C102.565 11.0156 106.204 13.696 106.204 19.0678Z"/></svg></a>
        <a class="s-yt" href="#" aria-label="YouTube"><svg viewBox="146.2 3.15 36.25 26.48" aria-hidden="true"><path d="M177.675 3.15625H150.98C148.344 3.15625 146.205 5.3139 146.205 7.972V24.8104C146.205 27.4685 148.344 29.6261 150.98 29.6261H177.675C180.31 29.6261 182.45 27.4685 182.45 24.8104V7.972C182.45 5.3139 180.31 3.15625 177.675 3.15625ZM168.622 17.559L161.201 21.2959C160.341 21.7296 159.338 21.0957 159.338 20.1392V12.6543C159.338 11.6867 160.341 11.0638 161.201 11.4976L168.622 15.2456C169.57 15.7239 169.57 17.0918 168.622 17.5701V17.559Z"/></svg></a>
      </div>
      <nav class="ft-links" aria-label="Footer">
        <a class="l1" href="about.html">About Us</a><span class="bar b1"></span>
        <a class="l2" href="pils-legal.html" data-section="terms">Terms and Conditions</a><span class="bar b2"></span>
        <a class="l3" href="piftick.html">PIFTICK</a><span class="bar b3"></span>
        <a class="l4" href="cookies.html">Cookies</a><span class="bar b4"></span>
        <a class="l5" href="contact.html">Contact Us</a>
      </nav>
      <p class="ft-accr abs">Accredited by</p>
      <span class="ft-badge abs"><img src="assets/img/pif-badge-white.svg" alt="Trusted Information Creator – Patient Information Forum"></span>
    </div>
  </footer>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="js/main.js"></script>
<script type="application/json" id="sticky-cfg">{"name": "MINTFORMED", "logo": "assets/img/logo.svg", "home": "index.html", "links": [{"label": "Home", "href": "index.html"}, {"label": "Products", "menu": [{"label": "MINT CONSENT", "href": "consent.html", "logo": "assets/img/logo-consent.svg", "note": "Digital consent, explained in clear language."}, {"label": "MINT PILs", "href": "pils.html", "logo": "assets/img/logo-pils.svg", "note": "Illustrated, interactive patient leaflets."}]}, {"label": "About Us", "href": "about.html"}, {"label": "Contact Us", "href": "contact.html"}], "tabs": [{"label": "Home", "href": "index.html", "icon": "home"}, {"label": "Products", "icon": "grid", "sheet": [{"label": "MINT CONSENT", "href": "consent.html", "logo": "assets/img/logo-consent.svg", "note": "Digital consent, explained clearly"}, {"label": "MINT PILs", "href": "pils.html", "logo": "assets/img/logo-pils.svg", "note": "Illustrated, interactive leaflets"}]}, {"label": "About", "href": "about.html", "icon": "info"}, {"label": "Contact", "href": "contact.html", "icon": "mail"}]}</script>
<script src="js/ui.js"></script>
</body>
</html>
'''

PAGES = {
    'index.html':   ('MINTFORMED – Be Informed With MINTFORMED', 'home', False, 'body_home.html'),
    'about.html':   ('About AMPM Training – MINTFORMED', 'about', True, 'body_about.html'),
    'contact.html': ('Contact Us – MINTFORMED', 'contact', False, 'body_contact.html'),
    'cookies.html': ('Cookies – Data Protection Policy – MINTFORMED', 'contact', True, 'body_cookies.html'),
    'piftick.html': ('AMPM Training gains PIF TICK accreditation – MINTFORMED', 'contact', True, 'body_piftick.html'),
}
only = sys.argv[1:]
for fn, (title, active, h92, body) in PAGES.items():
    if only and fn not in only: continue
    p = os.path.join(S, body)
    if not os.path.exists(p): continue
    html = HEAD.format(title=title, pg=fn.split('.')[0]) + header(active, h92) + open(p, encoding='utf-8').read() + FOOTER.replace('{fcls}', ' ft-c' if fn == 'contact.html' else '')
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(html)
    print('wrote', fn)
