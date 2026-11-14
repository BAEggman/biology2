#!/bin/bash
# L13c_build.sh <작업 폴더> — L13c 그림을 Gemini 원본(L13c_src/)에서 다시 만든다(같은 픽셀).
#  S1 = Gemini 가 장면 하나를 통째로 그린 바탕(1024 × 572 — 출연진 그림 L13c_ref_cast 를 올리고 「사건 하나가 벌어지는 장면」으로 · 2048 로 키움)
#  Z1 = 흰 덩이와 나뭇가지 팔 전령에게도 두 쪽 판 · 전령의 뒷팔을 성벽 틈 쪽으로 · 「Z」 잠 표시 지움
#  Z2b = 판 셋을 서로 떼어 놓음(붙으면 넉 쪽 판으로 읽힌다) · Z3 = 주민 셔츠 깃 밖으로 보라 망토
#  Z4 = 탑 위 궁수가 몸을 숙여 아래 여자 쪽으로 겨눔 · 화살 깃을 희게(붉은 깃이 「배지」로 읽혔다 — 일치 검사 1회)
#  그 위에 L13c_pil.py — 조끼 단추 · 배지 · 구슬 사슬 · 흰 쪽지 · 등불 빛과 깃발 · 빈 배지 자리.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L13c_src/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('Z1', 'Z2b', 'Z3', 'Z4'): Image.open(f'{D}/L13c_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
Z="python3 $D/zone3.py"
$Z crop "$W/base0.png" "$W/z" Z1 220 400 940 820
$Z paste "$W/base0.png" "$W/z" Z1 "$W/z/gem_Z1.png" "$W/base1.png" "234,440,800,815"
$Z crop "$W/base1.png" "$W/z" Z2 380 380 1200 840
$Z paste "$W/base1.png" "$W/z" Z2 "$W/z/gem_Z2b.png" "$W/base2.png" "445,465,805,695"
$Z crop "$W/base1.png" "$W/z" Z3 1680 700 2048 1010
$Z paste "$W/base2.png" "$W/z" Z3 "$W/z/gem_Z3.png" "$W/base3.png" "1700,740,2040,1008" --fit="1800,825,1875,915"
$Z crop "$W/base3.png" "$W/z" Z4 1740 20 2048 520
$Z paste "$W/base3.png" "$W/z" Z4 "$W/z/gem_Z4.png" "$W/base4.png" "1830,75,2044,498"
python3 "$D/L13c_pil.py" "$W/base4.png" "$W/final.png"
echo "→ $W/final.png"
