#!/bin/sh
# Rend une scène et en fait un aperçu réduit pour relecture : illustrations/apercu.sh co1_desserte
cd "$(dirname "$0")/.." && python3 illustrations/build.py "$1" >/dev/null && for f in $(ls -t widget/illustrations/*.png | head -1); do python3 -c "
from PIL import Image; import sys; im=Image.open('$f').convert('RGB'); im.thumbnail((1100,1100)); im.save('${2:-/tmp/apercu.jpg}', quality=88)"; echo "$f"; done
