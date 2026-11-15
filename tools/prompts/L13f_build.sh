#!/bin/sh
# L13f_build.sh <workdir> — L13f 「깃발 다섯 연대의 출정」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 출연진 그림을 올려 장면 통째 · 1024 → 2048) → 구역 편집(zone3.py: 오림은 모두 base0 에서 · 16:9 · 붙이기 전에 colormatch.py 로 빛깔 맞춤)
#  → L13f_pil.py(남은 자국 지우기 · 세균 · 망토 손의 Y 깃발 · 눈물 · 샘의 이음 깃발 · 배지)
#  구역 편집의 이름 = L13f_prompt_scene.txt 의 ## 머리. 뒤에 숫자 · b 가 붙은 것은 같은 채팅의 덧붙임(틀이 그대로라 같은 오림에 붙인다).
set -e
W=${1:-/tmp/L13f_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L13f_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZA3', 'ZB2', 'ZD', 'ZE1b', 'ZE2c', 'ZF2', 'ZG2', 'ZH2', 'ZI2', 'ZJ2'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
$Z crop base0.png z ZA 1440 80 2048 422;   $Z crop base0.png z ZB 1080 300 1780 694;  $Z crop base0.png z ZD 940 540 1830 1040
$Z crop base0.png z ZE1 840 60 1340 341;   $Z crop base0.png z ZE2 780 400 1380 738;  $Z crop base0.png z ZF 420 150 1000 476
$Z crop base0.png z ZG2 120 40 600 310;    $Z crop base0.png z ZH 0 400 400 625;      $Z crop base0.png z ZI 580 750 1280 1144
$Z crop base0.png z ZJ 120 800 580 1059
for p in ZA:ZA3 ZB:ZB2 ZD:ZD ZE1:ZE1b ZE2:ZE2c ZF:ZF2 ZG2:ZG2 ZH:ZH2 ZI:ZI2 ZJ:ZJ2; do
  c=${p%%:*}; g=${p##*:}; $CM z/up_$c.png z/gem_$g.png z/cm_$g.png
done
$Z paste base0.png z ZA  z/cm_ZA3.png  b1.png  "1460,80,2048,340;1515,340,2048,355;1600,355,2048,380;1715,380,2048,422"   # 큰 Y — 두 팔 끝의 집게가 세균 머리의 별 돌기를 문다(ZA2 의 같은 채팅 덧붙임 ZA3) · 작은 벌의 짧은 장대(경쇄)
$Z paste b1.png    z ZB  z/cm_ZB2.png  b2.png  "1085,320,1600,590;1588,380,1760,670" 6                    # 호스 몸의 둥근 창 · 호스 끝은 탑 벽으로 · D 자 명찰 벌(문턱 6 = 상자째 — 문턱이 높으면 호스가 얼룩졌다 · 두 상자는 겹쳐야 x 1600 에 세로 줄이 안 남는다)
$Z paste b2.png    z ZD  z/cm_ZD.png   b3.png  "1150,600,1600,820;1600,680,1700,820;1185,820,1700,1040"   # 지팡이 손잡이 Y 깃발 무리 · 임신부 배 창으로 깃발
$Z paste b3.png    z ZE2 z/cm_ZE2c.png b4.png  "880,400,1100,737;1100,600,1150,737"                      # 뚱보 경비 — 배를 키우고 깃발 · 꽃가루는 지움(ZE2b → 같은 채팅 ZE2c · Y 와 꽃가루는 PIL)
$Z paste b4.png    z ZF  z/cm_ZF2.png  b5.png  "430,150,1000,470" --fit="470,170,900,470"                 # 다섯 Y 바퀴 · 두 봉우리 쇠 장식 · 물줄기가 세균 배를 꿰뚫음(아래 끝 470 — Gemini 그림 맨 아랫줄의 점선이 이음선으로 남았다)
$Z paste b5.png    z ZE1 z/cm_ZE1b.png b6.png  "870,100,1300,328;870,328,1150,341"                      # 세 갈래 갈퀴로 벌레를 틈으로(호스 윗테는 피한다 — y 328 아래로 넘으면 호스 머리가 잘렸다)
$Z paste b6.png    z ZG2 z/cm_ZG2.png  b7.png  "125,45,540,308"                                          # 쌍둥이의 이음 깃발(J 자 고리)
$Z paste b7.png    z ZI  z/cm_ZI2.png  b8.png  "580,818,1180,1144"                                       # 두 세균의 깃발을 지움(Y 는 PIL)
$Z paste b8.png    z ZJ  z/cm_ZJ2.png  b9.png  "137,850,268,1062" 6                                      # 망토 손의 깃발을 지움(Y 는 PIL) — 창 안쪽을 통째로(문턱 6 · 얼룩진 창 안쪽을 한 빛깔로)
$Z paste b9.png    z ZH  z/cm_ZH2.png  b10.png "0,405,200,625"                                           # 눈물 · 샘을 맑게 · 큰 눈물방울(이음 깃발은 PIL)
python3 "$D/L13f_pil.py" b10.png final.png
echo "→ $W/final.png"
