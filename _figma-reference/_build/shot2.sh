#!/bin/sh
# usage: shot2.sh page.html width height out.png  (served from http://localhost:5500; narrow widths via same-origin iframe)
P="$1"; W="$2"; H="$3"; O="$4"; PR=/c/Users/Mosta/OneDrive/Desktop/flow/mint-pils
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
if [ $W -ge 800 ]; then
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --run-all-compositor-stages-before-draw --virtual-time-budget=10000 --window-size=$W,$H --screenshot="$(cygpath -w "$O")" "http://localhost:5500/$P" 2>/dev/null
else
  printf '<!doctype html><html><head><style>html,body{margin:0;overflow:hidden}iframe{border:0;display:block}</style></head><body><iframe src="/%s" width="%s" height="%s" scrolling="no"></iframe></body></html>' "$P" "$W" "$H" > "$PR/_shot.html"
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --run-all-compositor-stages-before-draw --virtual-time-budget=15000 --window-size=800,$H --screenshot="$(cygpath -w "$O.f.png")" "http://localhost:5500/_shot.html" 2>/dev/null
  rm -f "$PR/_shot.html"
  python -I -c "
from PIL import Image; import sys
im=Image.open(sys.argv[1]); im.crop((0,0,int(sys.argv[2]),im.height)).save(sys.argv[3])" "$(cygpath -w "$O.f.png")" $W "$(cygpath -w "$O")"; rm -f "$O.f.png"
fi
