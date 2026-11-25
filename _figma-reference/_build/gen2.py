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

IMGRANGES = {}
PAGES = [
  # out, title, product, (desktop, tablet, phone)
  ('consent.html', 'MINT CONSENT', 'consent', ('MintCONSENT1440', 'MintCONSENT991', 'MintCONSENT430')),
  ('consent-guide.html', 'MINT CONSENT – Guides', 'consent', ('MINTconsentGuide1440', 'MINTConsentGuide_991', 'MINTConsentGuide_430')),
  ('consent-pricing.html', 'MINT CONSENT – Pricing', 'consent', ('MINTConsentPricing1440', 'MINTConsentPricing_991', 'MINTconsentPricing_430')),
  ('consent-piftick.html', 'MINT CONSENT – PIF TICK', 'consent', ('MINTconsentpiftick1440', 'MINTConsentpiftick991', 'MINTconsentpiftick430')),
  ('pils.html', 'MINT PILs', 'pils', ('MintPILS_1440', 'MintPILS_991', 'MintPILS_430')),
  ('pils-guide.html', 'MINT PILs – Guides', 'pils', ('MINTPILSGuide1440', 'MINTPILSGuide_991', 'MINTPILSGuide_430')),
  ('pils-pricing.html', 'MINT PILs – Pricing', 'pils', ('MINTPILSPricing1440', 'MINTPILSPricing_991', 'MINTPILSPricing_430')),
  ('pils-piftick.html', 'MINT PILs – PIF TICK', 'pils', ('MINTPILPIFTICK1440', 'MINTPilspiftick991', 'MINTINPillspiftick430')),
  ('pils-legal.html', 'MINT PILs – Legal', 'pils', ('MINTPILSlegal1440', None, 'MINTPILsLegal_430')),
]

# font metrics (hhea ascender / descender, em units)
METRICS = {'Poppins': (1.05, .35), 'Montserrat': (.968, .251), 'Inter': (.96875, .2421875)}

def links(prod):
    p = 'consent' if prod == 'consent' else 'pils'
    legal = 'pils-legal.html'
    return {
        'Home': p + '.html', 'About': p + '-about.html', 'About Us': p + '-about.html', 'Guide': p + '-guide.html',
        'Contact Us': (p + '.html', 'contact'), 'Pricing': p + '-pricing.html', 'About AMPM': p + '-about.html',
        'Tutorials and Guides': p + '-guide.html', 'Cookies': p + '-cookies.html', 'PIFTICK': p + '-piftick.html',
        'MINTFORMED': 'index.html', 'Privacy Policy': (legal, 'privacy'), 'Terms and Conditions': (legal, 'terms'),
        'FAQ’s': (legal, 'faq'), 'Refunds Policy': (legal, 'refunds'), 'Copyright Information': (legal, 'copyright'),
        'Log in': '#', 'More Info': p + '-guide.html',
        'info@ampmtraining.com': 'mailto:info@ampmtraining.com', 'www.pifttick.org.uk': 'https://piftick.org.uk',
        'www.piftick.org.uk': 'https://piftick.org.uk',
    }

