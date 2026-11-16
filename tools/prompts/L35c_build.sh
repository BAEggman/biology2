#!/bin/bash
# L35c_build.sh <작업 폴더> — L35c 그림을 Gemini 원본(L35c_src/)에서 다시 만든다(같은 픽셀 · 2026-11-16 확인).
#  S1 = Gemini 가 장면 하나를 통째로 그린 바탕(1024 × 572 — 출연진 그림 cast_ref 를 올리고 「둑으로 갈린 두 연못 앞 합동 혼례가 짝마다 틀어지는 장면」 · 2048 로 키움)
#  자루 하객(배수성 — 자루 개수가 곧 세트 수): Z12A2 = 오른쪽 데크 하객 줄 통째 · P1A1 = 아빠 베이지 넷 · P4B1 = 젊은이 베이지 둘 + 초록 둘
#    P3cA1 = 아이 셋(둘은 끈으로 묶이고 하나 홀로) + 씨 없는 수박 · P3fix = P3c 상자가 덮은 아빠 오른쪽 아래 자루를 base2 에서 되돌린 조각
#    P5eB1 = 밀 농부 여섯(베이지 · 초록 · 금빛 둘씩 — 일곱이던 것을 같은 대화에서 하나 덜어 냄) → 옛 다리 그림자는 deckfill 로 바닥을 메움
#  Z11cA1 = 오른 연못의 빨강 · 파랑 물고기(제 빛깔끼리 입맞춤 · 꼬리로 따귀) · Z3A1 = 하늘을 가리키며 파란 발을 든 부비새 수컷 + 고개 돌려 하품하는 빨간 발 암컷
#  Z15bB1 = 긴 층계참 사이로 갑자기 높은 단이 솟는 거인의 돌계단 + 거미줄 뒤집어쓴 치타가 높은 단을 뛰어오름(거북 비탈 그대로)
#  Z14bA1 = 둑 먼 끝 물목 세 갈래(돌 쌓는 일꾼 둘 · 곁에 늘어진 얼룩 새끼 / 허물어진 끝의 섞인 오리 / 좁은 틈의 얼룩 새끼 줄)
#    Z14cA1 = 오른쪽 돌담 끝을 둥글게 · 오림 밖으로 걸친 옛 새끼 지움 · 수평선 잇기 · 길 위 옛 오리 발 지움(넓힌 오림)
#  Z1bB1 = 파리 둘만(사과 · 산사 열매를 하나씩 끌어안고 뾰로통 · 날개에 검은 띠) · Z2bB1 = 붉은 머리 새 지움 + 벤치 왼쪽 불빛 → 해바라기 둘(여름 — 뒤에 Z2cA1 이 매미로 갈았다)
#  Z5bA1 = 붉은 성게의 주황 알 · 보라 성게의 정자가 알에 닿아 튕겨 나감 · Z4bB1 = 몸이 안 맞아 어긋나며 진땀 흘리는 달팽이 둘
#  Z8A1 = 알 속 새끼를 사람 아기에서 반반 무늬 도롱뇽 새끼(창백 · 이마에 물수건)로
#  ⚠ 구역마다 처음 오린 바탕에서 오린다(뒤 편집의 상자 가장자리 번짐이 오림에 섞이면 픽셀이 달라진다 — 배운 것 (62)).
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L35c_src/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('Z12A2', 'P1A1', 'P4B1', 'P3cA1', 'Z11cA1', 'P5eB1', 'Z3A1', 'Z15bB1', 'Z14bA1', 'Z1bB1', 'Z14cA1', 'Z2bB1', 'Z5bA1', 'Z4bB1', 'Z8A1', 'Z8A2', 'Z5cB1', 'Z9A1', 'Z14dB2', 'Z2cA1', 'Z7A2', 'Z5dB1', 'P2A2', 'P6B1'):
    Image.open(f'{D}/L35c_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"; DF="python3 $D/deckfill.py"
# 자루 하객
$Z crop "$W/base0.png" "$W/z" Z12 1150 720 2048 1144
$CM "$W/z/up_Z12.png" "$W/z/gem_Z12A2.png" "$W/z/cm_Z12A2.png"
$Z paste "$W/base0.png" "$W/z" Z12 "$W/z/cm_Z12A2.png" "$W/base1.png" "1150,790,2048,1144"
$Z crop "$W/base1.png" "$W/z" P1 1170 740 1380 1120
$Z crop "$W/base1.png" "$W/z" P4 1505 740 1715 1110
$CM "$W/z/up_P1.png" "$W/z/gem_P1A1.png" "$W/z/cm_P1A1.png"
$CM "$W/z/up_P4.png" "$W/z/gem_P4B1.png" "$W/z/cm_P4B1.png"
$Z paste "$W/base1.png" "$W/z" P1 "$W/z/cm_P1A1.png" "$W/t1.png" "1170,740,1380,1100"
$Z paste "$W/t1.png" "$W/z" P4 "$W/z/cm_P4B1.png" "$W/base2.png" "1505,740,1715,1100"
$Z crop "$W/base2.png" "$W/z" P3b 1260 860 1480 1135
$CM "$W/z/up_P3b.png" "$W/z/gem_P3cA1.png" "$W/z/cm_P3cA1.png"
$Z paste "$W/base2.png" "$W/z" P3b "$W/z/cm_P3cA1.png" "$W/base3.png" "1290,880,1455,1130"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
b = Image.open(f'{W}/base3.png').convert('RGB'); b.paste(Image.open(f'{D}/L35c_src/P3fix.webp').convert('RGB'), (1302, 875)); b.save(f'{W}/base3.png')
PY
# 물고기 · 밀 농부
$Z crop "$W/base3.png" "$W/z" Z11c 1240 210 1900 580
$Z crop "$W/base3.png" "$W/z" P5d 1660 600 2048 1144
$Z crop "$W/base3.png" "$W/z" Z3 560 450 1000 800
$Z crop "$W/base3.png" "$W/z" Z8 1180 580 1540 760
$CM "$W/z/up_Z11c.png" "$W/z/gem_Z11cA1.png" "$W/z/cm_Z11cA1.png"
$Z paste "$W/base3.png" "$W/z" Z11c "$W/z/cm_Z11cA1.png" "$W/base4.png" "1425,310,1830,482"
$CM "$W/z/up_P5d.png" "$W/z/gem_P5eB1.png" "$W/z/cm_P5eB1.png"
$Z paste "$W/base4.png" "$W/z" P5d "$W/z/cm_P5eB1.png" "$W/t_P5e.png" "1705,690,2048,1144;1680,863,1714,1144" --R=0
$DF "$W/t_P5e.png" "$W/t_P5e.png" "1676,1076;1706,1037;1745,1048;1757,1066;1762,1087;1800,1089;1800,1144;1676,1144" 2.5 0.6
$DF "$W/t_P5e.png" "$W/t_P5e.png" "1781,1129;1797,1129;1797,1144;1781,1144" 1.2 0.0
$DF "$W/t_P5e.png" "$W/base5.png" "1678,1120;1690,1120;1690,1140;1678,1140" 1.2 0.0
# 부비새 · 언덕
$CM "$W/z/up_Z3.png" "$W/z/gem_Z3A1.png" "$W/z/cm_Z3A1.png"
$Z paste "$W/base5.png" "$W/z" Z3 "$W/z/cm_Z3A1.png" "$W/base6.png" "655,478,955,715"
$Z crop "$W/base5.png" "$W/z" Z15b 240 0 1060 420
$CM "$W/z/up_Z15b.png" "$W/z/gem_Z15bB1.png" "$W/z/cm_Z15bB1.png"
$Z paste "$W/base6.png" "$W/z" Z15b "$W/z/cm_Z15bB1.png" "$W/base7.png" "262,0,880,262"
# 물목 · 파리
$Z crop "$W/base6.png" "$W/z" Z14b 1100 30 1640 300
$CM "$W/z/up_Z14b.png" "$W/z/gem_Z14bA1.png" "$W/z/cm_Z14bA1.png"
$Z paste "$W/base7.png" "$W/z" Z14b "$W/z/cm_Z14bA1.png" "$W/t_Z14b.png" "1180,100,1640,200;1240,200,1640,248"
$Z crop "$W/base7.png" "$W/z" Z1b 0 0 560 560
$Z crop "$W/base7.png" "$W/z" Z5b 300 430 780 660
$CM "$W/z/up_Z1b.png" "$W/z/gem_Z1bB1.png" "$W/z/cm_Z1bB1.png"
$Z paste "$W/t_Z14b.png" "$W/z" Z1b "$W/z/cm_Z1bB1.png" "$W/base8.png" "150,190,500,395"
$Z crop "$W/t_Z14b.png" "$W/z" Z14c 1100 30 1720 300
$Z crop "$W/base8.png" "$W/z" Z2b 40 480 720 1100
$Z crop "$W/base8.png" "$W/z" Z4b 470 600 760 760
$CM "$W/z/up_Z14c.png" "$W/z/gem_Z14cA1.png" "$W/z/cm_Z14cA1.png"
$Z paste "$W/base8.png" "$W/z" Z14c "$W/z/cm_Z14cA1.png" "$W/base9.png" "1570,100,1718,250;1195,188,1242,216"
# 벤치 · 성게 · 달팽이 · 도롱뇽
$CM "$W/z/up_Z2b.png" "$W/z/gem_Z2bB1.png" "$W/z/cm_Z2bB1.png"
$Z paste "$W/base9.png" "$W/z" Z2b "$W/z/cm_Z2bB1.png" "$W/base10.png" "60,495,300,812"
$CM "$W/z/up_Z5b.png" "$W/z/gem_Z5bA1.png" "$W/z/cm_Z5bA1.png"
$Z paste "$W/base10.png" "$W/z" Z5b "$W/z/cm_Z5bA1.png" "$W/base11.png" "320,462,645,632"
$CM "$W/z/up_Z4b.png" "$W/z/gem_Z4bB1.png" "$W/z/cm_Z4bB1.png"
$Z paste "$W/base11.png" "$W/z" Z4b "$W/z/cm_Z4bB1.png" "$W/base12.png" "520,624,668,692"
$CM "$W/z/up_Z8.png" "$W/z/gem_Z8A1.png" "$W/z/cm_Z8A1.png"
$Z paste "$W/base12.png" "$W/z" Z8 "$W/z/cm_Z8A1.png" "$W/base13.png" "1255,628,1432,742"
# 일치 검사 1회 뒤 — 젊은이 팔꿈치(P5d 상자 가장자리에 깎인 것)를 base4 에서 되돌림 · 늘어진 새끼에 얼룩점(PIL)
cp "$W/base13.png" "$W/t_fix1.png"
python3 "$D/restore_poly.py" "$W/base4.png" "$W/t_fix1.png" "1674,861;1701,861;1697,879;1691,893;1690,912;1674,912" 1.0
python3 "$D/L35c_pil.py" "$W/t_fix1.png" "$W/t_fix2.png"
#  Z8A2 = 도롱뇽 부모가 고개를 숙여 눈물을 글썽이며 새끼를 내려다봄(Z8A1 과 같은 대화) · Z5cB1 = 정자가 모두 알 쪽으로 가서 별 모양 불꽃과 함께 튕겨 나감
#  Z9A1 = 갈색 노새를 말 몸 · 갈기 · 꼬리 + 당나귀 귀로 · 유모차 덮개를 젖혀 텅 빈 속에 거미줄
$Z crop "$W/t_fix2.png" "$W/z" Z5c 300 430 780 660
$CM "$W/z/up_Z8.png" "$W/z/gem_Z8A2.png" "$W/z/cm_Z8A2.png"
$Z paste "$W/t_fix2.png" "$W/z" Z8 "$W/z/cm_Z8A2.png" "$W/base14.png" "1280,600,1425,666"
$Z crop "$W/base14.png" "$W/z" Z9 1480 370 2048 790
$CM "$W/z/up_Z5c.png" "$W/z/gem_Z5cB1.png" "$W/z/cm_Z5cB1.png"
$Z paste "$W/base14.png" "$W/z" Z5c "$W/z/cm_Z5cB1.png" "$W/base15.png" "320,462,645,632"
$CM "$W/z/up_Z9.png" "$W/z/gem_Z9A1.png" "$W/z/cm_Z9A1.png"
$Z paste "$W/base15.png" "$W/z" Z9 "$W/z/cm_Z9A1.png" "$W/base16.png" "1490,395,1895,688"
#  Z14dB2 = 물속 돌담 틈을 넓혀 얼룩 새끼 셋이 줄지어 지나감(같은 대화 두 번째 — 처음엔 셋째가 담에 겹침)
$Z crop "$W/base16.png" "$W/z" Z14d 1100 30 1720 300
$CM "$W/z/up_Z14d.png" "$W/z/gem_Z14dB2.png" "$W/z/cm_Z14dB2.png"
$Z paste "$W/base16.png" "$W/z" Z14d "$W/z/cm_Z14dB2.png" "$W/base17.png" "1520,172,1712,250"
#  Z2cA1 = 해바라기 둘을 지우고 오른쪽 화분 나무줄기에 울어 대는 매미(해바라기 = 팽압 L53b 예약 — 내 설계의 「피할 것」을 어겨 갈았다)
$Z crop "$W/base17.png" "$W/z" Z2c 40 480 720 1100
$CM "$W/z/up_Z2c.png" "$W/z/gem_Z2cA1.png" "$W/z/cm_Z2cA1.png"
$Z paste "$W/base17.png" "$W/z" Z2c "$W/z/cm_Z2cA1.png" "$W/base18.png" "60,495,335,812"
#  Z7A2 = 할머니가 상 위에서 쥔 붉은 실패 · 왼쪽으로 뻗어 끊어진 실 둘 · 오른쪽으로 뻗어 두 도롱뇽 앞발을 묶은 실(같은 대화 두 번째 — 처음엔 구도가 바뀜)
#    일치 검사 2회 (마)「사건 그림과 소품 전시 사이」 → 짝마다 따로 놀던 장면을 할머니의 붉은 실 하나로 잇고 상 = 접합 전 · 후의 금을 실로 보이게
$Z crop "$W/base18.png" "$W/z" Z7 880 380 1460 790
$CM "$W/z/up_Z7.png" "$W/z/gem_Z7A2.png" "$W/z/cm_Z7A2.png"
$Z paste "$W/base18.png" "$W/z" Z7 "$W/z/cm_Z7A2.png" "$W/base19.png" "930,565,1400,750"
#  일치 검사 3회 뒤 — Z5dB1 = 알 여섯 · 정자 다섯을 크게, 정자마다 알에 부딪혀 굵은 곡선을 그리며 튕겨 나감(작은 불꽃이 「수정 성공」으로 읽힐 수 있다는 지적)
#    P2A2 = 엄마가 두 팔을 들어 자루 둘을 머리 양옆에 다 보이게(같은 대화 두 번째 — 처음엔 그대로 돌려줌)
$Z crop "$W/base19.png" "$W/z" Z5d 320 440 660 640
$Z crop "$W/base19.png" "$W/z" P2 1330 740 1600 1110
$CM "$W/z/up_Z5d.png" "$W/z/gem_Z5dB1.png" "$W/z/cm_Z5dB1.png"
$Z paste "$W/base19.png" "$W/z" Z5d "$W/z/cm_Z5dB1.png" "$W/base20.png" "362,462,580,572"
$CM "$W/z/up_P2.png" "$W/z/gem_P2A2.png" "$W/z/cm_P2A2.png"
$Z paste "$W/base20.png" "$W/z" P2 "$W/z/cm_P2A2.png" "$W/base21.png" "1362,772,1512,925"
#  일치 검사 4회 뒤 — P6B1 = 수레의 낟알 더미 → 이삭이 늘어진 귀리 다발 · 잎채소 → 끈으로 묶은 큰 담뱃잎 다발(푸른 잎 · 말린 금빛 잎) — 「귀리 · 담배로 안 읽힘」(3 · 4회)
$Z crop "$W/base21.png" "$W/z" P6 1690 840 2048 1144
$CM "$W/z/up_P6.png" "$W/z/gem_P6B1.png" "$W/z/cm_P6B1.png"
$Z paste "$W/base21.png" "$W/z" P6 "$W/z/cm_P6B1.png" "$W/base22.png" "1738,840,2048,1048"
cp "$W/base22.png" "$W/final.png"
echo "→ $W/final.png"
