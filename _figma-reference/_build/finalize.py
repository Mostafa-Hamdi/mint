# usage: python -I finalize.py <project>
# Last build step (after gen.py / bake.py / make_about.py). Safe to run again: it replaces what it added before.
#   SEO: description, canonical, Open Graph / Twitter, JSON-LD, robots.txt, sitemap.xml
#   a11y: skip link, a main landmark on every page, an h1 in every layout
#   perf / CSP: no Bootstrap JS bundle (unused), no inline handlers, lazy decor images
import os, re, sys, datetime

SITE = os.environ.get('MINT_SITE', 'https://mint-rdwd.vercel.app').rstrip('/')
ROOT = sys.argv[1]

DESC = {
    'index.html': 'MINTFORMED builds clear, trusted digital patient information: MINT CONSENT for digital consent and MINT PILs for patient information leaflets.',
    'about.html': 'About AMPM Training, the team behind MINTFORMED: accredited patient information, built with clinicians for clearer, safer care.',
    'contact.html': 'Contact MINTFORMED in the UK, Saudi Arabia or Egypt about MINT CONSENT and MINT PILs.',
    'cookies.html': 'How MINTFORMED uses cookies and protects your data.',
    'piftick.html': 'AMPM Training has gained the PIF TICK, the UK quality mark for trusted health information.',
    'consent.html': 'MINT CONSENT: digital, informed patient consent that is clear, recorded and easy for clinicians and patients.',
    'consent-guide.html': 'MINT CONSENT guides: step-by-step videos and answers to common questions.',
    'consent-pricing.html': 'MINT CONSENT pricing: choose your country and get a plan for your practice.',
    'consent-piftick.html': 'MINT CONSENT content is created under the PIF TICK quality mark for trusted health information.',
    'consent-cookies.html': 'How MINT CONSENT uses cookies and protects your data.',
    'consent-about.html': 'About AMPM Training, the team behind MINT CONSENT.',
    'pils.html': 'MINT PILs: digital patient information leaflets your patients can read, watch and keep, sent straight from your clinic.',
    'pils-guide.html': 'MINT PILs guides: step-by-step videos and answers to common questions.',
    'pils-pricing.html': 'MINT PILs pricing: choose your country and get a plan for your practice.',
    'pils-piftick.html': 'MINT PILs content is created under the PIF TICK quality mark for trusted health information.',
    'pils-cookies.html': 'How MINT PILs uses cookies and protects your data.',
    'pils-legal.html': 'MINT PILs legal: privacy policy, terms and conditions, refunds, FAQs and copyright.',
    'pils-about.html': 'About AMPM Training, the team behind MINT PILs.',
}
PRIORITY = {'index.html': '1.0', 'pils.html': '0.9', 'consent.html': '0.9'}

ORG = ('{"@context":"https://schema.org","@type":"Organization","name":"MINTFORMED","url":"%s/",'
       '"logo":"%s/assets/img/favicon.svg","brand":[{"@type":"Brand","name":"MINT CONSENT"},'
       '{"@type":"Brand","name":"MINT PILs"}]}') % (SITE, SITE)


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


def head_block(name, title):
    url = SITE + '/' + ('' if name == 'index.html' else name)
    site = 'MINT PILs' if name.startswith('pils') else 'MINT CONSENT' if name.startswith('consent') else 'MINTFORMED'
    d = esc(DESC[name])
    t = esc(title)
    return '\n'.join([
        '    <!-- seo -->',
        f'    <meta name="description" content="{d}" />',
        '    <meta name="robots" content="index, follow" />',
        f'    <link rel="canonical" href="{url}" />',
        '    <meta property="og:type" content="website" />',
        f'    <meta property="og:site_name" content="{site}" />',
        f'    <meta property="og:title" content="{t}" />',
        f'    <meta property="og:description" content="{d}" />',
        f'    <meta property="og:url" content="{url}" />',
        '    <meta name="twitter:card" content="summary" />',
        f'    <meta name="twitter:title" content="{t}" />',
        f'    <meta name="twitter:description" content="{d}" />',
        '    <meta name="format-detection" content="telephone=no" />',
        f'    <script type="application/ld+json">{ORG}</script>' if name == 'index.html' else '',
        '    <!-- /seo -->',
    ]).replace('\n\n', '\n')


def fix(name, h):
    title = re.search(r'<title>([^<]*)</title>', h).group(1)
    # SEO block (replaced on re-runs)
    h = re.sub(r'\s*<!-- seo -->.*?<!-- /seo -->', '', h, flags=re.S)
    h = h.replace('</title>\n', '</title>\n' + head_block(name, title) + '\n', 1)
    # Bootstrap JS is not used by any page
    h = re.sub(r'\s*<script\s+src="https://cdn\.jsdelivr\.net/npm/bootstrap@[^"]*bootstrap\.bundle\.min\.js"[^>]*>\s*</script>', '', h)
    # forms are handled in ui.js (no inline handlers, so the CSP needs no 'unsafe-inline' for scripts)
    h = re.sub(r'\s+onsubmit="return false;?"', '', h)
    # main landmark + skip link target
    if '<main' in h:
        h = re.sub(r'<main(?![^>]*id=)', '<main id="main" tabindex="-1"', h, count=1)
    else:
        h = re.sub(r'<div class="page (v2[^"]*)"(?! role)', r'<div class="page \1" role="main" id="main" tabindex="-1"', h, count=1)
    if 'class="skip"' not in h:
        h = h.replace('<body>', '<body>\n    <a class="skip" href="#main">Skip to content</a>', 1)
    # one h1 per layout: promote the first h2 where a layout has none
    def layout(m):
        s = m.group(0)
        if '<h1' in s:
            return s
        return re.sub(r'<h2(\b[^>]*)>(.*?)</h2>', r'<h1\1>\2</h1>', s, count=1, flags=re.S)
    h = re.sub(r'<section\s+class="fv fv-[dtm][^"]*".*?(?=<section\s+class="fv fv-|</div>\s*<script)', layout, h, flags=re.S)
    # decor in hidden layouts never downloads; visible decor decodes off the main thread
    h = re.sub(r'<img(?![^>]*loading=)(\s[^>]*class="decor)', r'<img loading="lazy" decoding="async"\1', h)
    return h


pages = sorted(f for f in os.listdir(ROOT) if f.endswith('.html') and not f.startswith('_'))
for name in pages:
    if name not in DESC:
        print('no description for', name); continue
    p = os.path.join(ROOT, name)
    src = open(p, encoding='utf-8').read()
    out = fix(name, src)
    if out != src:
        open(p, 'w', encoding='utf-8', newline='').write(out)
    print(name, 'h1:', out.count('<h1'))

today = datetime.date.today().isoformat()
urls = ''.join(
    f'  <url><loc>{SITE}/{"" if n == "index.html" else n}</loc><lastmod>{today}</lastmod>'
    f'<priority>{PRIORITY.get(n, "0.6")}</priority></url>\n' for n in pages if n in DESC)
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(
    f'User-agent: *\nAllow: /\nDisallow: /_figma-reference/\n\nSitemap: {SITE}/sitemap.xml\n')
