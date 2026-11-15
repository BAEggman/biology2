#!/bin/sh
# L48f_build.sh <workdir> — L48f 「짚단 부부의 혼례와 이혼」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · L48a 를 출연진으로 올려 장면 통째 = S2b · 1024 → 2048)
#  → 구역 편집(zone3.py · 16:9 · colormatch.py): ZP(칸막이 · base0) → ZX(춤판 짚단 X · base0) → ZR(밧줄 → 쇠고리 · b2) → ZF(앞 쌍 발 · b2) → ZS(세사기 실 두 빛깔 · b4)
#  → L48f_pil.py(이발사 끝 바꾸기 · 장화 윤곽 토막 · 춤판 X 끝의 짝 빛깔 · 띠 결 잔 점)
set -e
W=${1:-/tmp/L48f_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L48f_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZP1', 'ZX2', 'ZR1', 'ZF1', 'ZS1'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z ZP 1100 611 2048 1144;  $Z crop base0.png z ZX 1180 340 2048 828
$CM z/up_ZP.png z/gem_ZP1.png z/cm_ZP1.png;  $CM z/up_ZX.png z/gem_ZX2.png z/cm_ZX2.png
$Z paste base0.png z ZP z/cm_ZP1.png b1.png "1290,860,1900,1144;1550,796,1615,860"                       # 목수 — 가로 판자 → 점선 위 칸막이(무릎 꿇고 못질)
$Z paste b1.png    z ZX z/cm_ZX2.png b2.png "1420,365,1765,795;1420,795,1548,828;1617,795,1765,828"       # 춤판 짚단 넷 → 두 다발 X(칸막이 꼭대기 1548 ~ 1617 × 795 아래는 b1 그대로)
$Z crop b2.png z ZR 1180 340 2048 828;       $Z crop b2.png z ZF 1380 640 1820 888
$CM z/up_ZR.png z/gem_ZR1.png z/cm_ZR1.png;  $CM z/up_ZF.png z/gem_ZF1.png z/cm_ZF1.png
$Z paste b2.png    z ZR z/cm_ZR1.png b3.png "1180,380,1420,828;1770,380,2048,828"                         # 줄다리기 밧줄 끝이 사내 뒤로 돌아 기둥 · 벽 쇠고리에
$Z paste b3.png    z ZF z/cm_ZF1.png b4.png "1422,770,1548,875;1617,770,1768,875"                         # 앞 쌍 장화 한 켤레 · 그림자 하나(아래 끝 875 — 888 이면 목수 머리 윗동이 잘린다)
$Z crop b4.png z ZS 0 700 450 953;           $CM z/up_ZS.png z/gem_ZS1.png z/cm_ZS1.png
$Z paste b4.png    z ZS z/cm_ZS1.png b5.png "10,834,440,953;10,800,118,834"                               # 세사기 실 — 남색 · 하늘색 두 빛깔(할머니 발 · 짚단 밑동은 피함)
python3 "$D/L48f_pil.py" b5.png final.png
echo "→ $W/final.png"
