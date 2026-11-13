#!/bin/bash
# L12g_build.sh <작업 폴더> — L12g 그림을 Gemini 원본(L12g_src/)에서 다시 만든다(같은 픽셀).
#  s2.webp = 둘째 바탕(채택) · s1.webp = 첫 바탕(헛간 오른쪽 · 좌판만 옮겨 심음) · Z1 · Z2 · Z6 · ZL · Z7 · Z8 = 구역 편집 결과.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L12g_src/s2.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base.png')
Image.open(f'{D}/L12g_src/s1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/s1_2048.png')
for n in ('Z1', 'Z2', 'Z6', 'ZL', 'Z7', 'Z8'): Image.open(f'{D}/L12g_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
python3 "$D/L12g_pil0.py" base.png s1_2048.png p0.png
python3 "$D/zone3.py" crop p0.png z Z1 1270 320 1630 560
python3 "$D/zone3.py" paste p0.png z Z1 z/gem_Z1.png p1.png "1350,352,1516,492"
python3 "$D/zone3.py" crop p1.png z Z2 905 450 1105 750
python3 "$D/zone3.py" paste p1.png z Z2 z/gem_Z2.png p2.png "958,552,1056,702"
python3 "$D/L12g_pil6.py" p2.png z/gem_Z6.png p3.png
python3 "$D/zone3.py" crop p3.png z ZL 1613 750 2048 1040
python3 "$D/zone3.py" paste p3.png z ZL z/gem_ZL.png p4.png "1816,884,1896,1028;1914,836,1998,1028"
python3 "$D/zone3.py" crop p4.png z Z7 0 40 420 320
python3 "$D/zone3.py" paste p4.png z Z7 z/gem_Z7.png p5.png "22,58,292,328" --ident --R=2
python3 "$D/L12g_pil7.py" p5.png p5t.png
python3 "$D/zone3.py" crop p5t.png z Z8 1420 480 1630 620
python3 "$D/zone3.py" paste p5t.png z Z8 z/gem_Z8.png p6.png "1480,506,1588,614"
python3 "$D/L12g_pil1.py" p6.png final.png
echo "→ $W/final.png"
