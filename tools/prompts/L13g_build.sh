#!/bin/sh
# L13g_build.sh <workdir> — L13g 「봄 잔칫날의 성」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 출연진 그림을 올려 장면 통째 · 1024 → 2048) → 구역 편집(zone3.py: 오림은 모두 base0 에서 · 16:9 · colormatch.py 로 빛깔 맞춤)
#  → L13g_pil.py(자국 지우기 · 집게 Y(IgE · 2형 · 3형) · 꽃가루 · 아기의 이음 깃발 · 배지)
set -e
W=${1:-/tmp/L13g_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L13g_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('GZA', 'GZB', 'GZC2', 'GZD'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z ZA 620 360 1140 652;   $Z crop base0.png z ZB 640 740 1240 1077;  $Z crop base0.png z ZC2 1110 560 1550 808;  $Z crop base0.png z ZD 430 470 870 718
for p in ZA:GZA ZB:GZB ZC2:GZC2 ZD:GZD; do c=${p%%:*}; g=${p##*:}; $CM z/up_$c.png z/gem_$g.png z/cm_$g.png; done
$Z paste base0.png z ZA  z/cm_GZA.png  b1.png "700,380,1050,652"        # 뚱보 경비 — 큰 배 · 가슴 원판 지움 · 왼 주먹의 불 지움
$Z paste b1.png    z ZB  z/cm_GZB.png  b2.png "650,760,1110,1077"       # 아나필락시스 — 퉁퉁 부은 얼굴 · 드럼통 뚜껑이 터져 날아감
$Z paste b2.png    z ZC2 z/cm_GZC2.png b3.png "1240,640,1420,790"       # 수혈 — 호스의 유리 방울 속 붉은 원반이 터짐
$Z paste b3.png    z ZD  z/cm_GZD.png  b4.png "470,480,822,705"         # 항독소 — 경비가 깃발을 한 아름 환자 위로 쏟아붓는다(일치 검사 1회 — 들고만 있었다) · 오른쪽 끝 822 = 뚱보 경비 배(ZA) 앞에서 멈춤(넘으면 배 왼쪽이 곧게 잘린다)
python3 "$D/L13g_pil.py" b4.png final.png
echo "→ $W/final.png"
