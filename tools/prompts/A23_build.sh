#!/bin/sh
# A23_build.sh <작업 폴더> — 23장 덧붙임(2026-11-16 · Opus 5.5 · 지시서 차례 8 의 둘째 몫)의 그림 둘(L35b · L35a)을 같은 픽셀로 다시 만든다.
#   바탕 = 덧붙임 전 그림(커밋 5e2bec1) · Gemini 조각 = A23_src/*.webp → colormatch → zone3 paste.
#   L35b: BSA1 = 하늘의 빨간 하트 수컷 까마귀(청록 · 보랏빛 부채 꽁지) + 수수한 암컷(성선택 · 성적 이형)
#         BTB1 = 데크 위 크기순 구슬 홈통 둘 — 가운데를 쪼인 홈통(분단성) · 양끝을 쪼인 홈통(안정화) · 작은 까마귀 둘
#         BPA1 = 개울 왼쪽 웅덩이의 짝 구슬(섞인 짝만 멀쩡 = 이형접합 우세) + 흔한 흰 구슬만 노리는 까마귀 · 발치의 검은 한 알(빈도의존)
#   L35a: ARB1 = 수문 앞 풀 둑의 크기가 고르게 커지는 검은 구슬 한 줄(연속 · 다인자) — 곁 연못은 두 빛깔(이산)
#   ⚠ L35b 의 세 오림은 모두 덧붙임 전 바탕(base0)에서 오리고, 붙임은 차례로(b1 → b2 → b3).
set -e
W=${1:?작업 폴더}; P=/tmp/b2/tools/prompts
mkdir -p "$W/z"; cd "$W"
for L in L35b L35a; do git -C /tmp/b2 show 5e2bec1:lesson/img/$L.webp > ${L}_base0.webp; done
python3 -c "
from PIL import Image
for L in ['L35b','L35a']: Image.open(L+'_base0.webp').convert('RGB').save(L+'_base0.png')
for n in ['BSA1','BTB1','BPA1','ARB1']: Image.open('$P/A23_src/'+n+'.webp').convert('RGB').save('z/gem_'+n+'.png')
"
python3 $P/zone3.py crop L35b_base0.png z BS 480 0 1320 290
python3 $P/zone3.py crop L35b_base0.png z BT 420 800 1100 1144
python3 $P/zone3.py crop L35b_base0.png z BP 1380 740 1800 1144
python3 $P/zone3.py crop L35a_base0.png z AR 1380 560 1900 1144
python3 $P/colormatch.py z/up_BS.png z/gem_BSA1.png z/cm_BSA1.png
python3 $P/zone3.py paste L35b_base0.png z BS z/cm_BSA1.png L35b_b1.png "895,5,1235,190"
python3 $P/colormatch.py z/up_BT.png z/gem_BTB1.png z/cm_BTB1.png
python3 $P/zone3.py paste L35b_b1.png z BT z/cm_BTB1.png L35b_b2.png "495,835,840,1140"
python3 $P/colormatch.py z/up_BP.png z/gem_BPA1.png z/cm_BPA1.png
python3 $P/zone3.py paste L35b_b2.png z BP z/cm_BPA1.png L35b_final.png "1500,890,1780,1140"
python3 $P/colormatch.py z/up_AR.png z/gem_ARB1.png z/cm_ARB1.png
python3 $P/zone3.py paste L35a_base0.png z AR z/cm_ARB1.png L35a_final.png "1550,710,1895,1100"
echo "→ $W/L35b_final.png · $W/L35a_final.png"
