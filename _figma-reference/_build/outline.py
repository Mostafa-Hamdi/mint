# usage: outline.py file.svg [imgdir]  -> compact element outline
import sys, re, base64, os, hashlib
import xml.etree.ElementTree as ET
f=sys.argv[1]; imgdir=sys.argv[2] if len(sys.argv)>2 else None
NS='{http://www.w3.org/2000/svg}'; XL='{http://www.w3.org/1999/xlink}href'
root=ET.parse(f).getroot()
defs={}; imgs={}
for el in root.iter():
    i=el.get('id')
    if i: defs[i]=el
# image data: <image id=.. xlink:href=data:..>
for el in root.iter(NS+'image'):
    h=el.get(XL) or el.get('href') or ''
    m=re.match(r'data:image/(\w+);base64,(.*)',h,re.S)
    if m:
        data=base64.b64decode(m.group(2)); ext='jpg' if m.group(1)=='jpeg' else m.group(1)
        hid=hashlib.md5(data).hexdigest()[:8]
        imgs[el.get('id')]=(hid+'.'+ext, el.get('width'), el.get('height'))
        if imgdir:
            os.makedirs(imgdir,exist_ok=True); p=os.path.join(imgdir,hid+'.'+ext)
            if not os.path.exists(p): open(p,'wb').write(data)
def pat_img(pid):
    p=defs.get(pid)
    if p is None: return None
    for u in p.iter(NS+'use'):
        ref=(u.get(XL) or u.get('href') or '').lstrip('#'); tr=u.get('transform','')
        if ref in imgs: return imgs[ref][0]+' '+tr
    return pid
def grad(gid):
    g=defs.get(gid)
    if g is None: return gid
    st=' '.join((s.get('stop-color') or '#000')+('/'+s.get('stop-opacity') if s.get('stop-opacity') else '')+'@'+(s.get('offset') or '0') for s in g.iter(NS+'stop'))
    return f"{g.tag.replace(NS,'')}({g.get('x1')},{g.get('y1')}->{g.get('x2')},{g.get('y2')}) {st}"
def paint(v):
    if not v: return ''
    m=re.match(r'url\(#(.*)\)',v)
    if m:
        k=m.group(1)
        if k.startswith('pattern'): return 'IMG:'+str(pat_img(k))
        return grad(k)
    return v
def bbox(d):
    n=[float(x) for x in re.findall(r'-?\d*\.?\d+(?:e-?\d+)?',d)]
    xs=n[0::2]; ys=n[1::2]
    if not xs: return ''
    return f'{min(xs):.0f},{min(ys):.0f} {max(xs)-min(xs):.0f}x{max(ys)-min(ys):.0f}'
out=[]
def walk(el,dep):
    tag=el.tag.replace(NS,'')
    if tag in ('defs','clipPath','mask'): return
    ind='  '*dep; a=el.attrib
    ex=''
    for k in ('opacity','fill-opacity','stroke','stroke-width','transform','filter','style'):
        if k in a and not (k=='style' and 'white-space' in a[k]): ex+=f' {k}={paint(a[k]) if k=="stroke" else a[k]}'
    if tag=='g':
        out.append(f"{ind}G {a.get('id','')}{ex}")
        for c in el: walk(c,dep+1)
        return
    if tag=='rect':
        out.append(f"{ind}R {a.get('id','')} {a.get('x','0')},{a.get('y','0')} {a.get('width')}x{a.get('height')} rx={a.get('rx','')} fill={paint(a.get('fill'))}{ex}")
    elif tag in ('path','circle','ellipse','line'):
        b=bbox(a.get('d','')) if tag=='path' else f"{a.get('cx',a.get('x1'))},{a.get('cy',a.get('y1'))} r={a.get('r',a.get('rx'))}"
        out.append(f"{ind}P {a.get('id','')} [{b}] fill={paint(a.get('fill'))}{ex}")
    elif tag=='text':
        lines=[f"({t.get('x')},{t.get('y')})"+repr(t.text or '') for t in el.iter(NS+'tspan')]
        st=[]
        for t in el.iter(NS+'tspan'):
            if t.get('fill') or t.get('font-weight'): st.append(f"[{t.get('font-weight','')}/{t.get('fill','')}]{t.text!r}")
        out.append(f"{ind}T {a.get('font-family')} {a.get('font-size')}/{a.get('font-weight','400')} ls={a.get('letter-spacing')} fill={paint(a.get('fill'))}{ex} :: "+' | '.join(lines)+(' {'+' '.join(st)+'}' if st else ''))
    elif tag=='image':
        pass
    else:
        out.append(f"{ind}{tag} {a.get('id','')}")
    for c in el:
        if tag!='text': walk(c,dep+1)
walk(root,0)
def fx(t):
    try: return t.encode('latin1').decode('utf8')
    except Exception: return t
sys.stdout.reconfigure(encoding='utf-8')
print('\n'.join(fx(x) for x in out))
