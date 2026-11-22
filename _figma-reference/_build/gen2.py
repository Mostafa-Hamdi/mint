# Figma SVG frames -> static HTML pages (MINT CONSENT / MINT PILs sub-sites)
# usage: python -I gen2.py <svgdir> <projectdir> [page ...]
import sys, os, re, io, copy, base64, hashlib, html, json
import xml.etree.ElementTree as ET
from PIL import Image

SVGDIR, PROJ = sys.argv[1], sys.argv[2]
ONLY = set(sys.argv[3:])
NS = 'http://www.w3.org/2000/svg'; XLN = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', NS); ET.register_namespace('xlink', XLN)
N = '{%s}' % NS; XL = '{%s}href' % XLN

PAGES = [
  # out, title, product, (desktop, tablet, phone)
  ('consent.html', 'MINT CONSENT', 'consent', ('MintCONSENT1440', 'MintCONSENT991', 'MintCONSENT430')),
  ('consent-guide.html', 'MINT CONSENT – Guides', 'consent', ('MINTconsentGuide1440', 'MINTConsentGuide_991', 'MINTConsentGuide_430')),
  ('consent-pricing.html', 'MINT CONSENT – Pricing', 'consent', ('MINTConsentPricing1440', 'MINTConsentPricing_991', 'MINTconsentPricing_430')),
  ('consent-piftick.html', 'MINT CONSENT – PIF TICK', 'consent', ('MINTconsentpiftick1440', 'MINTConsentpiftick991', 'MINTconsentpiftick430')),
  ('consent-cookies.html', 'MINT CONSENT – Cookies', 'consent', ('MINTconsentcookie1440', 'MINTconsentcookies991', 'MINTconsentcookies430')),
  ('pils.html', 'MINT PILs', 'pils', ('MintPILS_1440', 'MintPILS_991', 'MintPILS_430')),
  ('pils-guide.html', 'MINT PILs – Guides', 'pils', ('MINTPILSGuide1440', 'MINTPILSGuide_991', 'MINTPILSGuide_430')),
  ('pils-pricing.html', 'MINT PILs – Pricing', 'pils', ('MINTPILSPricing1440', 'MINTPILSPricing_991', 'MINTPILSPricing_430')),
  ('pils-piftick.html', 'MINT PILs – PIF TICK', 'pils', ('MINTPILPIFTICK1440', 'MINTPilspiftick991', 'MINTINPillspiftick430')),
  ('pils-cookies.html', 'MINT PILs – Cookies', 'pils', ('MINTPILCookies1440', 'MINTPilscookies991', 'MINTPilscookies430')),
  ('pils-legal.html', 'MINT PILs – Legal', 'pils', ('MINTPILSlegal1440', 'MINTPILsLegal_991', 'MINTPILsLegal_430')),
]

# font metrics (hhea ascender / descender, em units)
METRICS = {'Poppins': (1.05, .35), 'Montserrat': (.968, .251), 'Inter': (.96875, .2421875)}

def links(prod):
    p = 'consent' if prod == 'consent' else 'pils'
    legal = 'pils-legal.html'
    return {
        'Home': p + '.html', 'About': 'about.html', 'About Us': 'about.html', 'Guide': p + '-guide.html',
        'Contact Us': p + '.html#contact', 'Pricing': p + '-pricing.html', 'About AMPM': 'about.html',
        'Tutorials and Guides': p + '-guide.html', 'Cookies': p + '-cookies.html', 'PIFTICK': p + '-piftick.html',
        'MINTFORMED': 'index.html', 'Privacy Policy': legal, 'Terms and Conditions': legal, 'FAQ’s': p + '-guide.html',
        'Refunds Policy': legal, 'Copyright Information': legal, 'Log in': '#', 'More Info': p + '-guide.html',
        'info@ampmtraining.com': 'mailto:info@ampmtraining.com', 'www.pifttick.org.uk': 'https://piftick.org.uk',
        'www.piftick.org.uk': 'https://piftick.org.uk', 'MINT CONSENT': None, 'MINT PILs': None,
    }

def fx(t):
    try: return t.encode('latin1').decode('utf8')
    except Exception: return t

def num(v, d=0.0):
    try: return float(re.sub('[a-z%]+$', '', v))
    except Exception: return d

