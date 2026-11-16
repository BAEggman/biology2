#!/bin/sh
# A11_build.sh <workdir> — 11장(광합성) 덧붙임의 +정거장 그림(2026-11-16 · Opus 5.5 · 지시서 차례 7)을 다시 만든다(같은 픽셀).
#  L45a: 바탕(2026-11-16 의 lesson/img/L45a.webp 무손실) + M1(잎 널과 꼬투리 사이 — 하늘 꼭대기에서 곧게 내려온 햇살 기둥이 잎 모자 여자의 무릎 위 열린 도시락으로 쏟아져 샌드위치
#        · 다른 손으로 물뿌리개를 기울임 · 곁의 빨간 셔츠 남자가 빈 접시를 무릎에 두고 그 도시락의 샌드위치를 집음).
#        첫 판 L1(풀밭만 오린 구역)은 햇살이 잎 널 모서리에서 끊겨 「널에서 빛이 나온다」 · 「제 도시락을 싸는지 모르겠다」(일치 검사 1회 6·4·0)
#        → 하늘까지 세로로 오린 구역(M)에서 다시 그렸다.
set -e
W=${1:-/tmp/A11_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/A11_src"
mkdir -p "$W/a/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/L45a_base_1116.webp').convert('RGB').save(f'{W}/a/base0.png')
Image.open(f'{S}/M1.webp').convert('RGB').save(f'{W}/a/z/gem_M1.png')
PY
cd "$W/a" && $Z crop base0.png z M 840 0 1300 1144 && $CM z/up_M.png z/gem_M1.png z/cm_M1.png && $Z paste base0.png z M z/cm_M1.png final.png "970,0,1064,600;916,582,1220,910"
echo "→ $W/a/final.png"
