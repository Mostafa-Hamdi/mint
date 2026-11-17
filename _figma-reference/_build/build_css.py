# Converts "123.5u" tokens into calc(var(--u)*123.5) so the 1440 design scales
# 1:1 at >=1440px and proportionally below it (desktop layout only).
import re, sys
src, dst = sys.argv[1], sys.argv[2]
css = open(src, encoding='utf-8').read()
css = re.sub(r'(?<![\w.#-])(-?\d+(?:\.\d+)?)u\b', lambda m: f'calc(var(--u) * {m.group(1)})', css)
open(dst, 'w', encoding='utf-8').write(css)
print('built', dst, len(css))