IMG_OUT = os.path.join(PROJ, 'assets', 'v2')
os.makedirs(IMG_OUT, exist_ok=True)

def save_image(data):
    h = hashlib.md5(data).hexdigest()[:10]
    im = Image.open(io.BytesIO(data))
    alpha = im.mode in ('RGBA', 'LA', 'P') and im.convert('RGBA').getextrema()[3][0] < 255
    if max(im.size) > 2400:
        s = 2400 / max(im.size); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    if alpha:
        fn = h + '.png'; p = os.path.join(IMG_OUT, fn)
        if not os.path.exists(p): im.convert('RGBA').save(p, optimize=True)
    else:
        fn = h + '.jpg'; p = os.path.join(IMG_OUT, fn)
        if not os.path.exists(p): im.convert('RGB').save(p, quality=82, optimize=True, progressive=True)
    return fn

def paint_color(v, defs):
    if not v: return None
    m = re.match(r'url\(#(.*)\)', v)
    if m:
        g = defs.get(m.group(1))
        stops = [s.get('stop-color', '#000') for s in g.iter(N + 'stop')] if g is not None else []
        return stops[-1] if stops else '#000'
    return v

def frame(name, prod, bp):
    path = os.path.join(SVGDIR, name + '.svg')
    tree = ET.parse(path); root = tree.getroot()
    W, H = num(root.get('width')), num(root.get('height'))
    defs = {e.get('id'): e for e in root.iter() if e.get('id')}
    parent = {c: p for p in root.iter() for c in p}
    # images -> files
    for im in root.iter(N + 'image'):
        h = im.get(XL) or im.get('href') or ''
        m = re.match(r'data:image/\w+;base64,(.*)', h, re.S)
        if m:
            fn = save_image(base64.b64decode(m.group(1)))
            for k in (XL, 'href'):
                if k in im.attrib: del im.attrib[k]
            im.set(XL, '../v2/' + fn)
    # collect stroke boxes (inputs) and filled rects (buttons)
    rects = []
    for r in root.iter(N + 'rect'):
        if r.get('width') and r.get('height'):
            x, y = num(r.get('x', '0')), num(r.get('y', '0'))
            tr = r.get('transform', '')
            mt = re.match(r'translate\(([-\d.]+)(?:[ ,]([-\d.]+))?\)', tr)
            if mt: x += float(mt.group(1)); y += float(mt.group(2) or 0)
            elif tr: continue
            rects.append((x, y, num(r.get('width')), num(r.get('height')), r.get('fill'), r.get('stroke'), num(r.get('rx', '0'))))
    texts = []
    for t in list(root.iter(N + 'text')):
        anc = parent.get(t); bad = False
        while anc is not None:
            if anc.get('transform'): bad = True
            anc = parent.get(anc)
        texts.append((t, bad))
    # strip texts from decor
    for t, _ in texts:
        parent[t].remove(t)
    for e in root.iter():
        if e.get('id') and e.tag not in (N + 'clipPath', N + 'linearGradient', N + 'radialGradient', N + 'pattern', N + 'image', N + 'filter', N + 'mask'):
            del e.attrib['id']
    svg_rel = f'assets/svg/{name}.svg'
    os.makedirs(os.path.join(PROJ, 'assets', 'svg'), exist_ok=True)
    data = ET.tostring(root, encoding='unicode')
    open(os.path.join(PROJ, svg_rel), 'w', encoding='utf-8').write(data)

    L = links(prod)
    out = []; inputs = []
    def inside(px, py, r, pad=2):
        return r[0] - pad <= px <= r[0] + r[2] + pad and r[1] - pad <= py <= r[1] + r[3] + pad
    for t, bad in texts:
        fam = (t.get('font-family') or 'Poppins').split(',')[0].strip("'\" ")
        fs = num(t.get('font-size', '16')); fw = t.get('font-weight', '400')
        fw = {'bold': '700', 'normal': '400'}.get(fw, fw)
        fill = paint_color(t.get('fill'), defs) or '#000'
        ls = t.get('letter-spacing', '0')
        lsv = num(ls) * (fs if ls.endswith('em') else 1)
        asc, desc = METRICS.get(fam, (1.0, .25))
        spans = list(t.iter(N + 'tspan'))
        lines = {}
        for s in spans:
            y = round(num(s.get('y')), 2)
            lines.setdefault(y, []).append(s)
        full = fx(' '.join(''.join(s.text or '' for s in v) for v in lines.values())).strip()
        if not full: continue
        if bad: print('  ! transformed text skipped:', full[:40], file=sys.stderr); continue
        first = spans[0]; fx0, fy0 = num(first.get('x')), num(first.get('y'))
        # placeholder -> input
        if fill.upper() == '#95A5A4' and fw == '400':
            box = next((r for r in rects if r[5] and r[5].upper() == '#95A5A4' and inside(fx0, fy0, r)), None)
            if box:
                tag = 'textarea' if 'Message' in full else 'input'
                typ = '' if tag == 'textarea' else ' type="%s"' % ('email' if 'mail' in full.lower() else 'tel' if 'phone' in full.lower() else 'text')
                st = f'--x:{box[0]:.1f};--y:{box[1]:.1f};--w:{box[2]:.1f};--h:{box[3]:.1f};--f:{fs:g};--pl:{fx0 - box[0]:.1f}'
                el = f'<{tag} class="fi"{typ} style="{st}" placeholder="{html.escape(full)}" aria-label="{html.escape(full)}"' + ('></textarea>' if tag == 'textarea' else '>')
                inputs.append(el); continue
        style = f"font:{fw} calc({fs:g}*var(--u))/{asc + desc:.4f} {fam},sans-serif;color:{fill}"
        if lsv: style += f";letter-spacing:calc({lsv:.3f}*var(--u))"
        line_html = []
        for y, ss in lines.items():
            x0 = num(ss[0].get('x'))
            inner = ''
            for s in ss:
                txt = html.escape(fx(s.text or '').rstrip('\n'))
                sst = []
                if s.get('font-weight'): sst.append('font-weight:' + {'bold': '700'}.get(s.get('font-weight'), s.get('font-weight')))
                if s.get('fill'): sst.append('color:' + (paint_color(s.get('fill'), defs) or fill))
                if s.get('font-size'): sst.append(f"font-size:calc({num(s.get('font-size')):g}*var(--u))")
                inner += f'<span style="{";".join(sst)}">{txt}</span>' if sst else txt
            line_html.append(f'<span class="ln" style="--x:{x0:.2f};--y:{y - asc * fs:.2f}">{inner}</span>')
        body = ''.join(line_html)
        key = full.rstrip(' :')
        href = L.get(key)
        if href and href.startswith(PAGE_FILE + '#'): href = href[len(PAGE_FILE):]
        if href is not None or key in ('Send', 'Continue'):
            box = None
            cand = [r for r in rects if inside(fx0 + 2, fy0 - fs * .3, r, 0) and r[2] < 700 and r[3] < 120 and (r[4] not in (None, 'none') or r[5])]
            if cand: box = min(cand, key=lambda r: r[2] * r[3])
            if key in ('Send', 'Continue'):
                hit = f'<button class="hit" type="submit" style="--x:{box[0]:.1f};--y:{box[1]:.1f};--w:{box[2]:.1f};--h:{box[3]:.1f};--r:{box[6]:g}" aria-label="{key}"></button>' if box else ''
                out.append(f'<p class="tx" aria-hidden="true" style="{style}">{body}</p>{hit}' if box else f'<p class="tx" style="{style}">{body}</p>')
            elif box:
                out.append(f'<p class="tx" aria-hidden="true" style="{style}">{body}</p><a class="hit" href="{href}" style="--x:{box[0]:.1f};--y:{box[1]:.1f};--w:{box[2]:.1f};--h:{box[3]:.1f};--r:{box[6]:g}">{html.escape(key)}</a>')
            else:
                cur = ' aria-current="page"' if href == PAGE_FILE else ''
                tone = ' lk-on-dark' if fill.lower() in ('white', '#fff', '#ffffff') or fill.upper() == '#EAFAF5' else ''
                out.append(f'<a class="tx lk{tone}" href="{href}"{cur} style="{style}">{body}</a>')
            continue
        if key == 'GET IN TOUCH':
            out.append(f'<span class="anchor" data-anchor="contact" style="--y:{fy0 - 140:.1f}"></span>')
        tag = 'h1' if fs >= 56 and not any('<h1' in o for o in out) else 'h2' if fs >= 34 else 'h3' if fs >= 26 else 'p'
        out.append(f'<{tag} class="tx" style="{style}">{body}</{tag}>')
    form = ''
    if inputs:
        form = '<form class="ff" action="#" method="post" onsubmit="return false">' + ''.join(inputs) + '</form>'
        # move the Send button inside the form
        out = [o.replace('<button class="hit"', '<button form="f-' + bp + '" class="hit"') for o in out]
        form = form.replace('<form class="ff"', f'<form id="f-{bp}" class="ff"')
    return W, H, svg_rel, '\n'.join(out) + '\n' + form

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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="css/v2.css" rel="stylesheet">
  <link href="css/ui.css" rel="stylesheet">
