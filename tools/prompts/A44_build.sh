#!/bin/sh
# A44_build.sh <작업 폴더> — 44장 덧붙임(2026-11-15 · Opus 5.5)의 그림 넷(L17a · L17c · L17d · L17e)을 같은 픽셀로 다시 만든다.
#   바탕 = 덧붙임 전 그림(커밋 2e7b66b) · Gemini 조각 = A44_src/*.webp → colormatch → zone3 paste → A44_fix.py(L17c 김 끝 지움 · 꺾쇠 / L17d 소금 알갱이 · 칼).
set -e
W=${1:?작업 폴더}; P=/tmp/b2/tools/prompts
mkdir -p "$W"; cd "$W"
for L in L17a L17c L17d L17e; do git -C /tmp/b2 show 2e7b66b:lesson/img/$L.webp > ${L}_base0.webp; done
python3 -c "
from PIL import Image
for L in ['L17a','L17c','L17d','L17e']: Image.open(L+'_base0.webp').convert('RGB').save(L+'_base0.png')
for n in ['CA2','EA2','DA2','DN','AF']: Image.open('$P/A44_src/'+n+'.webp').save('gem_'+n+'.png')
"
# L17c — 물통 모서리의 레몬 병 · 선반의 마개 병 둘(NH₄⁺ 가두기)
python3 $P/zone3.py crop L17c_base0.png . CA 0 330 800 780
python3 $P/colormatch.py up_CA.png gem_CA2.png gemc_CA2.png
python3 $P/zone3.py paste L17c_base0.png . CA gemc_CA2.png L17c_b2.png "195,335,480,482;70,595,225,775" 28
python3 $P/A44_fix.py L17c L17c_b2.png L17c_final.png
# L17e — 운하 앞 돌벽의 액자(K 보존 이뇨제)
python3 $P/zone3.py crop L17e_base0.png . EA 1188 744 1899 1144
python3 $P/colormatch.py up_EA.png gem_EA2.png gemc_EA2.png
python3 $P/zone3.py paste L17e_base0.png . EA gemc_EA2.png L17e_final.png "1412,806,1764,1144" 28
# L17d — 들머리 솔털 · 소금 섞인 물줄기(근위 등삼투) → NHE3 기계 · 레몬 · 분필 · 연기 · 빨간 드럼
python3 $P/zone3.py crop L17d_base0.png . DA 0 0 560 315
python3 $P/colormatch.py up_DA.png gem_DA2.png gemc_DA2.png
python3 $P/zone3.py paste L17d_base0.png . DA gemc_DA2.png L17d_b1.png "0,0,545,172;0,168,400,315" 28
python3 $P/A44_fix.py L17d L17d_b1.png L17d_b2.png
python3 $P/zone3.py crop L17d_b2.png . DN 420 0 1060 360
python3 $P/colormatch.py up_DN.png gem_DN.png gemc_DN.png
python3 $P/zone3.py paste L17d_b2.png . DN gemc_DN.png L17d_final.png "425,100,650,355;650,95,1005,300" 28
# L17a — 폭포를 앨범 방패로 되미는 사내(여과를 막는 두 힘)
python3 $P/zone3.py crop L17a_base0.png . AF 240 170 880 530
python3 $P/colormatch.py up_AF.png gem_AF.png gemc_AF.png
python3 $P/zone3.py paste L17a_base0.png . AF gemc_AF.png L17a_final.png "425,325,605,505" 28
echo "→ $W/L17{a,c,d,e}_final.png"
