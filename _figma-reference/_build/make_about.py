# usage: make_about.py <project dir>
# Builds consent-about.html and pils-about.html: the About page shown inside each product site
# (product header, tab bar and family switcher instead of the MINTFORMED ones), and points every
# "About" link on that product's pages to it.
import sys, os, re, json, glob
proj = sys.argv[1]
src = open(os.path.join(proj, 'about.html'), encoding='utf-8').read()
CFG = re.compile(r'(<script type="application/json" id="sticky-cfg">)(.*?)(</script>)', re.S)
for p, name in (('consent', 'MINT CONSENT'), ('pils', 'MINT PILs')):
    about = p + '-about.html'
    home = open(os.path.join(proj, p + '.html'), encoding='utf-8').read()
    cfg = json.loads(CFG.search(home).group(2))
    for lst in (cfg.get('links', []), cfg.get('tabs', [])):
        for l in lst:
            if l.get('href') == 'about.html': l['href'] = about
    page = CFG.sub(lambda m: m.group(1) + json.dumps(cfg) + m.group(3), src, count=1)
    page = re.sub(r'<title>[^<]*</title>', f'<title>About AMPM Training – {name}</title>', page, count=1)
    page = page.replace('class="page pg-about"', f'class="page pg-about pg-{p}-about"')
    open(os.path.join(proj, about), 'w', encoding='utf-8').write(page)
    # every About link on this product's pages (header/tabs config, page links, footer "About AMPM")
    n = 0
    for f in glob.glob(os.path.join(proj, p + '*.html')):
        if os.path.basename(f) == about: continue
        s = open(f, encoding='utf-8').read()
        m = CFG.search(s)
        if m:
            c = json.loads(m.group(2))
            for lst in (c.get('links', []), c.get('tabs', [])):
                for l in lst:
                    if l.get('href') == 'about.html': l['href'] = about
            s = s[:m.start(2)] + json.dumps(c) + s[m.end(2):]
        s2 = s.replace('href="about.html"', f'href="{about}"')
        n += s2.count(f'href="{about}"')
        open(f, 'w', encoding='utf-8').write(s2)
    print(about, 'links', n)
