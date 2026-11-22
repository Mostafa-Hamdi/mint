# usage: bake.py <project dir> <dump file>
# Writes the re-flowed <section> markup captured by prerender.html back into the product pages,
# so they open already laid out (no re-flow at load time).
import sys, os, re, json, html as H
proj, dump = sys.argv[1], sys.argv[2]
raw = open(dump, encoding='utf-8').read()
m = re.search(r'<pre id="out">JSON_START(.*?)JSON_END</pre>', raw, re.S)
if not m: sys.exit('no JSON in dump')
data = json.loads(H.unescape(m.group(1)))
done = 0
for key, inner in data.items():
    page, bp = key.split('|')
    path = os.path.join(proj, page)
    s = open(path, encoding='utf-8').read()
    pat = re.compile(r'(<section class="fv fv-' + bp + r'\b[^>]*>)(.*?)(</section>)', re.S)
    if not pat.search(s):
        print('missing section', key); continue
    s = pat.sub(lambda mm: mm.group(1) + '\n' + inner.strip() + '\n' + mm.group(3), s, count=1)
    open(path, 'w', encoding='utf-8').write(s)
    done += 1
print('baked', done, 'sections')
