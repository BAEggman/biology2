#!/bin/sh
# L13b_build2.sh <workdir> — L13b 다시 짓기 「가시 하나에서 번진 안뜰의 난리」(2026-11-14 · 사건 장면) 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 출연진 그림 = L13c_src/cast_ref.webp · 1024 → 2048) → 구역 편집 B1 · B2 · B3b · B4 · B7(zone3.py) → L13b_pil2.py → 구역 편집 B8s(물기둥 밑동의 작은 물보라 · 돌벽 틈 — PIL 의 Y 합류 · 폭포 전단까지 담아 올렸다) · B9 · B10(PIL 의 갈색 끈을 담아 올렸다)
#  (옛 판 — 조각 세우기 — 은 L13b_build.sh · L13b_src/ 에 그대로 둔다. 구역 편집 B5 · B6(가는 물줄기를 저수지에서 나오게)은 둘 다 실패해 PIL 로 다시 그렸다.)
set -e
W=${1:-/tmp/L13b_build2}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L13b_src2"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('B1', 'B2', 'B3b', 'B4', 'B7', 'B8s', 'B9', 'B10'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z B1 180 380 780 860 ;   $Z paste base0.png z B1 z/gem_B1.png base1.png "270,420,636,800"          # 호스 끝 없이 이어짐 · 옆구리 구멍으로 비집고 나오는 경비
$Z crop base0.png z B2 560 420 1080 900 ;  $Z paste base1.png z B2 z/gem_B2.png base2.png "648,470,968,892"          # 뚱보 경비 · 손바닥으로 밀어내는 세균
$Z crop base0.png z B3 0 780 480 1144 ;    $Z paste base2.png z B3 z/gem_B3b.png base3.png "30,840,330,1120"          # 달팽이의 펜촉이 세균 옆구리에
$Z crop base2.png z B4 1300 760 1720 1144 ; $Z paste base3.png z B4 z/gem_B4.png base4.png "1336,896,1720,1144"      # 세균 배의 구멍을 꿰뚫는 곧은 물줄기
$Z crop base4.png z B7 1500 160 1780 500 ; $Z paste base4.png z B7 z/gem_B7.png base5.png "1560,245,1703,482"        # 집낙지가 기다란 두루마리를 두 쪽으로 찢는다(일치 검사 2회 「찢는지 확실치 않다」 → 사건으로)
python3 "$D/L13b_pil2.py" base5.png pil.png
$Z crop pil.png z B8s 1490 720 1790 1000 ; $Z paste pil.png z B8s z/gem_B8s.png post8.png "1588,880,1676,937;1648,836,1672,880"   # 물기둥 밑동의 작은 물보라 · 기둥과 폭포 사이 돌벽을 깨끗이(일치 검사 2 ~ 4회 「출발점이 물길 폭포와 붙어 구별 안 됨」)
$Z crop post8.png z B9 1170 760 1480 1060 ; $Z paste post8.png z B9 z/gem_B9.png post9.png "1268,812,1428,1000"        # 굵은 줄기가 작은 흰 덩이의 세균 위로 쏟아진다(일치 검사 3회 「닿는 자리가 분명치 않다」)
$Z crop post9.png z B10 1270 160 1610 450 ; $Z paste post9.png z B10 z/gem_B10.png final.png "1345,200,1535,300"       # 망토가 안은 두루마리 끝이 두 겹 띠로 풀려 깍둑썰기 기계 윗구멍으로(일치 검사 3회 「망토와 기계의 인과가 약하다」)
echo "→ $W/final.png"
