#!/bin/sh
# L54c_build.sh <workdir> — L54c 「꼭대기의 떠도는 대륙과 하늘에서 떨어진 돌」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · L54a 출연진을 올려 장면 통째 = S1a · 1024 → 2048)
#  → 구역 편집(zone3.py · colormatch.py · restore_poly.py):
#    ZP(판게아의 마른 바다 띠에 바다 동물 떼죽음 — 판 하나를 상자 하나로 붙이고, 상자에 든 왼쪽 위 작은 판 · 오른쪽 아래 벼랑은 원래 그림으로 되돌림)
#    · ZK(캥거루만 태운 판 · 사슴 지움) · ZB(침팬지 아기 얼굴을 둥글고 납작하게)
#    · ZD(공룡 둘이 × 눈으로 넘어짐 — 상자가 오림 거의 전부라 정합은 소행성 · 구덩이 쪽으로 --fit)
#    · ZC(나침반 · 같은 채팅 ZC2 = 두 배 크기 · 바늘 둘레 둥근 화살표 · 찡그린 얼굴)
#    · ZR(긴 흙 도랑 → 흙먼지가 사방으로 터지는 굴 하나 · 고개 내민 굴짐승 — 「한 계통에서 쏟아져 흩어짐」)
#    · ZS(땅속 뿌리를 하나로 잇기 — 「한 조상에서 여러 꼴」)
#  → 일치 검사 1회(○ 40 · △ 6 · ✕ 0) 뒤 L54c_pil.py(나침반 바늘이 「멈춰 있다」로 읽혀 — 굵은 둥근 화살표 · 바늘 잔상)
#  → 일치 검사 2회(○ 46 · △ 3 · ✕ 0) 뒤 ZM(두 회 모두 (마)에서 왼쪽 엄마들이 따로 노는 도해 느낌 → 침팬지 아기가 사람 아기에게 건너가 얼굴을 맞대고 두 엄마가 놀라 봄 · 탭 둘에 말을 달리해 ZN1 씀)
set -e
W=${1:-/tmp/L54c_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L54c_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"; RP="python3 $D/restore_poly.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZP1', 'ZK1', 'ZB1', 'ZD1', 'ZC2', 'ZR1', 'ZS1', 'ZN1'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
cm() { $CM z/up_$1.png z/gem_$2.png z/cm_$2.png; }
$Z crop base0.png z ZP 400 60 1240 532;     cm ZP ZP1
$Z paste base0.png z ZP z/cm_ZP1.png b1.png "404,64,1238,426"                                         # 판게아 — 마른 바다 띠의 떼죽음(물고기 뼈 · 뒤집힌 삼엽충 · 조개 · 바랜 산호)
$RP base0.png b1.png "396,56;474,56;474,122;440,134;396,142" 3                                        #  상자에 든 왼쪽 위 작은 판은 원래대로
$RP base0.png b1.png "1250,312;1200,336;1160,362;1120,382;1080,400;1046,430;1250,430" 3               #  오른쪽 아래 고원 벼랑도 원래대로
$Z crop base0.png z ZK 1100 0 1520 236;     cm ZK ZK1
$Z paste b1.png z ZK z/cm_ZK1.png b2.png "1190,12,1432,170"                                           # 캥거루 둘만 태운 판(사슴 지움)
$Z crop base0.png z ZB 280 580 620 771;     cm ZB ZB1
$Z paste b2.png z ZB z/cm_ZB1.png b3.png "338,684,442,771"                                            # 침팬지 아기의 둥글고 납작한 얼굴
$Z crop base0.png z ZD 1500 40 2048 348;    cm ZD ZD1
$Z paste b3.png z ZD z/cm_ZD1.png b4.png "1502,56,2048,348" 28 --fit="1502,90,1770,330;1830,130,2048,348"   # × 눈으로 넘어지는 공룡 둘
$Z crop base0.png z ZC 1540 360 1820 518;   cm ZC ZC2
$Z paste b4.png z ZC z/cm_ZC2.png b5.png "1574,370,1708,500"                                          # 큰 나침반(바늘 둘레 둥근 화살표) · 찡그린 얼굴
$Z crop base0.png z ZR 690 500 1310 849;    cm ZR ZR1
$Z paste b5.png z ZR z/cm_ZR1.png b6.png "908,560,1252,849"                                           # 흙먼지가 터지는 굴 하나 · 고개 내민 굴짐승
$Z crop base0.png z ZS 1220 780 1800 1106;  cm ZS ZS1
$Z paste b6.png z ZS z/cm_ZS1.png b7.png "1290,880,1770,1104"                                         # 하나로 이어진 뿌리
$Z crop b7.png z ZM 262 548 662 773;      cm ZM ZN1
$Z paste b7.png z ZM z/cm_ZN1.png b7m.png "268,550,602,773" 28 --fit="268,550,602,773"              # 일치 검사 2회 뒤 — 두 아기가 얼굴을 맞대고 두 엄마가 놀라 봄(같은 아기 얼굴을 「견주는」 사건)
python3 $D/L54c_pil.py b7m.png b8.png                                                                  # 일치 검사 1회 뒤 — 나침반 안: 굵은 둥근 화살표 · 바늘 잔상(「멈춘 바늘」 → 「빙빙 도는 바늘」)
cp b8.png final.png
echo "→ $W/final.png"