</head>
<body>
<div class="page v2 pg-{slug}">
'''
FOOT = '''</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="js/v2.js"></script>
<script src="js/ui.js"></script>
</body>
</html>
'''

for out, title, prod, names in PAGES:
    slug = out[:-5]
    PAGE_FILE = out
    if ONLY and slug not in ONLY: continue
    parts = []
    L = links(prod)
    for bp, name in zip(('d', 't', 'm'), names):
        if name is None: continue
        if not os.path.exists(os.path.join(SVGDIR, name + '.svg')):
            print('missing', name, file=sys.stderr); continue
        W, H, rel, body = frame(name, prod, bp)
        home = L['Home']
        lb = {'d': (60, 10, 240, 78), 't': (40, 10, 225, 78), 'm': (60, 6, 180, 86)}[bp]
        logo = f'<a class="hit hit-logo" href="{home}" style="--x:{lb[0]};--y:{lb[1]};--w:{lb[2]};--h:{lb[3]};--r:12" aria-label="{"MINT CONSENT" if prod == "consent" else "MINT PILs"} home"></a>'
        extra = ' fv-td' if (bp == 't' and names[0] is None) else ''
        menu = ''
        if bp == 'm':
            menu = ('<button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mnav"></button>'
                    '<nav class="mnav" id="mnav" aria-label="Main">' + ''.join(f'<a href="{L[k]}">{k}</a>' for k in ('Home', 'About', 'Guide', 'Contact Us')) + '</nav>\n')
        parts.append(f'<section class="fv fv-{bp}{extra}" style="--W:{W:g};--H:{H:g}" aria-label="{html.escape(title)}">\n'
                     f'<object class="decor" type="image/svg+xml" data="{rel}" tabindex="-1" aria-hidden="true"></object>\n{logo}{menu}{body}\n</section>\n')
    p_ = 'consent' if prod == 'consent' else 'pils'
    cfg = {'name': 'MINT CONSENT' if prod == 'consent' else 'MINT PILs', 'logo': f'assets/img/logo-{p_}.svg', 'home': p_ + '.html',
           'links': [{'label': 'Home', 'href': p_ + '.html'}, {'label': 'About', 'href': 'about.html'}, {'label': 'Guide', 'href': p_ + '-guide.html'},
                     {'label': 'Pricing', 'href': p_ + '-pricing.html'}, {'label': 'Contact Us', 'href': p_ + '.html#contact'}],
           'tabs': [{'label': 'Home', 'href': p_ + '.html', 'icon': 'home'}, {'label': 'Guide', 'href': p_ + '-guide.html', 'icon': 'book'},
                    {'label': 'Pricing', 'href': p_ + '-pricing.html', 'icon': 'tag'}, {'label': 'About', 'href': 'about.html', 'icon': 'info'},
                    {'label': 'Contact', 'href': p_ + '.html#contact', 'icon': 'mail'}]}
    foot = FOOT.replace('<script src="js/ui.js"></script>', '<script type="application/json" id="sticky-cfg">' + json.dumps(cfg) + '</script>\n<script src="js/ui.js"></script>')
    open(os.path.join(PROJ, out), 'w', encoding='utf-8').write(HEAD.format(title=html.escape(title), slug=slug) + ''.join(parts) + foot)
    print('wrote', out)
