#!/bin/sh
# A17_build.sh <workdir> — 17장 덧붙임의 +정거장 그림(L10a · 2026-11-15 · Opus 5.5)을 다시 만든다(같은 픽셀).
#  L10a: 바탕(2026-11-15 의 lesson/img/L10a.webp 를 무손실로 둔 것) + KZ1(왼쪽 정거장 오른쪽 레일 위의 털모자 코사크 춤꾼 · 레일 아래 바닥의 모자 없는 짧은 레일 토막
#        · 빛나는 금빛 판 · 곧장 떨어져 앉은 작은 보라 상자 · 포크 꽂힌 구슬 — 두 탭 가운데 KZb)
#  → L10a_pil.py(중산모 → 상자 점선 화살 = 스캐닝 · 정거장 앞 바닥의 금 간 짙은 회색 칩 1 · 2 · 2 = GTP)
#  → 일치 검사 1회 뒤 KC1(춤꾼 옷 — 큰 검은 털모자 + 붉은 제복이 「영국 근위병」으로 읽혀 넓적한 회색 파파하 · 탄띠 단 남색 웃옷 · 붉은 허리띠로 · 두 탭 가운데 KCa · 정합 대신 --ident)
set -e
W=${1:-/tmp/A17_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/A17_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/L10a_base_1115.webp').convert('RGB').save(f'{W}/base0.png')
Image.open(f'{S}/KZ1.webp').convert('RGB').save(f'{W}/z/gem_KZ1.png')
Image.open(f'{S}/KC1.webp').convert('RGB').save(f'{W}/z/gem_KC1.png')
PY
cd "$W" && $Z crop base0.png z KZ 430 760 1110 1144 && $CM z/up_KZ.png z/gem_KZ1.png z/cm_KZ1.png && $Z paste base0.png z KZ z/cm_KZ1.png k1.png "486,768,626,918;616,960,912,1104"
python3 $D/L10a_pil.py k1.png k2.png
$Z crop k2.png z KC 430 760 720 923 && $CM z/up_KC.png z/gem_KC1.png z/cm_KC1.png && $Z paste k2.png z KC z/cm_KC1.png final.png "488,772,628,914" 28 --ident
echo "→ $W/final.png"
