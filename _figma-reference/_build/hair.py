# rows that differ from both neighbours while the neighbours match each other (a lone hairline across the width)
import sys
from PIL import Image, ImageChops
for f in sys.argv[1:]:
    im=Image.open(f).convert('RGB'); W,H=im.size
    rows=[im.crop((0,y,W,y+1)) for y in range(H)]
    hits=[]
    for y in range(2,H-2):
        a,b,c=rows[y-1],rows[y],rows[y+1]
        if max(x[1] for x in ImageChops.difference(a,c).getextrema())>6: continue
        d=ImageChops.difference(a,b).convert('L')
        n=sum(1 for v in d.getdata() if v>8)
        if n>W*0.6: hits.append((y,n,im.getpixel((W//2,y-1)),im.getpixel((W//2,y))))
    import os; print(os.path.basename(f), hits[:12])
