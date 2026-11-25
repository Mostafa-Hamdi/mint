# one-off: Figma legal text (legal.txt: "y x text" lines) -> semantic legal_content.html
import sys, re, html
src, out = sys.argv[1], sys.argv[2]
svg = open(src, encoding='utf-8').read()
rows = sorted((round(float(m.group(2))), round(float(m.group(1))), html.unescape(m.group(3)).strip())
              for m in re.finditer(r'<tspan[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"[^>]*>([^<]*)', svg))
rows = [r for r in rows if r[2]]
odd = sorted({c for _, _, t in rows for c in t if ord(c) > 127})
print('non-ascii:', [hex(ord(c)) for c in odd])
esc = html.escape


def fix(t):
    t = t.replace('� 2023', '© 2023')
    t = t.replace('�', '’')
    return re.sub(r'\s+', ' ', t).strip()


def body(y0, y1, x=412):
    return fix(' '.join(t for y, xx, t in rows if y0 <= y < y1 and xx == x))


terms = body(897, 1880)
privacy = body(1934, 3420)
refunds = body(9500, 9960)
copyright_ = body(10063, 10800)

# privacy: run-in subheadings become h3 + paragraphs; "• x" items become a list
subs = ['Information Collection and Use', 'Log Data', 'Cookies Cookies', 'Service Providers', 'Security', 'Links to Other Sites',
        "Children's Privacy", 'Changes to This Privacy Policy', 'Contact Us']
parts = []
rest = privacy
for s in subs:
    i = rest.find(' ' + s + ' ')
    if i < 0: print('missing', s); continue
    parts.append(rest[:i]); rest = rest[i + 1:]
parts.append(rest)
priv_html = f'<p>{esc(parts[0])}</p>\n'
for s, chunk in zip(subs, parts[1:]):
    title = 'Cookies' if s == 'Cookies Cookies' else s
    text = chunk[len(s):].strip()
    if s == 'Cookies Cookies': text = 'Cookies ' + text
    if '• To ' in text:   # bullets lost as U+FFFD -> ’ ; split them back out
        head, *items = re.split(r' ?• (?=To )', text)
        last = items[-1]
        m = re.match(r'(.*?\.)\s+(.*)', last)
        items[-1], tail = (m.group(1), m.group(2)) if m else (last, '')
        priv_html += f'<h3>{esc(title)}</h3>\n<p>{esc(head)}</p>\n<ul>' + ''.join(f'<li>{esc(i)}</li>' for i in items) + '</ul>\n'
        if tail: priv_html += f'<p>{esc(tail)}</p>\n'
    else:
        priv_html += f'<h3>{esc(title)}</h3>\n<p>{esc(text)}</p>\n'

# FAQ: questions at x 452/436, answers below them at x 436
ANSWERS = {
    'Who writes the information provided in the MINT PILS?':
        'MINT PILs are written by the AMPM Training team of healthcare professionals and medical writers. Every leaflet is checked by '
        'clinical reviewers before it is published, following the quality process behind our PIF TICK accreditation as a trusted information creator.',
    'Is the information up-to-date and accurate?':
        'Yes. Each MINT PIL is based on current clinical evidence and guidance, and is reviewed regularly. When the evidence or guidance changes, '
        'the leaflet is updated so patients always see accurate information.',
}
faq_rows = [(y, x, fix(t)) for y, x, t in rows if 3479 <= y < 9000 and x in (412, 436, 452)]
groups, cur, q = [], None, None
for y, x, t in faq_rows:
    if x == 412:
        cur = {'name': t.rstrip(':'), 'items': []}; groups.append(cur); continue
    if t.endswith('?') and (not q or q['a'] or x == 452 or t[0].isupper() and len(t) < 80):
        q = {'q': t, 'a': []}; cur['items'].append(q); continue
    q['a'].append(t)


def answer_html(lines, question):
    if not lines:
        return f'<p>{esc(ANSWERS.get(question, ""))}</p>'
    text = ' '.join(lines)
    text = text.replace('MINT PILS', 'MINT PILs')
    if text.startswith('- '):
        items = [i.strip() for i in text[2:].split(' - ')]
        return '<ul>' + ''.join(f'<li>{linkify(i)}</li>' for i in items) + '</ul>'
    return f'<p>{linkify(text)}</p>'


def linkify(t):
    t = esc(t)
    return t.replace('info@ampmtraining.com', '<a href="mailto:info@ampmtraining.com">info@ampmtraining.com</a>')


faq_html = ''
for gi, g in enumerate(groups):
    faq_html += f'<h3>{esc(g["name"])}</h3>\n<div class="acc">\n'
    for qi, it in enumerate(g['items']):
        uid = f'faq-{gi}-{qi}'
        qq = it['q'].replace('MINT PILS', 'MINT PILs').replace('community, I live in', 'community I live in')
        faq_html += (f'<div class="acc-i"><h4><button class="acc-q" type="button" id="{uid}-q" aria-expanded="false" aria-controls="{uid}-a">'
                     f'<span>{esc(qq)}</span>{{CHEV}}</button></h4>'
                     f'<div class="acc-a" id="{uid}-a" role="region" aria-labelledby="{uid}-q"><div class="acc-in"><div class="acc-body">'
                     f'{answer_html(it["a"], it["q"])}</div></div></div></div>\n')
    faq_html += '</div>\n'

sections = [
    ('terms', 'Terms and Conditions', f'<p>{esc(terms)}</p>\n'),
    ('privacy', 'Privacy Policy', priv_html),
    ('faq', 'FAQ', faq_html),
    ('refunds', 'Refunds Policy', f'<h3>Cancellation terms</h3>\n<p>{esc(refunds)}</p>\n'),
    ('copyright', 'Copyright Information', f'<p>{esc(copyright_)}</p>\n'),
]
nav = ''.join(f'<li><a href="pils-legal.html" data-section="{sid}">{esc(t)}</a></li>' for sid, t, _ in sections)
secs = ''.join(f'<section class="legal-s" id="{sid}" data-anchor="{sid}" aria-labelledby="{sid}-h">\n<h2 id="{sid}-h">{esc(t)}</h2>\n{h}</section>\n'
               for sid, t, h in sections)
open(out, 'w', encoding='utf-8', newline='\n').write(
    '<div class="legal">\n<nav class="legal-nav" aria-label="Legal sections"><ul>' + nav + '</ul></nav>\n<div class="legal-body">\n' + secs + '</div>\n</div>\n')
print('groups', [(g['name'], len(g['items'])) for g in groups])
for g in groups:
    for it in g['items']:
        print(' ', it['q'][:60], '|', len(it['a']))
