#!/bin/bash
# L43d_build.sh <작업 폴더> — L43d 그림을 Gemini 원본(L43d_src/)에서 다시 만든다(같은 픽셀).
#  s1.webp = 바탕(밑그림 L43d_sketch.py — 담 띠 둘 · 벽돌집 · 눈알 · 응원단 두 조 · 오른쪽 길가 세 묶음만 · 마당 바닥은 비움)
#  Z2(눈알) · Z4(달걀 · 양) · Z5(두 아기) · Z6(뼈) = 또렷하게 다시 그려 제자리에 붙인다 · B2 = 어른 옷 속 아기를 주황 스웨터 · 갈색 장화의 아기로 바꿈
#  Z1(벽돌집 + 초록 응원단) · Z3(보라 응원단) · PR(인쇄 기계 한 대) = 오려 붙일 조각의 원본 — 붙이는 것은 L43d_pil.py.
#  두 마당의 가구(끈 · 단 · 깔개 · 팻말 · 기계 · 종이띠) · 화살 · 끈 타래 · 흰자 · 배지는 모두 L43d_pil.py 가 그린다.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L43d_src/s1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base.png')
for n in ('PR', 'Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6', 'B2'): Image.open(f'{D}/L43d_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
python3 "$D/zone3.py" crop base.png z Z2 0 730 180 990
python3 "$D/zone3.py" crop base.png z Z4 1420 0 2048 475
python3 "$D/zone3.py" crop base.png z Z5 1430 470 2048 850
python3 "$D/zone3.py" crop base.png z Z6 1400 850 2048 1144
python3 "$D/zalign.py" base.png z Z2 z/gem_Z2.png r2.png "4,734,176,986" --key=20,20
python3 "$D/zalign.py" r2.png z Z4 z/gem_Z4.png r4.png "1424,4,2044,471" --key=20,20
python3 "$D/zalign.py" r4.png z Z5 z/gem_Z5.png r5.png "1434,474,2044,846" --key=20,20
python3 "$D/zalign.py" r5.png z Z6 z/gem_Z6.png r6.png "1404,854,2044,1144" --key=20,20
python3 "$D/zone3.py" crop r6.png z B2 1690 556 2044 850
python3 "$D/zone3.py" paste r6.png z B2 z/gem_B2.png r7.png "1694,560,2040,846" --fit="1742,560,1924,846"
python3 "$D/L43d_pil.py" r7.png z/gem_Z1.png z/gem_Z3.png z/gem_PR.png final.png
echo "→ $W/final.png"
