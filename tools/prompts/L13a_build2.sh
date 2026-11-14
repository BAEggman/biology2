#!/bin/sh
# L13a_build2.sh <workdir> — L13a 다시 짓기 「성벽이 뚫린 첫 순간」(2026-11-14 · 사건 장면) 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 출연진 그림 = L13c_src/cast_ref.webp · 1024 → 2048) → 구역 편집 A1 ~ A4(zone3.py) → L13a_pil2.py
#  (옛 판 — 조각 세우기 — 은 L13a_build.sh · L13a_src/ 에 그대로 둔다.)
set -e
W=${1:-/tmp/L13a_build2}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L13a_src2"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('A1', 'A2', 'A3', 'A4'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z A1 840 330 1460 730 ;  $Z paste base0.png z A1 z/gem_A1.png base1.png "1030,345,1450,722"          # 세균을 통째로 입 안에 · 파리채에 맞는 둘째 세균
python3 "$D/restore_poly.py" base0.png base1.png "1420,560;1452,560;1452,724;1370,724;1414,636"                       #   오두막 지붕 모서리는 원래대로
$Z crop base0.png z A2 1690 640 2048 1144 ; $Z paste base1.png z A2 z/gem_A2.png base2.png "1700,770,2010,1142"        # 잠옷 병정 — 종이 · 책 · 장화 한 짝 · 맨발 · 털모자
$Z crop base0.png z A3 420 600 900 1000 ;   $Z paste base2.png z A3 z/gem_A3.png base3.png "424,625,730,800"            # 금빛 꼰 밧줄 · 자루로 거꾸로 빠지는 세균
$Z crop base2.png z A4 1540 860 1860 1144 ; $Z paste base3.png z A4 z/gem_A4.png base4.png "1600,930,1760,1100"        # 털 뭉치 둘 → 계단 위 털모자 하나
python3 "$D/L13a_pil2.py" base4.png final.png
echo "→ $W/final.png"
