#!/bin/sh
# A10_build.sh <workdir> — 10장(세포호흡) 덧붙임의 +정거장 그림(2026-11-16 · Opus 5.5 · 지시서 차례 7)을 다시 만든다(같은 픽셀).
#  바탕 = 2026-11-16 의 lesson/img/L31a · L31b · L31c.webp 를 무손실로 둔 것.
#  L31a: S1(붉은 커튼 문 오른쪽 벽의 세로 그림 안내판 — 붉은 정육면체 · 흰 공 → 화살 → 잿빛 연기 · 파란 물방울 · 금빛 동전 / 액자 셋 = 초록 당구대 · 레몬 · 벽돌 담장의 펌프집 · 글자 없음)
#  L31b: T1(입고실 가위 노인의 앞치마 위 가죽 허리띠 — 넥타이 · 립스틱 · 파란 짐표 · 빈 초록 네모 통 · 빈 파란 둥근 양동이 · 가죽 주머니 하나)
#        → L31b_pil.py(일치 검사 1회 「둥근 양동이 윗면이 연파랑이라 물이 찬 것으로 읽힌다」 → 테 안쪽을 어두운 속으로 = 빈 양동이 NAD⁺)
#  L31c: F1(열린 뒷문 안쪽 바닥 — 문턱 너머 바람(흰 물결 선 · 작은 흰 방울)에 X 눈으로 쓰러진 창백한 손님 · 노란 비옷 · 이마에 선글라스 · 붉은 블록 한 아름의 손님)
set -e
W=${1:-/tmp/A10_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/A10_src"
mkdir -p "$W/a/z" "$W/b/z" "$W/c/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
for sub, base, gems in (('a', 'L31a', ['S1']), ('b', 'L31b', ['T1']), ('c', 'L31c', ['F1'])):
    Image.open(f'{S}/{base}_base_1116.webp').convert('RGB').save(f'{W}/{sub}/base0.png')
    for g in gems: Image.open(f'{S}/{g}.webp').convert('RGB').save(f'{W}/{sub}/z/gem_{g}.png')
PY
cd "$W/a" && $Z crop base0.png z S 1640 0 2048 700 && $CM z/up_S.png z/gem_S1.png z/cm_S1.png && $Z paste base0.png z S z/cm_S1.png final.png "1878,98,2042,528"
cd "$W/b" && $Z crop base0.png z T 0 230 500 950 && $CM z/up_T.png z/gem_T1.png z/cm_T1.png && $Z paste base0.png z T z/cm_T1.png b1.png "45,600,228,772"
python3 $D/L31b_pil.py b1.png final.png
cd "$W/c" && $Z crop base0.png z F 1560 560 2048 1144 && $CM z/up_F.png z/gem_F1.png z/cm_F1.png && $Z paste base0.png z F z/cm_F1.png final.png "1722,768,2048,1120"
echo "→ $W/a/final.png · $W/b/final.png · $W/c/final.png"
