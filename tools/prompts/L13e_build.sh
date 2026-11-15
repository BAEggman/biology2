#!/bin/sh
# L13e_build.sh <workdir> — L13e 「무기고의 깃발 맞추기」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 장면 통째 · 1024 → 2048) → 구역 편집 Z1 ~ Z8(zone3.py: 같은 자리 오림 → Gemini → 정합해 상자만 붙임) → L13e_pil.py(글자 지우기 · 단추 · 배지)
#  오림(crop)은 그때그때의 바탕에서 했다 — 아래 순서 그대로 해야 같은 그림이 나온다. Z2 · Z3 은 첫 오림(가로로 긴 꼴)에서 Gemini 가 틀을 다시 짜 16:9 로 다시 오렸다(Z2b · Z3b).
set -e
W=${1:-/tmp/L13e_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L13e_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('Z1', 'Z2b', 'Z3c', 'Z4', 'Z5', 'Z6', 'Z7', 'Z8'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z Z1 700 340 1200 800 ;    $Z paste base0.png z Z1 z/gem_Z1.png base1.png "880,360,1060,512;825,512,965,620;1030,500,1112,585;888,640,962,712;1040,648,1112,722"   # 세균 돌기 셋 · 별 깃발 · 세모 깃발이 돌기에 닿음
$Z crop base1.png z Z2b 660 700 1400 1116 ; $Z paste base1.png z Z2b z/gem_Z2b.png base2.png "690,790,1085,1065;1135,800,1345,1055"   # 빛 동그라미 — 똑같은 벌 부챗살 · 줄로 가는 벌
$Z crop base1.png z Z3b 40 340 760 745 ;    $Z paste base2.png z Z3b z/gem_Z3c.png base3.png "300,445,606,740;200,565,342,618"       # 작은 슬롯머신 릴 둘 · 벌이 두 손잡이를 함께(팔 셋 → 둘은 같은 채팅 Z3c)
$Z crop base3.png z Z4 1400 740 2048 1110 ; $Z paste base3.png z Z4 z/gem_Z4.png base4.png "1430,748,1855,978"                         # 바닥 뚜껑 → 호스 위의 둥근 뚜껑 구멍
$Z crop base4.png z Z5 240 880 660 1116 ;   $Z paste base4.png z Z5 z/gem_Z5.png base5.png "360,880,612,1116"                          # 바구니의 깃발 = 모두 똑같은 별
$Z crop base4.png z Z6 980 760 1519 1063 ;  $Z paste base5.png z Z6 z/gem_Z6.png base6.png "1072,830,1222,1004"                        # 줄로 가는 벌의 깃발에 깃대 · 줄이 별 위에
$Z crop base4.png z Z7 1560 300 2048 574 ;  $Z paste base6.png z Z7 z/gem_Z7.png base7.png "1740,312,1932,442"                         # 창의 세균 — 기둥의 세균과 같은 돌기 셋
$Z crop base4.png z Z8 900 360 1300 585 ;   $Z paste base7.png z Z8 z/gem_Z8.png base8.png "1115,465,1256,572"                         # 병정의 눈길을 세균 쪽으로
python3 "$D/L13e_pil.py" base8.png final.png
echo "→ $W/final.png"