LEGAL_HEADINGS = {'Terms and conditions': 'terms', 'Privacy Policy': 'privacy', 'FAQ': 'faq', 'Refunds Policy': 'refunds', 'Copyright Information': 'copyright'}
LEGAL_SIDE = {'Terms Of Use': 'terms', 'Privacy Policy': 'privacy', 'FAQ': 'faq', 'Refunds Policy': 'refunds', 'Copyrights Information': 'copyright'}

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
    hh = 97.0
    for g in root.iter(N + 'g'):
        if (g.get('id') or '').startswith('Header'):
            r = next(g.iter(N + 'rect'), None)
            if r is not None and r.get('height'): hh = num(r.get('height'))
            break
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
    # a thin white gap between the drawn header and the first full-width block is hidden along with the header
    nxt = [r[1] for r in rects if r[2] >= W * .95 and r[3] > 150 and hh < r[1] <= hh + 80 and (r[4] or '').lower() not in ('white', '#ffffff', '#fff')]
    if nxt: hh = min(nxt)
    # small teal stroke paths = the accordion chevrons/arrows drawn in the design
    chevs = []
    for pth in root.iter(N + 'path'):
        if (pth.get('stroke') or '').upper() != '#00A48F' or parent.get(pth) is None: continue
        nums = [float(v) for v in re.findall(r'-?\d*\.?\d+', pth.get('d', ''))]
        xs, ys_ = nums[0::2], nums[1::2]
        if xs and max(xs) - min(xs) < 30 and max(ys_) - min(ys_) < 30:
            chevs.append(((min(xs) + max(xs)) / 2, (min(ys_) + max(ys_)) / 2))
    texts = []
    for t in list(root.iter(N + 'text')):
        anc = parent.get(t); bad = False
        while anc is not None:
            if anc.get('transform'): bad = True
            anc = parent.get(anc)
        texts.append((t, bad))
    textparent = {id(t): parent[t] for t, _ in texts}
    # strip texts from decor
    for t, _ in texts:
        parent[t].remove(t)
    # Figma often splits one paragraph into two text layers in the same group: the regular words and the bold
    # words (e.g. "AMPM Training", "PIF TICK"), each placed on the same lines. Merge them back into one paragraph
    # with styled runs so it can be read and re-flowed as one.
    def _sp(t): return list(t.iter(N + 'tspan'))
    merged = set()
    groups = {}
    for t, bad in texts:
        if bad: continue
        g = textparent.get(id(t))
        groups.setdefault(id(g), []).append(t)
    LK = links(prod)
    for members in groups.values():
        if len(members) < 2: continue
        members = sorted(members, key=lambda t: -len(_sp(t)))
        T = members[0]
        tys = {round(num(q.get('y')), 1) for q in _sp(T)}
        for B in members[1:]:
            if B.get('font-family') != T.get('font-family') or B.get('font-size') != T.get('font-size'): continue
            bs = _sp(B)
            if not bs or not ({round(num(q.get('y')), 1) for q in bs} & tys): continue
            lk_txt = fx(''.join(q.text or '' for q in bs)).strip(' :')
            lk_href = LK.get(lk_txt)
            if isinstance(lk_href, tuple): lk_href = None
            if lk_txt in LK and not (lk_href and '@' in lk_txt): continue      # links stay links (an e-mail inside a sentence joins it)
            for q in bs:
                nq = ET.Element(N + 'tspan', {'x': q.get('x'), 'y': q.get('y')})
                nq.text = q.text
                if lk_txt in LK and lk_href: nq.set('data-href', lk_href)
                for k in ('font-weight', 'fill', 'font-size'):
                    val = q.get(k) or B.get(k)
                    if val and val != T.get(k): nq.set(k, val)
                T.append(nq)
            merged.add(id(B))
        # keep tspans in reading order: by line, then left to right
        if any(id(B) in merged for B in members[1:]):
            sp = sorted(_sp(T), key=lambda q: (round(num(q.get('y')), 1), num(q.get('x'))))
            for q in _sp(T): T.remove(q)
            for q in sp: T.append(q)
    texts = [(t, b) for t, b in texts if id(t) not in merged]
    # footer group (drawn last in Figma, often over the bottom of the content)
    foot_g = next((g for g in root.iter(N + 'g') if re.search('footer', g.get('id') or '', re.I)), None)
    foot_ids = set()
    FOOT_Y = []
    if foot_g is not None:
        for r_ in foot_g.iter(N + 'rect'):
            if not r_.get('width') or num(r_.get('width')) < W * .9: continue
            ry = num(r_.get('y', '0')); mt_ = re.match(r'translate\(([-\d.]+)(?:[ ,]([-\d.]+))?\)', r_.get('transform', ''))
            if mt_: ry += float(mt_.group(2) or 0)
            FOOT_Y.append(ry)
        FOOT_Y = [min(FOOT_Y)] if FOOT_Y else []
    if foot_g is not None:
        for t, _ in texts:
            a_ = textparent.get(id(t))
            while a_ is not None:
                if a_ is foot_g: foot_ids.add(id(t)); break
                a_ = parent.get(a_)
    for e in root.iter():
        if e.get('id') and e.tag not in (N + 'clipPath', N + 'linearGradient', N + 'radialGradient', N + 'pattern', N + 'image', N + 'filter', N + 'mask'):
            del e.attrib['id']
    # square-cornered rectangles meeting edge to edge leave faint light lines at fractional scales: draw them crisp
    for r_ in root.iter(N + 'rect'):
        if not r_.get('rx') and not (r_.get('fill') or '').startswith('url(#pattern'): r_.set('shape-rendering', 'crispEdges')
    svg_rel = f'assets/svg/{name}.svg'
    os.makedirs(os.path.join(PROJ, 'assets', 'svg'), exist_ok=True)
    data = ET.tostring(root, encoding='unicode')
    open(os.path.join(PROJ, svg_rel), 'w', encoding='utf-8').write(data)
    # the same drawing without the footer: used for content strips, so nothing is hidden under the footer
    svg_nf = None
    if foot_g is not None and parent.get(foot_g) is not None:
        fp = parent[foot_g]; idx = list(fp).index(foot_g); fp.remove(foot_g)
        svg_nf = f'assets/svg/{name}-nf.svg'
        open(os.path.join(PROJ, svg_nf), 'w', encoding='utf-8').write(ET.tostring(root, encoding='unicode'))
        fp.insert(idx, foot_g)

    L = links(prod)
    out = []; inputs = []; tinfo = []; input_y = []; side = []
    def inside(px, py, r, pad=2):
        return r[0] - pad <= px <= r[0] + r[2] + pad and r[1] - pad <= py <= r[1] + r[3] + pad
    ALLTXT = [(num(s.get('y')), fx(s.text or '')) for t, _ in texts for s in t.iter(N + 'tspan')]
    FOOTIDX = set(); _prev = [0, False]
    for t, bad in texts:
        if _prev[1]: FOOTIDX.update(range(_prev[0], len(out)))
        _prev[0], _prev[1] = len(out), id(t) in foot_ids
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
        if not full and spans:
            # Figma left the e-mail run empty after "...by email on" — fill it in as the real address
            sy = num(spans[0].get('y'))
            if any(abs(yy - sy) < 1 and 'email on' in tt for yy, tt in ALLTXT):
                spans[0].text = 'info@ampmtraining.com'; lines = {round(sy, 2): [spans[0]]}; full = spans[0].text
        if not full: continue
        if bad: print('  ! transformed text skipped:', full[:40], file=sys.stderr); continue
        first = spans[0]; fx0, fy0 = num(first.get('x')), num(first.get('y'))
        ty = fy0 - asc * fs; tbot = max(lines) + desc * fs
        tinfo.append((ty, tbot, fx0, fill.upper(), re.sub(r'\s+', ' ', full), id(t) in foot_ids))
        # placeholder -> input
        if fill.upper() == '#95A5A4' and fw == '400':
            box = next((r for r in rects if r[5] and r[5].upper() == '#95A5A4' and inside(fx0, fy0, r)), None)
            if box:
                tag = 'textarea' if 'Message' in full else 'input'
                typ = '' if tag == 'textarea' else ' type="%s"' % ('email' if 'mail' in full.lower() else 'tel' if 'phone' in full.lower() else 'text')
                st = f'--x:{box[0]:.1f};--y:{box[1]:.1f};--w:{box[2]:.1f};--h:{box[3]:.1f};--f:{fs:g};--pl:{fx0 - box[0]:.1f}'
                el = f'<{tag} class="fi"{typ} style="{st}" placeholder="{html.escape(full)}" aria-label="{html.escape(full)}"' + ('></textarea>' if tag == 'textarea' else '>')
                inputs.append(el); input_y.append(box[1]); continue
        style = f"font:{fw} calc({fs:g}*var(--u))/{asc + desc:.4f} {fam},sans-serif;color:{fill}"
        if lsv: style += f";letter-spacing:calc({lsv:.3f}*var(--u))"
        line_html = []
        for y, ss in lines.items():
            # every run sits at its own Figma x, so text placed after another element (e.g. an inline link) never overlaps it
            for s in ss:
                txt = html.escape(fx(s.text or '').rstrip('\n'))
                if not txt: continue
                sst = []
                if s.get('font-weight'): sst.append('font-weight:' + {'bold': '700'}.get(s.get('font-weight'), s.get('font-weight')))
                if s.get('fill'): sst.append('color:' + (paint_color(s.get('fill'), defs) or fill))
                if s.get('font-size'): sst.append(f"font-size:calc({num(s.get('font-size')):g}*var(--u))")
                st = (';' + ';'.join(sst)) if sst else ''
                if s.get('data-href'): txt = f'<a href="{s.get("data-href")}">{txt}</a>'
                hard = ' data-br' if fx(s.text or '').rstrip('  ').endswith(('\n', '\r')) else ''
                line_html.append(f'<span class="ln"{hard} style="--x:{num(s.get("x")):.2f};--y:{y - asc * fs:.2f}{st}">{txt}</span>')
        body = ''.join(line_html)
        key = re.sub(r'\s+', ' ', full).strip(' :')
        # breadcrumb "Home/Page": Home is a link, the current page is plain text
        mb = re.match(r'^Home\s*/\s*(.+)$', key)
        if mb and len(lines) == 1:
            crumb = (f'<nav class="tx crumb" aria-label="Breadcrumb" style="{style}"><span class="ln" style="--x:{fx0:.2f};--y:{ty:.2f}">'
                     f'<a href="{L["Home"]}">Home</a><span class="crumb-sep" aria-hidden="true">/</span><span aria-current="page">{html.escape(mb.group(1))}</span></span></nav>')
            out.append((ty, crumb)); continue
        # section headings on the legal page become scroll targets (never links)
        if PAGE_FILE == 'pils-legal.html' and fam == 'Poppins' and key in LEGAL_HEADINGS:
            out.append((ty, f'<span class="anchor" data-anchor="{LEGAL_HEADINGS[key]}" style="--y:{ty:.1f}"></span>'))
            tag = 'h2' if fs >= 34 else 'h3'
            out.append((ty, f'<{tag} class="tx" style="{style}">{body}</{tag}>'))
            continue
        # legal page: the drawn side list is rebuilt as a sticky HTML nav (see below)
        if PAGE_FILE == 'pils-legal.html' and fam == 'Montserrat' and (key in LEGAL_SIDE or (key == 'Legal' and fs <= 24)):
            side.append((key, fx0, fy0)); continue
        # pricing: the drawn "Select your country" card becomes a real country picker, "Continue" a real button
        if key == 'Select your country':
            card = min((r for r in rects if inside(fx0, fy0 - 5, r, 0) and r[2] < 700 and r[3] < 150), key=lambda r: r[2] * r[3], default=None)
            if card:
                opts = ''.join(f'<li role="option" id="cty-{bp}-{v}" data-v="{v}" aria-selected="false"><span class="cty-f f-{v}" aria-hidden="true"></span>{n}</li>'
                               for v, n in (('uk', 'United Kingdom'), ('ksa', 'Saudi Arabia'), ('eg', 'Egypt')))
                out.append((ty, f'<div class="cty" data-cty style="--x:{card[0]:.1f};--y:{card[1]:.1f};--w:{card[2]:.1f};--h:{card[3]:.1f};--tx:{fx0 - card[0]:.1f};--f:{fs:g}">'
                                f'<button type="button" class="cty-b" aria-haspopup="listbox" aria-expanded="false" aria-controls="cty-l-{bp}">'
                                f'<span class="cty-v">Select your country</span></button>'
                                f'<ul class="cty-l" id="cty-l-{bp}" role="listbox" aria-label="Country" tabindex="-1">{opts}</ul></div>'))
                continue
        if key == 'Continue' and PAGE_FILE.endswith('pricing.html'):
            out.append((ty, f'<p class="tx" aria-hidden="true" style="{style}">{body}</p>'
                            f'<button class="hit cty-go" type="button" style="--x:{fx0 - 8:.1f};--y:{ty - 6:.1f};--w:150;--h:{fs * 1.4 + 16:.1f};--r:8">Continue</button>'))
            continue
        target = L.get(key)
        if fam == 'Montserrat' and key in LEGAL_SIDE: target = ('pils-legal.html', LEGAL_SIDE[key])
        sec = None
        if isinstance(target, tuple): target, sec = target
        href = target
        dsec = f' data-section="{sec}"' if sec else ''
        if href is not None or key in ('Send', 'Continue'):
            box = None
            cand = [r for r in rects if inside(fx0 + 2, fy0 - fs * .3, r, 0) and r[2] < 700 and r[3] < 120 and (r[4] not in (None, 'none') or r[5])]
            if cand: box = min(cand, key=lambda r: r[2] * r[3])
            if key in ('Send', 'Continue'):
                hit = f'<button class="hit" type="submit" style="--x:{box[0]:.1f};--y:{box[1]:.1f};--w:{box[2]:.1f};--h:{box[3]:.1f};--r:{box[6]:g}" aria-label="{key}"></button>' if box else ''
                out.append((ty, f'<p class="tx" aria-hidden="true" style="{style}">{body}</p>{hit}' if box else f'<p class="tx" style="{style}">{body}</p>'))
            elif box:
                out.append((ty, f'<p class="tx" aria-hidden="true" style="{style}">{body}</p><a class="hit" href="{href}"{dsec} style="--x:{box[0]:.1f};--y:{box[1]:.1f};--w:{box[2]:.1f};--h:{box[3]:.1f};--r:{box[6]:g}">{html.escape(key)}</a>'))
            else:
                cur = ' aria-current="page"' if href == PAGE_FILE and not sec else ''
                tone = ' lk-on-dark' if fill.lower() in ('white', '#fff', '#ffffff') or fill.upper() == '#EAFAF5' else ''
                out.append((ty, f'<a class="tx lk{tone}" href="{href}"{dsec}{cur} style="{style}">{body}</a>'))
            continue
        if key == 'GET IN TOUCH':
            out.append((ty, f'<span class="anchor" data-anchor="contact" style="--y:{fy0 - 40:.1f}"></span>'))
        tag = 'h1' if fs >= 56 and not any('<h1' in o[1] for o in out) else 'h2' if fs >= 34 else 'h3' if fs >= 26 else 'p'
        # left-aligned body paragraphs over several lines get re-flowed at runtime (see js/v2.js):
        # Figma's manual line breaks go, real paragraph breaks stay, line height is evened out
        firsts = [num(v[0].get('x')) for v in lines.values()]
        flow = ''
        left_ = max(firsts) - min(firsts) < 1.5
        # phones: every text block (headings too, left or centred) is re-flowed with the mobile type scale
        if (tag == 'p' and fs < 30 and left_) or (bp == 'm' and fs < 90):
            box = [r for r in rects if r[0] - 1 <= fx0 <= r[0] + r[2] and r[1] - 1 <= ty + 2 <= r[1] + r[3]
                   and r[2] < W * .98 and r[3] > 40 and (fx0 - r[0]) < r[2] / 3]
            cw = ''
            if box:
                bx = min(box, key=lambda r: r[2] * r[3])
                cw = f' data-cw="{bx[0] + bx[2] - (fx0 - bx[0]):.1f}"'
            ys_ = sorted(lines)
            gap = sorted(b - a for a, b in zip(ys_, ys_[1:]))[len(ys_) // 2 - 1] if len(ys_) > 1 else fs * 1.5
            flow = f' data-flow data-fs="{fs:g}" data-gap="{gap:.2f}" data-x="{fx0:.2f}" data-asc="{asc}"{cw}'
        out.append((ty, f'<{tag} class="tx"{flow} data-yb="{tbot:.1f}" style="{style}">{body}</{tag}>'))
    if _prev[1]: FOOTIDX.update(range(_prev[0], len(out)))
    if inputs:
        out = [(y, o.replace('<button class="hit"', '<button form="f-' + bp + '" class="hit"')) for y, o in out]
        out.append((min(input_y), f'<form id="f-{bp}" class="ff" action="#" method="post" onsubmit="return false">' + ''.join(inputs) + '</form>'))

    # ---------- accordions: cards (white -> #EAFAF5) holding a question and a #288C91 answer ----------
    imgs = [r for r in rects if (r[4] or '').startswith('url(#pattern')]
    IMGRANGES[name] = ','.join(f'{r[1]:.0f}-{r[1] + r[3]:.0f}' + ('f' if r[2] >= W * .95 else '') for r in imgs)
    ref = None
    try: ref = Image.open(os.path.join(PROJ, '_figma-reference', 'v2', name + '.png')).convert('RGB')
    except Exception: pass
    accs = []
    def qkey(q): return re.sub(r'[^a-z0-9]', '', q.lower())
    for r in rects:
        x, y, w, h, f = r[0], r[1], r[2], r[3], r[4] or ''
        if not f.startswith('url(#') or w < 300 or h < 60: continue
        if (paint_color(f, defs) or '').upper() != '#EAFAF5': continue
        ans = [t for t in tinfo if t[3] == '#288C91' and x <= t[2] <= x + w and t[0] >= y and t[1] <= y + h + 2]
        ins = None; cend = None
        if ans:
            a0 = min(t[0] for t in ans)
            qs = [t for t in tinfo if t[3] == '#3A495B' and x <= t[2] <= x + w and t[0] >= y - 2 and t[1] <= a0 + 2]
            if not qs: continue
            ANSWERS.setdefault(qkey(' '.join(t[4] for t in sorted(qs))), ' '.join(t[4] for t in sorted(ans)))
        else:
            # a question card with no answer in this frame: borrow the answer the design gives in another frame
            qs = [t for t in tinfo if t[3] == '#3A495B' and x <= t[2] <= x + w and t[0] >= y - 2 and t[1] <= y + h + 2]
            if not qs: continue
            ins = ANSWERS.get(qkey(' '.join(t[4] for t in sorted(qs))))
            if not ins: continue
        qtop, qbot = min(t[0] for t in qs), max(t[1] for t in qs)
        pad = qtop - y
        if ins:
            hc = h; y0 = y1 = y + h
        else:
            hc = (qbot - y) + pad; e = min(pad, 14)
            # a full-width block (the footer) drawn over the card ends it visually
            cover = [rr[1] for rr in rects if rr[2] >= W * .95 and y + hc < rr[1] < y + h]
            cend = None
            if cover:
                # the footer is drawn over this card: end the card right after its content and draw its bottom edge in HTML
                ab = max([t[1] for t in ans] + [im[1] + im[3] for im in imgs if x <= im[0] <= x + w and y < im[1] < y + h])
                y0, y1 = y + hc - e, max(y + hc - e + 21, ab + pad - e)
                def _px(px_, py_):
                    if not ref: return '#F4FBF9'
                    return '#%02X%02X%02X' % ref.getpixel((min(max(int(px_), 0), ref.width - 1), min(max(int(py_), 0), ref.height - 1)))
                cend = dict(e=e, c1=_px(x + 6, y + hc - e / 2), c2=_px(x + w - 6, y + hc - e / 2), pbg=_px(max(x - 6, 1), y + hc), skip=y + h)
            if cover: pass
            else: y0, y1 = y + hc - e, y + h - e
            if y1 - y0 < 20: continue
        # chevron centre from the Figma render (green/teal pixels at the right of the question row)
        cx, cy = x + w - 34.5, y + hc / 2; bg = '#FBFEFD'
        ch = [c for c in chevs if x + w - 100 <= c[0] <= x + w and y <= c[1] <= y + hc]
        if ch:
            cx, cy = ch[0]
            if ref and 0 <= int(cx + 20) < ref.width and 0 <= int(cy) < ref.height:
                bg = '#%02X%02X%02X' % ref.getpixel((int(cx + 20), int(cy)))
        elif ref:
            px = [(i, j) for i in range(int(x + w - 90), int(x + w)) for j in range(int(y), int(y + hc))
                  if 0 <= i < ref.width and 0 <= j < ref.height and (lambda p: p[1] > 150 and p[0] < 150 and p[2] < 170)(ref.getpixel((i, j)))]
            if px:
                cx = (min(p[0] for p in px) + max(p[0] for p in px)) / 2; cy = (min(p[1] for p in px) + max(p[1] for p in px)) / 2
                bp_ = ref.getpixel((min(int(cx + 20), ref.width - 1), int(cy)))
                bg = '#%02X%02X%02X' % bp_
        accs.append(dict(x=x, y=y, w=w, hc=hc, y0=y0, y1=y1, cx=cx, cy=cy, bg=bg, q=' '.join(t[4] for t in sorted(qs)), ins=ins, qx=min(t[2] for t in qs) - x, cend=(cend if not ins else None)))
    accs.sort(key=lambda a: a['y'])
    decor_obj = f'<object class="decor" type="image/svg+xml" data="{svg_rel}" tabindex="-1" aria-hidden="true"></object>'
    # sticky legal nav: same pills as the design (295x40, 57 apart), rebuilt in HTML over a cover of the drawn one
    legal_nav = ''
    if side:
        head = next((s for s in side if s[0] == 'Legal'), None)
        pills = [s for s in side if s[0] != 'Legal']
        px_ = (head[1] if head else min(p[1] for p in pills) - 80)
        top0 = min(p[2] for p in pills) - 25.7
        htop = (head[2] - 22 if head else top0 - 40)
        bottom = max(p[2] for p in pills) - 25.7 + 40
        foot = FOOT_Y
        end_y = min(foot) if foot else H - 600
        out.append((end_y - 1, f'<span class="anchor" data-anchor="legal-end" style="--y:{end_y - 40:.1f}"></span>'))
        links_ = ''.join(f'<a class="lgn-a" href="pils-legal.html" data-section="{LEGAL_SIDE[k]}">{html.escape(k)}</a>'
                         for k, _, _ in sorted(pills, key=lambda p: p[2]))
        legal_nav = (f'<span class="lgn-cover" style="--x:{px_ - 14:.1f};--y:{htop - 8:.1f};--w:{295 + 28};--h:{bottom - htop + 18:.1f}" aria-hidden="true"></span>'
                     f'<nav class="lgn" aria-label="Legal sections" style="--x:{px_:.1f};--y:{htop:.1f};--gap:{57 - 40}">'
                     f'<div class="lgn-in"><p class="lgn-h">Legal</p>{links_}</div></nav>')
    # ---------- accordions rebuilt in HTML (guide + legal FAQ) ----------
    # The drawn question cards are replaced by a real accordion list: question buttons, animated answers,
    # answer images cropped from the design. Each run of cards becomes one "zone" that flows with its content.
    zones = []
    if 'guide' in PAGE_FILE or 'legal' in PAGE_FILE:
        def crop_img(r):
            m_ = re.match(r'url\(#(.*)\)', r[4] or '')
            pat = defs.get(m_.group(1)) if m_ else None
            use = next(pat.iter(N + 'use'), None) if pat is not None else None
            if use is None: return None
            im_el = defs.get((use.get(XL) or use.get('href') or '').lstrip('#'))
            if im_el is None: return None
            fn = (im_el.get(XL) or '').split('/')[-1]
            fp = os.path.join(IMG_OUT, fn)
            if not os.path.exists(fp): return None
            tr = use.get('transform', '')
            mm = re.match(r'matrix\(([^)]*)\)', tr); ms = re.match(r'scale\(([^)]*)\)', tr)
            if mm: a_, _, _, d_, e_, f_ = [float(v) for v in re.split(r'[ ,]+', mm.group(1).strip())]
            elif ms:
                vv = [float(v) for v in re.split(r'[ ,]+', ms.group(1).strip())]; a_, d_ = vv[0], vv[-1]; e_ = f_ = 0
            else: return None
            iw, ih = num(im_el.get('width')), num(im_el.get('height'))
            src = Image.open(fp); sx = src.width / iw
            box_ = (-e_ / a_ * sx, -f_ / d_ * sx, (-e_ + 1) / a_ * sx, (-f_ + 1) / d_ * sx)
            c = src.convert('RGB').crop(tuple(int(round(v)) for v in box_))
            tw = int(min(c.width, r[2] * 2)); c = c.resize((tw, int(tw * r[3] / r[2])), Image.LANCZOS)
            out_fn = 'crop-' + hashlib.md5((fn + repr(box_)).encode()).hexdigest()[:10] + '.jpg'
            c.save(os.path.join(IMG_OUT, out_fn), quality=84, optimize=True, progressive=True)
            return out_fn
        cards = []
        for r in rects:
            x, y, w, h, f = r[0], r[1], r[2], r[3], r[4] or ''
            if not f.startswith('url(#') or w < 300 or h < 60: continue
            if (paint_color(f, defs) or '').upper() != '#EAFAF5': continue
            inside_ = [t for t in tinfo if not t[5] and x - 2 <= t[2] <= x + w and y - 2 <= t[0] and t[0] < y + h]
            qs = [t for t in inside_ if t[3] == '#3A495B']
            if not qs: continue
            q0 = min(qs)
            # the question = the navy text at the top of the card (it can wrap over several lines)
            qs = [t for t in qs if t[0] <= q0[1] + 4]
            qbot = max(t[1] for t in qs)
            rest = sorted([t for t in inside_ if t not in qs and t[0] >= qbot - 2], key=lambda t: (round(t[0]), t[2]))
            ims = [im for im in imgs if x <= im[0] <= x + w and qbot < im[1] < y + h]
            cards.append(dict(x=x, y=y, w=w, h=h, qs=qs, qbot=qbot, rest=rest, ims=ims, fs=max(t[0] for t in [(0,)])))
        cards.sort(key=lambda c: c['y'])
        _seen = set(); _cards = []
        for c in cards:
            k_ = (round(c['y']), round(c['x']))
            if k_ in _seen: continue
            _seen.add(k_); _cards.append(c)
        cards = _cards
        # group cards into zones; a heading between cards (e.g. "Patients:") starts a new zone
        for c in cards:
            z = zones[-1] if zones else None
            if z:
                last = z['cards'][-1]; gap_top = last['y'] + last['h']
                between = [t for t in tinfo if not t[5] and gap_top - 2 < t[0] < c['y'] and not any(t in cc['qs'] or t in cc['rest'] for cc in z['cards'])]
                if c['y'] - gap_top < 90 and not between:
                    z['cards'].append(c); continue
            zones.append(dict(cards=[c]))
        for z in zones:
            cs = z['cards']
            z['top'] = cs[0]['y']; z['bottom'] = max(c['y'] + c['h'] for c in cs)
            z['x'] = min(c['x'] for c in cs); z['w'] = max(c['w'] for c in cs)
            if z['x'] < 8 or z['x'] + z['w'] > W - 8: z['x'], z['w'] = 16.0, W - 32.0   # edge-to-edge cards get a gutter
            z['gap'] = min([b['y'] - (a['y'] + a['h']) for a, b in zip(cs, cs[1:])] + [24])
            z['pbg'] = ('#%02X%02X%02X' % ref.getpixel((max(int(z['x']) - 8, 1), min(int(z['top']) + 4, ref.height - 1)))) if ref else '#FFFFFF'
        def para_html(txt):
            txt = re.sub(r'\s+([.,;:!?])', r'\1', txt.strip())
            parts_ = [p.strip() for p in re.split(r'\s(?=- )', txt) if p.strip()]
            h_ = ''.join(f'<p>{html.escape(p)}</p>' for p in parts_)
            return re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+[\w])', r'<a href="mailto:\1">\1</a>', h_)
        first_open = 'guide' in PAGE_FILE
        for zi, z in enumerate(zones):
            items = []
            for ci, c in enumerate(z['cards']):
                q = re.sub(r'\s+', ' ', ' '.join(t[4] for t in sorted(c['qs'], key=lambda t: (round(t[0]), t[2])))).strip()
                qfs = max(16, min(20, (c['qs'][0][1] - c['qs'][0][0]) / 1.4))
                # answer: texts under the question in reading order (+ images), or the answer borrowed from another frame
                blocks = []
                line_y, buf = None, []
                for t in c['rest']:
                    if line_y is not None and t[0] - line_y > 4:
                        blocks.append((line_y, ' '.join(buf))); buf = []
                    if not buf: line_y = t[0]
                    buf.append(t[4])
                if buf: blocks.append((line_y, ' '.join(buf)))
                content = [(by, para_html(bt)) for by, bt in blocks]
                for im in c['ims']:
                    fn_ = crop_img(im)
                    if fn_: content.append((im[1], f'<figure class="az-media"><img src="assets/v2/{fn_}" alt="" loading="lazy"><span class="az-play" aria-hidden="true"></span></figure>'))
                content.sort(key=lambda v: v[0])
                ans_html = ''.join(v[1] for v in content)
                if not ans_html:
                    borrowed = ANSWERS.get(qkey(q))
                    if borrowed: ans_html = para_html(borrowed)
                iid = f'az-{bp}-{zi}-{ci}'
                is_open = first_open and zi == 0 and ci == 0 and bool(ans_html)
                chev = '<i class="az-c" aria-hidden="true"></i>' if ans_html else ''
                btn = (f'<button class="az-q" type="button" id="{iid}-q" aria-expanded="{"true" if is_open else "false"}" aria-controls="{iid}-a"'
                       f' style="--qf:{qfs:g}"><span>{html.escape(q)}</span>{chev}</button>') if ans_html else f'<div class="az-q az-static" style="--qf:{qfs:g}"><span>{html.escape(q)}</span></div>'
                panel = (f'<div class="az-a" id="{iid}-a" role="region" aria-labelledby="{iid}-q"><div class="az-in"><div class="az-body">{ans_html}</div></div></div>') if ans_html else ''
                items.append(f'<div class="az-i{" open" if is_open else ""}"><h3 class="az-h">{btn}</h3>{panel}</div>')
            z['html'] = (f'<div class="bd az" style="--pbg:{z["pbg"]};--x:{z["x"]:.1f};--w:{z["w"]:.1f};--gap:{max(12, z["gap"]):.1f}">'
                         f'<div class="az-list">' + ''.join(items) + '</div></div>')
    if zones:
        fr_ = FOOT_Y
        ftop_z = min(fr_) if fr_ else H
        bands_z = []; cur = 0
        for zi, z in enumerate(zones):
            bands_z.append((cur, z['top'], None)); bands_z.append((z['top'], z['top'], ('zone', zi)))
            cur = z['bottom']
            if cur >= ftop_z - 1:
                bands_z.append((0, 0, ('space', 0))); cur = ftop_z
        bands_z.append((cur, H, None))
        zr = [(z['top'], z['bottom']) for z in zones]
        html_z = []
        for ys, ye, kind in bands_z:
            if kind:
                if kind[0] == 'zone': html_z.append(zones[kind[1]]['html'])
                else: html_z.append(f'<div class="bd az-space" style="--pbg:{zones[-1]["pbg"]}"></div>')
                continue
            if ye <= ys: continue
            items = [o for k, (y, o) in enumerate(out) if (ys <= y < ye or (ys == 0 and y < 0))
                     and (k in FOOTIDX or not any(a_ <= y < b_ for a_, b_ in zr))]
            has_img = any(r[1] < ye and r[1] + r[3] > ys for r in imgs)
            dec = decor_obj if has_img else f'<img class="decor" src="{svg_rel}" alt="" aria-hidden="true">'
            html_z.append(f'<div class="bd" style="--y0:{ys:.1f};--h:{ye - ys:.1f}"><div class="bd-in">{dec}\n' + '\n'.join(items) + '</div></div>')
        return W, H, hh, '\n'.join(html_z) + legal_nav, True
    # full-photo hero (product home pages): the 1024-tall full-width block right under the header
    hero = next(((min(r[1], hh), r[1] + r[3]) for r in rects if r[2] >= W * .95 and 700 <= r[3] <= 1200 and hh - 5 <= r[1] <= hh + 60
                 and any(im[2] >= W * .9 and im[1] < r[1] + 50 for im in imgs)), None)
    ftop = None
    if svg_nf:
        fr = FOOT_Y
        ftop = min(fr) if fr else None
    ce = ftop
    if ftop:
        cb = [t[1] for t in tinfo if not t[5] and t[1] > ftop - 400]
        if cb: ce = max(ftop, max(cb) + 60)
        for a in accs: ce = max(ce, a['y1'] if not a['ins'] else a['y0'])
    under = bool(ftop and (ce > ftop + 1 or any(a['cend'] for a in accs)))
    if under and ce < max([a['y1'] for a in accs if a['cend']] + [0]): ce = max(a['y1'] for a in accs if a['cend'])
    if not accs and not hero and not under:
        return W, H, hh, decor_obj + '\n' + '\n'.join(o for _, o in out) + legal_nav, False
    # bands: the page is cut into horizontal strips; each answer is its own strip that can fold to 0.
    # Answers borrowed from another frame are inserted as their own HTML strip under the question card.
    # The hero is its own strip that shrinks to the screen height (cropping the photo evenly top and bottom).
    bands = []; cur = 0
    if hero:
        bands.append((0, hero[0], None)); bands.append((hero[0], hero[1], 'hero')); cur = hero[1]
    for i, a in enumerate(accs):
        if a['ins']:
            bands.append((cur, a['y0'], None)); bands.append((a['y0'], a['y0'], ('ins', i))); cur = a['y0']
        else:
            bands.append((cur, a['y0'], None)); bands.append((a['y0'], a['y1'], i)); cur = a['y1']
            if a['cend']:
                bands.append((a['y1'], a['y1'], ('end', i))); cur = max(a['y1'], a['cend']['skip'])
    if under:
        bands.append((cur, ce, None)); bands.append((ftop, H, 'foot'))
    else:
        bands.append((cur, H, None))
    bands = [b_ for b_ in bands if b_[1] > b_[0] or b_[2] is not None]
    open_first = 'guide' in PAGE_FILE
    html_bands = []
    def answer_html(t):
        parts_ = [p.strip() for p in re.split(r'\s(?=- )', t) if p.strip()]
        out_ = ''.join(f'<p>{html.escape(p)}</p>' for p in parts_)
        return re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', out_)
    for ys, ye, acc in bands:
        if isinstance(acc, tuple) and acc[0] == 'end':
            c = accs[acc[1]]['cend']; a = accs[acc[1]]
            html_bands.append(f'<div class="bd cend" style="--pbg:{c["pbg"]};--x:{a["x"]:.1f};--w:{a["w"]:.1f};--e:{c["e"]:.1f};--c1:{c["c1"]};--c2:{c["c2"]}"><span class="cend-in" aria-hidden="true"></span></div>')
            continue
        if isinstance(acc, tuple):
            a = accs[acc[1]]
            pb = ('#%02X%02X%02X' % ref.getpixel((2, min(int(a["y0"]) + 2, ref.height - 1)))) if ref else '#D7ECE9'
            html_bands.append(f'<div class="bd acc ins closed" id="acc-{bp}-{acc[1]}" style="--pbg:{pb};--x:{a["x"]:.1f};--w:{a["w"]:.1f};--fs:{20 if W >= 1000 else 16};--pl:{a["qx"]:.1f}"><div class="ans"><div class="ans-in">{answer_html(a["ins"])}</div></div></div>')
            continue
        if under:
            items = [o for k, (y, o) in enumerate(out) if (k in FOOTIDX) == (acc == 'foot') and (acc == 'foot' or ys <= y < ye or (ys == 0 and y < 0))]
        else:
            items = [o for (y, o) in out if ys <= y < ye or (ys == 0 and y < 0)]
        # toggles live in the band that holds their question row
        for i, a in enumerate(accs):
            if ys <= a['y'] < ye:
                is_open = open_first and i == 0 and not a['ins']
                items.append(f'<button class="acc-t" type="button" aria-expanded="{"true" if is_open else "false"}" aria-controls="acc-{bp}-{i}" '
                             f'style="--x:{a["x"]:.1f};--y:{a["y"]:.1f};--w:{a["w"]:.1f};--h:{a["hc"]:.1f}"><span class="visually-hidden">{html.escape(a["q"])}</span>'
                             f'<span class="acc-c" style="--cx:{a["cx"] - a["x"]:.1f};--cy:{a["cy"] - a["y"]:.1f};--bg:{a["bg"]}" aria-hidden="true"></span></button>')
        has_img = any(r[1] < ye and r[1] + r[3] > ys for r in imgs)
        src_ = svg_nf if (under and acc != 'foot') else svg_rel
        dec = (decor_obj.replace(svg_rel, src_) if has_img else f'<img class="decor" src="{src_}" alt="" aria-hidden="true">')
        if acc == 'hero':
            # centre the hero text block vertically (the photo stays put): shift = hero centre - content centre
            ht = [t for t in tinfo if ys <= t[0] and t[1] <= ye]
            dy = ((ye - ys) / 2 - ((min(t[0] for t in ht) + max(t[1] for t in ht)) / 2 - ys)) if ht else 0
            html_bands.append(f'<div class="bd hero" style="--y0:{ys:.1f};--h:{ye - ys:.1f}"><div class="bd-in">{dec}\n'
                              f'<div class="hero-c" style="--dy:{dy:.1f}">' + '\n'.join(items) + '</div></div></div>')
        elif acc == 'foot':
            html_bands.append(f'<div class="bd" style="--y0:{ys:.1f};--h:{ye - ys:.1f}"><div class="bd-in">{dec}\n' + '\n'.join(items) + '</div></div>')
        elif acc is None:
            html_bands.append(f'<div class="bd" style="--y0:{ys:.1f};--h:{ye - ys:.1f}"><div class="bd-in">{dec}\n' + '\n'.join(items) + '</div></div>')
        else:
            is_open = open_first and acc == 0
            html_bands.append(f'<div class="bd acc{"" if is_open else " closed"}" id="acc-{bp}-{acc}" style="--y0:{ys:.1f};--h:{ye - ys:.1f}"><div class="bd-in">{dec}\n' + '\n'.join(items) + '</div></div>')
    return W, H, hh, '\n'.join(html_bands) + legal_nav, True

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
    # answers the Figma file leaves blank (written for the site, keyed like qkey())
    ANSWERS = {
        'whowritestheinformationprovidedinthemintpils':
            'MINT PILs are written by the AMPM Training team of healthcare professionals and medical writers. '
            'Every leaflet is checked by clinical reviewers before it is published, following the quality process '
            'behind our PIF TICK accreditation as a trusted information creator.',
        'istheinformationuptodateandaccurate':
            'Yes. Each MINT PIL is based on current clinical evidence and guidance, and is reviewed regularly. '
            'When the evidence or guidance changes, the leaflet is updated so patients always see accurate information.',
    }
    for name in names:   # first pass: learn every question's answer from all three frames
        if name and os.path.exists(os.path.join(SVGDIR, name + '.svg')): frame(name, prod, 'x')
    for bp, name in zip(('d', 't', 'm'), names):
        if name is None: continue
        if not os.path.exists(os.path.join(SVGDIR, name + '.svg')):
            print('missing', name, file=sys.stderr); continue
        W, H, HH, body, banded = frame(name, prod, bp)
        extra = (' fv-td' if (bp == 't' and names[0] is None) else '') + (' banded' if banded else '')
        rf = os.path.join(os.path.dirname(SVGDIR), 'runs', name + '.txt')
        runs_attr = f' data-runs="{open(rf).read().strip()}"' if bp == 'm' and os.path.exists(rf) else ''
        if runs_attr and IMGRANGES.get(name): runs_attr += f' data-imgs="{IMGRANGES[name]}" data-svg="assets/svg/{name}.svg"'
        parts.append(f'<section class="fv fv-{bp}{extra}"{runs_attr} style="--W:{W:g};--H:{H:g};--HH:{HH:g}" aria-label="{html.escape(title)}">\n{body}\n</section>\n')
    p_ = 'consent' if prod == 'consent' else 'pils'
    cfg = {'name': 'MINT CONSENT' if prod == 'consent' else 'MINT PILs', 'logo': f'assets/img/logo-{p_}.svg', 'home': p_ + '.html',
           'links': [{'label': 'Home', 'href': p_ + '.html'}, {'label': 'About', 'href': p_ + '-about.html'}, {'label': 'Guide', 'href': p_ + '-guide.html'},
                     {'label': 'Pricing', 'href': p_ + '-pricing.html'}, {'label': 'Contact Us', 'href': p_ + '.html', 'section': 'contact'}],
           'tabs': [{'label': 'Home', 'href': p_ + '.html', 'icon': 'home'}, {'label': 'Guide', 'href': p_ + '-guide.html', 'icon': 'book'},
                    {'label': 'Pricing', 'href': p_ + '-pricing.html', 'icon': 'tag'}, {'label': 'About', 'href': p_ + '-about.html', 'icon': 'info'},
                    {'label': 'Contact', 'href': p_ + '.html', 'section': 'contact', 'icon': 'mail'}]}
    cfg['family'] = [
        {'label': 'MINTFORMED', 'href': 'index.html', 'logo': 'assets/img/logo.svg', 'note': 'Back to the main site', 'main': True},
        {'label': 'MINT CONSENT', 'href': 'consent.html', 'logo': 'assets/img/logo-consent.svg', 'note': 'Digital consent, explained clearly', 'current': prod == 'consent'},
        {'label': 'MINT PILs', 'href': 'pils.html', 'logo': 'assets/img/logo-pils.svg', 'note': 'Illustrated, interactive leaflets', 'current': prod == 'pils'},
        {'label': 'MINT FAMILY', 'note': 'The family health app', 'soon': True}]
    foot = FOOT.replace('<script src="js/ui.js"></script>', '<script type="application/json" id="sticky-cfg">' + json.dumps(cfg) + '</script>\n<script src="js/ui.js"></script>')
    open(os.path.join(PROJ, out), 'w', encoding='utf-8').write(HEAD.format(title=html.escape(title), slug=slug) + ''.join(parts) + foot)
    print('wrote', out)
