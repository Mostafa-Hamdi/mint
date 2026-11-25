# usage: runs.py <png> <out.txt>
# Rows of a text-free render that can be repeated or removed unnoticed: row y == row y+1 (within tolerance)
# across the whole width. Writes "a-b,a-b,..." runs (design rows, 1px = 1 unit at the frame width).
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
open(sys.argv[2], 'w').write(','.join(f'{a}-{b}' for a, b in runs))
print(sys.argv[1].split('/')[-1].split('\\')[-1], len(runs), 'runs')
