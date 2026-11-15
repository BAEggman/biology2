#!/bin/sh
# L54b_build.sh <workdir> — L54b 「절벽의 돌 기록을 오르는 탐사대」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · L54a 출연진을 올려 장면 통째 = S1b · 1024 → 2048)
#  → 구역 편집(zone3.py · colormatch.py): ZE(빵 같은 누비 타원 → 분홍 물렁 생물) · ZM(고리 꼴 → 손잡은 세포 덩이 · 둘째 ZM2 = 두 배로)
#    · ZU(삼엽충 위아래 화산재 띠 · 둘째 ZU2 = 띠가 화석을 가로지르지 않게 · 점박이 잿빛) · ZJ(두 병 꼭 반 · 같은 채팅 ZJ2 = 바이스 두 턱 사이)
#    → 일치 검사 1회(○ 31 · △ 4 · ✕ 0) 뒤 ZF(수염 탐험가가 웃으며 내려옴 → 쾅 소리에 깜짝 놀란 얼굴 — 터짐과 한 사건으로)
set -e
W=${1:-/tmp/L54b_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L54b_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZE1', 'ZM1', 'ZM2', 'ZU2', 'ZJ2', 'ZF1'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
cm() { $CM z/up_$1.png z/gem_$2.png z/cm_$2.png; }
$Z crop base0.png z ZE 1400 600 2048 964;   cm ZE ZE1
$Z paste base0.png z ZE z/cm_ZE1.png b1.png "1410,630,2048,860"                                      # 에디아카라 — 분홍 누비 타원(머리 혹) · 고사리 잎 그대로
$Z crop base0.png z ZM 1180 700 1500 880;   cm ZM ZM1
$Z paste b1.png z ZM z/cm_ZM1.png b2.png "1250,740,1420,880"                                          # 고리 꼴 → 손잡은 세포 덩이(작음 — 아래 ZM2 가 두 배로 덮음)
$Z crop base0.png z ZU 940 300 1420 570;    cm ZU ZU2
$Z paste b2.png z ZU z/cm_ZU2.png b3.png "945,335,1420,570"                                          # 삼엽충 위아래 점박이 화산재 띠 · 끌은 위 띠에
$Z crop base0.png z ZJ 1500 300 2048 608;   cm ZJ ZJ2
$Z paste b3.png z ZJ z/cm_ZJ2.png b4.png "1530,345,1680,560;1868,360,1995,470;1820,470,1995,605"     # 두 병 반반 · 바이스 두 턱 사이(옛 병 뚜껑 자리까지)
$Z crop b4.png z ZM2 1200 700 1520 880;     cm ZM2 ZM2
$Z paste b4.png z ZM2 z/cm_ZM2.png b5.png "1262,752,1410,880"                                         # 손잡은 초록 세포 덩이(두 배)
$Z crop b5.png z ZF 1100 260 1400 429;      cm ZF ZF1
$Z paste b5.png z ZF z/cm_ZF1.png b6.png "1178,270,1292,396"                                          # 수염 탐험가의 깜짝 놀란 얼굴(동그란 눈 · 벌린 입 · 놀람 선)
cp b6.png final.png
echo "→ $W/final.png"
