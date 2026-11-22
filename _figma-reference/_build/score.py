# usage: score.py ref.png web.png -> % pixels within diff<30 over ref area
import sys
from PIL import Image, ImageChops
a=Image.open(sys.argv[1]).convert('RGB'); b=Image.open(sys.argv[2]).convert('RGB')
b=b.crop((0,0,a.width,a.height))
d=ImageChops.difference(a,b).convert('L')
h=d.histogram(); print(f'{sum(h[:30])/sum(h)*100:.1f}%')
