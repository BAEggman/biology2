#!/bin/sh
# A18_build.sh <workdir> — 18장 덧붙임의 +정거장 그림(2026-11-15 · Opus 5.5)을 다시 만든다(같은 픽셀).
#  L25b: 바탕(2026-11-15 의 L25b.webp 무손실) + BF1(왼쪽 위 나무 아래 줄무늬 차양 가방 공방 — 다 만든 가방이 판매대에 오르자 셔터가 반쯤 쾅 · 두 탭 가운데 BFa)
#  L25a: 바탕 + AI1(맨 뒤 줄 왼쪽 바깥 풀밭 — 제 작은 빨간 매트 위 작은 인쇄 기계 · 종이띠 끝에서 걸어 나오는 대머리 문지기 · AIa)
#  L37b: 바탕 + CF1(오른쪽 아래 바닥 — 초록 잎 잉크로 꽃 도장을 찍는 꼬마 · 꽃 자국에서 멈춘 작은 기계(거미줄) · 세로로 갈라진 두 끈의 같은 자리 꽃 · 같은 채팅 둘째 고침 = 끈 왼끝을 푼 끝으로)
#        → 원래 회색 기계(s4) 모양 되돌림(restore_poly — Gemini 가 오른쪽 면을 깎았다) → CW1(오른쪽 벽 선반 — 엄마 · 아빠 짚 뭉치 · 비누 거품 통 · 둘째 고침 = 엄마 쪽 긴 종이띠)
#        → L37b_pil.py(일치 검사 1회 뒤 — 엄마 머릿수건의 분홍이 꽃 자국 분홍과 같아 하늘색 · 흰 물방울로)
set -e
W=${1:-/tmp/A18_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/A18_src"
mkdir -p "$W/b/z" "$W/a/z" "$W/c/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
for sub, base, gems in (('b', 'L25b', ['BF1']), ('a', 'L25a', ['AI1']), ('c', 'L37b', ['CF1', 'CW1'])):
    Image.open(f'{S}/{base}_base_1115.webp').convert('RGB').save(f'{W}/{sub}/base0.png')
    for g in gems: Image.open(f'{S}/{g}.webp').convert('RGB').save(f'{W}/{sub}/z/gem_{g}.png')
PY
cd "$W/b" && $Z crop base0.png z BF 200 20 760 335 && $CM z/up_BF.png z/gem_BF1.png z/cm_BF1.png && $Z paste base0.png z BF z/cm_BF1.png final.png "252,42,492,288"
cd "$W/a" && $Z crop base0.png z AI 0 60 560 375 && $CM z/up_AI.png z/gem_AI1.png z/cm_AI1.png && $Z paste base0.png z AI z/cm_AI1.png final.png "40,200,240,312"
cd "$W/c" && $Z crop base0.png z CF 1450 830 2048 1144 && $CM z/up_CF.png z/gem_CF1.png z/cm_CF1.png && $Z paste base0.png z CF z/cm_CF1.png c1.png "1558,865,2048,1122;1479,1005,1558,1122" 28 --ident
python3 $D/restore_poly.py base0.png c1.png "1352,845;1475,824;1592,852;1595,1000;1587,1030;1500,1052;1445,1063;1400,1052;1350,1032" 1.5
$Z crop base0.png z CW 1600 20 2048 440 && $CM z/up_CW.png z/gem_CW1.png z/cm_CW1.png && $Z paste c1.png z CW z/cm_CW1.png c2.png "1750,140,2015,438"
python3 $D/L37b_pil.py c2.png final.png
echo "→ $W/b/final.png · $W/a/final.png · $W/c/final.png"
