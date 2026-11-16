#!/bin/sh
# A42_build.sh <workdir> — 42장(소화계) 덧붙임의 +정거장 그림(2026-11-16 · Opus 5.5 · 지시서 차례 7)을 다시 만든다(같은 픽셀).
#  바탕 = 2026-11-16 의 lesson/img/L12a · L12b · L12d.webp 를 무손실로 둔 것.
#  L12a: AB2(흙 항아리 물줄기 밑의 첫 병부터 오른쪽 아래로 닿아 이어진 탄산 병 여섯 — 검은 셋 · 노란 불꽃 · 위쪽부터 검어지는 넷째 · 초록 둘
#        · 같은 채팅 둘째 고침 = 병마다 유리 빛줄기 · 따로 떨어진 병 · 사슬을 짧게) → L12a_pil.py(물을 맞은 첫 병 · 불꽃 자리 병에서 튀어 날아가는 빨간 왕관 마개 = 활성 부위가 드러남)
#  L12d: DM2(벽 높이 긴 나무 선반 — 치약 짜 넣는 어금니 단지 · 구멍 난 이 · 뼈에 기댄 성냥갑 / 칼 꽂힌 소금 덩이 · 핥는 흰 염소 / 구린 노란 덩이 단지 · 은빛 구슬 단지
#        · 같은 채팅 둘째 고침 = 1.2 배 · 선반을 머리 바로 위로 — Gemini 가 위로 69px 더 그려 돌려줌 → 정합이 −65px 로 맞춘다)
#  L12b: C2(흰 오솔길과 흙길이 만나는 자리 위 — 지그재그 꼬리 작은 기름방울을 뭉쳐 주황 구명 튜브 낀 큰 공을 만드는 일꾼 · 짐꾼의 기름방울에도 튜브
#        · 둘째 고침 = 꼬리를 물결에서 지그재그로(올챙이로 읽힐까)) → J3(둑 위 — 곳간 벽돌 벽에서 나온 초록 호스가 매듭 · 벽 쪽이 불룩 · 누런 피부의 아픈 일꾼
#        · 첫 판 J1 은 「레몬빛 피부」가 이름난 만화 집안처럼 그려져 Gemini 스스로 이어 고치기를 거절 → 새 채팅에서 「칙칙한 겨자빛 · 짐꾼과 같은 얼굴」)
#        → E1(초록 방울 떨어지는 자리 오른쪽의 큰 노란 기름 덩이가 금 가며 초록 테 두른 작은 방울로 흩어짐)
#        → A2(앞벽 윗전에 허리까지 박힌 일꾼 둘 — 사슬 왼쪽 끝에서 뗀 구슬 하나 · 두 손에 하나씩 떼어 낸 짝 / 뗏목 일꾼 둘 — 사슬 오른쪽 끝에서 뗀 구슬 · 빛깔 네모 종이띠를 가위로 낱장
#        · 둘째 고침 = 뗀 구슬과 사슬 사이 물 틈 · 가운데 일꾼은 구슬 하나씩)
#        → L12b_pil.py(일치 검사 2회 「종이띠 빛깔 네모가 옅다」 → 띠와 낱장의 네모만 채도 ↑)
set -e
W=${1:-/tmp/A42_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/A42_src"
mkdir -p "$W/a/z" "$W/b/z" "$W/d/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
for sub, base, gems in (('a', 'L12a', ['AB2']), ('b', 'L12b', ['C2', 'J3', 'E1', 'A2']), ('d', 'L12d', ['DM2'])):
    Image.open(f'{S}/{base}_base_1116.webp').convert('RGB').save(f'{W}/{sub}/base0.png')
    for g in gems: Image.open(f'{S}/{g}.webp').convert('RGB').save(f'{W}/{sub}/z/gem_{g}.png')
PY
cd "$W/a" && $Z crop base0.png z AB 420 520 1060 1080 && $CM z/up_AB.png z/gem_AB2.png z/cm_AB2.png && $Z paste base0.png z AB z/cm_AB2.png a1.png "476,545,612,705;560,672,718,862;678,800,900,975"
python3 $D/L12a_pil.py a1.png final.png
cd "$W/d" && $Z crop base0.png z DM 560 0 1700 560 && $CM z/up_DM.png z/gem_DM2.png z/cm_DM2.png && $Z paste base0.png z DM z/cm_DM2.png final.png "596,40,1694,340"
cd "$W/b" && $Z crop base0.png z C 300 200 800 640 && $CM z/up_C.png z/gem_C2.png z/cm_C2.png && $Z paste base0.png z C z/cm_C2.png b1.png "348,322,474,464;455,272,642,480"
$Z crop b1.png z J 880 340 1320 680 && $CM z/up_J.png z/gem_J3.png z/cm_J3.png && $Z paste b1.png z J z/cm_J3.png b2.png "1028,370,1280,553"
$Z crop b2.png z E 340 520 780 790 && $CM z/up_E.png z/gem_E1.png z/cm_E1.png && $Z paste b2.png z E z/cm_E1.png b3.png "438,630,718,730"
$Z crop b3.png z A 740 560 1320 880 && $CM z/up_A.png z/gem_A2.png z/cm_A2.png && $Z paste b3.png z A z/cm_A2.png b4.png "796,620,1318,762"
python3 $D/L12b_pil.py b4.png final.png
echo "→ $W/a/final.png · $W/b/final.png · $W/d/final.png"
