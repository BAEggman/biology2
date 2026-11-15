#!/bin/sh
# L43f_build.sh <workdir> — L43f 「언덕 끈을 굴러 내려가는 인쇄 기계」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 출연진 = L43a 담장 마당 오림 + L43c 끈 · 두 탭에서 동시에 → S1b 씀)
#  → 그림 통째 고침 E1(새 채팅 · S1b 를 올림): 끈을 금빛 · 갈색 두 가닥으로 · 왼쪽 기계의 갈색 고리 · 세발 바퀴 · 튀어 오르는 기계 — 두 탭 가운데 E1b 씀 = 바탕(1024 → 2048)
#  → 구역 편집(zone3.py · colormatch.py): ZPL(왼쪽 기계의 종이를 등 뒤로 · 비탈 위 초록 띠까지) · ZPR(오른쪽 기계의 종이) ·
#    ZPR3(오른쪽 기계를 휘감던 긴 금빛 고리 지움 — 짧게 다시 그려 달라는 ZPR2 는 고리를 못 줄여 버림) · ZT(세발자전거 · 같은 채팅 ZT2 = 바퀴 넷 → 셋)
#  → L43f_pil.py(두 기계 밑의 주형 한 가닥 · 오른쪽 기계의 짧은 금빛 암호 고리 · 가닥과 종이의 5′→3′ 화살)
#  → 구역 편집 ZB(빵 옆의 글씨 같은 낙서 지움 · 주황 곰팡이) · ZR(담 밖 일꾼이 빛깔 네모 종이를 짚어 읽음)
#  → 일치 검사 1회(○ 40 · △ 7 · ✕ 0 · (마) 담 밖이 따로 노는 도해) 뒤 ZL(담 밖을 한 줄의 일로) · ZU2/ZU3(보라 종이띠 → 접힌 보라 돔)
#  → 일치 검사 2회(○ 45 · △ 4 · ✕ 0) 뒤 L43f_pil.py 에 ⓪(세발 기계의 끈이 금빛 고리 밑에서 나와 「끈이 두 갈래」로 읽힘 → 끈 머리를 풀빛으로 지우고 올 풀린 끝)
#  → 일치 검사 3회(○ 44 · △ 3 · ✕ 0) 뒤 L43f_pil2.py(사슬 위 「검은 구슬」 → 하늘빛 구슬)
set -e
W=${1:-/tmp/L43f_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L43f_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/E1b.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZPL1', 'ZPR1', 'ZPR31', 'ZT2', 'ZB1', 'ZR1', 'ZL1', 'ZU31'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
cm() { $CM z/up_$1.png z/gem_$2.png z/cm_$2.png; }
$Z crop base0.png z ZPL 380 180 1060 563;   cm ZPL ZPL1
$Z paste base0.png z ZPL z/cm_ZPL1.png b1.png "430,236,900,545"                                      # 왼쪽 기계의 종이 — 등 뒤로 나와 비탈 위 초록 띠까지
$Z crop base0.png z ZPR 1150 140 1790 500;  cm ZPR ZPR1
$Z paste b1.png z ZPR z/cm_ZPR1.png b2.png "1235,238,1462,348"                                        # 오른쪽 기계의 종이
$Z crop b2.png z ZPR3 1080 205 1747 580;    cm ZPR3 ZPR31
$Z paste b2.png z ZPR3 z/cm_ZPR31.png b3.png "1250,222,1585,578"                                      # 오른쪽 기계를 휘감던 긴 금빛 고리 지움
$Z crop b2.png z ZT 1560 128 1980 364;      cm ZT ZT2
$Z paste b3.png z ZT z/cm_ZT2.png b4.png "1592,136,1978,364" 28 --ident                               # 세발자전거(바퀴 셋) — 빛깔이 바뀌어 특징 정합이 안 돼 같은 자리로
python3 $D/L43f_pil.py b4.png p1.png                                                                  # 주형 한 가닥 · 짧은 암호 고리 · 5′→3′ 화살
$Z crop p1.png z ZB 0 930 380 1144;         cm ZB ZB1
$Z paste p1.png z ZB z/cm_ZB1.png p2.png "40,955,300,1110"                                            # 빵의 글씨 같은 낙서 지움 · 주황 곰팡이
$Z crop p1.png z ZR 1080 800 1440 1003;     cm ZR ZR1
$Z paste p2.png z ZR z/cm_ZR1.png p3.png "1120,850,1420,1003"                                         # 빛깔 네모 종이를 짚어 읽는 일꾼 · 따라 꿰는 구슬
$Z crop p3.png z ZL 880 487 2048 1144;      cm ZL ZL1
$Z paste p3.png z ZL z/cm_ZL1.png p4.png "900,700,2048,1144" 28 --fit="900,700,2048,1144"            # 일치 검사 1회 뒤 — 담 밖을 한 줄의 일로: 두루마리가 풀려 읽는 종이띠 → 꿴 사슬이 선 일꾼 손으로 → 빨강 · 파랑 꼬아 공 → 바나나가 잡아챈 공의 검은 구슬
$Z crop p4.png z ZU2 0 110 800 560;        cm ZU2 ZU31
$Z paste p4.png z ZU2 z/cm_ZU31.png p5.png "60,140,640,560"                                         # 일치 검사 1회 뒤 — 외발 기계의 보라 종이띠가 풀밭을 지나 주름 접힌 보라 돔으로(같은 채팅 둘째 ZU3 = 돔에서 빠져나간 꼬리 지움)
python3 $D/restore_poly.py p4.png p5.png "468,610;466,400;484,362;508,340;560,326;622,330;700,368;735,392;735,610" 1.5   #  상자에 든 왼쪽 기계 · 갈색 고리 · 화살은 원래대로
python3 $D/L43f_pil2.py p5.png p6.png                                                                 # 일치 검사 3회 뒤 — 사슬을 쥔 손의 먹선이 「검은 구슬」로 읽혀 하늘빛 구슬로(검은 구슬은 공 속 하나)
cp p6.png final.png
echo "→ $W/final.png"
