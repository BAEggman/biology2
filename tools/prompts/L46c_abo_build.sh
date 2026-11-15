#!/bin/sh
# L46c_abo_build.sh <작업 폴더> — L46c 면역 덧붙임(ABO 응집 · 2026-11-15 · Opus 5.5)을 같은 픽셀로 다시 만든다.
#   바탕 = 덧붙임 전 L46c(커밋 88b71a8 의 lesson/img/L46c.webp) · Gemini 조각 = L46c_src/GB.webp(GA2 → GB 같은 채팅 — 피 주머니 · 관 · 바늘 · 노란 층 위 원반 다섯)
#   → colormatch → zone3 paste(상자 둘) → L46c_abo_pil.py(주머니 점 · 떨어지는 원반 · 막대사탕 · 집게 다섯 · 식탁 원반의 초록 막대사탕).
set -e
W=${1:?작업 폴더}; P=/tmp/b2/tools/prompts
mkdir -p "$W"
git -C /tmp/b2 show 88b71a8:lesson/img/L46c.webp > "$W/base0.webp"
python3 -c "
from PIL import Image
Image.open('$W/base0.webp').convert('RGB').save('$W/base0.png')
Image.open('$P/L46c_src/GB.webp').save('$W/gem_GB.png')
"
cd "$W"
python3 $P/zone3.py crop base0.png . GA 0 0 720 405
python3 $P/colormatch.py up_GA.png gem_GB.png gemc_GB.png
python3 $P/zone3.py paste base0.png . GA gemc_GB.png b1.png "0,0,252,338;252,116,606,338" 28
python3 $P/L46c_abo_pil.py b1.png final.png
echo "→ $W/final.png"
