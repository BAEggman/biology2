#!/bin/sh
# A1213_build.sh <workdir> — 12장 덧붙임의 +정거장 그림(2026-11-15 · Opus 5.5)을 다시 만든다(같은 픽셀).
#  L19a: 바탕(2026-11-15 의 lesson/img/L19a.webp 를 무손실로 둔 것) + DA1(바닥 가운데 배양 접시 · 갈고리 발 · 잿빛 덩이)
#  L19d: 바탕(같은 날의 L19d.webp) + DC1(오른쪽 아래 마루의 검은 게 무리 둘 · 말뚝 울 · 붉은 호스)
set -e
W=${1:-/tmp/A1213_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/A1213_src"
mkdir -p "$W/a/z" "$W/d/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/L19a_base_1115.webp').convert('RGB').save(f'{W}/a/base0.png')
Image.open(f'{S}/L19d_base_1115.webp').convert('RGB').save(f'{W}/d/base0.png')
Image.open(f'{S}/DA1.webp').convert('RGB').save(f'{W}/a/z/gem_DA1.png')
Image.open(f'{S}/DC1.webp').convert('RGB').save(f'{W}/d/z/gem_DC1.png')
PY
cd "$W/a" && $Z crop base0.png z DA 880 830 1400 1123 && $CM z/up_DA.png z/gem_DA1.png z/cm_DA1.png && $Z paste base0.png z DA z/cm_DA1.png final.png "990,960,1365,1110"
cd "$W/d" && $Z crop base0.png z DC 1560 800 2048 1074 && $CM z/up_DC.png z/gem_DC1.png z/cm_DC1.png && $Z paste base0.png z DC z/cm_DC1.png final.png "1650,940,2048,1074"
echo "→ $W/a/final.png · $W/d/final.png"
