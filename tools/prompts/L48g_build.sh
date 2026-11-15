#!/bin/sh
# L48g_build.sh <workdir> — L48g 「아래층의 두 번째 이별과 마당의 시상식」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · L48f 를 출연진으로 올려 장면 통째 = G1b · 1024 → 2048)
#  → 구역 편집(zone3.py · colormatch.py): GA(오른쪽 방 후기 II) · GB(말기 II) · GS(두 오림 사이 띠) · GD(버섯 → 푸른곰팡이)
#    → 일치 검사 1회 뒤 H1(천막 치기) · H3(점선 곁 판자 울) · H2(계단 짚단 X) · H4(헛간 → 짚더미) · H5(아기 짚단)
#    → 2회 뒤 H6(계단 밑 옛 다리) · H7(헛간 오른 벽 손질)
#  → L48g_pil.py(이발사 다발 · 남은 말뚝 · 옛 발 · 포자 구름 청록)
set -e
W=${1:-/tmp/L48g_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L48g_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('GA1', 'GB1', 'GS2', 'GD2', 'H1', 'H3b', 'H2', 'H4', 'H5b', 'H6', 'H7'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
cm() { $CM z/up_$1.png z/gem_$2.png z/cm_$2.png; }
$Z crop base0.png z GA 570 340 1110 644;  cm GA GA1
$Z paste base0.png z GA z/cm_GA1.png b1.png "575,345,1105,644"                                 # 오른쪽 방 — X 가 한 다발씩 넷으로 · 다발마다 가까운 벽 밧줄 · C 자 조각
$Z crop base0.png z GB 520 660 1120 998;  cm GB GB1
$Z paste b1.png z GB z/cm_GB1.png b2.png "560,660,1115,998" 28 --fit="610,700,1075,998"         # 말기 II — 칸막이 · 양쪽 새 천막 · 풀리는 다발(상자가 오림을 거의 덮어 정합 자리는 --fit)
$Z crop b2.png z GS 560 560 1120 875;     cm GS GS2
$Z paste b2.png z GS z/cm_GS2.png b3.png "575,600,1105,705"                                    # GA(644) · GB(660) 사이 띠의 옛 X 발끝 지움 · 왼쪽 작은 천막 지붕
$Z crop base0.png z GD 1660 860 2048 1078; cm GD GD2
$Z paste b3.png z GD z/cm_GD2.png b4.png "1765,895,1915,1076"                                  # 붉은 갓 흰 점 버섯(무스카린 예약) → 통나무 위 푸른곰팡이
$Z crop b4.png z H1 0 680 500 961;        cm H1 H1
$Z paste b4.png z H1 z/cm_H1.png b5.png "10,690,470,955" 28 --ident                            # 왼쪽 방 앞 — 기둥 세우기 · 말뚝 박기(새 천막)
$Z crop b4.png z H3 480 720 1180 1114;    cm H3 H3b
$Z paste b5.png z H3 z/cm_H3b.png b6.png "490,722,1150,1112" 28 --fit="540,740,1140,1075"     # 오른쪽 방 앞 — 점선 곁 판자 울에 못질 · 새 천막
$Z crop b6.png z H2 330 230 650 410;      cm H2 H2
$Z paste b6.png z H2 z/cm_H2.png b7.png "420,262,575,410"                                      # 계단 짚단 둘 → X
$Z crop b6.png z H4 1040 520 1420 734;    cm H4 H4
$Z paste b7.png z H4 z/cm_H4.png b8.png "1110,640,1415,734"                                    # 헛간 오른 벽 밑 작은 문 → 한 다발 짚들이 짚더미로
$Z crop b6.png z H5 1590 440 1850 586;    cm H5 H5b
$Z paste b8.png z H5 z/cm_H5b.png b9.png "1650,500,1800,586"                                   # 할머니 가슴께 아기 짚단(남색 · 하늘색)
$Z crop b9.png z H6 300 250 700 475;      cm H6 H6
$Z paste b9.png z H6 z/cm_H6.png b10.png "395,262,610,470"                                     # 계단 밑 옛 다발 아랫동 · 다리 지움
$Z crop b9.png z H7 980 560 1300 740;     cm H7 H7
$Z paste b10.png z H7 z/cm_H7.png b11.png "1010,600,1200,738"                                  # GA · H4 · H3 상자가 만난 헛간 오른 벽 손질
python3 "$D/L48g_pil.py" b11.png final.png
echo "→ $W/final.png"
