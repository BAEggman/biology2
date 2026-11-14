#!/bin/sh
# L13d_build.sh <workdir> — L13d 「처형장과 옮겨 심은 집」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 장면 통째 · 1024 → 2048) → 구역 편집 Z1 ~ Z14(zone3.py: 같은 자리 오림 → Gemini → 정합해 상자만 붙임) → L13d_pil.py(단추 · 배지 · 알갱이 · 원판 · 점선)
#  오림(crop)은 그때그때의 바탕에서 했다 — 아래 순서 그대로 해야 같은 그림이 나온다.
set -e
W=${1:-/tmp/L13d_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L13d_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6', 'Z7', 'Z8', 'Z9', 'Z10', 'Z11', 'Z12', 'Z13', 'Z14'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z Z1 700 640 1260 1144 ;   $Z paste base0.png z Z1 z/gem_Z1.png base1.png "850,870,1065,1080"              # 펀치 · 배의 구멍 · 원판
$Z crop base0.png z Z2 1480 180 2048 760 ;   $Z paste base1.png z Z2 z/gem_Z2.png base2.png "1600,290,1965,545"            # 외눈 안경 병정을 흙덩이 위 여자 곁으로
$Z crop base0.png z Z3 1160 560 1600 1080 ;  $Z paste base2.png z Z3 z/gem_Z3.png base3.png "1290,795,1525,1035"           # 대머리 주민의 아랫몸 = 주머니 더미
$Z crop base0.png z Z4 1480 640 1940 1110 ;  $Z paste base3.png z Z4 z/gem_Z4.png base4.png "1538,680,1702,1012;1660,900,1790,992"   # 대장(외눈 안경 지움 · 뺨 감쌈) · 걸린 쪽지
$Z crop base4.png z Z5 0 380 640 900 ;       $Z paste base4.png z Z5 z/gem_Z5.png base5.png "15,395,548,700;15,700,430,885"          # 뼈를 길게 갈라 붉은 골수
$Z crop base5.png z Z6 1040 330 1720 680 ;   $Z paste base5.png z Z6 z/gem_Z6.png base6.png "1072,405,1528,622"            # 학교를 나온 맨나무 인형 — 갈팡질팡 · 흙더미 곁에서 머리 긁기
$Z crop base5.png z Z7 1690 190 2000 500 ;   $Z paste base6.png z Z7 z/gem_Z7.png base7.png "1822,302,1890,406"            # 창가의 아이
$Z crop base7.png z Z8 740 780 1100 1144 ;   $Z paste base7.png z Z8 z/gem_Z8.png base8.png "760,790,1052,1012"            # 펀치 병정의 조끼가 보이게
$Z crop base7.png z Z9 0 800 600 1144 ;      $Z paste base8.png z Z9 z/gem_Z9.png base9.png "0,860,468,1144"               # 왼쪽 아래 성벽 조각 지움
$Z crop base9.png z Z10 1590 280 1890 580 ;  $Z paste base9.png z Z10 z/gem_Z10.png base10.png "1604,318,1688,492"         # 여자 — 두 손을 어깨 옆으로(가슴이 보이게)
$Z crop base10.png z Z11 1640 280 1920 580 ; $Z paste base10.png z Z11 z/gem_Z11.png base11.png "1680,284,1866,515"        # 외눈 안경 병정 — 곧게 서서 조끼가 보이게
$Z crop base11.png z Z12 930 730 1170 960 ;  $Z paste base11.png z Z12 z/gem_Z12.png base12.png "1012,792,1162,918"        # 보라 망토를 셔츠 깃 속으로
$Z crop base11.png z Z13 60 20 760 400 ;     $Z paste base12.png z Z13 z/gem_Z13.png base13.png "70,22,702,382"            # 세균이 성벽을 기어오름 · 깃발이 몸에 꽂힘 · 날아가는 깃발
$Z crop base11.png z Z14 1250 700 1530 1030 ; $Z paste base13.png z Z14 z/gem_Z14.png base14.png "1298,836,1514,1022"      # 주머니가 셔츠 밑단까지
python3 "$D/L13d_pil.py" base14.png final.png
echo "→ $W/final.png"
