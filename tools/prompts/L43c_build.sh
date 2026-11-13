#!/bin/bash
# L43c_build.sh <작업 폴더> — L43c 그림을 Gemini 원본(L43c_src/)에서 다시 만든다(같은 픽셀).
#  s1.webp = 바탕(밑그림 L43c_sketch.py · 끈 없이 그리게 함) · Z1(응원단 · 양복 · 깔개 · 켜진 인쇄 기계) · Z2(집사) · Z3(사이렌 상자의 문지기) · Z4(꺼진 인쇄 기계) = 또렷하게 다시 그리기
#  P1 · P2 = 두 인쇄 기계를 옛 인쇄기(옆틀 둘 · 굴대 셋 · 톱니 둘 · 벨트 · 크랭크)로 바꿈 · W1 · W2 = 깔개 위 일꾼 넷의 셔츠를 노랑으로(L43a 의 일꾼과 같은 차림)
#  끈 · 깔판 · 빈 단 둘 · 단 앞면의 빛깔 자리 · 방석 옮기기는 L43c_pil.py 가 한다.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L43c_src/s1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base.png')
for n in ('Z1', 'Z2', 'Z3', 'Z4', 'P1', 'P2', 'W1', 'W2'): Image.open(f'{D}/L43c_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
python3 "$D/zone3.py" crop base.png z Z1 330 600 1450 1144
python3 "$D/zone3.py" crop base.png z Z2 90 230 540 520
python3 "$D/zone3.py" crop base.png z Z3 900 182 1150 430
python3 "$D/zone3.py" crop base.png z Z4 1460 240 1890 550
python3 "$D/zalign.py" base.png z Z1 z/gem_Z1.png q1.png "336,606,1444,1144" --key=400,16
python3 "$D/zalign.py" q1.png z Z2 z/gem_Z2.png q2.png "96,236,534,514" --key=20,20
python3 "$D/zalign.py" q2.png z Z3 z/gem_Z3.png q3.png "906,188,1144,424" --key=20,20
python3 "$D/zalign.py" q3.png z Z4 z/gem_Z4.png q4.png "1466,246,1884,544" --key=20,20
python3 "$D/zone3.py" crop q4.png z P1 1040 660 1470 1144
python3 "$D/zone3.py" crop q4.png z P2 1580 220 1900 540
python3 "$D/zone3.py" paste q4.png z P1 z/gem_P1.png q5.png "1052,706,1332,978"
python3 "$D/zone3.py" paste q5.png z P2 z/gem_P2.png q6.png "1622,250,1882,502"
python3 "$D/zone3.py" crop q6.png z W1 850 840 1120 1056
python3 "$D/zone3.py" crop q6.png z W2 1490 360 1710 536
python3 "$D/zone3.py" paste q6.png z W1 z/gem_W1.png q7.png "876,858,1096,1040"
python3 "$D/zone3.py" paste q7.png z W2 z/gem_W2.png q8.png "1508,372,1694,526" --fit="1530,400,1680,520"   # --fit: 붙일 상자가 조각을 거의 다 차지해 바깥 특징이 모자라다(없으면 닮음 변환이 1.04 배로 틀어진다)
python3 "$D/L43c_pil.py" q8.png final.png
echo "→ $W/final.png"
