#!/bin/bash
# L22e_build.sh <작업 폴더> — L22e 그림을 Gemini 원본(L22e_src/)에서 다시 만든다(같은 픽셀 · 2026-11-16 확인).
#  S1 = Gemini 가 장면 하나를 통째로 그린 바탕(1024 × 572 — 출연진 그림 cast_ref 를 올리고 「박람회 정원의 거목을 베어 낸 아침」 · 2048 로 키움)
#  ZBB2 = 화단 흙 경계(잎 모자 일꾼이 줄로 내리는 갈색 자루 · 뿌리 다리 일꾼) · ZCB1 = 그루터기 단면(초록 고리 일꾼 · 번갈아 두른 테 · 심판의 넥타이 없앰)
#  ZAA4 = 분수대(돌 연못 + 판자 물통 · 사과 · 포도) · 선반의 큰 병 아홉 · 작은 스포이트 병 여덟(파라솔 없음 · 의사 빠짐)
#  ZDA2 = 작업대 — 왼쪽 병 화초만 시듦 · 뒤 선반 없앰 · 넘어진 빈 병 셋(호박색 · 성냥 · 칼) → 바닥에 굴러다니던 성냥 · 칼은 deckfill 로 지움
#  ZGA1 = 고리 김밥(오이 안 · 햄 밖 여덟 짝 · 가운데 밥) · ZHB1 = 대나무 마디 새싹(잎겨드랑이마다 졸린 눈 · 꼭대기 큰 눈)
#  ZEA1 = 흙 — 왼쪽 위 부식질 · 고리 사슬 없앰 · 바구니 든 뿌리 다리 꼬마 · 점토 조각의 칼 · 자갈 · 은구슬 · 뿌리털로 날아가는 칼과 물보라
#  ZFB2 = 세로로 가른 굵은 뿌리(청록 · 분홍 다발 · 검은 안감 · 속에서 뚫고 나오는 곁뿌리)
#  ZIA1 · ZJB1 = 파라솔 둘 지움(【펴 든 파라솔】 = 파라믹소 예약 — 깃발 줄은 그대로 잇기)
#  ZKA1 = 딸기 밑 부식질을 오른쪽 끝까지(x 1820 의 세로 이음매) · 진땀 흘리는 꼬마
#  ZLB1 = 딸기 포기의 가로 이음매(ZAA4 상자 아래 가장자리 y 470) — Gemini 가 띠를 세로로 4 % 늘려 그려 --affine 으로 붙임 → L22e_pil.py = 유리 윗테의 턱(x 1700)
#  ZMA1 = 바구니 속을 또렷이(봉한 물병 · 칼 · 자갈 · 빨간 머리 성냥) · ZNB1 = 새삼이 말라 비틀어져 조각이 떨어짐 · ZOA2 = 통처럼 불룩한 판자 물통 · 연못 물방울이 물통으로(겉에 흘러내린 물은 같은 대화에서 지움)
#  L22e_tubes.py = 초록 고리 안쪽 토막은 청록 · 바깥쪽은 분홍(Gemini 가 S1 · ZP 두 번 섞어 그려 빛깔만 바꿈)
#  ZQB1 = 뿌리털을 짧고 곧은 털 솔로(갈라진 흰 선이 곁뿌리로 읽힘)
#  ⚠ 구역마다 처음 오린 바탕에서 오린다(뒤 편집의 상자 가장자리 번짐이 오림에 섞이면 픽셀이 달라진다 — 배운 것 (62)).
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
Image.open(f'{D}/L22e_src/S1.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZBB2', 'ZCB1', 'ZAA4', 'ZDA2', 'ZGA1', 'ZHB1', 'ZEA1', 'ZFB2', 'ZIA1', 'ZJB1', 'ZKA1', 'ZLB1', 'ZMA1', 'ZNB1', 'ZOA2', 'ZQB1'):
    Image.open(f'{D}/L22e_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"; DF="python3 $D/deckfill.py"
# 분수대 · 선반(ZA) · 화단 흙 경계(ZB) — 둘 다 base0 에서 오림
$Z crop "$W/base0.png" "$W/z" ZA 1300 40 2048 470
$Z crop "$W/base0.png" "$W/z" ZB 1380 420 2048 860
$CM "$W/z/up_ZB.png" "$W/z/gem_ZBB2.png" "$W/z/cm_ZBB2.png"
$Z paste "$W/base0.png" "$W/z" ZB "$W/z/cm_ZBB2.png" "$W/base1.png" "1570,560,1810,835"
# 그루터기 단면(ZC) — base1 에서
$Z crop "$W/base1.png" "$W/z" ZC 660 180 1340 620
$CM "$W/z/up_ZC.png" "$W/z/gem_ZCB1.png" "$W/z/cm_ZCB1.png"
$Z paste "$W/base1.png" "$W/z" ZC "$W/z/cm_ZCB1.png" "$W/t_ZC.png" "675,185,1330,600"
$CM "$W/z/up_ZA.png" "$W/z/gem_ZAA4.png" "$W/z/cm_ZAA4.png"
$Z paste "$W/t_ZC.png" "$W/z" ZA "$W/z/cm_ZAA4.png" "$W/base2.png" "1330,150,1700,420;1700,120,2048,470"
# 작업대(ZD) — base2 에서
$Z crop "$W/base2.png" "$W/z" ZD 1130 790 1830 1144
$CM "$W/z/up_ZD.png" "$W/z/gem_ZDA2.png" "$W/z/cm_ZDA2.png"
$Z paste "$W/base2.png" "$W/z" ZD "$W/z/cm_ZDA2.png" "$W/t_ZD.png" "1270,860,1800,1144"
$DF "$W/t_ZD.png" "$W/t_ZD.png" "1663,1118;1694,1124;1695,1135;1665,1128" 1.2 0.0
$DF "$W/t_ZD.png" "$W/t_ZD.png" "1704,1110;1717,1109;1755,1123;1755,1136;1741,1137;1703,1120" 1.2 0.0
$DF "$W/t_ZD.png" "$W/base3.png" "1664,1119;1678,1121;1679,1127;1664,1125" 1.0 0.0
# 김밥(ZG) · 새싹(ZH) — base3 에서
$Z crop "$W/base3.png" "$W/z" ZG 700 820 1180 1144
$Z crop "$W/base3.png" "$W/z" ZH 940 480 1240 900
$CM "$W/z/up_ZG.png" "$W/z/gem_ZGA1.png" "$W/z/cm_ZGA1.png"
$Z paste "$W/base3.png" "$W/z" ZG "$W/z/cm_ZGA1.png" "$W/t_ZG.png" "740,930,1080,1110"
$CM "$W/z/up_ZH.png" "$W/z/gem_ZHB1.png" "$W/z/cm_ZHB1.png"
$Z paste "$W/t_ZG.png" "$W/z" ZH "$W/z/cm_ZHB1.png" "$W/base4.png" "1000,500,1120,860"
# 흙(ZE) · 가른 뿌리(ZF) — base4 에서
$Z crop "$W/base4.png" "$W/z" ZE 1330 520 1820 900
$Z crop "$W/base4.png" "$W/z" ZF 1700 560 2048 900
$CM "$W/z/up_ZE.png" "$W/z/gem_ZEA1.png" "$W/z/cm_ZEA1.png"
$Z paste "$W/base4.png" "$W/z" ZE "$W/z/cm_ZEA1.png" "$W/base5.png" "1390,540,1820,800"
$CM "$W/z/up_ZF.png" "$W/z/gem_ZFB2.png" "$W/z/cm_ZFB2.png"
$Z paste "$W/base5.png" "$W/z" ZF "$W/z/cm_ZFB2.png" "$W/base6.png" "1870,640,2040,830"
# 파라솔 둘(ZI · ZJ) — base6 에서
$Z crop "$W/base6.png" "$W/z" ZI 1500 0 2048 330
$Z crop "$W/base6.png" "$W/z" ZJ 1300 700 1840 1000
$CM "$W/z/up_ZI.png" "$W/z/gem_ZIA1.png" "$W/z/cm_ZIA1.png"
$Z paste "$W/base6.png" "$W/z" ZI "$W/z/cm_ZIA1.png" "$W/t_ZI.png" "1600,10,2048,240"
$CM "$W/z/up_ZJ.png" "$W/z/gem_ZJB1.png" "$W/z/cm_ZJB1.png"
$Z paste "$W/t_ZI.png" "$W/z" ZJ "$W/z/cm_ZJB1.png" "$W/base7.png" "1340,790,1830,920"
# 부식질 이음매(ZK) — base7 에서
$Z crop "$W/base7.png" "$W/z" ZK 1640 470 2048 720
$CM "$W/z/up_ZK.png" "$W/z/gem_ZKA1.png" "$W/z/cm_ZKA1.png"
$Z paste "$W/base7.png" "$W/z" ZK "$W/z/cm_ZKA1.png" "$W/base8.png" "1792,537,2048,640;1800,640,1952,714"
# 딸기 이음매(ZL) · 바구니(ZM) — base8 에서
$Z crop "$W/base8.png" "$W/z" ZL 1560 330 2048 590
$Z crop "$W/base8.png" "$W/z" ZM 1380 560 1640 820
$CM "$W/z/up_ZL.png" "$W/z/gem_ZLB1.png" "$W/z/cm_ZLB1.png"
$Z paste "$W/base8.png" "$W/z" ZL "$W/z/cm_ZLB1.png" "$W/t_ZLa.png" "1566,395,2048,533" --affine
python3 "$D/L22e_pil.py" "$W/t_ZLa.png" "$W/t_ZLp.png"
$CM "$W/z/up_ZM.png" "$W/z/gem_ZMA1.png" "$W/z/cm_ZMA1.png"
$Z paste "$W/t_ZLp.png" "$W/z" ZM "$W/z/cm_ZMA1.png" "$W/base9.png" "1484,660,1566,736"
# 새삼(ZN) · 판자 물통(ZO) — base9 에서 · 그다음 관 토막 빛깔
$Z crop "$W/base9.png" "$W/z" ZN 300 240 660 620
$Z crop "$W/base9.png" "$W/z" ZO 1300 100 1760 400
$CM "$W/z/up_ZN.png" "$W/z/gem_ZNB1.png" "$W/z/cm_ZNB1.png"
$Z paste "$W/base9.png" "$W/z" ZN "$W/z/cm_ZNB1.png" "$W/t_ZN.png" "362,305,592,602"
$CM "$W/z/up_ZO.png" "$W/z/gem_ZOA2.png" "$W/z/cm_ZOA2.png"
$Z paste "$W/t_ZN.png" "$W/z" ZO "$W/z/cm_ZOA2.png" "$W/t_ZO.png" "1450,105,1700,368"
python3 "$D/L22e_tubes.py" "$W/t_ZO.png" "$W/base10.png"
# 뿌리털(ZQ) — base10 에서: 곁뿌리처럼 갈라진 흰 선 → 짧고 곧은 털 솔(일치 검사 1회 △ 「뿌리털이 곁뿌리처럼 보인다」)
$Z crop "$W/base10.png" "$W/z" ZQ 1560 540 1860 760
$CM "$W/z/up_ZQ.png" "$W/z/gem_ZQB1.png" "$W/z/cm_ZQB1.png"
$Z paste "$W/base10.png" "$W/z" ZQ "$W/z/cm_ZQB1.png" "$W/final.png" "1600,585,1830,712"
echo "L22e_build ok → $W/final.png"
