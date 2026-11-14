#!/bin/bash
# L13b_build.sh <작업 폴더> — L13b 그림을 Gemini 원본(L13b_src/ · L13a_src/E1)에서 다시 만든다(같은 픽셀).
#  바탕 그림이 없다 — 하늘 · 회색 돌 성벽 · 무너진 틈은 s13_lib.castle_wall()(L13a 와 같은 성) · 진홍 호스 · 물줄기 셋 · 인터폰 판 · 줄 · 전선 · 배지는 L13b_pil.py 가 그린다.
#  조각 그림(크림빛 민 바탕 — 프롬프트 L13b_prompt_sprites.txt): L13a 의 인물 · 물건 조각을 Gemini 에 올려 「같은 인물을 이렇게」로 다시 그리게 했다
#   U1(흰 덩이 셋 — 팔로 감쌈 · 배 창 속 비눗방울 · 레몬 물과 합쳐짐) · U2(세균을 베어 문 파리채 경비 · 젖은 세균을 든 작은 흰 덩이)
#   U3(성냥을 들고 세균을 밀어내는 뚱보 경비) · U4B(가시 박힌 손가락을 받쳐 든 주민) · U5(앞벽을 뗀 집 — 망토 · 깍둑썰기 기계 · 집낙지)
#   U6(확성기 단 이웃 집과 판자 대는 주민 · 수화기에 외치는 주민) · U7(부풀어 새는 호스 토막 · 경비가 비집고 나오는 호스 토막)
#   U8(지친 경비 둘과 죽은 세균의 누런 웅덩이 — 원본 크기 JPEG) · U9(물길 셋 → 저수지 + 보 · 구멍 난 세균) · U10(만년필 든 달팽이 · 튤립)
#   · L13a_src/E1(무너진 돌덩이).
set -e
D="$(cd "$(dirname "$0")" && pwd)"; W="${1:-.}"; mkdir -p "$W/z"
python3 - "$D" "$W" <<'PY'
import sys
from PIL import Image
D, W = sys.argv[1], sys.argv[2]
for n in ('U1', 'U2', 'U3', 'U4B', 'U5', 'U6', 'U7', 'U9', 'U10'): Image.open(f'{D}/L13b_src/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
Image.open(f'{D}/L13b_src/U8.jpg').convert('RGB').save(f'{W}/z/gem_U8.png')
Image.open(f'{D}/L13a_src/E1.webp').convert('RGB').save(f'{W}/z/gem_E1.png')
PY
python3 "$D/L13b_pil.py" "$W/z" "$W/final.png"
echo "→ $W/final.png"
