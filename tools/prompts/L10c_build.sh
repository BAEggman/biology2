#!/bin/bash
# L10c_build.sh <작업 폴더> — L10c 그림을 Gemini 원본(L10c_src/)에서 다시 만든다(같은 픽셀).
#  s1.webp = 바탕(밑그림 L10c_sketch.py — 선로는 비워 둠) · ZC(무언극 배우 · 휜 빨간 몸) · ZD(에임스) · ZE(사다리 왼쪽 · 게 · 수리공) · ZG(사다리 가운데 · 오른쪽 받침대) = 또렷하게 다시 그린 구역.
#  ZA2(빨간 매직펜 교정원 · 칠장이) · ZB2(삽 일꾼 · 원숭이) · ZF2(뼈 비치는 기계의 푸른 빛줄기 · 부러진 끝) = 또렷하게 그린 ZA · ZB · ZF 를 다시 올려 사람 · 빛줄기를 바꾼 것(덱 예약과 겹쳐서 — L10c_설계.md). ZA · ZB · ZF.webp 는 그 원본(기록).
#  열차 여섯 · 구슬 사슬 · 빨간 동그라미 · 선로 · 보라 칸과 방울 · 검은 구슬은 L10c_trains.py(PIL).
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L10c_src/s1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base.png')
for n in ('ZA2', 'ZB2', 'ZC', 'ZD', 'ZE', 'ZF2', 'ZG'): Image.open(f'{D}/L10c_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
python3 "$D/zone3.py" crop base.png z ZA 20 330 250 820
python3 "$D/zone3.py" crop base.png z ZB 20 790 250 1140
python3 "$D/zone3.py" crop base.png z ZC 1030 360 1320 880
python3 "$D/zone3.py" crop base.png z ZD 1380 600 2048 1120
python3 "$D/zone3.py" crop base.png z ZE 300 20 1010 410
python3 "$D/zone3.py" crop base.png z ZF 1330 20 1870 350
python3 "$D/zalign.py" base.png z ZA z/gem_ZA2.png qa.png "24,334,246,804" --key=20,20 --F=2
python3 "$D/zalign.py" qa.png z ZB z/gem_ZB2.png qb.png "24,802,246,1136" --key=20,300 --F=2 --M=1,0,0      # 두 사람이 다 바뀌어 맞출 특징이 없다 — 같은 틀로 본다
python3 "$D/zalign.py" qb.png z ZC z/gem_ZC.png qc.png "1034,364,1316,876" --key=20,20
python3 "$D/zalign.py" qc.png z ZD z/gem_ZD.png qd.png "1384,604,2044,1116" --key=20,20
python3 "$D/zalign.py" qd.png z ZE z/gem_ZE.png qe.png "304,24,1006,406" --tone=1
python3 "$D/zalign.py" qe.png z ZF z/gem_ZF2.png qf.png "1334,24,1866,346" --tone=1
python3 "$D/zone3.py" crop qf.png z ZG 940 60 1400 400
python3 "$D/zalign.py" qf.png z ZG z/gem_ZG.png qg.png "992,100,1346,396" --tone=1
python3 "$D/L10c_trains.py" qg.png final.png
echo "→ $W/final.png"
