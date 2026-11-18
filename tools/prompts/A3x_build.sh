#!/bin/sh
# A3x_build.sh <작업 폴더> — 29 · 30 · 35 ~ 39장 덧붙임(지시서 차례 9 의 둘째 몫) 그림을 A3x_src/*.webp 원본에서 같은 픽셀로 다시 만든다.
set -e
W=${1:?작업 폴더}; P=/tmp/b2/tools/prompts
mkdir -p "$W/z"; cd "$W"
for L in L22d L34a L36c; do
  git -C /tmp/b2 show HEAD:lesson/img/$L.webp > ${L}_base0.webp
  python3 -c "from PIL import Image; Image.open('${L}_base0.webp').convert('RGB').save('${L}_base0.png')"
done
python3 - "$P" <<'PY'
import sys
from PIL import Image
P = sys.argv[1]
for n in ['ZAA1', 'ZBA1', 'ZCA1', 'FLA1', 'GYA1', 'SDA1', 'FRA1']:
    Image.open(f'{P}/A3x_src/{n}.webp').convert('RGB').save(f'z/gem_{n}.png')
PY
Z="python3 $P/zone3.py"; CM="python3 $P/colormatch.py"

# 1. L22d (s11 ~ s13)
$Z crop L22d_base0.png z ZA 640 20 1440 470
$Z crop L22d_base0.png z ZB 680 420 1480 870
$Z crop L22d_base0.png z ZC 680 694 1480 1144
$CM z/up_ZA.png z/gem_ZAA1.png z/cm_ZAA1.png
$CM z/up_ZB.png z/gem_ZBA1.png z/cm_ZBA1.png
$CM z/up_ZC.png z/gem_ZCA1.png z/cm_ZCA1.png
$Z paste L22d_base0.png z ZA z/cm_ZAA1.png L22d_b1.png "800,100,1300,460"
$Z paste L22d_b1.png z ZB z/cm_ZBA1.png L22d_b2.png "960,425,1215,865"
$Z paste L22d_b2.png z ZC z/cm_ZCA1.png L22d_b3.png "950,865,1205,1140"
python3 $P/A3x_L22d_pil.py L22d_b3.png L22d_final.png

# 2. L34a (s13)
$Z crop L34a_base0.png z FL 1360 0 2048 360
$CM z/up_FL.png z/gem_FLA1.png z/cm_FLA1.png
$Z paste L34a_base0.png z FL z/cm_FLA1.png L34a_final.png "1630,5,2040,235"

# 3. L36c (s11 ~ s13)
$Z crop L36c_base0.png z GY 480 694 1280 1144
$Z crop L36c_base0.png z SD 1040 694 1840 1144
$Z crop L36c_base0.png z FR 1248 694 2048 1144
$CM z/up_GY.png z/gem_GYA1.png z/cm_GYA1.png
$CM z/up_SD.png z/gem_SDA1.png z/cm_SDA1.png
$CM z/up_FR.png z/gem_FRA1.png z/cm_FRA1.png
$Z paste L36c_base0.png z GY z/cm_GYA1.png L36c_b1.png "620,820,1115,1142"
python3 $P/A3x_L36c_pil.py

echo "A3x_build ok → $W/L22d_final.png · $W/L34a_final.png · $W/L36c_final.png"
