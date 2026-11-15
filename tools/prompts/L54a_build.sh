#!/bin/sh
# L54a_build.sh <workdir> — L54a 「번개 치는 원시 바닷가의 수프 솥」 그림을 처음부터 다시 만든다(같은 픽셀).
#  C1(출연진 · L52a 알약 손님 둘을 올림) → S1(출연진을 올려 장면 통째 = S1a · 1024 → 2048)
#  → 구역 편집(zone3.py · colormatch.py): ZC(파란 웅덩이 → 잿빛 푸른 점토 · 같은 채팅 둘째 ZC2) · ZT(탁자 — 천 위의 파리 · 구더기 / 백조목 · 부러진 목 · 둘째 ZT2 = 왼쪽 주둥이 지움)
#    · ZW2(좁은 파도가 종이 거품과 밧줄 거품을 덮침 — 첫 ZW1 은 파도가 줄무늬 바위까지 덮어 버림) · ZB(물속 붉은 · 잿빛 줄무늬 바위와 녹 조각) · ZR(리본 끝이 접혀 된 종이 손이 짧은 리본에 같은 차례로 베낌)
#    → 일치 검사 1회(○ 56 · △ 5 · ✕ 1) 뒤 ZK(물통이 쩍 갈라지고 틈에서 방울) · ZC3(점토가 물 · 젤리처럼 보임 → 불투명 · 울퉁불퉁 · 같은 채팅 ZC4 로 빈 작은 거품)
#    → 3회(○ 64 · △ 2 · ✕ 0) 뒤 ZN(백조의 목 · 머리를 비치는 유리로 · 그 안에 갇힌 먼지 덩이 — PIL 점은 「겉무늬」로 읽혔다)
#    → 4회(○ 53 · △ 2 · ✕ 1 — 비치는 머리 안의 고운 먼지가 작은 그림에서 안 보임)
#  → L54a_pil.py(만화식 먼지 알갱이 — 유리 머리 안 덩이 · 부리 앞 공중 · 부러진 목으로 떨어짐 · 물속 위쪽 붉은 조각 하나를 잿빛으로)
set -e
W=${1:-/tmp/L54a_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L54a_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZC2', 'ZT2', 'ZW2', 'ZB1', 'ZR1', 'ZK1', 'ZC4', 'ZN1'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
cm() { $CM z/up_$1.png z/gem_$2.png z/cm_$2.png; }
$Z crop base0.png z ZC 800 744 1504 1140;   cm ZC ZC2
$Z paste base0.png z ZC z/cm_ZC2.png b1.png "820,965,1445,1144;820,900,1400,965;1130,780,1400,900"   # 웅덩이 → 점토 더미(거품이 점토에 박힘 · 갓 돋는 작은 거품)
$Z crop base0.png z ZT 0 660 800 1110;      cm ZT ZT2
$Z paste b1.png z ZT z/cm_ZT2.png b1t.png "20,680,780,1010"                                          # 탁자 — 천 위에만 파리 · 구더기 · 백조목(구멍은 부리뿐 · 목 안 먼지) · 부러진 목 · 유리 조각
$Z crop b1.png z ZW2 1000 590 1660 961;     cm ZW2 ZW2
$Z paste b1t.png z ZW2 z/cm_ZW2.png b2.png "1290,600,1560,795;1405,795,1600,961"                     # 좁은 파도 — 찢겨 날리는 종이 · 물보라 속 멀쩡한 금빛 밧줄 거품
$Z crop base0.png z ZB 1480 700 2048 1020;  cm ZB ZB1
$Z paste b2.png z ZB z/cm_ZB1.png b3.png "1600,720,2048,900;1600,900,1790,955"                       # 물속 — 흰 방울에 녹스는 쇳조각 · 붉은 · 잿빛 줄무늬 바위
$Z crop b3.png z ZR 1050 780 1470 1016;     cm ZR ZR1
$Z paste b3.png z ZR z/cm_ZR1.png b4.png "1128,782,1395,1014"                                        # 큰 거품 속 — 리본 끝의 종이접기 손이 짧은 리본에 같은 차례로 네모를 붙임
$Z crop b4.png z ZK 1500 360 1980 630;      cm ZK ZK1
$Z paste b4.png z ZK z/cm_ZK1.png b5.png "1590,360,1652,500;1825,360,1892,525"                       # 물통 둘이 쩍 갈라짐 · 틈에서 솟구치는 흰 방울(곁의 청록 손님은 그대로)
$Z crop b4.png z ZC3 800 762 1480 1144;     cm ZC3 ZC4
$Z paste b5.png z ZC3 z/cm_ZC4.png b6.png "805,880,1460,1144"                                        # 점토 — 불투명 · 울퉁불퉁 · 손자국 · 왼쪽 끝 빈 작은 거품(큰 거품 속은 그대로 남음)
$Z crop b6.png z ZN 400 735 640 870;        cm ZN ZN1
$Z paste b6.png z ZN z/cm_ZN1.png b7.png "468,756,562,866"                                           # 백조 목 · 머리 = 비치는 유리 · 머리 안에 갇힌 먼지 덩이 · 부리 끝만 열림
python3 "$D/L54a_pil.py" b7.png final.png
echo "→ $W/final.png"
