# usage: runs.py <png> <out.txt>
# Rows of a text-free render that can be repeated or removed unnoticed: row y == row y+1 (within tolerance)
# across the whole width. Writes "a-b,a-b:#rrggbb,..." (design rows); a colour is added when the run is one flat
# colour across the width, so added space can be a plain block of that colour.
import sys
from PIL import Image, ImageChops
im = Image.open(sys.argv[1]).convert('RGB')
W, H = im.size
same = []
prev = im.crop((0, 0, W, 1))
for y in range(1, H):
    row = im.crop((0, y, W, y + 1))
    d = ImageChops.difference(prev, row).getextrema()
    same.append(max(c[1] for c in d) <= 6)
    prev = row
runs, start = [], None
for y, ok in enumerate(same):
    if ok and start is None: start = y
    if not ok and start is not None:
        if y - start >= 6: runs.append((start + 1, y))
        start = None
if start is not None and len(same) - start >= 6: runs.append((start + 1, len(same)))
out = []
for a, b in runs:
    mid = (a + b) // 2
    row = im.crop((0, mid, W, mid + 1))
    ex = row.getextrema()
    flat = max(hi - lo for lo, hi in ex) <= 4
    c = row.getpixel((W // 2, 0))
    out.append(f'{a}-{b}' + (':#%02X%02X%02X' % c if flat else ''))
open(sys.argv[2], 'w').write(','.join(out))
print(sys.argv[1].split('/')[-1].split('\\')[-1], len(runs), 'runs')
