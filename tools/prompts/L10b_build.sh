#!/bin/bash
# L10b_build.sh <작업 폴더> — L10b 그림을 Gemini 원본(L10b_src/)에서 다시 만든다(같은 픽셀).
#  s2.webp = 둘째 바탕(채택 — 돔을 넓힌 밑그림 L10b_sketch.py) · Z1(돔 안 할아버지) · Z2(나무판 든 셋) · Z3(황제) · Z4(칠장이 · 받침대 객차 · 페인트 통) · Z5(짐꾼) · Z6b(콩 모양 손님채 · 오두막) · Z7(천막 지붕의 사슬과 구멍) = 구역 편집 결과.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L10b_src/s2.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base.png')
for n in ('Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6b', 'Z7'): Image.open(f'{D}/L10b_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
python3 "$D/L10b_pil0.py" base.png z/gem_Z1.png q1.png                      # Z1 은 손으로 잰 변환으로(Gemini 가 돔 안만 다시 잡아 돌려줌)
python3 "$D/zone3.py" crop q1.png z Z2 1330 280 1960 600
python3 "$D/zone3.py" crop q1.png z Z3 120 310 400 600
python3 "$D/zone3.py" crop q1.png z Z4 340 850 900 1110
python3 "$D/zone3.py" crop q1.png z Z5 1280 800 1640 1110
python3 "$D/zalign.py" q1.png z Z2 z/gem_Z2.png q2.png "1336,286,1954,586" --tone=1
python3 "$D/zalign.py" q2.png z Z3 z/gem_Z3.png q3.png "126,316,394,586" --tone=1
python3 "$D/zalign.py" q3.png z Z4 z/gem_Z4.png q4.png "360,856,846,1104" --tone=1
python3 "$D/zalign.py" q4.png z Z5 z/gem_Z5.png q5.png "1432,806,1634,1104;1326,1000,1432,1104;1408,968,1432,1000" --key=900,80
python3 "$D/zone3.py" crop q5.png z Z6 1630 720 2048 1130
python3 "$D/L10b_bean.py" z/gem_Z6b.png z/gem_Z6c.png                        # 손님채를 세로로 눌러 길고 낮은 콩 꼴로
python3 "$D/zalign.py" q5.png z Z6 z/gem_Z6c.png q6.png "1636,740,2046,1126" --key=200,150 --M=0.9773,6.2,-0.7
python3 "$D/zone3.py" crop q6.png z Z7 880 750 1230 960
python3 "$D/zalign.py" q6.png z Z7 z/gem_Z7.png q7.png "886,756,1152,954;1152,866,1224,954" --tone=1
python3 "$D/L10b_pil1.py" q7.png final.png
echo "→ $W/final.png"
